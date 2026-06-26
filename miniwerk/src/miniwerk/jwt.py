"""JWT wrappers"""

import asyncio
import logging
import stat
from pathlib import Path

from multikeyjwt import Issuer, Verifier
from multikeyjwt.keygen import generate_keypair

from .config import MWConfig

LOGGER = logging.getLogger(__name__)
PUBDIR_MODE = stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH | stat.S_IXGRP | stat.S_IXOTH
PRIVDIR_MODE = stat.S_IRWXU


async def check_create_keypair() -> tuple[Path, Path]:
    """Check if we have keypair, if not create it, returns the file paths"""
    config = MWConfig.singleton()
    privkeypath = config.data_path / "private" / "jwt.key"
    privdir = privkeypath.parent
    privdir.mkdir(parents=True, exist_ok=True)
    privdir.chmod(PRIVDIR_MODE)
    pubkeypath = config.data_path / "publickeys" / "kraftwerk.pub"
    pubdir = pubkeypath.parent
    pubdir.mkdir(parents=True, exist_ok=True)
    pubdir.chmod(PUBDIR_MODE)

    if privkeypath.exists() and pubkeypath.exists():
        return privkeypath, pubkeypath

    LOGGER.info("Generating keypair, this will take a moment")
    _, cpk = await asyncio.get_event_loop().run_in_executor(None, generate_keypair, privkeypath, None)
    pubkeypath.write_bytes(cpk.read_bytes())
    LOGGER.info(f"Wrote {pubkeypath}")

    return privkeypath, pubkeypath


async def get_issuer() -> Issuer:
    """Get JWT issuer, init keys if needed"""
    privkeypath, _ = await check_create_keypair()
    return Issuer(privkeypath=privkeypath, keypasswd=None)


async def get_verifier() -> Verifier:
    """Get JWT verifier, init keys if needed"""
    _, pubkeypath = await check_create_keypair()
    return Verifier(pubkeypath=pubkeypath.parent)
