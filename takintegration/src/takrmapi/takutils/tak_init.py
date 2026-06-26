"""Init TAK management connection capability"""

from typing import List
import asyncio
import logging
import shutil
import secrets
import string

from libpvarki.schemas.product import UserCRUDRequest
from takrmapi import config
from takrmapi.takutils import tak_helpers
from takrmapi.takutils.tak_helpers import UserCRUD
from takrmapi.takutils.tak_rest_helpers import RestHelpers
from takrmapi.takutils.tak_pkg_helpers import TAKPackageZip, TAKDataPackage
from takrmapi.takutils.tak_pkg_viteasset import TAKViteAsset
from takrmapi.takutils.tak_pkg_dynpkg import TAKDynPkgHelper

LOGGER = logging.getLogger(__name__)


# CHECK FOR mtlsclient cert in tak cert folder /opt/tak/cert/files


async def setup_tak_mgmt_conn() -> None:
    """Setup required credentials to manage TAK"""
    # FIXME: Refactor to separate helpers not requiring a dummy user

    user: UserCRUD = UserCRUD(UserCRUDRequest(uuid="not_needed", callsign="mtlsclient", x509cert="not_needed"))
    t_helpers = tak_helpers.Helpers(user)
    t_rest_helper = RestHelpers(user)

    # Wait for the TAK API to start responding
    for _ in range(60):
        data = await t_rest_helper.tak_api_user_list()

        if not data["success"]:
            LOGGER.info("TAK API not ready yet. Waiting...")
            LOGGER.info(data)
            await asyncio.sleep(5)  # nosec
        else:
            LOGGER.info("TAK API responding, moving on...")
            break

    # Move mtlsclient.pem in place if not there already
    if not await t_helpers.user_cert_exists():
        # Copy mtlsclient.pem from /data/persistent/public/mtlsclient.pem to
        new_filepath = config.TAK_CERTS_FOLDER / "mtlsclient.pem"
        shutil.copy("/data/persistent/public/mtlsclient.pem", new_filepath)
    else:
        LOGGER.info("mtlsclient cert already in place. No need to copy from /data/persistent...")

    # Check if we can already use TAK rest api. If not then add the mtlsinit as admin user
    data = await t_rest_helper.tak_api_user_list()
    if not data["data"]:
        LOGGER.info("Adding mtlsclient as administrator to TAK")
        await t_helpers.add_admin_to_tak_with_cert()
    else:
        LOGGER.info("Got user list, mtlsclient cert already added as admin")


async def setup_tak_defaults() -> None:
    """Set common required defaults to tak"""
    user: UserCRUD = UserCRUD(UserCRUDRequest(uuid="not_needed", callsign="mtlsclient", x509cert="not_needed"))
    t_rest_helper = RestHelpers(user)
    tak_missionpkg = TAKPackageZip(user)

    LOGGER.info("Starting to set set TAK defaults")
    await tak_setup_mesh_key()
    await tak_setup_default_missions(t_rest_helper=t_rest_helper)
    await tak_setup_default_profiles(t_rest_helper=t_rest_helper)
    await tak_setup_profile_files(t_rest_helper=t_rest_helper, tak_missionpkg=tak_missionpkg)


async def tak_setup_mesh_key() -> None:
    """Create/load TAK network mesh key"""
    # Create environment specific networkMeshKey
    if not config.TAK_SERVER_NETWORKMESH_KEY_FILE.exists():
        mesh_str: str = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(64))
        config.TAK_SERVER_NETWORKMESH_KEY_FILE.write_text(mesh_str, encoding="utf-8")


async def tak_setup_default_missions(t_rest_helper: RestHelpers) -> None:
    """Create default TAK missions if missing"""
    # Check that the "RECON" mission is available
    mission_recon_available = await t_rest_helper.tak_api_mission_get(groupname="RECON")

    if not mission_recon_available["data"]:
        mission_added = await t_rest_helper.tak_api_mission_put(
            groupname="RECON",
            description="Recon feed for validated information",
            default_role="MISSION_SUBSCRIBER",
        )

        if not mission_added["data"]:
            LOGGER.error("Unable to add RECON mission! Check takapi logs for possible errors.")
            return

        # Update mission keywords
        mission_keywords_added = await t_rest_helper.tak_api_mission_keywords(groupname="RECON", keywords=["#RECON"])
        if not mission_keywords_added:
            LOGGER.error("Unable to add keywords to RECON mission! Check takapi logs for possible errors.")
            return
    else:
        LOGGER.info("RECON mission already in place, no need to add again.")


