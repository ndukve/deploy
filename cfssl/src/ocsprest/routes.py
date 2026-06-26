"""aiohttp routes"""

from typing import List, Dict, Any
import asyncio
import logging
import tempfile
import uuid
from pathlib import Path
import json
import time

from libadvian.tasks import TaskMaster
from libadvian.logging import init_logging
from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.responses import FileResponse

from ocsprest import __version__
from .config import RESTConfig
from .helpers import cfssl_loglevel, dump_crl, refresh_oscp

from libpvarki.shell import call_cmd

LOGGER = logging.getLogger(__name__)
ROUTER = APIRouter()


# FIXME: Use proper response schemas etc


@ROUTER.post("/refresh")
async def refresh_all(request: Request) -> Dict[str, Any]:
    """calls cfssl ocsprefresh"""
    _ = request
    # Don't bother waiting for the result
    TaskMaster.singleton().create_task(refresh_oscp())
    return {"success": True}


@ROUTER.post("/csr/sign")
async def csr_sign(request: Request) -> Dict[str, Any]:
    """Sign a CSR, we have to do it via CLI if we want CFSSL to add the Authority Information Access properties"""
    cnf = RESTConfig().singleton()
    data = await request.json()
    csrtmp = Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.csr"
    certtmp = csrtmp.with_suffix(".crt")
    try:
        csrtmp.write_text(data["certificate_request"])
        args_sign: List[str] = [
            str(cnf.cfssl),
            "sign",
            f"-config {cnf.conf}",
            f"-db-config {cnf.dbconf}",
            f"-ca {cnf.cacrt}",
            f"-ca-key {cnf.cakey}",
            f"-profile {data['profile']}",
            f"-csr {csrtmp}",
            f"-loglevel {cfssl_loglevel()}",
        ]
        cmd_sign = " ".join(args_sign)
        ret_sign, out_sign, _ = await call_cmd(cmd_sign)
        if ret_sign != 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": f"CFSSL CLI call to sign failed, code {ret_sign}. See server logs",
                },
            )
        resp_sign = json.loads(out_sign)
        if not data.get("bundle", True):
            return {"result": {"certificate": resp_sign["cert"].replace("\n", "\\n")}}
        # Create the bundle
        certtmp.write_text(resp_sign["cert"])
        args_bundle: List[str] = [
            str(cnf.cfssl),
            "bundle",
            f"-ca-bundle {cnf.rootcacrt}",
            f"-int-bundle {cnf.cacrt}",
            "-flavor optimal",
            f"-cert {certtmp}",
            f"-loglevel {cfssl_loglevel()}",
        ]
        cmd_bundle = " ".join(args_bundle)
        ret_bundle, out_bundle, _ = await call_cmd(cmd_bundle)
        if ret_bundle != 0:
            LOGGER.error(
                "CFSSL CLI call to bundle failed, returning the signed cert anyway"
            )
            return {"result": {"certificate": resp_sign["cert"].replace("\n", "\\n")}}
        resp_bundle = json.loads(out_bundle)
        return {"result": {"certificate": resp_bundle["bundle"].replace("\n", "\\n")}}
    finally:
        csrtmp.unlink()
        certtmp.unlink()


@ROUTER.post("/ocsp/sign")
async def ocsp_sign_one(request: Request) -> Dict[str, Any]:
    """calls cfssl ocspsign"""
    data = await request.json()
    certtmp = Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.pem"
    try:
        certtmp.write_text(data["cert"])
        status = data.get("status", "good")

        cnf = RESTConfig.singleton()
        args: List[str] = [
            str(cnf.cfssl),
            "ocspsign",
            f"-cert {certtmp}",
            f"-ca {cnf.cacrt}",
            f"-status={status}",
            f"-responder {cnf.respcrt}",
            f"-responder-key {cnf.respkey}",
            f"-loglevel {cfssl_loglevel()}",
        ]
        cmd = " ".join(args)
        LOGGER.info("Running ocspsign")
        ret, out, _ = await call_cmd(cmd)
        # TODO: How to inject the response to the database ??
        _resp = json.loads(out)
        if ret != 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": f"CFSSL CLI call to ocspsign failed, code {ret}. See server logs",
                },
            )
        # TODO: Should we return the signed OCSP response ? can rmapi do something with it ??
        return {"success": True}
    finally:
        certtmp.unlink()


@ROUTER.post("/dump_crl")
async def call_dump_crl(request: Request) -> Dict[str, Any]:
    """Dump CRL to shared directory, triggering reloads for everyone interested in it is beyond us though"""
    _ = request
    # Don't bother waiting for the result
    TaskMaster.singleton().create_task(dump_crl())
    return {"success": True}


@ROUTER.get("/crl/crl.pem")
async def get_crl_pem(request: Request) -> FileResponse:
    """Dump CRL to shared directory, triggering reloads for everyone interested in it is beyond us though"""
    _ = request
    ret = await dump_crl()
    if ret != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": f"CFSSL CLI call to dump_crl failed, code {ret}. See server logs",
            },
        )
    cnf = RESTConfig.singleton()
    cnf.crl = Path(cnf.crl)
    pem_path = cnf.crl.parent / f"{cnf.crl.stem}.pem"
    return FileResponse(pem_path, media_type="application/x-pem-file")


@ROUTER.get("/crl/crl.der")
async def get_crl_der(request: Request) -> FileResponse:
    """Dump CRL to shared directory, triggering reloads for everyone interested in it is beyond us though"""
    _ = request
    ret = await dump_crl()
    if ret != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": f"CFSSL CLI call to dump_crl failed, code {ret}. See server logs",
            },
        )
    der_path = RESTConfig.singleton().crl
    return FileResponse(der_path, media_type="application/pkix-crl")


@ROUTER.get("/healthcheck")
async def healthcheck(request: Request) -> Dict[str, Any]:
    """Health check"""
    _ = request
    retval = "success"
    grace = 15
    cnf = RESTConfig.singleton()
    cnf.crl = Path(cnf.crl)
    try:
        modtime = time.time() - cnf.crl.stat().st_mtime
    except FileNotFoundError:
        LOGGER.warning("{} does not exist yet".format(cnf.crl))
        return {"healthcheck": "crlfail"}
    LOGGER.debug("{} modified {} seconds ago".format(cnf.crl, modtime))
    if modtime > (cnf.crl_refresh + grace):
        LOGGER.warning("{} modified too long ago ({}s)".format(cnf.crl, modtime))
        retval = "crlfail"
    return {"healthcheck": retval}


def get_app() -> FastAPI:
    """Get the app"""
    app = FastAPI(
        docs_url="/api/docs", openapi_url="/api/openapi.json", version=__version__
    )
    app.include_router(router=ROUTER, prefix="/api/v1")
    LOGGER.debug("Returning {}".format(app))
    return app


def app_w_logging() -> FastAPI:
    """init logging and create app"""
    init_logging()
    app = get_app()
    return app


async def refresher() -> None:
    """Dump the CRL and refresh OCSP periodically"""
    try:
        while True:
            try:
                await asyncio.gather(dump_crl(), refresh_oscp())
            except asyncio.TimeoutError as exc:
                LOGGER.warning("Ignoring timeout: {}".format(exc))
            await asyncio.sleep(RESTConfig.singleton().crl_refresh)
    except asyncio.CancelledError:
        LOGGER.debug("Cancelled")
