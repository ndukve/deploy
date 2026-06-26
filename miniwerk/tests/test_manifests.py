"""Test manifest creation"""

import json
import logging
from pathlib import Path

import pytest

from miniwerk.config import MWConfig
from miniwerk.jwt import get_verifier
from miniwerk.manifests import create_all_product_manifests, create_rasenmaeher_manifest

LOGGER = logging.getLogger(__name__)


def check_jwt_pubkey(pth: Path) -> None:
    """Check JWT pubkey has been copied"""
    pubkeypth = pth.parent / "publickeys" / "kraftwerk.pub"
    assert pubkeypth.exists()


@pytest.mark.asyncio
async def test_rm_manifest() -> None:
    """Check RASENMAEHER manifest creation"""
    config = MWConfig.singleton()
    pth = await create_rasenmaeher_manifest()
    script_path = pth.parent / "hosts_script.sh"
    assert script_path.exists()
    check_jwt_pubkey(pth)
    manifest = json.loads(pth.read_text(encoding="utf-8"))
    LOGGER.debug(f"manifest={manifest}")
    assert manifest["dns"] == config.domain
    assert "fake" in manifest["products"]
    assert "tak" in manifest["products"]
    assert "cryptpad" in manifest["products"]
    assert "certcn" in manifest["products"]["tak"]
    assert manifest["products"]["tak"]["certcn"] == "tak.pytest.pvarki.fi"
    assert manifest["products"]["cryptpad"]["api"] == "https://rmcryptpad.pytest.pvarki.fi:4626/"
    assert manifest["products"]["cryptpad"]["uri"] == "https://mtls.cryptpad.pytest.pvarki.fi:4626/"
    assert manifest["products"]["cryptpad"]["certcn"] == "cryptpad.pytest.pvarki.fi"


@pytest.mark.asyncio
async def test_fakeproduct_manifest() -> None:
    """Check fakeproduct manifest"""
    config = MWConfig.singleton()
    pth = [cand for cand in await create_all_product_manifests() if "/fake/" in str(cand)][0]  # noqa: RUF015
    script_path = pth.parent / "hosts_script.sh"
    assert script_path.exists()
    check_jwt_pubkey(pth)
    manifest = json.loads(pth.read_text(encoding="utf-8"))
    LOGGER.debug(f"manifest={manifest}")
    verifier = await get_verifier()
    claims = verifier.decode(manifest["rasenmaeher"]["init"]["csr_jwt"])
    LOGGER.debug(f"claims={claims}")
    assert claims["csr"]
    assert claims["nonce"]
    assert f"mtls.{config.domain}" in manifest["rasenmaeher"]["mtls"]["base_uri"]


@pytest.mark.asyncio
async def test_cryptpad_manifest() -> None:
    """Check cryptpad manifest"""
    config = MWConfig.singleton()
    pth = [cand for cand in await create_all_product_manifests() if "/cryptpad/" in str(cand)][0]  # noqa: RUF015
    script_path = pth.parent / "hosts_script.sh"
    assert script_path.exists()
    check_jwt_pubkey(pth)
    manifest = json.loads(pth.read_text(encoding="utf-8"))
    LOGGER.debug(f"manifest={manifest}")
    assert manifest["product"]["dns"] == f"cryptpad.{config.domain}"
    assert manifest["product"]["api"] == f"https://rmcryptpad.{config.domain}:4626/"
    assert manifest["product"]["uri"] == f"https://mtls.cryptpad.{config.domain}:4626/"
