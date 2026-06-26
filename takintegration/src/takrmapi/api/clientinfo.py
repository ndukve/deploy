"""Endpoints for information for the end-user"""

import logging
import base64
from typing import List, Dict
from fastapi import APIRouter, Depends, BackgroundTasks
from libpvarki.middleware import MTLSHeader
from libpvarki.schemas.product import UserCRUDRequest

from takrmapi.takutils import tak_helpers
from takrmapi.takutils.tak_pkg_helpers import TAKDataPackage, TAKPackageZip
from ..config import TAK_MISSIONPKG_ENABLED_PACKAGES


LOGGER = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


@router.post("/fragment", deprecated=True)
async def client_instruction_fragment(user: UserCRUDRequest, background_tasks: BackgroundTasks) -> List[Dict[str, str]]:
    """Return zip package containing client config and certificates"""
    localuser = tak_helpers.UserCRUD(user)
    tak_missionpkg = TAKPackageZip(localuser)

    mp_list: list[TAKDataPackage] = []
    for mp in TAK_MISSIONPKG_ENABLED_PACKAGES:
        mp_list.append(TAKDataPackage(template_path=mp, template_type="mission"))

    await tak_missionpkg.create_zip_bundles(datapackages=mp_list)

    returnable: List[Dict[str, str]] = []

    for pkg in mp_list:
        contents = pkg.zip_path.read_bytes()
        returnable.append(
            {
                "title": pkg.zip_path.name,
                "data": f"data:application/zip;base64,{base64.b64encode(contents).decode('ascii')}",
                "filename": f"{localuser.callsign}_{pkg.zip_path.name}",
            }
        )
        # Remove/clear temp in background
        background_tasks.add_task(tak_missionpkg.helpers.remove_tmp_dir, pkg.zip_tmp_folder)

    return returnable
