"""helpers"""

from typing import Tuple, List, Optional
import logging
import asyncio
import base64
import enum
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import serialization

from libpvarki.shell import call_cmd

from .config import RESTConfig

LOGGER = logging.getLogger(__name__)


def cfssl_loglevel() -> int:
    """Return CFSSL loglevel 0-5"""
    our_level = LOGGER.getEffectiveLevel()
    if our_level < 10:
        return 0
    return round(our_level / 10) - 1


class CRLType(enum.IntEnum):
    """Root or intermediate (or why not both)"""

    ROOT = 1
    INTERMEDIATE = 2
    MERGED = 3


def crlpaths(crltype: CRLType = CRLType.MERGED) -> Tuple[Path, Path]:
    """Path to CRL files by CRLType"""
    cnf = RESTConfig.singleton()
    cnf.crl = Path(cnf.crl)
    der_path = cnf.crl.parent / f"{cnf.crl.stem}_{crltype.name.lower()}.der"
    pem_path = cnf.crl.parent / f"{cnf.crl.stem}_{crltype.name.lower()}.pem"
    return der_path, pem_path


async def merge_crl() -> int:
    """Merge CRL files"""
    cnf = RESTConfig.singleton()
    cnf.crl = Path(cnf.crl)
    root_der, root_pem = crlpaths(CRLType.ROOT)
    intermediate_der, intermediate_pem = crlpaths(CRLType.INTERMEDIATE)
    retcodes = await asyncio.gather(
        dump_crl(CRLType.ROOT), dump_crl(CRLType.INTERMEDIATE)
    )
    for ret in retcodes:
        if ret != 0:
            return ret
    der_path = cnf.crl
    pem_path = cnf.crl.parent / f"{cnf.crl.stem}.pem"
    LOGGER.info("Writing {}".format(der_path))
    der_path.write_bytes(root_der.read_bytes() + intermediate_der.read_bytes())
    LOGGER.info("Writing {}".format(pem_path))
    pem_path.write_bytes(root_pem.read_bytes() + intermediate_pem.read_bytes())
    return 0


async def dump_crl(crltype: CRLType = CRLType.MERGED) -> int:
    """Dump CRL to shared directory, triggering reloads for everyone interested in it is beyond us though"""
    cnf = RESTConfig.singleton()
    cnf.crl = Path(cnf.crl)
    cnf.rootcacrt = Path(cnf.rootcacrt)
    cnf.rootcakey = Path(cnf.rootcakey)
    cnf.cacrt = Path(cnf.cacrt)
    cnf.cakey = Path(cnf.cakey)

    cafile: Optional[Path] = None
    cakey: Optional[Path] = None

    # If merged is requested dump root and intermediate first, then merge them
    if crltype == CRLType.MERGED:
        return await merge_crl()

    if crltype == CRLType.ROOT:
        cafile = cnf.rootcacrt
        cakey = cnf.rootcakey
    if crltype == CRLType.INTERMEDIATE:
        cafile = cnf.cacrt
        cakey = cnf.cakey
    der_path, pem_path = crlpaths(crltype)

    if not cafile or not cakey:
        return -1

    args: List[str] = [
        str(cnf.cfssl),
        "crl",
        f"-db-config {cnf.dbconf}",
        f"-ca {cafile}",
        f"-ca-key {cakey}",
        f"-expiry {cnf.crl_lifetime}",
        f"-loglevel {cfssl_loglevel()}",
    ]
    cmd = " ".join(args)
    ret, der_b64, _ = await call_cmd(cmd)
    if ret != 0:
        return ret
    der_bytes = base64.b64decode(der_b64)
    LOGGER.info("Writing {}".format(der_path))
    der_path.write_bytes(der_bytes)
    LOGGER.debug("Parsing the CRL")
    crl = x509.load_der_x509_crl(der_bytes)
    LOGGER.info("Writing {}".format(pem_path))
    pem_path.write_bytes(crl.public_bytes(encoding=serialization.Encoding.PEM))
    return ret


async def refresh_oscp() -> int:
    """Call the OCSP refresh script"""
    cnf = RESTConfig.singleton()
    args: List[str] = [
        str(cnf.cfssl),
        "ocsprefresh",
        f"-db-config {cnf.dbconf}",
        f"-ca {cnf.cacrt}",
        f"-ca-key {cnf.cakey}",
        f"-responder {cnf.respcrt}",
        f"-responder-key {cnf.respkey}",
        f"-interval {cnf.ocsp_lifetime}",
        f"-loglevel {cfssl_loglevel()}",
    ]
    cmd = " ".join(args)
    LOGGER.info("Running ocsprefresh")
    ret, _, _ = await call_cmd(cmd)
    return ret
