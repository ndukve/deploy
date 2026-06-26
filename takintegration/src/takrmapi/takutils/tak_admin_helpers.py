"""Helpers for TAK administrator actions"""

from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path
import logging

from takrmapi import config
from takrmapi.takutils.tak_helpers import UserCRUD
from takrmapi.takutils.tak_pkg_vars import TAKDataPackagePathVars

LOGGER = logging.getLogger(__name__)


@dataclass
class TAKAdminHelper:
    """TAK admin helpers"""

    user: UserCRUD

    # TODO
    @property
    def check_user_permissions(self) -> bool:
        """Check if the user has permission to use elevated actions"""
        # TODO
        return True

    @property
    def get_available_datapackages(self) -> Dict[str, Any]:
        """Return available packages and files"""
        dir_content: Dict[str, Any] = {"default": self.get_dir_content(TAKDataPackagePathVars.env_pkg_default_folder)}
        if TAKDataPackagePathVars.extra_pkg_available:
            dir_content["extra"] = self.get_dir_content(TAKDataPackagePathVars.env_pkg_extra_folder)

        # Get the "type" folders from /general. Packages are located under all of these
        tf: Dict[str, Any] = self.get_dir_content(Path(config.TAK_DATAPACKAGE_TEMPLATES_FOLDER) / "general")

        for f in tf:
            dir_content[f"general_{f}"] = self.get_dir_content(
                Path(config.TAK_DATAPACKAGE_TEMPLATES_FOLDER) / "general" / f
            )

        return dir_content

    def get_dir_content(self, dirpath: Path) -> Dict[str, Any]:
        """Get dir content"""
        dir_content: Dict[str, Any] = {}
        for item in dirpath.iterdir():
            if item.is_dir():
                dir_content[item.name] = "dir"
            else:
                dir_content[item.name] = "file"

        return dir_content
