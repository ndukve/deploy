"""Descriptions API"""

from __future__ import annotations
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Request
from libpvarki.middleware import MTLSHeader
from libpvarki.schemas.product import ProductDescription
from pydantic import BaseModel, Field

from .usercrud import comes_from_rm

router = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])
router_v2 = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


class ProductComponent(BaseModel):
    """Project component info"""

    type: Literal["link", "markdown", "component"]
    ref: str


class ProductDescriptionExtended(BaseModel):
    """Description of a product"""

    shortname: str = Field(
        description="Short name for the product, used as slug/key in dicts and urls"
    )
    title: str = Field(description="Fancy name for the product")
    icon: Optional[str] = Field(description="URL for icon")
    description: str = Field(description="Short-ish description of the product")
    language: str = Field(description="Language of this response")
    docs: str = Field(description="Link to documentation")
    component: ProductComponent = Field(description="Component type and ref")

    class Config:
        """Pydantic configs"""

        extra = "forbid"


@router.get(
    "/description/{language}",
    response_model=ProductDescription,
)
async def return_product_description(
    language: str, request: Request
) -> ProductDescription:
    """The product description"""
    comes_from_rm(request)
    # FIXME: return in correct Rune format
    if language == "fi":
        return ProductDescription(
            shortname="mtx",
            title="MediaMTX",
            icon=None,
            description="Videon suoratoistopalvelu",
            language="fi",
        )
    return ProductDescription(
        shortname="mtx",
        title="MediaMTX",
        icon=None,
        description="Video streaming service",
        language="en",
    )


@router_v2.get(
    "/description/{language}",
    response_model=ProductDescriptionExtended,
)
async def return_product_description_extended(
    language: str, request: Request
) -> ProductDescriptionExtended:
    """Fetch description from each product in manifest"""
    comes_from_rm(request)
    shortname = "mtx"
    if language == "fi":
        return ProductDescriptionExtended(
            shortname=shortname,
            title="MediaMTX",
            icon="/ui/mtx/mtxlogo.svg",
            description="Videon suoratoistopalvelu",
            language=language,
            docs="https://docs.pvarki.fi/fi/docs/guides/mtx-guide",
            component=ProductComponent(
                type="component", ref=f"/ui/{shortname}/remoteEntry.js"
            ),
        )
    if language == "sv":
        return ProductDescriptionExtended(
            shortname=shortname,
            title="MediaMTX",
            icon="/ui/mtx/mtxlogo.svg",
            description="Videoströmningstjänst",
            language=language,
            docs="https://docs.pvarki.fi/sv/docs/guides/mtx-guide",
            component=ProductComponent(
                type="component", ref=f"/ui/{shortname}/remoteEntry.js"
            ),
        )
    return ProductDescriptionExtended(
        shortname=shortname,
        title="MediaMTX",
        icon="/ui/mtx/mtxlogo.svg",
        description="Video streaming service",
        language=language,
        docs="https://docs.pvarki.fi/en/docs/guides/mtx-guide",
        component=ProductComponent(
            type="component", ref=f"/ui/{shortname}/remoteEntry.js"
        ),
    )
