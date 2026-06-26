"""Routes for interoperation between products"""

import logging

from fastapi import APIRouter, Depends, Request
from libpvarki.middleware import MTLSHeader
from libpvarki.schemas.generic import OperationResultResponse


from .usercrud import comes_from_rm
from ..db.product import Product
from ..db.errors import NotFound
from ..db.engine import EngineWrapper
from ..schema.interop import ProductAddRequest, ProductAuthzResponse

LOGGER = logging.getLogger(__name__)

interoprouter = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


@interoprouter.post("/add")
async def add_product(
    product: ProductAddRequest,
    request: Request,
) -> OperationResultResponse:
    """Product needs interop privileges. This can only be called by RASENMAEHER"""
    comes_from_rm(request)
    try:
        exists = await Product.by_cn(product.certcn)
        if exists:
            LOGGER.info("Product {} already exists".format(product.certcn))
    except NotFound:
        with EngineWrapper.singleton().get_session() as session:
            dbproduct = Product(certcn=product.certcn)
            session.add(dbproduct)
            session.commit()
    result = OperationResultResponse(success=True)
    return result


@interoprouter.get("/authz")
async def get_authz(
    request: Request,
) -> ProductAuthzResponse:
    """Get authz info for the product"""
    payload = request.state.mtlsdn
    product = await Product.by_cn(payload.get("CN"))
    result = ProductAuthzResponse(
        type="basic",
        username=product.certcn,
        password=product.mtxpassword,
        ro_password=product.stream_ro_password,
    )
    return result
