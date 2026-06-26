"""Interop contract routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ..db.product import Product
from ..schema import OperationResultResponse
from ..schema.interop import ProductAddRequest, ProductAuthzResponse
from .security import get_client_cn, require_rm_caller, require_verified_mtls_header

interoprouter = APIRouter(dependencies=[Depends(require_verified_mtls_header)])


@interoprouter.post("/add", response_model=OperationResultResponse)
async def add_product(
    product: ProductAddRequest, request: Request
) -> OperationResultResponse:
    """Register a peer product."""
    require_rm_caller(request)
    await Product.create_or_update(certcn=product.certcn)
    return OperationResultResponse(success=True)


@interoprouter.get("/authz", response_model=ProductAuthzResponse)
async def get_authz(request: Request) -> ProductAuthzResponse:
    """Return product-to-product authz credentials."""
    product = await Product.by_cn(get_client_cn(request))
    return ProductAuthzResponse(
        type="basic", username=product.api_username, password=product.api_password
    )
