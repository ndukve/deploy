"""Helper functions to manage environment specific tak data packages.
Some extra packages might be enabled based on what services are available in current environment.
"""

from typing import List, Any, Dict, ClassVar
import logging
from dataclasses import dataclass
from pathlib import Path

from pydantic import Field, Extra
from pydantic.main import BaseModel  # pylint: disable=E0611 # false positive

from takrmapi import config

from takrmapi.takutils.tak_pkg_helpers import TAKDataPackage

LOGGER = logging.getLogger(__name__)


class TAKDynPkg(BaseModel):  # pylint: disable=too-few-public-methods
    """TAK Dynamic package schema"""

    name: str = Field(description="Package name")
    pkg_path: Path = Field(default=Path("na"), description="Path to package folder")
    enabled: bool = Field(default=False, description="Dynamic package is enabled in this environment")
    pkg_type: str = Field(default="datapackage", description="Package type")
    native_pkg: bool = Field(default=True, description="Dynamic package is found under local templates")
    non_native_src: Path = Field(default=Path("na"), description="Non native package source path")

    class Config:  # pylint: disable=too-few-public-methods
        """TAKDynPkg Config"""

        extra = Extra.forbid


@dataclass
class TAKDynPkgHelper:
    """Additional TAK datapackages triggered by ENV"""

    dynpackages_available: ClassVar[bool] = False

    pkgmap: ClassVar[Dict[str, Any]] = {
        "mtx": TAKDynPkg(
            name="mtx",
            pkg_path=Path(config.TAK_DATAPACKAGE_TEMPLATES_FOLDER) / "general" / "Plugins" / "UAStool-Streaming",
            pkg_type="client",
        ),
        "airguardian": TAKDynPkg(
            name="airguardian",
            pkg_path=Path(config.TAK_DATAPACKAGE_TEMPLATES_FOLDER) / "general" / "Plugins" / "Airguardian",
            pkg_type="environment",
        ),
        "battlelog-mock": TAKDynPkg(
            name="battlelog-mock",
            pkg_path=Path(config.TAK_DATAPACKAGE_TEMPLATES_FOLDER) / "general" / "Plugins" / "Battlelog-mock",
            pkg_type="client",
        ),
    }

    def __post_init__(self) -> None:
        """Post init"""
        self.mtx_check()
        self.battlelog_check()
        self.airguard_check()

    @classmethod
    def enable_package(cls, name: str) -> None:
        """Set package as enabled"""
        cls.pkgmap[name].enabled = True

    @classmethod
    def mtx_check(cls) -> None:
        """Check if mtx is used in current environment"""
        if config.MTX_SERVER_FQDN != "Not Available - ENV not set":
            cls.dynpackages_available = True
            cls.enable_package(name="m")

    @classmethod
    def battlelog_check(cls) -> None:
        """TODO?? Check if battlelog is used in current environment"""
        LOGGER.debug("TODO remove jotain jotain...")

    @classmethod
    def airguard_check(cls) -> None:
        """Check if airguard is used in current environment"""
        if config.AIRGUARD_API != "Not Available - ENV not set":
            cls.dynpackages_available = True
            cls.enable_package(name="airguardian")

    @classmethod
    def get_dyn_packages(cls, pkg_type: str = "all") -> List[TAKDataPackage]:
        """Get available enabled packages"""
        dpackages: List[TAKDataPackage] = []
        for _, pkg in cls.pkgmap.items():
            if pkg.enabled and (pkg_type in ("all", pkg.pkg_type)):
                dpackages.append(
                    TAKDataPackage(
                        template_path=pkg.pkg_path,
                        template_type=pkg.pkg_type,
                    )
                )

        return dpackages
