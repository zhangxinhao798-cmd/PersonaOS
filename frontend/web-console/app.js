const RELATIONSHIPS = {
  assistant: {
    label: "Assistant",
    description: "Practical, clear support for everyday tasks and questions.",
    scenario: "Task support, explanations, and focused everyday help.",
  },
  mentor: {
    label: "Mentor",
    description: "Structured guidance that helps you think and improve.",
    scenario: "Learning, reflection, planning, and skill development.",
  },
  companion: {
    label: "Companion",
    description: "A warm, supportive style for open-ended conversation.",
    scenario: "Open conversation, shared reflection, and steady presence.",
  },
  analyst: {
    label: "Analyst",
    description: "Neutral, precise discussion focused on evidence and tradeoffs.",
    scenario: "Research, comparison, diagnosis, and decision analysis.",
  },
};

const state = {
  personas: [],
  activeSessionId: "",
  activePersonaId: "",
  activeRelationshipType: "assistant",
  language: "en",
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
    throw new Error(payload.message || payload.error || "Request failed.");
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
  return RELATIONSHIPS[state.activeRelationshipType];
}

function displayPersonaVersion(persona) {
  return persona?.version || persona?.current_version_id || "unknown version";
}

function displayPersonaDescription(persona) {
  return persona?.description || persona?.metadata?.description || "This persona has no description yet.";
}

function displayPersonaStyle(persona) {
  return persona?.style || "Not specified by this persona package.";
}

function displayPersonaTraits(persona) {
  if (Array.isArray(persona?.traits)) return persona.traits;
  return Object.entries(persona?.traits || {}).map(([name, value]) => `${name}: ${value}`);
}

function displayPersonaScenarios(persona) {
  return Array.isArray(persona?.suitable_scenarios) ? persona.suitable_scenarios : [];
}

function displayLanguage() {
  return state.language === "zh-CN" ? "中文" : "English";
}

function personaInitial(persona) {
  return (persona?.name || "P").trim().charAt(0).toUpperCase();
}

function setLoading(isLoading) {
  state.isLoading = isLoading;
  messageInput.disabled = isLoading;
  sendMessageButton.disabled = isLoading;
  newSessionButton.disabled = isLoading;
  sendMessageButton.textContent = isLoading ? "Sending" : "Send";
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
  personaName.textContent = persona?.name || "No persona selected";
  personaVersion.textContent = persona ? displayPersonaVersion(persona) : "none";
  personaDescription.textContent = persona
    ? displayPersonaDescription(persona)
    : "Load personas to inspect the available digital identities.";
  personaStyle.textContent = displayPersonaStyle(persona);
  renderTextList(personaTraits, displayPersonaTraits(persona), "trait");
  renderTextList(personaScenarios, displayPersonaScenarios(persona), "scenario");
  personaAvatar.textContent = personaInitial(persona);
  relationshipType.textContent = relationship.label;
  relationshipDescription.textContent = relationship.description;
  relationshipScenario.textContent = relationship.scenario;
  sessionStatus.textContent = state.activeSessionId || "not started";
  chatTitle.textContent = persona ? `Meet ${persona.name}` : "Choose who you want to meet";
  summaryPersona.textContent = persona?.name || "none";
  summaryRelationship.textContent = relationship.label;
  summaryLanguage.textContent = displayLanguage();
  sessionSummary.hidden = !state.activeSessionId;
}

function renderTextList(container, items, className) {
  container.innerHTML = "";
  const values = items.length > 0 ? items : ["Not specified"];
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
  setNotice("Relationship selected. Start a new experience to apply it.");
}

function renderRelationshipGallery() {
  relationshipGallery.innerHTML = "";
  for (const [id, relationship] of Object.entries(RELATIONSHIPS)) {
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
    scenario.textContent = `Use for: ${relationship.scenario}`;
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
  label.textContent = role === "assistant" ? activePersona()?.name || role : role;
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
  const item = appendMessage("assistant loading", "Thinking through the active persona...");
  item.setAttribute("aria-busy", "true");
  return item;
}

function replaceMessage(item, role, content) {
  item.className = `message ${role}`;
  item.removeAttribute("aria-busy");
  item.querySelector(".message-role").textContent = role === "assistant" ? activePersona()?.name || role : role;
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
    setNotice(`Loaded ${state.personas.length} persona(s).`);
  } catch (error) {
    setNotice(`Could not load personas: ${error.message}`, true);
  }
}

async function createSession() {
  const personaId = personaSelect.value;
  if (!personaId) {
    setNotice("Choose a persona first.", true);
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
    setNotice(`${activeRelationship().label} session created.`);
    messageInput.focus();
  } catch (error) {
    setNotice(`Could not create session: ${error.message}`, true);
  }
}

async function loadHistory() {
  if (!state.activeSessionId) {
    setNotice("Create a session first.", true);
    return;
  }
  try {
    const payload = await apiRequest(`/sessions/${encodeURIComponent(state.activeSessionId)}/history`);
    renderHistory(payload.history || []);
    setNotice("History loaded.");
  } catch (error) {
    setNotice(`Could not load history: ${error.message}`, true);
  }
}

async function sendMessage(event) {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text || !state.activeSessionId) {
    setNotice(text ? "Start an experience first." : "Type a message first.", true);
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
    setNotice("Reply received.");
  } catch (error) {
    replaceMessage(loadingMessage, "system", `Error: ${error.message}`);
    setNotice(`Message failed: ${error.message}`, true);
  } finally {
    setLoading(false);
    messageInput.focus();
  }
}

personaSelect.addEventListener("change", () => selectPersona(personaSelect.value));
relationshipSelect.addEventListener("change", () => {
  selectRelationship(relationshipSelect.value);
});
languageSelect.addEventListener("change", () => {
  state.language = languageSelect.value;
  document.documentElement.lang = state.language;
  updateExperience();
  setNotice(state.language === "zh-CN" ? "已选择中文界面入口。" : "English interface entry selected.");
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

relationshipSelect.value = state.activeRelationshipType;
renderRelationshipGallery();
languageSelect.value = state.language;
document.documentElement.lang = state.language;
let welcomeSeen = false;
try { welcomeSeen = localStorage.getItem("personaos_welcome_seen") === "true"; } catch (error) { /* UI preference only. */ }
setWelcomeVisible(!welcomeSeen);
updateExperience();
updateEmptyState();
loadPersonas();
