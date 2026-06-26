"""Endpoints for information for the end-user"""

import logging
import base64
from fastapi import APIRouter, Depends, BackgroundTasks
from libpvarki.middleware import MTLSHeader
from libpvarki.schemas.product import UserCRUDRequest
from takrmapi.takutils import tak_helpers
from takrmapi.takutils.tak_pkg_helpers import TAKDataPackage, TAKPackageZip
from .schemas import TakZipFile, ClientInstructionData, ClientInstructionResponse

from ..config import TAK_MISSIONPKG_ENABLED_PACKAGES


LOGGER = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


@router.post("/data", response_model=ClientInstructionResponse)
async def client_instruction_fragment(
    user: UserCRUDRequest, background_tasks: BackgroundTasks
) -> ClientInstructionResponse:
    """Return zip package containing client config and certificates"""
    localuser = tak_helpers.UserCRUD(user)
    tak_missionpkg = TAKPackageZip(localuser)

    mp_list: list[TAKDataPackage] = []
    for m in TAK_MISSIONPKG_ENABLED_PACKAGES:
        mp_list.append(TAKDataPackage(template_path=m, template_type="mission"))

    await tak_missionpkg.create_zip_bundles(datapackages=mp_list)

    tak_zips = []
    for mpkg in mp_list:
        contents = mpkg.zip_path.read_bytes()
        tak_zips.append(
            TakZipFile(
                title=mpkg.zip_path.name,
                filename=f"{localuser.callsign}_{mpkg.zip_path.name}",
                data=f"data:application/zip;base64,{base64.b64encode(contents).decode('ascii')}",
            )
        )

        # Remove/clear temp in background
        background_tasks.add_task(tak_missionpkg.helpers.remove_tmp_dir, mpkg.zip_tmp_folder)

    return ClientInstructionResponse(data=ClientInstructionData(tak_zips=tak_zips))
