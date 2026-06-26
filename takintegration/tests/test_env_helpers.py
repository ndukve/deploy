"""Tests for env_helpers"""

import pytest

from takrmapi.takutils.env_helpers import env_float


def test_env_float_happy_float(monkeypatch: pytest.MonkeyPatch) -> None:
    """Env var set to a valid float string is returned as float."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "3.14")
    assert env_float("TEST_ENV_FLOAT", 1.0) == pytest.approx(3.14)


def test_env_float_happy_int(monkeypatch: pytest.MonkeyPatch) -> None:
    """Env var set to an integer string is coerced to float."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "10")
    result = env_float("TEST_ENV_FLOAT", 1.0)
    assert isinstance(result, float)
    assert result == pytest.approx(10.0)


def test_env_float_illegal_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """Env var set to a non-numeric string falls back to the default."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "not_a_number")
    assert env_float("TEST_ENV_FLOAT", 5.0) == pytest.approx(5.0)


def test_env_float_illegal_value_emits_warning(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Illegal env var value produces a WARNING log entry and returns the default."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "bad")
    with caplog.at_level("WARNING", logger="takrmapi.takutils.env_helpers"):
        result = env_float("TEST_ENV_FLOAT", 25.0)
    assert "TEST_ENV_FLOAT" in caplog.text
    assert result == pytest.approx(25.0)


def test_env_float_exceeds_max_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Value above max_value falls back to the default."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "601")
    assert env_float("TEST_ENV_FLOAT", 5.0, max_value=600.0) == pytest.approx(5.0)


def test_env_float_at_max_boundary_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Value exactly at max_value is accepted (inclusive upper bound)."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "600")
    assert env_float("TEST_ENV_FLOAT", 5.0, max_value=600.0) == pytest.approx(600.0)


def test_env_float_missing_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Absent env var returns the default value."""
    monkeypatch.delenv("TEST_ENV_FLOAT", raising=False)
    assert env_float("TEST_ENV_FLOAT", 7.5) == pytest.approx(7.5)


def test_env_float_empty_string_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty string env var is treated as unset and returns the default."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "")
    assert env_float("TEST_ENV_FLOAT", 2.0) == pytest.approx(2.0)


def test_env_float_at_min_boundary_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Value exactly at min_value is accepted (inclusive lower bound)."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "0")
    assert env_float("TEST_ENV_FLOAT", 0.0) == pytest.approx(0.0)


def test_env_float_negative_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Negative value is below min_value and falls back to the default."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "-1.0")
    assert env_float("TEST_ENV_FLOAT", 5.0) == pytest.approx(5.0)


def test_env_float_inf_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Infinity exceeds the default max_value of 600.0 and falls back to the default."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "inf")
    assert env_float("TEST_ENV_FLOAT", 5.0) == pytest.approx(5.0)


def test_env_float_nan_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """NaN fails all comparisons and falls back to the default."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "nan")
    assert env_float("TEST_ENV_FLOAT", 5.0) == pytest.approx(5.0)


def test_env_float_whitespace_padded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Whitespace-padded numeric string is accepted since float() strips whitespace."""
    monkeypatch.setenv("TEST_ENV_FLOAT", "  3.14  ")
    assert env_float("TEST_ENV_FLOAT", 1.0) == pytest.approx(3.14)


def test_env_float_falsy_default_missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Absent env var falls back to a falsy default of 0.0 correctly.

    0.0 is falsy in Python, so the 'os.getenv(key) or default' expression
    must be evaluated carefully: None or 0.0 yields 0.0, not a silent discard.
    """
    monkeypatch.delenv("TEST_ENV_FLOAT", raising=False)
    assert env_float("TEST_ENV_FLOAT", 0.0) == pytest.approx(0.0)


def test_env_float_invalid_default_raises() -> None:
    """A default outside the allowed range raises ValueError immediately at startup."""
    with pytest.raises(ValueError, match="default .* is outside allowed range"):
        env_float("TEST_ENV_FLOAT", 9999.0, max_value=600.0)


def test_env_float_inverted_bounds_raises() -> None:
    """min_value > max_value is a programming error caught via the default validation."""
    with pytest.raises(ValueError, match="default .* is outside allowed range"):
        env_float("TEST_ENV_FLOAT", 5.0, min_value=100.0, max_value=10.0)
