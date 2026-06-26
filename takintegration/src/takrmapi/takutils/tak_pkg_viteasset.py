"""Helper functions to manage tak data packages"""

from typing import List, ClassVar
import logging
from dataclasses import dataclass
from pathlib import Path

from takrmapi.takutils.tak_pkg_helpers import TAKDataPackage
from takrmapi.takutils.tak_pkg_vars import TAKViteAssetVars

LOGGER = logging.getLogger(__name__)


@dataclass
class TAKViteAsset:
    """TAK Vite Assets helper"""

    _vite: ClassVar[TAKViteAssetVars] = TAKViteAssetVars()

    @staticmethod
    def is_vite_enabled() -> bool:
        """Check if Vite Assets are enabled"""
        return TAKViteAssetVars.vite_asset_enabled

    @staticmethod
    def get_vite_folder() -> Path:
        """Return Vite Assets package path"""
        return TAKViteAssetVars.vite_asset_default_folder

    @staticmethod
    def vite_folder_exists() -> bool:
        """Return Vite Assets package path"""
        return TAKViteAssetVars.vite_asset_default_folder.exists()

    @staticmethod
    def get_vite_packages() -> List[TAKDataPackage]:
        """Return list of available Vite packages"""
        if not TAKViteAsset.vite_folder_exists():
            LOGGER.warning(
                "Vite asset folder '{}' missing. Unable to list content!".format(
                    TAKViteAssetVars.vite_asset_default_folder
                )
            )
            return []
        vite_packages: List[TAKDataPackage] = []
        for item in TAKViteAsset.get_vite_folder().iterdir():
            vite_packages.append(
                TAKDataPackage(
                    template_path=item,
                    template_type="vite",
                )
            )
        return vite_packages
