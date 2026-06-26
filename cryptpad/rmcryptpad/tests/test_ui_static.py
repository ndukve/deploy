"""Tests for serving the federated UI bundle."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rmcryptpad.config import RMCryptPadSettings
from rmcryptpad.web.application import get_app_no_init


def test_ui_bundle_is_served_from_nested_mount(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify the UI static mount serves the built bundle."""

    async def noop_init_db() -> None:
        return None

    ui_dir = tmp_path / "ui"
    ui_dir.mkdir()
    (ui_dir / "remoteEntry.js").write_text("// remote bundle\n", encoding="utf-8")

    monkeypatch.setattr("rmcryptpad.web.application.init_db", noop_init_db)
    monkeypatch.setattr(
        "rmcryptpad.web.application.OIDCKeyManager.singleton", lambda: None
    )
    monkeypatch.setenv("RMCRYPTPAD_UI_DIR", str(ui_dir))
    RMCryptPadSettings._singleton = None  # pylint: disable=protected-access
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.get("/ui/cryptpad/remoteEntry.js")

    assert response.status_code == 200
    assert response.text == "// remote bundle\n"
