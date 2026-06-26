"""Descriptions API"""

from typing import Optional, Literal
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, Extra
from libpvarki.schemas.product import ProductDescription
from libpvarki.middleware import MTLSHeader
from takrmapi.config import read_tak_fqdn


LOGGER = logging.getLogger(__name__)

router = APIRouter()  # These endpoints are public
router_v2 = APIRouter()

router_v2_admin = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


class ProductComponent(BaseModel):  # pylint: disable=too-few-public-methods
    """Project component info"""

    type: Literal["link", "markdown", "component"]
    ref: str


class ProductDescriptionExtended(BaseModel):
    """Description of a product"""

    shortname: str = Field(description="Short name for the product, used as slug/key in dicts and urls")
    title: str = Field(description="Fancy name for the product")
    icon: Optional[str] = Field(description="URL for icon")
    description: str = Field(description="Short-ish description of the product")
    language: str = Field(description="Language of this response")
    docs: Optional[str] = Field(description="Link to documentation")
    component: ProductComponent = Field(description="Component type and ref")

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configs"""

        extra = Extra.forbid


@router.get(
    "/{language}",
    response_model=ProductDescription,
)
async def return_product_description(language: str) -> ProductDescription:
    """Fetch description from each product in manifest"""
    if language == "fi":
        # FIXME: Localize
        return ProductDescription(
            shortname="tak",
            title="TAK: Team Awareness Kit",
            icon=None,
            description="Situational awareness system",
            language="en",
        )
    if language == "sv":
        # FIXME: Localize
        return ProductDescription(
            shortname="tak",
            title="TAK: Team Awareness Kit",
            icon=None,
            description="Situational awareness system",
            language="en",
        )
    # Fall back to English
    return ProductDescription(
        shortname="tak",
        title="TAK: Team Awareness Kit",
        icon=None,
        description="Situational awareness system",
        language="en",
    )


@router_v2.get(
    "/{language}",
    response_model=ProductDescriptionExtended,
)
async def return_product_description_extended(language: str) -> ProductDescriptionExtended:
    """Fetch description from each product in manifest"""

    if language == "fi":
        return ProductDescriptionExtended(
            shortname="tak",
            title="TAK: Team Awareness Kit",
            icon="/ui/tak/taklogo.svg",
            description="Tilannekuvajärjestelmä",
            language="fi",
            docs="https://docs.pvarki.fi/fi/docs/guides/tak-guide",
            component=ProductComponent(type="component", ref="/ui/tak/remoteEntry.js"),
        )
    if language == "sv":
        return ProductDescriptionExtended(
            shortname="tak",
            title="TAK: Team Awareness Kit",
            icon="/ui/tak/taklogo.svg",
            description="Situationsbildsystem",
            language="sv",
            docs="https://docs.pvarki.fi/sv/docs/guides/tak-guide",
            component=ProductComponent(type="component", ref="/ui/tak/remoteEntry.js"),
        )
    # Fall back to English
    return ProductDescriptionExtended(
        shortname="tak",
        title="TAK: Team Awareness Kit",
        icon="/ui/tak/taklogo.svg",
        description="Situational awareness system",
        language="en",
        docs="https://docs.pvarki.fi/en/docs/guides/tak-guide",
        component=ProductComponent(type="component", ref="/ui/tak/remoteEntry.js"),
    )


@router_v2_admin.get(
    "/{language}",
    response_model=ProductDescriptionExtended,
)
async def return_admin_product_description_extended(language: str) -> ProductDescriptionExtended:
    """Fetch admin description from each product in manifest"""

    if language == "fi":
        return ProductDescriptionExtended(
            shortname="tak-server",
            title="TAK Server",
            icon=None,
            description="TAK Serverin hallintapaneeli",
            language="fi",
            docs=None,
            component=ProductComponent(type="link", ref="https://" + read_tak_fqdn() + ":8443"),
        )
    if language == "sv":
        return ProductDescriptionExtended(
            shortname="tak-server",
            title="TAK Server",
            icon=None,
            description="TAK Server kontrollpanel",
            language="sv",
            docs=None,
            component=ProductComponent(type="link", ref="https://" + read_tak_fqdn() + ":8443"),
        )
    # Fall back to English
    return ProductDescriptionExtended(
        shortname="tak-server",
        title="TAK Server",
        icon=None,
        description="Control panel for TAK Server",
        language="en",
        docs=None,
        component=ProductComponent(type="link", ref="https://" + read_tak_fqdn() + ":8443"),
    )
