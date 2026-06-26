"""Wrap mkcert calls"""

import logging
from pathlib import Path

from .config import KeyType, MWConfig
from .helpers import call_cmd, certs_copy, mkcert_ca_cert
from .jwt import PRIVDIR_MODE

LOGGER = logging.getLogger(__name__)


async def call_mkcert(config: MWConfig) -> tuple[int, list[str]]:
    """Construct Cermkcerttbot command and call the entrypoint, returns the args for easier unit testing"""
    config.mk_cert_dir.mkdir(parents=True, exist_ok=True)
    config.mk_cert_dir.chmod(PRIVDIR_MODE)
    args: list[str] = [
        "--cert-file",
        str(config.mk_cert_dir / "cert.pem"),
        "--key-file",
        str(config.mk_cert_dir / "privkey.pem"),
    ]
    if config.keytype == KeyType.ECDSA:
        args.append("--ecdsa")
    args.append(" ".join(config.fqdns))

    if config.ci:
        LOGGER.info("Running under CI, not actually calling mkcert")
        return 0, args

    cmd = "mkcert " + " ".join(args)
    retcode = await call_cmd(cmd)
    if retcode == 0:
        fullchain = (config.mk_cert_dir / "cert.pem").read_bytes()
        fullchain += mkcert_ca_cert().read_bytes()
        (config.mk_cert_dir / "fullchain.pem").write_bytes(fullchain)
    return retcode, args


async def get_mk_certs() -> Path:
    """Get certs from mkcert, copy them to the configured path, return configured path"""
    config = MWConfig.singleton()
    retcode, _ = await call_mkcert(config)
    if retcode != 0:
        raise RuntimeError("mkcert returned error")
    copydir = config.le_copy_path / config.le_cert_name
    certs_copy(copydir, config.mk_cert_dir)
    pubdir = Path("/ca_public")
    pubdir.mkdir(parents=True, exist_ok=True)
    capath = pubdir / "miniwerk_ca.pem"
    capath.write_bytes(mkcert_ca_cert().read_bytes())
    LOGGER.info(f"Wrote {capath}")
    return copydir