async def tak_setup_default_profiles(t_rest_helper: RestHelpers) -> None:
    """Create default TAK profiles"""
    # Check that the "TAK-Defaults" profile is in place
    default_profile_available = await t_rest_helper.tak_api_get_device_profile(profile_name="Default-ATAK")
    LOGGER.debug("Available TAK profiles: {}".format(default_profile_available))
    if (
        default_profile_available
        and "data" in default_profile_available
        and "status" in default_profile_available["data"]
        and default_profile_available["data"]["status"] == "NOT_FOUND"
    ):
        LOGGER.info("Default-ATAK profile missing. Adding profile.")
        await t_rest_helper.tak_api_add_device_profile(profile_name="Default-ATAK", groups=["default"])
        await t_rest_helper.tak_api_update_device_profile(
            profile_name="Default-ATAK",
            profile_vars={
                "profile_active": True,
                "apply_on_connect": True,
                "apply_on_enrollment": False,
                "profile_type": "Connection",
                "tool": None,
                "groups": ["default"],
            },
        )


async def tak_setup_profile_files(t_rest_helper: RestHelpers, tak_missionpkg: TAKPackageZip) -> None:
    """Upload default tak profile files and bundles to TAK"""
    # Get current 'Default-ATAK' profile files
    profile_files = await t_rest_helper.tak_api_get_device_profile_files(profile_name="Default-ATAK")

    # Check dst default profile files before uploading
    local_profile_files: List[TAKDataPackage] = []
    for profile_file in config.TAK_DATAPACKAGE_ADDON_FOLDER_FILES:
        p_file: TAKDataPackage = TAKDataPackage(template_path=profile_file, template_type="environment")
        # Skip already uploaded files
        if await t_rest_helper.check_file_in_profile_files(datapackage=p_file, tak_profile_files=profile_files):
            continue
        local_profile_files.append(p_file)

    # Upload default files to profile
    for pf in local_profile_files:
        if pf.is_template_file:
            await tak_missionpkg.render_tak_manifest_template(pf)

        await t_rest_helper.tak_api_upload_file_to_profile(
            profile_name="Default-ATAK",
            datapackage=pf,
        )

    # Check for already uploaded bundles
    tmp_bundles: List[TAKDataPackage] = []
    if TAKViteAsset.is_vite_enabled():
        tmp_bundles.extend(TAKViteAsset.get_vite_packages())
    if TAKDynPkgHelper.dynpackages_available:
        tmp_bundles.extend(TAKDynPkgHelper.get_dyn_packages())

    upload_bundles: List[TAKDataPackage] = []
    for b in tmp_bundles:
        if await t_rest_helper.check_file_in_profile_files(datapackage=b, tak_profile_files=profile_files):
            continue
        upload_bundles.append(b)

    for bundle in config.TAK_DATAPACKAGE_ADDON_FOLDER_ZIP_PACKAGES:
        b_package: TAKDataPackage = TAKDataPackage(template_path=bundle, template_type="environment")
        if await t_rest_helper.check_file_in_profile_files(datapackage=b_package, tak_profile_files=profile_files):
            continue
        upload_bundles.append(b_package)

    # Create zip bundles and upload to profile from those missing in dst
    if len(upload_bundles) > 0:
        await tak_missionpkg.create_zip_bundles(datapackages=upload_bundles)
        for dp in upload_bundles:
            await t_rest_helper.tak_api_upload_file_to_profile(profile_name="Default-ATAK", datapackage=dp)
            await tak_missionpkg.helpers.remove_tmp_dir(dp.zip_tmp_folder)


async def get_tak_defaults() -> None:
    """Get common required defaults used in tak"""

    LOGGER.debug("Getting TAK defaults")
    # Read the tak server networkMeshKey to memory.
    while not config.TAK_SERVER_NETWORKMESH_KEY_FILE.exists():
        LOGGER.debug("Waiting for TAK_SERVER_NETWORKMESH_KEY_FILE to be populated")
        await asyncio.sleep(2)

    config.TAK_SERVER_NETWORKMESH_KEY_STR = config.TAK_SERVER_NETWORKMESH_KEY_FILE.read_text(encoding="utf-8")
