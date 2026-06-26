"""Schemas for userinfo.py, including client instructions and mission ZIP files."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field, Extra


class TakZipFile(BaseModel):  # pylint: disable=too-few-public-methods
    """Represents a single ZIP file containing mission data or product instructions."""

    title: str = Field(description="Original filename or title of the zip file.")
    filename: str = Field(description="Filename used for download, includes user callsign.")
    data: str = Field(
        description="Base64-encoded zip file contents", examples=["data:application/zip;base64,UEsDBBQAAAAI..."]
    )

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configs"""

        extra = Extra.forbid


class ClientInstructionData(BaseModel):  # pylint: disable=too-few-public-methods
    """Container for a list of mission-related ZIP files sent to a client."""

    tak_zips: List[TakZipFile] = Field(description="List of packaged mission zip files.")

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configs"""

        extra = Extra.forbid


class ClientInstructionResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Response schema for returning client mission instructions."""

    data: ClientInstructionData = Field(description="Container object for returned data.")

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configs"""

        extra = Extra.forbid


class TAKAdminPackageListResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Response schema for returning available TAK datapackages."""

    data: Dict[str, Any] = Field(description="Response dict containing available packages")

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configs"""

        extra = Extra.forbid
