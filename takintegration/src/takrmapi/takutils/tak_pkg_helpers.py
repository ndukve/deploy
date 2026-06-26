"""Helper functions to manage tak data packages"""

import base64
import binascii
import hashlib
from typing import List, Any, Dict, ClassVar
import logging
from dataclasses import dataclass, field
from pathlib import Path
import tempfile
import asyncio
import os
import shutil
from jinja2 import Template

from libpvarki.mtlshelp.pkcs12 import convert_pem_to_pkcs12
from takrmapi import config
from takrmapi.takutils.env_helpers import env_float
from takrmapi.takutils.tak_helpers import UserCRUD, Helpers
from takrmapi.takutils.tak_pkg_vars import TAKDataPackagePathVars, TAKViteAssetVars, UserTAKTemplateVars


LOGGER = logging.getLogger(__name__)
KEYPAIR_TIMEOUT = env_float("TAK_RMAPI_KEYPAIR_TIMEOUT", 5.0, max_value=600.0)


@dataclass
class TAKPkgVars:
    """TAK datapackage variables"""

    package_default_path: Path
    package_extra_path: Path
    is_mission_package: bool
    zip_complete: bool
    zip_path: Path
    zip_tmp_folder: Path
    template_file_render_str: str


def _get_secret_key_from_environ(key_descriptor: str = "KEY") -> bytes:
    """Fetch the secret key from the environment variable."""

    from_env = os.environ.get("TAKRMAPI_SECRET_KEY", "")
    try:
        key_candidate = base64.b64decode(from_env.encode("ascii"))
    except (TypeError, binascii.Error) as e:
        raise RuntimeError("TAKRMAPI_SECRET_KEY is not valid base64 encoded string.") from e

    if len(key_candidate) < 32:
        raise RuntimeError("TAKRMAPI_SECRET_KEY is too short. It should be at least 32 bytes long.")

    sha256 = hashlib.sha256()
    sha256.update(key_candidate)
    sha256.update(key_descriptor.encode("ascii"))
    return sha256.digest()


