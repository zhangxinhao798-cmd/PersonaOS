const state = {
  personas: [],
  activeSessionId: "",
  activePersonaId: "",
  isLoading: false,
};

const apiBaseInput = document.querySelector("#apiBase");
const personaSelect = document.querySelector("#personaSelect");
const reloadPersonasButton = document.querySelector("#reloadPersonas");
const newSessionButton = document.querySelector("#newSession");
const loadHistoryButton = document.querySelector("#loadHistory");
const messageForm = document.querySelector("#messageForm");
const messageInput = document.querySelector("#messageInput");
const messages = document.querySelector("#messages");
const emptyState = document.querySelector("#emptyState");
const notice = document.querySelector("#notice");
const sessionStatus = document.querySelector("#sessionStatus");
const personaStatus = document.querySelector("#personaStatus");
const personaName = document.querySelector("#personaName");
const personaVersion = document.querySelector("#personaVersion");
const personaDescription = document.querySelector("#personaDescription");
const chatTitle = document.querySelector("#chatTitle");
const sendMessageButton = document.querySelector("#sendMessage");

function apiBase() {
  return apiBaseInput.value.replace(/\/+$/, "");
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${apiBase()}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
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

function displayPersonaVersion(persona) {
  return persona?.version || persona?.current_version_id || "unknown version";
}

function displayPersonaDescription(persona) {
  return (
    persona?.description ||
    persona?.metadata?.description ||
    "This persona has no description yet."
  );
}

function setLoading(isLoading) {
  state.isLoading = isLoading;
  messageInput.disabled = isLoading;
  sendMessageButton.disabled = isLoading;
  sendMessageButton.textContent = isLoading ? "Sending" : "Send";
}

function updateStatus() {
  sessionStatus.textContent = state.activeSessionId || "none";
  const persona = activePersona();
  personaStatus.textContent = persona ? persona.name : "none";
  renderPersonaIdentity(persona);
}

function renderPersonaIdentity(persona) {
  personaName.textContent = persona?.name || "No persona selected";
  personaVersion.textContent = persona ? displayPersonaVersion(persona) : "none";
  personaDescription.textContent = persona
    ? displayPersonaDescription(persona)
    : "Load personas from the API to inspect the active digital identity.";
  chatTitle.textContent = persona
    ? `Conversation with ${persona.name}`
    : "Start a persona session";
}

function renderPersonas() {
  personaSelect.innerHTML = "";
  for (const persona of state.personas) {
    const option = document.createElement("option");
    option.value = persona.id;
    option.textContent = `${persona.name} (${persona.id})`;
    personaSelect.appendChild(option);
  }
  if (state.personas.length > 0) {
    state.activePersonaId = state.personas[0].id;
    personaSelect.value = state.activePersonaId;
  }
  updateStatus();
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
  const label = item.querySelector(".message-role");
  const body = item.querySelector(".message-content");
  label.textContent = role === "assistant" ? activePersona()?.name || role : role;
  body.textContent = content;
  messages.scrollTop = messages.scrollHeight;
}

function renderHistory(history) {
  for (const item of messages.querySelectorAll(".message")) {
    item.remove();
  }
  for (const turn of history) {
    appendMessage(turn.role || "unknown", turn.content || "");
  }
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
      body: JSON.stringify({ persona_id: personaId }),
    });
    state.activeSessionId = payload.session.session_id;
    state.activePersonaId = personaId;
    for (const item of messages.querySelectorAll(".message")) {
      item.remove();
    }
    updateStatus();
    updateEmptyState();
    setNotice("Session created. The active persona is ready.");
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
    const payload = await apiRequest(
      `/sessions/${encodeURIComponent(state.activeSessionId)}/history`,
    );
    renderHistory(payload.history || []);
    setNotice("History loaded.");
  } catch (error) {
    setNotice(`Could not load history: ${error.message}`, true);
  }
}

async function sendMessage(event) {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    setNotice("Type a message first.", true);
    return;
  }
  if (!state.activeSessionId) {
    setNotice("Create a session first.", true);
    return;
  }

  appendMessage("user", text);
  const loadingMessage = appendLoadingMessage();
  messageInput.value = "";
  setLoading(true);
  try {
    const payload = await apiRequest(
      `/sessions/${encodeURIComponent(state.activeSessionId)}/messages`,
      {
        method: "POST",
        body: JSON.stringify({ message: text }),
      },
    );
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

personaSelect.addEventListener("change", () => {
  state.activePersonaId = personaSelect.value;
  updateStatus();
});
reloadPersonasButton.addEventListener("click", loadPersonas);
newSessionButton.addEventListener("click", createSession);
loadHistoryButton.addEventListener("click", loadHistory);
messageForm.addEventListener("submit", sendMessage);

updateStatus();
updateEmptyState();
loadPersonas();
