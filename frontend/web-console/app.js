const DEFAULT_LANGUAGE = "zh-CN";
const SUPPORTED_LANGUAGES = new Set(["zh-CN"]);
const RELATIONSHIP_IDS = ["assistant", "mentor", "companion", "analyst"];

const state = {
  personas: [],
  activeSessionId: "",
  activePersonaId: "",
  activeRelationshipType: "assistant",
  language: DEFAULT_LANGUAGE,
  translations: {},
  isLoading: false,
};

const apiBaseInput = document.querySelector("#apiBase");
const welcomeExperience = document.querySelector("#welcomeExperience");
const dismissWelcomeButton = document.querySelector("#dismissWelcome");
const showWelcomeButton = document.querySelector("#showWelcome");
const personaSelect = document.querySelector("#personaSelect");
const personaGallery = document.querySelector("#personaGallery");
const relationshipSelect = document.querySelector("#relationshipSelect");
const relationshipGallery = document.querySelector("#relationshipGallery");
const relationshipDescription = document.querySelector("#relationshipDescription");
const relationshipScenario = document.querySelector("#relationshipScenario");
const relationshipType = document.querySelector("#relationshipType");
const languageSelect = document.querySelector("#languageSelect");
const reloadPersonasButton = document.querySelector("#reloadPersonas");
const newSessionButton = document.querySelector("#newSession");
const loadHistoryButton = document.querySelector("#loadHistory");
const messageForm = document.querySelector("#messageForm");
const messageInput = document.querySelector("#messageInput");
const messages = document.querySelector("#messages");
const emptyState = document.querySelector("#emptyState");
const notice = document.querySelector("#notice");
const sessionStatus = document.querySelector("#sessionStatus");
const personaName = document.querySelector("#personaName");
const personaVersion = document.querySelector("#personaVersion");
const personaDescription = document.querySelector("#personaDescription");
const personaStyle = document.querySelector("#personaStyle");
const personaTraits = document.querySelector("#personaTraits");
const personaScenarios = document.querySelector("#personaScenarios");
const personaAvatar = document.querySelector("#personaAvatar");
const chatTitle = document.querySelector("#chatTitle");
const sendMessageButton = document.querySelector("#sendMessage");
const sessionSummary = document.querySelector("#sessionSummary");
const summaryPersona = document.querySelector("#summaryPersona");
const summaryRelationship = document.querySelector("#summaryRelationship");
const summaryLanguage = document.querySelector("#summaryLanguage");

function t(key, values = {}) {
  const value = key.split(".").reduce((current, part) => current?.[part], state.translations);
  if (typeof value !== "string") return key;
  return value.replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? `{${name}}`));
}

function applyTranslations() {
  document.title = t("app.page_title");
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-i18n-title]").forEach((element) => {
    element.title = t(element.dataset.i18nTitle);
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel));
  });
  renderRelationshipGallery();
  updateExperience();
  setLoading(state.isLoading);
}

async function loadLanguageResources(language) {
  if (!SUPPORTED_LANGUAGES.has(language)) throw new Error("unsupported language");
  const response = await fetch(`./i18n/${language}.json`);
  if (!response.ok) throw new Error(`language resource ${response.status}`);
  state.translations = await response.json();
  state.language = language;
  document.documentElement.lang = language;
  languageSelect.value = language;
  applyTranslations();
}

function apiBase() {
  return apiBaseInput.value.replace(/\/+$/, "");
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${apiBase()}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.message || payload.error || t("status.request_failed"));
  }
  return payload;
}

function setNotice(text, isError = false) {
  notice.textContent = text;
  notice.classList.toggle("error", isError);
}

function activePersona() {
  return state.personas.find((item) => item.id === state.activePersonaId);
}

function activeRelationship() {
  const base = `relationship.types.${state.activeRelationshipType}`;
  return {
    label: t(`${base}.name`),
    description: t(`${base}.description`),
    scenario: t(`${base}.scenario`),
  };
}

function displayPersonaVersion(persona) {
  return persona?.version || persona?.current_version_id || t("persona.unknown_version");
}

function displayPersonaDescription(persona) {
  return persona?.description || persona?.metadata?.description || t("persona.no_description");
}

function displayPersonaStyle(persona) {
  return persona?.style || t("persona.not_specified");
}

function displayPersonaTraits(persona) {
  if (Array.isArray(persona?.traits)) return persona.traits;
  return Object.entries(persona?.traits || {}).map(([name, value]) => `${name}: ${value}`);
}

function displayPersonaScenarios(persona) {
  return Array.isArray(persona?.suitable_scenarios) ? persona.suitable_scenarios : [];
}

function displayLanguage() {
  return t("language.zh_CN");
}

function personaInitial(persona) {
  return (persona?.name || "P").trim().charAt(0).toUpperCase();
}

function setLoading(isLoading) {
  state.isLoading = isLoading;
  messageInput.disabled = isLoading;
  sendMessageButton.disabled = isLoading;
  newSessionButton.disabled = isLoading;
  sendMessageButton.textContent = t(isLoading ? "chat.sending" : "chat.send");
}