@dataclass
class TAKDataPackage:
    """TAK Datapackage helper"""

    template_path: Path
    template_type: str

    _pkgvars: TAKPkgVars = field(init=False)
    _ephemeral_aes_key: ClassVar[bytes] = b""
    _ephemeral_hmac_key: ClassVar[bytes] = b""

    # TODO savolaiset muuttujat
    # _zip_path: Path = field(init=False)
    # _zip_tmp_folder: Path = field(init=False)

    def __post_init__(self) -> None:
        """Template variables post init"""

        match self.template_type:
            case "client":
                __package_default_path = Path(TAKDataPackagePathVars.client_pkg_default_folder) / self.template_path
                __package_extra_path = Path(TAKDataPackagePathVars.client_pkg_extra_folder) / self.template_path
                __is_mission_package = False
            case "environment":
                __package_default_path = Path(TAKDataPackagePathVars.env_pkg_default_folder) / self.template_path
                __package_extra_path = Path(TAKDataPackagePathVars.env_pkg_extra_folder) / self.template_path
                __is_mission_package = False
            case "mission":
                __package_default_path = Path(TAKDataPackagePathVars.missionpkg_default_folder) / self.template_path
                __package_extra_path = Path(TAKDataPackagePathVars.missionpkg_extra_folder) / self.template_path
                __is_mission_package = True
            case "vite":
                __package_default_path = Path(TAKViteAssetVars.vite_asset_default_folder) / self.template_path
                __package_extra_path = Path("not-used-in-vite")
                __is_mission_package = False

        self._pkgvars = TAKPkgVars(
            package_default_path=__package_default_path,
            package_extra_path=__package_extra_path,
            is_mission_package=__is_mission_package,
            zip_complete=False,
            zip_path=Path("na"),
            zip_tmp_folder=Path("na"),
            template_file_render_str="",
        )

    @classmethod
    def get_ephemeral_aes_key(cls) -> bytes:
        """Return key for ephemeral file requests"""
        if not cls._ephemeral_aes_key:
            cls._ephemeral_aes_key = _get_secret_key_from_environ("AESKEY")

        return cls._ephemeral_aes_key

    @classmethod
    def get_ephemeral_hmac_key(cls) -> bytes:
        """Return key for ephemeral file requests"""
        if not cls._ephemeral_hmac_key:
            cls._ephemeral_hmac_key = _get_secret_key_from_environ("HMACKEY")

        return cls._ephemeral_hmac_key

    @property
    def is_folder(self) -> bool:
        """Check if package is folder"""
        if self.default_path_found and self.extra_path_found:
            if self._pkgvars.package_default_path.is_dir() != self._pkgvars.package_extra_path.is_dir():
                raise ValueError(
                    "Mismatch in package paths! Both default and extra path should either be file or folder! {}".format(
                        self.template_path
                    )
                )

        if self._pkgvars.package_default_path.is_dir() or self._pkgvars.package_extra_path.is_dir():
            return True

        return False

    @property
    def path_found(self) -> bool:
        """Check if datapackage source folder is found"""
        if self.default_path_found or self.extra_path_found:
            return True
        return False

    @property
    def default_path_found(self) -> bool:
        """Data package default path is found"""
        return self._pkgvars.package_default_path.exists()

    @property
    def extra_path_found(self) -> bool:
        """Data package extra/override path is found"""
        if self._pkgvars.package_extra_path == self._pkgvars.package_default_path:
            return False
        return self._pkgvars.package_extra_path.exists()

    @property
    def default_path(self) -> Path:
        """Return default datapackage path"""
        return self._pkgvars.package_default_path

    @property
    def extra_path(self) -> Path:
        """Return data package extra/override path"""
        return self._pkgvars.package_extra_path

    @property
    def get_package_files(self) -> Dict[str, Path]:
        """Return combined default+extra file list. Content from extra overrides default"""
        # Extra package files
        pkg_extra_files: Dict[str, Any] = {}
        if self.extra_path_found:
            LOGGER.debug("Extra content found for data package from path {}".format(self._pkgvars.package_extra_path))
            for root, _, files in os.walk(self._pkgvars.package_extra_path):
                for name in files:
                    f_src_path = Path(root) / name
                    f_pkg_str = str(f_src_path).replace(str(self._pkgvars.package_extra_path) + "/", "")
                    pkg_extra_files[f_pkg_str] = f_src_path

        # Default package files, override using extras
        pkg_files: Dict[str, Any] = {}

        for root, _, files in os.walk(self._pkgvars.package_default_path):
            for name in files:
                if name in pkg_extra_files:
                    pkg_files[name] = pkg_extra_files[name]
                    LOGGER.debug("Package file {} overridden with {}".format(name, pkg_extra_files[name]))
                    pkg_extra_files.pop(name)
                else:
                    f_src_path = Path(root) / name
                    f_pkg_str = str(f_src_path).replace(str(self._pkgvars.package_extra_path) + "/", "")
                    pkg_files[f_pkg_str] = f_src_path

        # Add extra files if there are some left.
        if pkg_extra_files:
            LOGGER.debug("Additional files are added to data package from {}".format(self._pkgvars.package_extra_path))
            for e_name, e_path in pkg_extra_files.items():
                pkg_files[e_name] = e_path
                # pkg_files.append(extra_file)

        return pkg_files

    @property
    def is_mission_package(self) -> bool:
        """Is mission"""
        return self._pkgvars.is_mission_package

    @property
    def package_name(self) -> str:
        """Return local package name"""
        if self.default_path_found:
            return self._pkgvars.package_default_path.name
        return self._pkgvars.package_extra_path.name

    @property
    def package_single_file_path(self) -> Path:
        """Return single file package path"""
        # "Extra" file overrides the default if found
        if self.extra_path_found:
            return self.extra_path
        return self.default_path

    @property
    def package_upload_src_file(self) -> Path:
        """Return package zip path or single file path"""
        if self._pkgvars.zip_complete:
            return self._pkgvars.zip_path
        # "Extra" file overrides the default if found
        if self.extra_path_found:
            return self.extra_path
        return self.default_path

    @property
    def package_upload_dst_fname(self) -> str:
        """Return package name that should be in destination"""
        if self.is_template_file:
            return self.template_path.name.replace(".tpl", "")

        if self.is_folder:
            return self.template_path.name + ".zip"

        return self.template_path.name

    @property
    def is_template_file(self) -> bool:
        """Check if is template file (.tpl)"""
        if self.template_path.name.endswith(".tpl"):
            return True
        return False

    @property
    def zip_complete(self) -> bool:
        """Zip complete"""
        return self._pkgvars.zip_complete

    @zip_complete.setter
    def zip_complete(self, z_complete: bool) -> None:
        """Set zip complete"""
        self._pkgvars.zip_complete = z_complete

    @property
    def zip_path(self) -> Path:
        """Return package tmp zip path"""
        return self._pkgvars.zip_path

    @zip_path.setter
    def zip_path(self, z_path: Path) -> None:
        """Set package tmp zip path"""
        self._pkgvars.zip_path = z_path

    @property
    def zip_tmp_folder(self) -> Path:
        """Return package tmp folder path"""
        return self._pkgvars.zip_tmp_folder

    @zip_tmp_folder.setter
    def zip_tmp_folder(self, z_tmp_folder: Path) -> None:
        """Set package tmp folder path"""
        self._pkgvars.zip_tmp_folder = z_tmp_folder

    @property
    def template_str(self) -> str:
        """Return rendered template file str"""
        return self._pkgvars.template_file_render_str

    @template_str.setter
    def template_str(self, template_content: str) -> None:
        """Set rendered template file str"""
        self._pkgvars.template_file_render_str = template_content


