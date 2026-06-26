"""Test CLI scripts"""

import asyncio
import os

import pytest
from libadvian.binpackers import ensure_str

from miniwerk import __version__
from miniwerk.config import MWConfig


@pytest.mark.asyncio
async def test_version_cli():  # type: ignore
    """Test the CLI parsing for default version dumping works"""
    cmd = "miniwerk --version"
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out = await asyncio.wait_for(process.communicate(), 10)
    # Demand clean exit
    assert process.returncode == 0
    # Check output
    assert ensure_str(out[0]).strip().endswith(__version__)


@pytest.mark.asyncio
async def test_manifest_cli():  # type: ignore
    """Test the CLI command for dumping manifests works"""
    conf = MWConfig()
    cmd = "miniwerk manifests"
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=os.environ,
    )
    await asyncio.wait_for(process.communicate(), 10)
    # Demand clean exit
    assert process.returncode == 0
    # Check output
    for manifile in conf.product_manifest_paths.values():
        assert manifile.exists()