function resetVisibleSession() {
  state.activeSessionId = "";
  for (const item of messages.querySelectorAll(".message")) item.remove();
}

function setWelcomeVisible(isVisible) {
  welcomeExperience.hidden = !isVisible;
  document.body.classList.toggle("welcome-open", isVisible);
}

function selectPersona(personaId) {
  state.activePersonaId = personaId;
  personaSelect.value = personaId;
  resetVisibleSession();
  renderPersonaGallery();
  updateExperience();
  updateEmptyState();
}

function updateExperience() {
  const persona = activePersona();
  const relationship = activeRelationship();
  personaName.textContent = persona?.name || t("persona.none");
  personaVersion.textContent = persona ? displayPersonaVersion(persona) : t("persona.not_specified");
  personaDescription.textContent = persona
    ? displayPersonaDescription(persona)
    : t("persona.load_hint");
  personaStyle.textContent = displayPersonaStyle(persona);
  renderTextList(personaTraits, displayPersonaTraits(persona), "trait");
  renderTextList(personaScenarios, displayPersonaScenarios(persona), "scenario");
  personaAvatar.textContent = personaInitial(persona);
  relationshipType.textContent = relationship.label;
  relationshipDescription.textContent = relationship.description;
  relationshipScenario.textContent = relationship.scenario;
  sessionStatus.textContent = state.activeSessionId || t("session.not_started");
  chatTitle.textContent = persona ? t("chat.title_with_persona", { name: persona.name }) : t("chat.title_empty");
  summaryPersona.textContent = persona?.name || t("persona.none");
  summaryRelationship.textContent = relationship.label;
  summaryLanguage.textContent = displayLanguage();
  sessionSummary.hidden = !state.activeSessionId;
}

function renderTextList(container, items, className) {
  container.innerHTML = "";
  const values = items.length > 0 ? items : [t("persona.not_specified")];
  for (const value of values) {
    const item = document.createElement(container.tagName === "UL" ? "li" : "span");
    item.className = className;
    item.textContent = value;
    container.appendChild(item);
  }
}

function renderPersonas() {
  personaSelect.innerHTML = "";
  for (const persona of state.personas) {
    const option = document.createElement("option");
    option.value = persona.id;
    option.textContent = `${persona.name} · ${displayPersonaVersion(persona)}`;
    personaSelect.appendChild(option);
  }
  if (state.personas.length > 0) {
    state.activePersonaId = state.personas[0].id;
    personaSelect.value = state.activePersonaId;
  }
  renderPersonaGallery();
  updateExperience();
}

function renderPersonaGallery() {
  personaGallery.innerHTML = "";
  for (const persona of state.personas) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "persona-option";
    button.classList.toggle("selected", persona.id === state.activePersonaId);
    button.setAttribute("aria-pressed", String(persona.id === state.activePersonaId));

    const avatar = document.createElement("span");
    avatar.className = "persona-option-avatar";
    avatar.textContent = personaInitial(persona);

    const copy = document.createElement("span");
    copy.className = "persona-option-copy";
    const name = document.createElement("strong");
    name.textContent = persona.name;
    const version = document.createElement("small");
    version.textContent = displayPersonaVersion(persona);
    const description = document.createElement("span");
    description.textContent = displayPersonaDescription(persona);
    copy.append(name, version, description);
    button.append(avatar, copy);

    button.addEventListener("click", () => selectPersona(persona.id));
    personaGallery.appendChild(button);
  }
}

function selectRelationship(relationshipId) {
  state.activeRelationshipType = relationshipId;
  relationshipSelect.value = relationshipId;
  resetVisibleSession();
  renderRelationshipGallery();
  updateExperience();
  updateEmptyState();
  setNotice(t("relationship.selected_notice"));
}

function renderRelationshipGallery() {
  relationshipGallery.innerHTML = "";
  for (const id of RELATIONSHIP_IDS) {
    const base = `relationship.types.${id}`;
    const relationship = {
      label: t(`${base}.name`),
      description: t(`${base}.description`),
      scenario: t(`${base}.scenario`),
    };
    const button = document.createElement("button");
    button.type = "button";
    button.className = "relationship-option";
    button.classList.toggle("selected", id === state.activeRelationshipType);
    button.setAttribute("aria-pressed", String(id === state.activeRelationshipType));
    const name = document.createElement("strong");
    name.textContent = relationship.label;
    const description = document.createElement("p");
    description.textContent = relationship.description;
    const scenario = document.createElement("span");
    scenario.textContent = `${t("relationship.works_well_for")}: ${relationship.scenario}`;
    button.append(name, description, scenario);
    button.addEventListener("click", () => selectRelationship(id));
    relationshipGallery.appendChild(button);
  }
}

function updateEmptyState() {
  emptyState.hidden = messages.querySelectorAll(".message").length > 0;
}

function appendMessage(role, content) {
  const item = document.createElement("article");
  item.className = `message ${role}`;
  const label = document.createElement("div");
  label.className = "message-role";
  label.textContent = role === "assistant"
    ? activePersona()?.name || role
    : role === "user"
      ? t("chat.role_user")
      : role === "system"
        ? t("chat.role_system")
        : role;
  const body = document.createElement("div");
  body.className = "message-content";
  body.textContent = content;
  item.append(label, body);
  messages.appendChild(item);
  updateEmptyState();
  messages.scrollTop = messages.scrollHeight;
  return item;
}