class TAKPackageZip:
    """TAK data package class"""

    def __init__(self, user: UserCRUD):
        self.user: UserCRUD = user
        self.helpers = Helpers(self.user)

    async def create_zip_bundles(
        # self, template_folders: list[Path], is_mission_package: bool = False
        self,
        datapackages: list[TAKDataPackage],
    ) -> None:
        """Create tak mission package packages to different app versions"""

        tasks: List[asyncio.Task[Any]] = []
        for dp in datapackages:
            if not dp.path_found:
                raise ValueError(
                    "'{}' package not found from default or extra paths '{}' '{}'".format(
                        dp.package_name, dp.default_path, dp.extra_path
                    )
                )

            # TODO tmpfile in memory
            dp.zip_tmp_folder = Path(tempfile.mkdtemp(suffix=f"_{self.user.callsign}"))

            LOGGER.info("Added {} to background tasks".format(dp.package_name))

            if dp.is_folder:
                tasks.append(asyncio.create_task(self.create_datapackage_zip(datapackage=dp)))
            else:
                raise ValueError(
                    "'{}' is file. create_zip_bundles works only with directories.".format(dp.default_path)
                )

        LOGGER.debug("Waiting for the zip tasks to finish")
        await asyncio.gather(*tasks)
        LOGGER.info("Background zipping tasks done")

    async def create_datapackage_zip(self, datapackage: TAKDataPackage) -> None:  # pylint: disable=too-many-locals
        """Loop through files in missionpkg templates folder"""
        # TODO maybe in memory fs for tmp files...

        # FIXME: use Paths for everything
        walk_dir = datapackage.default_path
        tmp_zip_folder = datapackage.zip_tmp_folder / walk_dir.name
        if datapackage.is_mission_package:
            tmp_zip_folder = datapackage.zip_tmp_folder / f"{config.TAK_SERVER_NAME}_{walk_dir.name}"
        tmp_zip_folder.mkdir(parents=True, exist_ok=True)

        LOGGER.debug("Moving files from '{}' to '{}' for bundling.".format(walk_dir, tmp_zip_folder))

        package_files: Dict[str, Any] = datapackage.get_package_files

        for pkg_file_path, org_full_path in package_files.items():
            dst_file = tmp_zip_folder / pkg_file_path
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            LOGGER.debug("org_full_path={} dst_file={}".format(org_full_path, dst_file))

            if dst_file.name.endswith(".tpl"):
                template_f = TAKDataPackage(template_path=org_full_path, template_type=datapackage.template_type)
                await self.render_tak_manifest_template(template_f)

                dst_template_file = dst_file.parent / template_f.package_upload_dst_fname

                LOGGER.debug("Handling template file -> '{}' for bundling.".format(dst_template_file))
                with open(dst_template_file, "w", encoding="utf-8") as filehandle:
                    filehandle.write(template_f.template_str)

                # Missionpackage zip specific peculiarities here
                if datapackage.is_mission_package:
                    if dst_template_file.name == "manifest.xml":
                        await self.tak_missionpackage_extras(dst_template_file, tmp_zip_folder)

            else:
                shutil.copy(org_full_path, dst_file)

        await self.zip_folder_content(str(tmp_zip_folder), str(tmp_zip_folder))

        datapackage.zip_path = Path(f"{tmp_zip_folder}.zip")
        datapackage.zip_complete = True

    async def render_tak_manifest_template(self, datapackage: TAKDataPackage) -> None:
        """Render tak manifest template"""

        template_user_vars = UserTAKTemplateVars(user=self.user, template_file=datapackage.package_single_file_path)

        with open(datapackage.package_single_file_path, "r", encoding="utf-8") as filehandle:
            template = Template(filehandle.read())
            datapackage.template_str = template.render(
                v=template_user_vars,
            )

    async def zip_folder_content(self, zipfile: str, tmp_folder: str) -> None:
        """Zip folder content"""
        await asyncio.get_running_loop().run_in_executor(None, shutil.make_archive, zipfile, "zip", tmp_folder)

    async def tak_missionpackage_extras(self, manifest_file: Path, tmp_folder: Path) -> None:
        """Check if there is some extra that needs to be done defined in the manifest"""
        manifest_rows = manifest_file.read_text().splitlines()
        for row in manifest_rows:
            # .p12 rows
            # <!--
            if "<!--" in row:
                continue

            # Add the certificate files to the zip package
            if ".p12" in row:
                await self.tak_missionpackage_add_p12(row, tmp_folder)

    async def tak_missionpackage_add_p12(self, row: str, tmp_folder: Path) -> None:
        """Handle manifest .p12 rows"""
        tmp_folder = await self.chk_manifest_file_extra_folder(row=row, tmp_folder=tmp_folder)
        # FIXME: do the blocking IO in executor
        LOGGER.info("PKCS12 Got template %s, tmp folder %s...", row, tmp_folder)
        if "rasenmaeher_ca-public.p12" in row:
            # FIXME: instead of adding the root key into the software, need a way to get full chain with Root CA
            templates_folder = Path(__file__).parent.parent / "templates"
            LOGGER.info("Searching keys from  %s...", templates_folder)
            ca_files = templates_folder.rglob("*.pem")
            srcdata = Path("/le_certs/rasenmaeher/fullchain.pem").read_bytes()
            for ca_f in sorted(ca_files):
                LOGGER.info("Adding PEM %s to CA bundle", ca_f.name)
                srcdata = srcdata + ca_f.read_bytes()

            tgtfile = Path(tmp_folder) / "rasenmaeher_ca-public.p12"
            LOGGER.info("Creating %s", tgtfile)
            p12bytes = convert_pem_to_pkcs12(srcdata, None, "public", None, "ca-chains")
            tgtfile.parent.mkdir(parents=True, exist_ok=True)
            LOGGER.debug("{} exists: {}".format(tgtfile.parent, tgtfile.parent.exists()))
            tgtfile.write_bytes(p12bytes)
            LOGGER.debug("{} exists: {}".format(tgtfile, tgtfile.exists()))
        elif f"{self.user.callsign}.p12" in row:
            tgtfile = Path(tmp_folder) / f"{self.user.callsign}.p12"
            await asyncio.wait_for(self.user.wait_for_keypair(), timeout=KEYPAIR_TIMEOUT)
            LOGGER.info("Creating {}".format(tgtfile))
            p12bytes = convert_pem_to_pkcs12(
                self.user.certpem, self.user.certkey, self.user.callsign, None, self.user.callsign
            )
            tgtfile.parent.mkdir(parents=True, exist_ok=True)
            tgtfile.write_bytes(p12bytes)
            LOGGER.debug("{} exists: {}".format(tgtfile, tgtfile.exists()))
        else:
            raise RuntimeError("IDK what to do")

    async def chk_manifest_file_extra_folder(self, row: str, tmp_folder: Path) -> Path:
        """Check folder path from manifest, return updated path if folder was located"""
        xml_value: str = row.split(">")[1].split("<")[0]
        if "/" in xml_value:
            manifest_file = tmp_folder / xml_value
            manifest_file.parent.mkdir(parents=True, exist_ok=True)
            LOGGER.info("File defined in manifest in folder {}".format(manifest_file.parent.absolute()))
            return manifest_file.parent.absolute()
        return tmp_folder
