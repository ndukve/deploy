"""Instructions API"""

from __future__ import annotations
from typing import Dict, Any
import logging
import json
from pathlib import Path

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import FileResponse
from libpvarki.middleware import MTLSHeader
from libpvarki.schemas.product import UserCRUDRequest

from ..db.user import User
from ..db.errors import NotFound
from .usercrud import comes_from_rm, create_user
from ..mediamtx import MediaMTXControl

LOGGER = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


@router.get("/assets/{file_path:path}")
async def get_asset(file_path: str) -> FileResponse:
    """Asset file"""
    basepath = Path("/opt/templates/assets")
    assetpath = basepath / file_path
    LOGGER.info("Looking for {} from {}".format(file_path, assetpath))
    if not assetpath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(assetpath))


@router.post("/instructions/{language}")
async def user_intructions(
    user: UserCRUDRequest, request: Request, language: str
) -> Dict[str, Any]:
    """return user instructions"""
    comes_from_rm(request)
    try:
        dbuser = await User.by_rmuuid(user.uuid)
    except NotFound:
        dbuser = await create_user(user)

    instructions_json_file = Path("/opt/templates/mediamtx.json")

    if not instructions_json_file.is_file():
        reason = "mediamtx json rune is missing from server."
        LOGGER.error("{} : {}".format(request.url, reason))
        raise HTTPException(status_code=500, detail=reason)

    instructions_data = json.loads(instructions_json_file.read_text(encoding="utf-8"))
    instructions_data.append(
        {
            "type": "Component",
            "name": "CredentialUser",
            "body": dbuser.username,
        }
    )
    instructions_data.append(
        {
            "type": "Component",
            "name": "CredentialPassword",
            "body": dbuser.mtxpassword,
        }
    )
    streams = await MediaMTXControl.singleton().get_paths(
        username=dbuser.username, password=dbuser.mtxpassword
    )
    streams_content = "<ul>\n"
    for streamdict in streams:
        streams_content += f"<li>{streamdict['path']}<ul>"
        for pname, purl in streamdict["urls"].items():
            streams_content += f'<li><a href="{purl}">{pname}</a></li>'
        streams_content += "</ul></li>\n"
    streams_content += "<ul>\n"
    instructions_data.append(
        {
            "type": "Component",
            "name": "StreamsList",
            "body": streams_content,
        }
    )

    return {
        "callsign": dbuser.username,
        "instructions": instructions_data,
        "language": language,
    }
