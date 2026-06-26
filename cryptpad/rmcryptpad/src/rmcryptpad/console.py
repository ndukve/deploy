"""CLI entrypoint for rmcryptpad."""

from __future__ import annotations

import uvicorn

from .web.application import get_app


def rmcryptpad_cli() -> None:
    """Run the API server."""
    uvicorn.run(get_app(), host="0.0.0.0", port=8000)  # nosec B104 - runs in container
