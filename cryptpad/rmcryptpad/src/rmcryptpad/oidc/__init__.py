"""OIDC support for rmcryptpad."""

from .keys import OIDCKeyManager
from .service import OIDCProvider

__all__ = ["OIDCKeyManager", "OIDCProvider"]
