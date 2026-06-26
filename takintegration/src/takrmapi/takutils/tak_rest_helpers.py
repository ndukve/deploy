"""Helper functions to manage tak"""

from typing import Any, Mapping, Union, cast, List, Dict
import logging
import time
import urllib.parse
import aiohttp


from libpvarki.schemas.product import UserCRUDRequest

from takrmapi.takutils.tak_helpers import UserCRUD, Helpers
from takrmapi.takutils.tak_pkg_helpers import TAKDataPackage


LOGGER = logging.getLogger(__name__)

# FIXME: Convert the helpers to dataclasses


class RestHelpers:  # pylint: disable=too-few-public-methods
    """Helper class to make queries against TAK rest API"""

    # FIXME: Refactor to separate helpers not requiring a dummy user
    def __init__(
        self,
        user: UserCRUD = UserCRUD(
            UserCRUDRequest(uuid="not_used_now", callsign="not_used_now", x509cert="not_used_now")
        ),
    ):
        """RestHelpers init"""
        self.helpers = Helpers(user)

    async def output_response_to_output(self, resp: aiohttp.ClientResponse) -> None:
        """Output response to log"""
        resp_text = await resp.text()
        LOGGER.info("Response status : {}, Response text : {}".format(resp.status, resp_text))

    async def tak_api_user_list(self) -> Mapping[str, Any]:
        """Get list of users from TAK"""
        async with await self.helpers.tak_mtls_client() as session:
            try:
                url = f"{self.helpers.tak_base_url()}/user-management/api/list-users"
                resp = await session.get(url, ssl=await self.helpers.tak_mtls_client_sslcontext())
                data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))
            except aiohttp.ClientError:
                return {"success": False, "data": []}
        LOGGER.info("tak_api_user_list={}".format(data))

        return {"success": True, "data": data}

    async def tak_api_mission_get(self, groupname: str) -> Mapping[str, Any]:
        """Get mission from TAK"""
        async with await self.helpers.tak_mtls_client() as session:
            try:
                url = f"{self.helpers.tak_base_url()}/Marti/api/missions/{groupname}"

                resp = await session.get(url, ssl=await self.helpers.tak_mtls_client_sslcontext())
                data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))

                if resp.status == 200:
                    return {"success": True, "data": data}

                LOGGER.info("Unable to find requested mission '{}' from TAK".format(groupname))
                await self.output_response_to_output(resp)
                return {"success": True, "data": data}
            except aiohttp.ClientError as e:
                LOGGER.exception(e)
                return {"success": False, "data": []}

    async def tak_api_mission_put(self, groupname: str, description: str, default_role: str) -> Mapping[str, Any]:
        """Put mission to TAK"""

        description_urlencoded = urllib.parse.quote(description)
        async with await self.helpers.tak_mtls_client() as session:
            try:
                url = f"{self.helpers.tak_base_url()}/Marti/api/missions/\
{groupname}?\
group=default&\
description={description_urlencoded}&\
tool=public&\
defaultRole={default_role}&\
inviteOnly=false&\
allowGroupChange=false"
                headers = {"Content-Type": "application/json", "accept": "*/*"}

                resp = await session.put(
                    url, json='"string"', ssl=await self.helpers.tak_mtls_client_sslcontext(), headers=headers
                )
                data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))
                if resp.status == 201:
                    return {"success": True, "data": data}

                LOGGER.info("Unable to add requested mission '{}' to TAK".format(groupname))
                await self.output_response_to_output(resp)
                return {"success": True, "data": data}
            except aiohttp.ClientError:
                return {"success": False, "data": []}

    async def tak_api_mission_keywords(self, groupname: str, keywords: List[str]) -> Mapping[str, Any]:
        """Put keywords to mission"""

        async with await self.helpers.tak_mtls_client() as session:
            try:
                url = f"{self.helpers.tak_base_url()}/Marti/api/missions/{groupname}/keywords"

                resp = await session.put(url, json=keywords, ssl=await self.helpers.tak_mtls_client_sslcontext())
                data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))

                if resp.status == 200:
                    return {"success": True, "data": data}

                LOGGER.info("Unable to add keywords {} to mission '{}'".format(keywords, groupname))
                await self.output_response_to_output(resp)
                return {"success": True, "data": data}

            except aiohttp.ClientError:
                return {"success": False, "data": []}

    async def tak_api_get_device_profile(self, profile_name: str) -> Mapping[str, Any]:
        """Get device profile from TAK"""
        async with await self.helpers.tak_mtls_client() as session:
            try:
                url = f"{self.helpers.tak_base_url()}/Marti/api/device/profile/{profile_name}"

                resp = await session.get(url, ssl=await self.helpers.tak_mtls_client_sslcontext(), json="{}")
                data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))

            except aiohttp.ClientError:
                return {"success": False, "data": {}}

            return {"success": True, "data": data}

    async def tak_api_get_device_profile_files(self, profile_name: str) -> Mapping[str, Any]:
        """Get device profile from TAK"""
        async with await self.helpers.tak_mtls_client() as session:
            try:
                url = f"{self.helpers.tak_base_url()}/Marti/api/device/profile/{profile_name}/files"

                resp = await session.get(url, ssl=await self.helpers.tak_mtls_client_sslcontext(), json="{}")
                data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))
            except aiohttp.ClientError:
                return {"success": False, "data": []}

            return {"success": True, "data": data}

    async def tak_api_add_device_profile(self, profile_name: str, groups: List[str]) -> Mapping[str, Any]:
        """Add device profile to TAK"""
        group_str: str = "?group=".join(groups)
        async with await self.helpers.tak_mtls_client() as session:
            try:
                # url = f"{self.helpers.tak_base_url()}/Marti/api/device/profile/{profile_name}"
                url = f"{self.helpers.tak_base_url()}/Marti/api/device/profile/{profile_name}?group={group_str}"

                resp = await session.post(url, ssl=await self.helpers.tak_mtls_client_sslcontext(), json={})
                data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))

                if resp.status == 201:
                    return {"success": True, "data": data}

                LOGGER.info("Unable to add device_profile '{}' ".format(profile_name))
                await self.output_response_to_output(resp)
                return {"success": True, "data": data}

            except aiohttp.ClientError:
                return {"success": False, "data": []}

    async def tak_api_update_device_profile(self, profile_name: str, profile_vars: Dict[Any, Any]) -> Mapping[str, Any]:
        """Update device profile at TAK"""

        profile_info = await self.tak_api_get_device_profile(profile_name=profile_name)

        async with await self.helpers.tak_mtls_client() as session:
            try:
                url = f"{self.helpers.tak_base_url()}/Marti/api/device/profile/{profile_name}"

                updated_time = int(time.time())

                resp = await session.put(
                    url,
                    ssl=await self.helpers.tak_mtls_client_sslcontext(),
                    json={
                        "id": profile_info["data"]["data"]["id"],
                        "name": profile_name,
                        "active": profile_vars["profile_active"],
                        "applyOnConnect": profile_vars["apply_on_connect"],
                        "applyOnEnrollment": profile_vars["apply_on_enrollment"],
                        "type": profile_vars["profile_type"],
                        "tool": profile_vars["tool"],
                        "updated": f"{updated_time}",
                        "groups": profile_vars["groups"],
                    },
                )
                data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))

                if resp.status == 200:
                    return {"success": True, "data": data}

                LOGGER.info("Unable to update device_profile '{}' ".format(profile_name))
                await self.output_response_to_output(resp)
                return {"success": True, "data": data}

            except aiohttp.ClientError:
                return {"success": False, "data": []}

    async def check_file_in_profile_files(
        self, datapackage: TAKDataPackage, tak_profile_files: Mapping[str, Any]
    ) -> bool:
        """Check if file is in given profile file list from TAK"""
        f: str = datapackage.package_name
        if datapackage.is_folder:
            f = datapackage.package_name + ".zip"
        if f.endswith(".tpl"):
            f = f.replace(".tpl", "")

        if len(tak_profile_files["data"]["data"]) > 0:
            for file in tak_profile_files["data"]["data"]:
                if file["name"] == f:
                    LOGGER.info(
                        "File '{}' is already attached to profile. No need to add again.".format(
                            datapackage.package_name
                        )
                    )
                    return True
        return False

    async def tak_api_upload_file_to_profile(self, profile_name: str, datapackage: TAKDataPackage) -> Mapping[str, Any]:
        """Add file to device profile at TAK"""

        profile_files = await self.tak_api_get_device_profile_files(
            profile_name=profile_name,
        )

        if await self.check_file_in_profile_files(datapackage=datapackage, tak_profile_files=profile_files):
            return {"success": True, "data": profile_files["data"]}

        async with await self.helpers.tak_mtls_client() as session:
            try:
                url = f"{self.helpers.tak_base_url()}\
/Marti/api/device/profile/{profile_name}/file?filename={datapackage.package_upload_dst_fname}"

                if datapackage.is_template_file:
                    resp = await session.put(
                        url,
                        ssl=await self.helpers.tak_mtls_client_sslcontext(),
                        data=datapackage.template_str.encode(encoding="utf-8"),
                    )
                    data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))
                else:
                    with open(datapackage.package_upload_src_file, "rb") as f:
                        resp = await session.put(
                            url, ssl=await self.helpers.tak_mtls_client_sslcontext(), data=f.read()
                        )
                        data = cast(Mapping[str, Union[Any, Mapping[str, Any]]], await resp.json(content_type=None))

                if resp.status == 200:
                    return {"success": True, "data": data}

                LOGGER.info("Unable to add device_profile '{}' ".format(datapackage.package_upload_dst_fname))
                await self.output_response_to_output(resp)
                return {"success": True, "data": data}

            except aiohttp.ClientError:
                return {"success": False, "data": []}
