"""Persistent signing key management for OIDC."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from ..config import RMCryptPadSettings


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_int(value: int) -> str:
    width = (value.bit_length() + 7) // 8
    return _b64url(value.to_bytes(width, "big"))


@dataclass
class OIDCKeyManager:
    """Load or create the RSA signing key used for OIDC tokens."""

    key_dir: Path = field(
        default_factory=lambda: Path(RMCryptPadSettings.singleton().oidc_key_dir)
    )
    _private_key: rsa.RSAPrivateKey | None = field(default=None, init=False, repr=False)

    _singleton: ClassVar[Optional["OIDCKeyManager"]] = None

    def __post_init__(self) -> None:
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self._private_key = self._load_or_create_private_key()

    @classmethod
    def singleton(cls) -> "OIDCKeyManager":
        """Return the cached key manager."""
        if cls._singleton is None:
            cls._singleton = cls(
                key_dir=Path(RMCryptPadSettings.singleton().oidc_key_dir)
            )
        return cls._singleton

    @property
    def private_key(self) -> rsa.RSAPrivateKey:
        """Return the private key."""
        assert self._private_key is not None
        return self._private_key

    @property
    def private_key_path(self) -> Path:
        """Return the path to the PEM key file."""
        return self.key_dir / "oidc-signing-key.pem"

    @property
    def kid(self) -> str:
        """Return the SHA-256 thumbprint of the public key."""
        pub = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return hashlib.sha256(pub).hexdigest()

    def _load_or_create_private_key(self) -> rsa.RSAPrivateKey:
        key_path = self.private_key_path
        if key_path.is_file():
            data = key_path.read_bytes()
            key = serialization.load_pem_private_key(data, password=None)
            if not isinstance(key, rsa.RSAPrivateKey):
                raise TypeError(f"Expected RSA private key, got {type(key).__name__}")
            return key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        key_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        return private_key

    def public_jwk(self) -> dict[str, Any]:
        """Return the public key as a JWK."""
        numbers = self.private_key.public_key().public_numbers()
        return {
            "kty": "RSA",
            "use": "sig",
            "alg": "RS256",
            "kid": self.kid,
            "n": _b64url_int(numbers.n),
            "e": _b64url_int(numbers.e),
        }

    def sign_jwt(self, header: dict[str, Any], payload: dict[str, Any]) -> str:
        """Sign a JWT using RS256."""
        header_b64 = _b64url(
            json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        payload_b64 = _b64url(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        signature = self.private_key.sign(
            signing_input, padding.PKCS1v15(), hashes.SHA256()
        )
        return f"{header_b64}.{payload_b64}.{_b64url(signature)}"

    def verify_jwt(self, token: str) -> dict[str, Any]:
        """Verify and decode a JWT signed with the managed key."""
        header_b64, payload_b64, signature_b64 = token.split(".")
        header: dict[str, Any] = json.loads(base64.urlsafe_b64decode(_pad(header_b64)))
        if header.get("alg") != "RS256":
            raise ValueError("Unsupported JWT algorithm")
        if header.get("kid") != self.kid:
            raise ValueError("Unknown JWT key id")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        signature = base64.urlsafe_b64decode(_pad(signature_b64))
        self.private_key.public_key().verify(
            signature, signing_input, padding.PKCS1v15(), hashes.SHA256()
        )
        result: dict[str, Any] = json.loads(base64.urlsafe_b64decode(_pad(payload_b64)))
        return result


def _pad(value: str) -> bytes:
    return value.encode("utf-8") + b"=" * (-len(value) % 4)
