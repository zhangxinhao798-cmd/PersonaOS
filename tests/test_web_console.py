"""Tests for PersonaOS Web Experience v0.3 static assets."""

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


def test_web_console_exposes_persona_identity_panel() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert 'id="personaGallery"' in html
    assert 'id="personaName"' in html
    assert 'id="personaVersion"' in html
    assert 'id="personaDescription"' in html
    assert "displayPersonaVersion" in app_js
    assert "displayPersonaDescription" in app_js
    assert "renderPersonaGallery" in app_js


def test_web_console_has_chat_experience_states() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")
    css = (WEB_CONSOLE / "style.css").read_text(encoding="utf-8")

    assert "AI Personality Experience" in html
    assert "appendLoadingMessage" in app_js
    assert "setLoading" in app_js
    assert ".message.user" in css
    assert ".message.assistant" in css
    assert ".message.loading" in css


def test_web_console_supports_relationship_selection() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert 'id="relationshipSelect"' in html
    assert 'value="assistant"' in html
    assert 'value="mentor"' in html
    assert 'value="companion"' in html
    assert 'value="analyst"' in html
    assert 'relationship: { relationship_type: state.activeRelationshipType }' in app_js
    assert 'id="relationshipType"' in html


def test_web_console_has_language_selection_structure() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert 'id="languageSelect"' in html
    assert 'value="zh-CN"' in html
    assert 'value="en"' in html
    assert "document.documentElement.lang = state.language" in app_js


def test_web_console_exposes_persona_experience_card() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")

    assert 'class="persona-experience"' in html
    assert 'id="personaName"' in html
    assert 'id="personaVersion"' in html
    assert 'id="personaDescription"' in html
    assert 'id="relationshipType"' in html


def test_web_console_does_not_render_persona_api_data_as_html() -> None:
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert "button.innerHTML" not in app_js
    assert "description.textContent = displayPersonaDescription(persona)" in app_js


def test_web_console_does_not_introduce_frontend_framework() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    combined = f"{html}\n{app_js}".lower()
    assert "react" not in combined
    assert "vite" not in combined
    assert "vue" not in combined
    assert "node_modules" not in combined


def test_web_experience_has_architecture_accurate_welcome_flow() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert 'id="welcomeExperience"' in html
    for concept in ("Digital Mind", "Persona", "Memory", "Skills", "Evolution"):
        assert concept in html
    assert "personaos_welcome_seen" in app_js
    assert 'id="showWelcome"' in html


def test_web_experience_displays_extended_persona_summary() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert 'id="personaStyle"' in html
    assert 'id="personaTraits"' in html
    assert 'id="personaScenarios"' in html
    assert "displayPersonaStyle" in app_js
    assert "displayPersonaTraits" in app_js
    assert "displayPersonaScenarios" in app_js


def test_web_experience_explains_relationship_usage() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert 'id="relationshipGallery"' in html
    assert 'id="relationshipScenario"' in html
    assert "renderRelationshipGallery" in app_js
    assert app_js.count("scenario:") == 4
    assert "description.textContent = relationship.description" in app_js


def test_web_experience_has_session_summary() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert 'id="sessionSummary"' in html
    assert 'id="summaryPersona"' in html
    assert 'id="summaryRelationship"' in html
    assert 'id="summaryLanguage"' in html
    assert "Session scoped" in html
    assert "sessionSummary.hidden = !state.activeSessionId" in app_js


def test_web_experience_preserves_i18n_extension_points() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")

    assert 'data-i18n="welcome.title"' in html
    assert 'data-i18n="setup.persona"' in html
    assert 'data-i18n="setup.relationship"' in html
    assert 'data-i18n="setup.language"' in html
