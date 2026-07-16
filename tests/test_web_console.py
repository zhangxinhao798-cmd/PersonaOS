"""Tests for the PersonaOS Web Experience language resource boundary."""

import json
from pathlib import Path


WEB_CONSOLE = Path("frontend") / "web-console"
ZH_CN_RESOURCE = WEB_CONSOLE / "i18n" / "zh-CN.json"
EN_US_RESOURCE = WEB_CONSOLE / "i18n" / "en-US.json"
I18N_INDEX = WEB_CONSOLE / "i18n" / "index.js"


def load_zh_cn() -> dict:
    return json.loads(ZH_CN_RESOURCE.read_text(encoding="utf-8"))


def test_web_console_files_exist() -> None:
    assert (WEB_CONSOLE / "index.html").exists()
    assert (WEB_CONSOLE / "app.js").exists()
    assert (WEB_CONSOLE / "style.css").exists()
    assert ZH_CN_RESOURCE.exists()
    assert EN_US_RESOURCE.exists()
    assert I18N_INDEX.exists()


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

    assert 'data-i18n="app.eyebrow"' in html
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
    assert 'value="en-US"' in html
    assert 'value="en-US" data-i18n="language.en_US" disabled' in html
    assert 'const DEFAULT_LANGUAGE = "zh-CN"' in app_js
    assert 'new Set(["zh-CN"])' in app_js
    assert "document.documentElement.lang = language" in app_js


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
    for concept in ("digital_mind", "persona", "memory", "skills", "evolution"):
        assert f'data-i18n="welcome.concepts.{concept}.name"' in html
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
    assert 'const RELATIONSHIP_IDS = ["assistant", "mentor", "companion", "analyst"]' in app_js
    assert "description.textContent = relationship.description" in app_js


def test_web_experience_has_session_summary() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert 'id="sessionSummary"' in html
    assert 'id="summaryPersona"' in html
    assert 'id="summaryRelationship"' in html
    assert 'id="summaryLanguage"' in html
    assert 'data-i18n="session.memory_scope"' in html
    assert "sessionSummary.hidden = !state.activeSessionId" in app_js


def test_web_experience_preserves_i18n_extension_points() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")

    assert 'data-i18n="welcome.title"' in html
    assert 'data-i18n="setup.persona"' in html
    assert 'data-i18n="setup.relationship"' in html
    assert 'data-i18n="setup.language"' in html


def test_zh_cn_resource_contains_required_ui_sections() -> None:
    resource = load_zh_cn()

    assert set(resource) == {
        "app",
        "welcome",
        "setup",
        "persona",
        "relationship",
        "language",
        "chat",
        "session",
        "status",
    }
    assert resource["app"]["page_title"] == "PersonaOS 体验"
    assert resource["setup"]["start"] == "开始体验"
    assert resource["chat"]["send"] == "发送"
    assert resource["chat"]["placeholder"] == "输入消息..."


def test_relationship_copy_is_loaded_from_language_resource() -> None:
    resource = load_zh_cn()
    relationship_types = resource["relationship"]["types"]

    assert set(relationship_types) == {"assistant", "mentor", "companion", "analyst"}
    for relationship in relationship_types.values():
        assert relationship["name"]
        assert relationship["description"]
        assert relationship["scenario"]


def test_web_console_loads_default_language_resource() -> None:
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    assert "loadLanguageResources(DEFAULT_LANGUAGE)" in app_js
    assert 'fetch(`./i18n/${language}.json`)' in app_js
    assert "applyTranslations" in app_js
    assert "navigator.language" not in app_js


def test_language_registry_preserves_future_english_extension() -> None:
    index_js = I18N_INDEX.read_text(encoding="utf-8")
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")

    assert '"en-US": "./en-US.json"' in index_js
    assert '"en-US"' in html
    assert 'value="en-US"' in html


def test_all_static_html_i18n_keys_exist_in_zh_cn() -> None:
    import re

    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    resource = load_zh_cn()

    def resolve(key: str):
        current = resource
        for part in key.split("."):
            current = current[part]
        return current

    keys = set(re.findall(r'data-i18n(?:-[a-z-]+)?="([^"]+)"', html))
    assert keys
    for key in keys:
        assert isinstance(resolve(key), str), key


def test_web_console_has_no_static_user_facing_english_copy() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_CONSOLE / "app.js").read_text(encoding="utf-8")

    for copy in (
        "Choose a persona",
        "Choose a relationship",
        "Start experience",
        "Send a message...",
        "Session scoped",
        "AI Personality Experience",
        "Language resource could not be loaded",
    ):
        assert copy not in html
        assert copy not in app_js


def test_primary_ui_copy_is_not_hard_coded_in_html() -> None:
    html = (WEB_CONSOLE / "index.html").read_text(encoding="utf-8")

    for copy in (
        "Choose a persona",
        "Choose a relationship",
        "Start experience",
        "Send a message...",
        "Session scoped",
    ):
        assert copy not in html
