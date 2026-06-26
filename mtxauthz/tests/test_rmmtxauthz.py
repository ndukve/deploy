"""Package level tests"""

from rmmtxauthz import __version__
from rmmtxauthz.config import RMMTXSettings


def test_version() -> None:
    """Make sure version matches expected"""
    assert __version__ == "1.6.1+260612"


def test_config() -> None:
    """Test some config features"""
    cnf = RMMTXSettings.singleton()
    protocols = cnf.protocols
    for key in ("hls", "webrtc", "rtsps", "rtmps", "srt"):
        assert key in protocols
    assert protocols["hls"].proto == "https"
    assert protocols["hls"].port == 9888
    assert protocols["rtsps"].proto == "rtsps"
    assert protocols["rtsps"].port == 8322
