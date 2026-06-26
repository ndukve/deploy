"""Tak data package vars"""

from typing import ClassVar
import logging
from dataclasses import dataclass
from pathlib import Path
import uuid
import hashlib
from takrmapi import config
from takrmapi.takutils.tak_helpers import UserCRUD


LOGGER = logging.getLogger(__name__)


@dataclass
class UserTAKTemplateVars:
    """TAK Template variable mapping to user/environment values"""

    user: UserCRUD
    template_file: Path

    # Deployment specific "static" var mapping for template files
    tak_server_deployment_name: ClassVar[str] = config.TAK_SERVER_NAME
    tak_server_public_address: ClassVar[str] = config.TAK_SERVER_FQDN
    mtx_server_public_address: ClassVar[str] = config.MTX_SERVER_FQDN
    mtx_server_srt_port: ClassVar[int] = config.MTX_SERVER_SRT_PORT
    mtx_server_observer_port: ClassVar[int] = config.MTX_SERVER_OBSERVER_PORT
    mtx_server_observer_proto: ClassVar[str] = config.MTX_SERVER_OBSERVER_PROTO
    mtx_server_observer_net_proto: ClassVar[str] = config.MTX_SERVER_OBSERVER_NET_PROTO

    @property
    def tak_userfile_uid(self) -> str:
        """Return UUID for users files"""
        return str(
            uuid.uuid5(uuid.NAMESPACE_URL, f"{config.TAK_SERVER_FQDN}/{self.user.callsign}/{self.template_file}")
        )

    @property
    def client_cert_name(self) -> str:
        """User cert name mapping."""
        return self.user.callsign

    @property
    def client_cert_password(self) -> str:
        """User pw mapping for cert in templates,"""
        return self.user.callsign

    @property
    def tak_network_mesh_key(self) -> str:
        """ATAK mesh key mapping. Same for whole deployment."""
        return str(hashlib.sha256(config.TAK_SERVER_NETWORKMESH_KEY_STR.encode("utf-8")).hexdigest())

    @property
    def client_mtx_username(self) -> str:
        """TODO Return users MTX username"""
        return "TODO-Username_Retrieve_Not_Implemented_Yet"

    @property
    def client_mtx_password(self) -> str:
        """TODO Return users MTX username"""
        return "TODO-PW-Retrieve-Not-Implemented-Yet"


@dataclass
class TAKDataPackagePathVars:
    """TAK Datapackage site vars"""

    extra_pkg_available: ClassVar[bool] = False

    # Templating internal variables
    client_pkg_default_folder: ClassVar[Path] = (
        Path(config.TAK_DATAPACKAGE_TEMPLATES_FOLDER) / "default" / "client-packages"
    )
    client_pkg_extra_folder: ClassVar[Path] = (
        Path(config.TAK_DATAPACKAGE_TEMPLATES_FOLDER) / config.TAK_DATAPACKAGE_ADDON_FOLDER / "client-packages"
    )
    env_pkg_default_folder: ClassVar[Path] = (
        Path(config.TAK_DATAPACKAGE_TEMPLATES_FOLDER) / "default" / "environment-packages"
    )
    env_pkg_extra_folder: ClassVar[Path] = (
        Path(config.TAK_DATAPACKAGE_TEMPLATES_FOLDER) / config.TAK_DATAPACKAGE_ADDON_FOLDER / "environment-packages"
    )
    missionpkg_default_folder: ClassVar[Path] = Path(config.TAK_MISSIONPKG_TEMPLATES_FOLDER) / "default"
    missionpkg_extra_folder: ClassVar[Path] = (
        Path(config.TAK_MISSIONPKG_TEMPLATES_FOLDER) / config.TAK_MISSIONPKG_ADDON_FOLDER
    )

    def __post_init__(self) -> None:
        """Template variables post init"""
        if config.TAK_DATAPACKAGE_ADDON_FOLDER not in ("default", "na"):
            TAKDataPackagePathVars.extra_pkg_available = True

        if config.TAK_MISSIONPKG_ADDON_FOLDER not in ("default", "na"):
            TAKDataPackagePathVars.extra_pkg_available = True


@dataclass
class TAKViteAssetVars:
    """TAK Vite Assets vars"""

    # Viteasset internal variables
    vite_asset_default_folder: ClassVar[Path] = Path(config.VITE_ASSET_SET_TEMPLATES_FOLDER) / config.VITE_ASSET_SET
    vite_asset_enabled: ClassVar[bool] = False

    def __post_init__(self) -> None:
        """Template variables post init"""
        if config.VITE_ASSET_SET != "not_used_by_default":
            TAKViteAssetVars.vite_asset_enabled = True
            if not self.vite_asset_default_folder.exists():
                LOGGER.warning("Vite asset folder '{}' missing. Unable to add!".format(self.vite_asset_default_folder))
