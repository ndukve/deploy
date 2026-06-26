"""MediaMTX control API abstraction"""

from typing import Optional, ClassVar, Sequence, Dict, Any
import logging
from dataclasses import dataclass
import ssl
from pathlib import Path

import aiohttp
from libpvarki.mtlshelp.context import get_ca_context

from .config import RMMTXSettings

LOGGER = logging.getLogger(__name__)


@dataclass
class MediaMTXControl:
    """MediaMTX control API abstraction"""

    _singleton: ClassVar[Optional["MediaMTXControl"]] = None

    @classmethod
    def singleton(cls) -> "MediaMTXControl":
        """Return singleton"""
        if not MediaMTXControl._singleton:
            MediaMTXControl._singleton = MediaMTXControl()
        return MediaMTXControl._singleton

    def get_session(self) -> aiohttp.ClientSession:
        """Get session"""
        cnf = RMMTXSettings.singleton()
        auth = aiohttp.BasicAuth(login=cnf.api_username, password=cnf.api_password)
        cadir = Path("/ca_public")
        if cadir.is_dir():
            ctx = get_ca_context(ssl.Purpose.SERVER_AUTH, cadir)
            conn = aiohttp.TCPConnector(ssl=ctx)
            return aiohttp.ClientSession(
                connector=conn, auth=auth, base_url=cnf.api_url, raise_for_status=True
            )
        # Fallback
        return aiohttp.ClientSession(
            auth=auth, base_url=cnf.api_url, raise_for_status=True
        )

    async def ensure_srt_pass(self) -> bool:
        """Ensure SRT password for authentication is set to server config"""
        cnf = RMMTXSettings.singleton()
        if cnf.srt_read_password == "CHANGEME":  # pragma: allowlist secret #nosec
            raise ValueError("SRT read password must not be default")
        if cnf.srt_pub_password == "CHANGEME":  # pragma: allowlist secret #nosec
            raise ValueError("SRT pub password must not be default")
        if cnf.srt_pub_password == cnf.srt_read_password:
            raise ValueError("SRT read and publish password must be different")
        async with self.get_session() as session:
            resp = await session.patch(
                "/v3/config/pathdefaults/patch",
                json={
                    "srtPublishPassphrase": cnf.srt_pub_password,
                    "srtReadPassphrase": cnf.srt_read_password,
                },
                raise_for_status=False,
            )
            if resp.status != 200:
                payload = await resp.json()
                LOGGER.error("Patch failed: %s", payload)
                return False
            resp = await session.get("/v3/config/pathdefaults/get")
            cfg = await resp.json()
            if cfg.get("srtPublishPassphrase") != cnf.srt_pub_password:
                LOGGER.error("Read back srtPublishPassphrase not what we expect")
                return False
            if cfg.get("srtReadPassphrase") != cnf.srt_read_password:
                LOGGER.error("Read back srtReadPassphrase not what we expect")
                return False
            return True

    async def get_paths(
        self, username: str, password: str = ""
    ) -> Sequence[Dict[str, Any]]:
        """Get active paths and generate their corresponding urls for each protocol
        insert_credentials MUST be in format: username:password@"""
        ret = []
        cnf = RMMTXSettings.singleton()
        async with self.get_session() as session:
            resp = await session.get("/v3/paths/list", params={"itemsPerPage": 1000})
            payload = await resp.json()
            for plitem in payload["items"]:
                path = f"/{plitem['name']}"
                item = {
                    "path": path,
                    "urls": {},
                }
                for pname, pinfo in cnf.protocols.items():
                    if pname == "rtmps":
                        url = f"{pinfo.proto}://{cnf.mtx_address}:{pinfo.port}{path}?user={username}&pass={password}"
                    elif pname == "srt":
                        clean_path = path.lstrip("/")
                        url = (
                            f"{pinfo.proto}://{cnf.mtx_address}:{pinfo.port}"
                            f"?streamid=read:{clean_path}:{username}:{password}&passphrase={cnf.srt_read_password}"
                        )
                    else:
                        url = f"{pinfo.proto}://{username}:{password}@{cnf.mtx_address}:{pinfo.port}{path}"
                    item["urls"][pname] = url  # type: ignore[index]
                ret.append(item)
        return ret
