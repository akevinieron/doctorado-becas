const state = {
  bootstrap: null,
  mode: "quick",
  currentStepIndex: 0,
  formData: { quick: {}, full: {} },
  errors: {},
  results: { quick: null, full: null },
  chatMessages: [],
  chatSuggestions: [],
  busy: { wizard: false, chat: false },
};

const elements = {};

document.addEventListener("DOMContentLoaded", () => {
  cacheElements();
  attachEventListeners();
  init();
});

async function init() {
  try {
    const bootstrap = await api("/api/bootstrap");
    state.bootstrap = bootstrap;
    state.chatMessages = [{ role: "assistant", body: bootstrap.assistant.greeting }];
    state.chatSuggestions = [
      "Que documentos me faltan para postular?",
      "Como funciona la evaluacion rapida?",
      "Que diferencia hay entre beca nacional e internacional?",
    ];
    renderStaticSections();
    renderInteractiveSections();
  } catch (error) {
    renderFatalError(error);
  }
}

function cacheElements() {
  elements.brandTitle = document.getElementById("brandTitle");
  elements.brandBadge = document.getElementById("brandBadge");
  elements.heroHeadline = document.getElementById("heroHeadline");
  elements.heroBody = document.getElementById("heroBody");
  elements.metricGrid = document.getElementById("metricGrid");
  elements.scholarshipGrid = document.getElementById("scholarshipGrid");
  elements.timelineGrid = document.getElementById("timelineGrid");
  elements.faqGrid = document.getElementById("faqGrid");
  elements.modeSwitch = document.getElementById("modeSwitch");
  elements.stepProgress = document.getElementById("stepProgress");
  elements.wizardHeader = document.getElementById("wizardHeader");
  elements.wizardForm = document.getElementById("wizardForm");
  elements.resultPanel = document.getElementById("resultPanel");
  elements.chatMessages = document.getElementById("chatMessages");
  elements.chatForm = document.getElementById("chatForm");
  elements.chatInput = document.getElementById("chatInput");
  elements.chatSubmitButton = document.getElementById("chatSubmitButton");
  elements.suggestionStrip = document.getElementById("suggestionStrip");
  elements.backStepButton = document.getElementById("backStepButton");
  elements.nextStepButton = document.getElementById("nextStepButton");
  elements.startQuickButton = document.getElementById("startQuickButton");
  elements.startFullButton = document.getElementById("startFullButton");
  elements.wizardSection = document.getElementById("wizardSection");
  elements.messageTemplate = document.getElementById("messageTemplate");
}

function attachEventListeners() {
  elements.backStepButton.addEventListener("click", handleBackStep);
  elements.nextStepButton.addEventListener("click", handleNextStep);
  elements.chatForm.addEventListener("submit", handleChatSubmit);
  elements.startQuickButton.addEventListener("click", () => activateMode("quick", true));
  elements.startFullButton.addEventListener("click", () => activateMode("full", true));
}

function renderStaticSections() {
  const { brand, hero, stats, scholarshipTypes, timeline, faq } = state.bootstrap;
  elements.brandTitle.textContent = brand.title;
  elements.brandBadge.textContent = brand.badge;
  elements.heroHeadline.textContent = hero.headline;
  elements.heroBody.textContent = hero.body;

  elements.metricGrid.innerHTML = stats
    .map(
      (item) => `
        <article class="metric-card">
          <span>${escapeHtml(item.label)}</span>
          <strong>${escapeHtml(item.value)}</strong>
          <p>${escapeHtml(metricNarrative(item.label))}</p>
        </article>
      `
    )
    .join("");

  elements.scholarshipGrid.innerHTML = scholarshipTypes
    .map(
      (item) => `
        <article class="info-card">
          <h4>${escapeHtml(item.name)}</h4>
          <p>${escapeHtml(item.description)}</p>
        </article>
      `
    )
    .join("");

  elements.timelineGrid.innerHTML = timeline
    .map(
      (item) => `
        <article class="timeline-card">
          <span>${escapeHtml(item.step)}</span>
          <h4>${escapeHtml(item.title)}</h4>
          <p>${escapeHtml(item.body)}</p>
        </article>
      `
    )
    .join("");

  elements.faqGrid.innerHTML = faq
    .map(
      (item) => `
        <article class="faq-card">
          <h4>${escapeHtml(item.question)}</h4>
          <p>${escapeHtml(item.answer)}</p>
        </article>
      `
    )
    .join("");
}

