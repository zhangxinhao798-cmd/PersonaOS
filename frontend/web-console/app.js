const state = {
  personas: [],
  activeSessionId: "",
  activePersonaId: "",
};

const apiBaseInput = document.querySelector("#apiBase");
const personaSelect = document.querySelector("#personaSelect");
const reloadPersonasButton = document.querySelector("#reloadPersonas");
const newSessionButton = document.querySelector("#newSession");
const loadHistoryButton = document.querySelector("#loadHistory");
const messageForm = document.querySelector("#messageForm");
const messageInput = document.querySelector("#messageInput");
const messages = document.querySelector("#messages");
const notice = document.querySelector("#notice");
const sessionStatus = document.querySelector("#sessionStatus");
const personaStatus = document.querySelector("#personaStatus");

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

function updateStatus() {
  sessionStatus.textContent = state.activeSessionId || "none";
  const persona = state.personas.find(
    (item) => item.id === state.activePersonaId,
  );
  personaStatus.textContent = persona ? persona.name : "none";
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

function appendMessage(role, content) {
  const item = document.createElement("article");
  item.className = `message ${role}`;

  const label = document.createElement("div");
  label.className = "message-role";
  label.textContent = role;

  const body = document.createElement("div");
  body.className = "message-content";
  body.textContent = content;

  item.append(label, body);
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
}

function renderHistory(history) {
  messages.innerHTML = "";
  for (const turn of history) {
    appendMessage(turn.role || "unknown", turn.content || "");
  }
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
    messages.innerHTML = "";
    updateStatus();
    setNotice("Session created.");
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
  messageInput.value = "";
  messageInput.disabled = true;
  try {
    const payload = await apiRequest(
      `/sessions/${encodeURIComponent(state.activeSessionId)}/messages`,
      {
        method: "POST",
        body: JSON.stringify({ message: text }),
      },
    );
    appendMessage("assistant", payload.message?.content || "");
    setNotice("Reply received.");
  } catch (error) {
    appendMessage("system", `Error: ${error.message}`);
    setNotice(`Message failed: ${error.message}`, true);
  } finally {
    messageInput.disabled = false;
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

loadPersonas();