function appendLoadingMessage() {
  const item = appendMessage("assistant loading", t("chat.thinking"));
  item.setAttribute("aria-busy", "true");
  return item;
}

function replaceMessage(item, role, content) {
  item.className = `message ${role}`;
  item.removeAttribute("aria-busy");
  item.querySelector(".message-role").textContent = role === "assistant"
    ? activePersona()?.name || role
    : role === "system"
      ? t("chat.role_system")
      : role;
  item.querySelector(".message-content").textContent = content;
  messages.scrollTop = messages.scrollHeight;
}

function renderHistory(history) {
  for (const item of messages.querySelectorAll(".message")) item.remove();
  for (const turn of history) appendMessage(turn.role || "unknown", turn.content || "");
  updateEmptyState();
}

async function loadPersonas() {
  try {
    const payload = await apiRequest("/personas");
    state.personas = payload.personas || [];
    renderPersonas();
    setNotice(t("status.loaded_personas", { count: state.personas.length }));
  } catch (error) {
    setNotice(t("status.load_personas_failed", { message: error.message }), true);
  }
}

async function createSession() {
  const personaId = personaSelect.value;
  if (!personaId) {
    setNotice(t("status.choose_persona"), true);
    return;
  }
  try {
    const payload = await apiRequest("/sessions", {
      method: "POST",
      body: JSON.stringify({
        persona_id: personaId,
        relationship: { relationship_type: state.activeRelationshipType },
      }),
    });
    state.activeSessionId = payload.session.session_id;
    state.activePersonaId = personaId;
    for (const item of messages.querySelectorAll(".message")) item.remove();
    updateExperience();
    updateEmptyState();
    setNotice(t("status.session_created", { relationship: activeRelationship().label }));
    messageInput.focus();
  } catch (error) {
    setNotice(t("status.create_session_failed", { message: error.message }), true);
  }
}

async function loadHistory() {
  if (!state.activeSessionId) {
    setNotice(t("status.create_session_first"), true);
    return;
  }
  try {
    const payload = await apiRequest(`/sessions/${encodeURIComponent(state.activeSessionId)}/history`);
    renderHistory(payload.history || []);
    setNotice(t("status.history_loaded"));
  } catch (error) {
    setNotice(t("status.history_failed", { message: error.message }), true);
  }
}

async function sendMessage(event) {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text || !state.activeSessionId) {
    setNotice(t(text ? "status.create_session_first" : "status.type_message"), true);
    return;
  }
  appendMessage("user", text);
  const loadingMessage = appendLoadingMessage();
  messageInput.value = "";
  setLoading(true);
  try {
    const payload = await apiRequest(`/sessions/${encodeURIComponent(state.activeSessionId)}/messages`, {
      method: "POST",
      body: JSON.stringify({ message: text }),
    });
    replaceMessage(loadingMessage, "assistant", payload.message?.content || "");
    setNotice(t("status.reply_received"));
  } catch (error) {
    replaceMessage(loadingMessage, "system", t("status.error_prefix", { message: error.message }));
    setNotice(t("status.message_failed", { message: error.message }), true);
  } finally {
    setLoading(false);
    messageInput.focus();
  }
}

personaSelect.addEventListener("change", () => selectPersona(personaSelect.value));
relationshipSelect.addEventListener("change", () => {
  selectRelationship(relationshipSelect.value);
});
languageSelect.addEventListener("change", async () => {
  const requested = languageSelect.value;
  if (!SUPPORTED_LANGUAGES.has(requested)) {
    languageSelect.value = state.language;
    setNotice(t("language.unavailable"), true);
    return;
  }
  await loadLanguageResources(requested);
  setNotice(t("language.selected"));
});
dismissWelcomeButton.addEventListener("click", () => {
  setWelcomeVisible(false);
  try { localStorage.setItem("personaos_welcome_seen", "true"); } catch (error) { /* UI preference only. */ }
});
showWelcomeButton.addEventListener("click", () => setWelcomeVisible(true));
reloadPersonasButton.addEventListener("click", loadPersonas);
newSessionButton.addEventListener("click", createSession);
loadHistoryButton.addEventListener("click", loadHistory);
messageForm.addEventListener("submit", sendMessage);

async function initialize() {
  relationshipSelect.value = state.activeRelationshipType;
  languageSelect.value = DEFAULT_LANGUAGE;
  let welcomeSeen = false;
  try { welcomeSeen = localStorage.getItem("personaos_welcome_seen") === "true"; } catch (error) { /* UI preference only. */ }
  setWelcomeVisible(!welcomeSeen);
  updateEmptyState();
  try {
    await loadLanguageResources(DEFAULT_LANGUAGE);
    setNotice(t("chat.notice_initial"));
    await loadPersonas();
  } catch (error) {
    setNotice(state.translations.status ? t("status.resource_failed") : "Language resource could not be loaded.", true);
  }
}

initialize();
