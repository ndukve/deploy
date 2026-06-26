"""Test CLI scripts"""

import asyncio

import pytest
from libadvian.binpackers import ensure_str

from rmmtxauthz import __version__


@pytest.mark.asyncio
async def test_version_cli() -> None:
    """Test the CLI parsing for default version dumping works"""
    cmd = "rmmtxauthz --version"
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