function renderInteractiveSections() {
  renderModeSwitch();
  renderWizard();
  renderResult();
  renderChatSuggestions();
  renderChatMessages();
}

function renderModeSwitch() {
  const modes = state.bootstrap.wizards;
  elements.modeSwitch.innerHTML = Object.entries(modes)
    .map(
      ([key, config]) => `
        <button
          type="button"
          class="mode-button ${state.mode === key ? "is-active" : ""}"
          data-mode="${key}"
        >
          ${escapeHtml(config.label)}
        </button>
      `
    )
    .join("");

  elements.modeSwitch.querySelectorAll("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => activateMode(button.dataset.mode, false));
  });
}

function activateMode(mode, scrollToWizard) {
  if (state.mode === mode) {
    if (scrollToWizard) {
      elements.wizardSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    return;
  }

  syncSharedData(state.mode, mode);
  state.mode = mode;
  state.currentStepIndex = 0;
  state.errors = {};
  renderInteractiveSections();

  if (scrollToWizard) {
    elements.wizardSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function syncSharedData(sourceMode, targetMode) {
  const source = state.formData[sourceMode];
  const target = state.formData[targetMode];
  const next = { ...target };
  for (const [key, value] of Object.entries(source)) {
    if (next[key] === undefined || next[key] === null || next[key] === "") {
      next[key] = value;
    }
  }
  state.formData[targetMode] = next;
}

function renderWizard() {
  const wizard = getCurrentWizard();
  const step = wizard.steps[state.currentStepIndex];

  elements.stepProgress.innerHTML = wizard.steps
    .map((item, index) => {
      const complete = validateStep(item, getCurrentData()).valid;
      const classes = [
        "step-chip",
        index === state.currentStepIndex ? "is-active" : "",
        index < state.currentStepIndex && complete ? "is-complete" : "",
      ]
        .filter(Boolean)
        .join(" ");
      return `<div class="${classes}">${escapeHtml(item.title)}</div>`;
    })
    .join("");

  elements.wizardHeader.innerHTML = `
    <p class="kicker">${escapeHtml(step.eyebrow)}</p>
    <h4>${escapeHtml(step.title)}</h4>
    <p>${escapeHtml(step.description)}</p>
    <p class="status-line">${escapeHtml(wizard.summary)}</p>
  `;

  const stepFields = getVisibleFieldsForStep(step);
  elements.wizardForm.innerHTML = stepFields.map(renderFieldCard).join("");
  bindFieldEvents(stepFields);

  elements.backStepButton.disabled = state.currentStepIndex === 0 || state.busy.wizard;
  elements.nextStepButton.disabled = state.busy.wizard;
  elements.nextStepButton.textContent =
    state.currentStepIndex === wizard.steps.length - 1
      ? state.busy.wizard
        ? "Calculando..."
        : "Calcular resultado"
      : "Siguiente";
}

function renderFieldCard(fieldName) {
  const definition = state.bootstrap.fields[fieldName];
  const value = getCurrentData()[fieldName];
  const error = state.errors[fieldName];
  const wide = definition.type === "textarea" || fieldName === "objetivo_profesional";
  const help = definition.hint ? `<p class="field-help">${escapeHtml(definition.hint)}</p>` : "";
  const errorBlock = error ? `<p class="field-error">${escapeHtml(error)}</p>` : "";

  let control = "";

  if (definition.type === "select") {
    const options = getFieldOptions(fieldName);
    control = `
      <select name="${fieldName}" data-field="${fieldName}">
        <option value="">Selecciona una opcion</option>
        ${options
          .map(
            (option) => `
              <option value="${escapeAttribute(option.value)}" ${
                String(value ?? "") === String(option.value) ? "selected" : ""
              }>
                ${escapeHtml(option.label)}
              </option>
            `
          )
          .join("")}
      </select>
    `;
  } else if (definition.type === "boolean") {
    control = `
      <div class="toggle-group" data-toggle-group="${fieldName}">
        ${[
          { label: "Si", value: "1" },
          { label: "No", value: "0" },
        ]
          .map(
            (option) => `
              <button
                type="button"
                class="toggle-button ${String(value ?? "") === option.value ? "is-active" : ""}"
                data-toggle-field="${fieldName}"
                data-value="${option.value}"
              >
                ${option.label}
              </button>
            `
          )
          .join("")}
      </div>
    `;
  } else if (definition.type === "textarea") {
    control = `
      <textarea
        name="${fieldName}"
        data-field="${fieldName}"
        placeholder="${escapeAttribute(definition.placeholder || "")}"
      >${escapeHtml(value ?? "")}</textarea>
    `;
  } else {
    const inputType = definition.type === "email" ? "email" : definition.type === "number" ? "number" : "text";
    const minAttr = definition.min !== undefined ? `min="${definition.min}"` : "";
    const maxAttr = definition.max !== undefined ? `max="${definition.max}"` : "";
    const stepAttr = definition.step !== undefined ? `step="${definition.step}"` : "";
    control = `
      <input
        type="${inputType}"
        name="${fieldName}"
        data-field="${fieldName}"
        value="${escapeAttribute(value ?? "")}"
        placeholder="${escapeAttribute(definition.placeholder || "")}"
        ${minAttr}
        ${maxAttr}
        ${stepAttr}
      />
    `;
  }

  return `
    <div class="field-card ${wide ? "wide" : ""}">
      <label for="${fieldName}">${escapeHtml(definition.label)}</label>
      ${control}
      ${help}
      ${errorBlock}
    </div>
  `;
}

function bindFieldEvents(stepFields) {
  stepFields.forEach((fieldName) => {
    const input = elements.wizardForm.querySelector(`[data-field="${fieldName}"]`);
    if (input) {
      input.addEventListener("input", handleFieldInput);
      input.addEventListener("change", handleFieldInput);
    }
  });

  elements.wizardForm.querySelectorAll("[data-toggle-field]").forEach((button) => {
    button.addEventListener("click", () => {
      updateFieldValue(button.dataset.toggleField, button.dataset.value);
    });
  });
}

function handleFieldInput(event) {
  const fieldName = event.target.dataset.field;
  updateFieldValue(fieldName, event.target.value);
}

function updateFieldValue(fieldName, rawValue) {
  const definition = state.bootstrap.fields[fieldName];
  let value = rawValue;

  if (definition.type === "number") {
    value = rawValue === "" ? "" : Number(rawValue);
  }

  if (definition.type === "boolean") {
    value = Number(rawValue);
  }

  const nextData = { ...getCurrentData(), [fieldName]: value };
  if (fieldName === "tipo_beca") {
    const currentLevel = nextData.nivel_estudio;
    const validOptions = getFieldOptions("nivel_estudio", nextData).map((option) => option.value);
    if (currentLevel && !validOptions.includes(currentLevel)) {
      nextData.nivel_estudio = "";
    }
  }

  state.formData[state.mode] = nextData;
  state.errors = { ...state.errors, [fieldName]: undefined };
  renderWizard();
  renderResult();
  renderChatSuggestions();
}

function handleBackStep() {
  state.currentStepIndex = Math.max(0, state.currentStepIndex - 1);
  state.errors = {};
  renderWizard();
  renderChatSuggestions();
}

async function handleNextStep() {
  const wizard = getCurrentWizard();
  const step = wizard.steps[state.currentStepIndex];
  const validation = validateStep(step, getCurrentData());

  if (!validation.valid) {
    state.errors = validation.errors;
    renderWizard();
    return;
  }

  state.errors = {};

  if (state.currentStepIndex < wizard.steps.length - 1) {
    state.currentStepIndex += 1;
    renderWizard();
    renderChatSuggestions();
    return;
  }

  await submitPrediction();
}

async function submitPrediction() {
  state.busy.wizard = true;
  renderWizard();

  try {
    const payload = { mode: state.mode, applicant: getCurrentData() };
    const response = await api("/api/eligibility/predict", { method: "POST", body: payload });
    state.results[state.mode] = response;
    state.chatSuggestions = [
      "Interpretame mi resultado y dime mis proximos pasos.",
      "Que documentos pendientes debo priorizar?",
      "Como puedo mejorar mi expediente?",
    ];
    renderResult();
    renderChatSuggestions();
    elements.resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    state.errors = { _form: error.message || "No fue posible calcular el resultado." };
    renderWizard();
    renderResult();
  } finally {
    state.busy.wizard = false;
    renderWizard();
  }
}

function renderResult() {
  const result = state.results[state.mode];
  const formLevelError = state.errors._form ? `<p class="field-error">${escapeHtml(state.errors._form)}</p>` : "";

  if (!result) {
    elements.resultPanel.classList.add("hidden");
    elements.resultPanel.innerHTML = formLevelError;
    return;
  }

  const probabilityPercent = Math.round((result.prediction.probability || 0) * 100);
  const signalMarkup = (result.signals || [])
    .map(
      (signal) => `
        <div class="signal-chip ${signal.tone === "caution" ? "caution" : "positive"}">
          ${escapeHtml(signal.label)}
        </div>
      `
    )
    .join("");

  const documentMarkup = result.documents
    .map(
      (item) => `
        <article class="document-card">
          <header>
            <h4>${escapeHtml(item.label)}</h4>
            <span class="document-status ${escapeAttribute(item.status)}">${escapeHtml(item.status)}</span>
          </header>
          <p>${escapeHtml(item.detail)}</p>
        </article>
      `
    )
    .join("");

  const nextStepsMarkup = result.next_steps
    .map((step) => `<li>${escapeHtml(step)}</li>`)
    .join("");

  elements.resultPanel.classList.remove("hidden");
  elements.resultPanel.innerHTML = `
    <div class="result-topline">
      <div>
        <p class="kicker">Resultado orientativo</p>
        <h3>${escapeHtml(getCurrentWizard().label)}</h3>
      </div>
      <span class="priority-chip ${escapeAttribute(result.prediction.priority_label)}">
        Prioridad ${escapeHtml(result.prediction.priority_label)}
      </span>
    </div>

    ${formLevelError}

    <div class="result-score">
      <div class="score-ring" style="--ring-value: ${probabilityPercent}%;">
        <div class="score-ring-inner">
          <span>Probabilidad</span>
          <strong>${probabilityPercent}%</strong>
        </div>
      </div>
      <div>
        <h4>${escapeHtml(result.prediction.explanation)}</h4>
        <p class="status-line">${escapeHtml(result.disclaimer)}</p>
      </div>
    </div>

    <section>
      <p class="kicker">Lectura rapida</p>
      <div class="signal-grid">${signalMarkup || '<div class="signal-chip positive">Perfil cargado correctamente.</div>'}</div>
    </section>

    <section>
      <p class="kicker">Checklist documental</p>
      <div class="document-grid">${documentMarkup}</div>
    </section>

    <section>
      <p class="kicker">Proximos pasos</p>
      <ol class="next-step-list">${nextStepsMarkup}</ol>
    </section>

    <div class="result-actions">
      <button type="button" class="cta secondary" id="resultAskAssistant">Llevar esto al chat</button>
      <button type="button" class="cta primary" id="downloadSummaryButton">Descargar resumen</button>
    </div>
  `;

  const askAssistant = document.getElementById("resultAskAssistant");
  if (askAssistant) {
    askAssistant.addEventListener("click", () => {
      elements.chatInput.value = "Interpretame mi resultado y dime mis proximos pasos.";
      elements.chatInput.focus();
      elements.chatInput.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  const downloadButton = document.getElementById("downloadSummaryButton");
  if (downloadButton) {
    downloadButton.addEventListener("click", downloadSummary);
  }
}

function renderChatMessages() {
  elements.chatMessages.innerHTML = "";
  const fragment = document.createDocumentFragment();

  state.chatMessages.forEach((message) => {
    const node = elements.messageTemplate.content.firstElementChild.cloneNode(true);
    node.classList.add(message.role);
    node.querySelector(".message-role").textContent = message.role === "user" ? "Ciudadano" : "Asistente";
    node.querySelector(".message-body").textContent = message.body;
    fragment.appendChild(node);
  });

  elements.chatMessages.appendChild(fragment);
  elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
  elements.chatSubmitButton.disabled = state.busy.chat;
  elements.chatSubmitButton.textContent = state.busy.chat ? "Consultando..." : "Enviar consulta";
}

function renderChatSuggestions() {
  const result = state.results[state.mode];
  const localSuggestions = state.chatSuggestions.length
    ? state.chatSuggestions
    : [
        "Que documentos me faltan para postular?",
        "Explicame el proceso paso a paso.",
        "Como se evalua la necesidad economica?",
      ];

  const merged = Array.from(
    new Set(
      [
        ...localSuggestions,
        ...(result
          ? ["Interpretame mi resultado y dime mis proximos pasos.", "Que puedo mejorar antes de aplicar?"]
          : []),
      ].filter(Boolean)
    )
  ).slice(0, 4);

  elements.suggestionStrip.innerHTML = merged
    .map(
      (item, index) => `
        <button
          type="button"
          class="suggestion-chip ${index === 0 ? "is-highlighted" : ""}"
          data-suggestion="${escapeAttribute(item)}"
        >
          ${escapeHtml(item)}
        </button>
      `
    )
    .join("");

  elements.suggestionStrip.querySelectorAll("[data-suggestion]").forEach((button) => {
    button.addEventListener("click", () => sendChatQuestion(button.dataset.suggestion));
  });
}

async function handleChatSubmit(event) {
  event.preventDefault();
  const question = elements.chatInput.value.trim();
  if (!question) {
    return;
  }
  await sendChatQuestion(question);
}

async function sendChatQuestion(question) {
  state.chatMessages.push({ role: "user", body: question });
  state.busy.chat = true;
  renderChatMessages();
  elements.chatInput.value = "";

  try {
    const wizard = getCurrentWizard();
    const step = wizard.steps[state.currentStepIndex];
    const payload = {
      question,
      applicant_context: getCurrentData(),
      prediction: state.results[state.mode]?.prediction || null,
      step_context: { mode: state.mode, step_id: step.id, step_title: step.title },
      allow_prediction: false,
    };
    const response = await api("/api/assistant/chat", { method: "POST", body: payload });

    const referenceText =
      response.references && response.references.length
        ? `\n\nFuentes: ${response.references.map((item) => item.source).join(", ")}`
        : "";

    state.chatMessages.push({ role: "assistant", body: `${response.answer}${referenceText}` });
    state.chatSuggestions = response.suggestions || state.chatSuggestions;
    renderChatSuggestions();
  } catch (error) {
    state.chatMessages.push({
      role: "assistant",
      body: `No pude responder ahora mismo. ${error.message || "Intenta de nuevo en unos segundos."}`,
    });
  } finally {
    state.busy.chat = false;
    renderChatMessages();
  }
}

function validateStep(step, values) {
  const errors = {};
  const stepFields = getVisibleFieldsForStep(step, values);

  stepFields.forEach((fieldName) => {
    const definition = state.bootstrap.fields[fieldName];
    const value = values[fieldName];

    if (definition.required && (value === undefined || value === null || value === "")) {
      errors[fieldName] = "Este campo es obligatorio.";
      return;
    }

    if (definition.type === "email" && value) {
      const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value));
      if (!emailValid) {
        errors[fieldName] = "Ingresa un correo valido.";
      }
    }

    if (definition.type === "number" && value !== "" && value !== undefined && value !== null) {
      const numericValue = Number(value);
      if (Number.isNaN(numericValue)) {
        errors[fieldName] = "Ingresa un valor numerico valido.";
        return;
      }
      if (definition.min !== undefined && numericValue < definition.min) {
        errors[fieldName] = `El valor minimo es ${definition.min}.`;
      }
      if (definition.max !== undefined && numericValue > definition.max) {
        errors[fieldName] = `El valor maximo es ${definition.max}.`;
      }
    }
  });

  return { valid: Object.keys(errors).length === 0, errors };
}

function getVisibleFieldsForStep(step, values = getCurrentData()) {
  return step.fields.filter((fieldName) => fieldVisible(state.bootstrap.fields[fieldName], values));
}

function fieldVisible(definition, values) {
  if (!definition.showWhen) {
    return true;
  }
  return values[definition.showWhen.field] === definition.showWhen.equals;
}

function getFieldOptions(fieldName, values = getCurrentData()) {
  const definition = state.bootstrap.fields[fieldName];
  if (definition.optionsByValue && definition.dependsOn) {
    const dependencyValue = values[definition.dependsOn];
    return definition.optionsByValue[dependencyValue] || definition.options;
  }
  return definition.options || [];
}

function getCurrentWizard() {
  return state.bootstrap.wizards[state.mode];
}

function getCurrentData() {
  return state.formData[state.mode] || {};
}

function downloadSummary() {
  const result = state.results[state.mode];
  if (!result) {
    return;
  }

  const summaryLines = [
    "Portal Ciudadano de Becas RD",
    `Modo: ${getCurrentWizard().label}`,
    "",
    "Resultado orientativo",
    `Probabilidad: ${Math.round((result.prediction.probability || 0) * 100)}%`,
    `Prioridad: ${result.prediction.priority_label}`,
    `Explicacion: ${result.prediction.explanation}`,
    "",
    "Checklist documental",
    ...result.documents.map((item) => `- ${item.label}: ${item.status}`),
    "",
    "Proximos pasos",
    ...result.next_steps.map((item) => `- ${item}`),
    "",
    "Perfil capturado",
    ...Object.entries(getCurrentData()).map(([key, value]) => `- ${key}: ${String(value ?? "")}`),
  ];

  const blob = new Blob([summaryLines.join("\n")], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `becas-rd-${state.mode}-resumen.txt`;
  anchor.click();
  URL.revokeObjectURL(url);
}

async function api(path, options = {}) {
  const config = {
    method: options.method || "GET",
    headers: { "Content-Type": "application/json" },
  };

  if (options.body !== undefined) {
    config.body = JSON.stringify(options.body);
  }

  const response = await fetch(path, config);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || "No fue posible completar la solicitud.");
  }

  return data;
}

function renderFatalError(error) {
  const message = error?.message || "No fue posible iniciar el portal.";
  document.body.innerHTML = `
    <main style="display:grid;place-items:center;min-height:100vh;padding:24px;background:#041118;color:#eef5f3;font-family:Albert Sans, sans-serif;">
      <section style="max-width:720px;border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:28px;background:rgba(255,255,255,0.03);">
        <p style="letter-spacing:0.18em;text-transform:uppercase;color:#d2a95a;font-size:0.82rem;">Error de inicio</p>
        <h1 style="font-family:Prata, serif;font-weight:400;">No fue posible cargar el portal</h1>
        <p style="color:#98aeb3;line-height:1.7;">${escapeHtml(message)}</p>
      </section>
    </main>
  `;
}

function metricNarrative(label) {
  if (label.includes("provincias")) {
    return "Cobertura territorial sintetica para orientar la priorizacion.";
  }
  if (label.includes("rutas")) {
    return "Dos caminos: diagnostico rapido o postulacion guiada.";
  }
  return "Todo ocurre en una sola sesion, sin depender de una cuenta.";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#96;");
}
