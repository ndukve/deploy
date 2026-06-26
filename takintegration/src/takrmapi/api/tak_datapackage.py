"""Endpoint to deliver files/templates from templates/tak_datapackage"""

from typing import cast
from pathlib import Path
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse, Response
from libpvarki.middleware.mtlsheader import MTLSHeader, DNDict
from libpvarki.schemas.product import UserCRUDRequest

from takrmapi.takutils import tak_helpers
from takrmapi.takutils.tak_pkg_helpers import TAKDataPackage, TAKPackageZip
from takrmapi.takutils.tak_admin_helpers import TAKAdminHelper

from .schemas import TAKAdminPackageListResponse

LOGGER = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


@router.get("/client-package/{package_path:path}")
async def return_clientpackage_zip(package_path: Path, request: Request, background_tasks: BackgroundTasks) -> Response:
    """Return zip package from folder contents under requested path, use folder name as package name"""
    payload = cast(DNDict, request.state.mtlsdn)
    callsign: str = payload["CN"]
    user: tak_helpers.UserCRUD = tak_helpers.UserCRUD(UserCRUDRequest(uuid="NA", callsign=callsign, x509cert=""))
    pkg_helper = TAKPackageZip(user)

    client_package = TAKDataPackage(template_path=package_path, template_type="client")

    # Check if the default or specific folder is found.
    if not client_package.path_found:
        raise HTTPException(status_code=404, detail="Requested datapackage not found in given path")

    await pkg_helper.create_zip_bundles(datapackages=[client_package])

    # Remove/clear temp in background
    background_tasks.add_task(pkg_helper.helpers.remove_tmp_dir, client_package.zip_tmp_folder)

    return FileResponse(client_package.zip_path)


@router.get("/client-file/{file_path:path}")
async def return_clientpackage_file(file_path: Path, request: Request) -> Response:
    """Return single file from tak_datapackages. If file ends with .tpl, return rendered file"""
    payload = cast(DNDict, request.state.mtlsdn)
    callsign: str = payload["CN"]
    user: tak_helpers.UserCRUD = tak_helpers.UserCRUD(UserCRUDRequest(uuid="NA", callsign=callsign, x509cert=""))

    tak_missionpkg = TAKPackageZip(user)

    client_file = TAKDataPackage(template_path=file_path, template_type="client")

    # Check if the file exists
    if not client_file.path_found:
        raise HTTPException(status_code=404, detail="Requested datapackage file not found")

    if client_file.is_folder:
        raise HTTPException(status_code=400, detail="Requested datapackage is not servicable file")

    if client_file.package_name.endswith(".tpl"):
        tak_missionpkg = TAKPackageZip(user)
        await tak_missionpkg.render_tak_manifest_template(client_file)
        return Response(client_file.template_str.encode(encoding="utf-8"), media_type="text/plain")

    return FileResponse(client_file.package_single_file_path)


@router.get("/environment-package/{package_path:path}")
async def return_envpackage_zip(package_path: Path, request: Request, background_tasks: BackgroundTasks) -> Response:
    """Return zip package from folder contents under requested path, use folder name as package name"""
    payload = cast(DNDict, request.state.mtlsdn)
    callsign: str = payload["CN"]
    user: tak_helpers.UserCRUD = tak_helpers.UserCRUD(UserCRUDRequest(uuid="NA", callsign=callsign, x509cert=""))
    pkg_helper = TAKPackageZip(user)

    client_package = TAKDataPackage(template_path=package_path, template_type="environment")

    # Check if the default or specific folder is found.
    if not client_package.path_found:
        raise HTTPException(status_code=404, detail="Requested datapackage not found in given path")

    await pkg_helper.create_zip_bundles(datapackages=[client_package])

    # Remove/clear temp in background
    background_tasks.add_task(pkg_helper.helpers.remove_tmp_dir, client_package.zip_tmp_folder)

    return FileResponse(client_package.zip_path)


@router.get("/package-list")
async def return_available_packages(request: Request) -> TAKAdminPackageListResponse:
    """Return available datapackages"""
    # TODO check if user has elevated privileges
    payload = cast(DNDict, request.state.mtlsdn)
    callsign: str = payload["CN"]
    user: tak_helpers.UserCRUD = tak_helpers.UserCRUD(UserCRUDRequest(uuid="NA", callsign=callsign, x509cert=""))
    adm_helper = TAKAdminHelper(user)

    return TAKAdminPackageListResponse(data=adm_helper.get_available_datapackages)
