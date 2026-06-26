"""FastAPI application factory for rmcryptpad."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .. import __version__
from ..config import RMCryptPadSettings
from ..db.dbinit import init_db
from ..oidc.keys import OIDCKeyManager
from .clients import router as clientsrouter
from .clients import router_admin as clientsrouter_admin
from .description import router as descriptionsrouter
from .description import router_v2 as descriptionsrouterv2
from .health import router as healthrouter
from .instructions import router as instructionsrouter
from .interop import interoprouter
from .oidc import router as oidcrouter
from .usercrud import crudrouter

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize the database and OIDC key manager on startup."""
    _ = app
    await asyncio.gather(init_db())
    OIDCKeyManager.singleton()
    yield None


def get_app_no_init() -> FastAPI:
    """Return the application without logging bootstrap."""
    app = FastAPI(
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        title="RM CryptPad integration API",
        lifespan=app_lifespan,
        version=__version__,
    )
    app.mount(
        "/ui/cryptpad",
        StaticFiles(directory=RMCryptPadSettings.singleton().ui_dir, check_dir=False),
        name="cryptpad-ui",
    )
    app.include_router(healthrouter, prefix="/api/v1", tags=["health"])
    app.include_router(crudrouter, prefix="/api/v1/users", tags=["users"])
    app.include_router(interoprouter, prefix="/api/v1/interop", tags=["interop"])
    app.include_router(instructionsrouter, prefix="/api/v1", tags=["instructions"])
    app.include_router(descriptionsrouter, prefix="/api/v1", tags=["description"])
    app.include_router(descriptionsrouterv2, prefix="/api/v2", tags=["description"])
    app.include_router(clientsrouter, prefix="/api/v2", tags=["clients"])
    app.include_router(clientsrouter_admin, prefix="/api/v2", tags=["admin-clients"])
    app.include_router(oidcrouter, tags=["oidc"])
    return app


def get_app() -> FastAPI:
    """Return the application with logging initialized."""
    settings = RMCryptPadSettings.singleton()
    LOGGER.debug("Active config: %s", settings)
    return get_app_no_init()
