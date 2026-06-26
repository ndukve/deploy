"""Package level tests"""

from miniwerk import __version__


def test_version() -> None:
    """Make sure version matches expected"""
    assert __version__ == "1.10.0+260613"
