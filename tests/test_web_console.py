"""Tests for PersonaOS Web Console v0.1 static assets."""

from pathlib import Path


WEB_CONSOLE = Path("frontend") / "web-console"


def test_web_console_files_exist() -> None:
    assert (WEB_CONSOLE / "index.html").exists()
    assert (WEB_CONSOLE / "app.js").exists()
    assert (WEB_CONSOLE / "style.css").exists()


def test_web_console_uses_existing_api_routes() -> None:
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert 'apiRequest("/personas")' in app_js
    assert 'apiRequest("/sessions"' in app_js
    assert "/messages" in app_js
    assert "/history" in app_js


def test_web_console_does_not_introduce_frontend_framework() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    combined = f"{html}\n{app_js}".lower()
    assert "react" not in combined
    assert "vite" not in combined
    assert "vue" not in combined
    assert "node_modules" not in combined
