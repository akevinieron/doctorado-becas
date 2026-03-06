const state = {
  bootstrap: null,
  mode: "quick",
  currentStepIndex: 0,
  convocationFilter: "all",
  selectedConvocationId: null,
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
    const bootstrap = normalizeBootstrap(await api("/api/bootstrap"));
    state.bootstrap = bootstrap;
    state.chatMessages = [{ role: "assistant", body: bootstrap.assistant.greeting }];
    state.chatSuggestions = [...bootstrap.assistant.entryPrompts];
    renderStaticSections();
    renderInteractiveSections();
  } catch (error) {
    renderFatalError(error);
  }
}

function normalizeBootstrap(raw = {}) {
  const hero = raw.hero || {};
  const brand = raw.brand || {};
  const assistant = raw.assistant || {};
  const scholarshipTypes = Array.isArray(raw.scholarshipTypes) ? raw.scholarshipTypes : [];

  const fallbackPrompts = [
    "No se por donde empezar. Que me recomiendas?",
    "Quiero una beca internacional. Que necesito primero?",
    "Que documentos debo reunir antes de aplicar?",
  ];
  const fallbackCapabilities = [
    "Te ayuda a interpretar convocatorias y documentos en lenguaje simple.",
    "Te orienta hacia una ruta rapida o una postulacion guiada segun tu avance.",
    "Traduce tu resultado orientativo en acciones concretas.",
  ];
  const fallbackFilters = [
    { id: "all", label: "Todas" },
    { id: "nacional", label: "Nacionales" },
    { id: "internacional", label: "Internacionales" },
    { id: "grado", label: "Grado" },
    { id: "maestria", label: "Maestria" },
    { id: "doctorado", label: "Doctorado" },
  ];

  const derivedConvocations = scholarshipTypes.map((item, index) => {
    const name = item?.name || `Convocatoria ${index + 1}`;
    const inferredType = /internacional/i.test(name) ? "internacional" : "nacional";
    const inferredLevel = /doctorado/i.test(name)
      ? "doctorado"
      : /grado/i.test(name)
        ? "grado"
        : "maestria";

    return {
      id: `derived-convocation-${index + 1}`,
      name,
      description: item?.description || hero.body || "Consulta la orientacion disponible para esta oportunidad.",
      type: inferredType,
      level: inferredLevel,
      deadline: hero.deadline || "Consulta el calendario vigente",
      status: "Informativa",
      defaultMode: inferredType === "internacional" ? "full" : "quick",
      prefill: {
        tipo_beca: inferredType,
        nivel_estudio: inferredLevel === "grado" ? "grado" : inferredLevel,
      },
    };
  });

  const fallbackFeatured = derivedConvocations[0] || {
    id: "featured-default",
    title: hero.headline || "Convocatoria destacada",
    deadline: hero.deadline || "Consulta el calendario vigente",
    type: "mixta",
    level: "maestria-doctorado",
    summary: hero.body || "Explora oportunidades de becas y activa una ruta de orientacion.",
    defaultMode: "full",
    prefill: {
      tipo_beca: "internacional",
      nivel_estudio: "maestria",
    },
  };

  return {
    ...raw,
    brand: {
      title: brand.title || "Beca tu Futuro",
      subtitle:
        brand.subtitle ||
        "Una plataforma que concentra oportunidades, orientacion y herramientas de preparacion para becas dominicanas.",
      badge: brand.badge || "Portal oficial de becas",
    },
    govBanner: raw.govBanner || {
      text: "Esta es una web oficial del Gobierno de la Republica Dominicana.",
      helper: "Asi es como puedes saberlo",
    },
    header: raw.header || {
      nav: [
        { label: "Inicio", href: "#inicio" },
        { label: "Convocatorias", href: "#convocatorias" },
        { label: "Orientacion IA", href: "#orientacion" },
        { label: "Postulacion", href: "#herramientas" },
      ],
      primaryCta: "Ver convocatorias",
      secondaryCta: "Iniciar orientacion",
    },
    hero: {
      status: hero.status || "Ya esta disponible",
      headline: hero.headline || "Convocatoria nacional e internacional 2026",
      body:
        hero.body ||
        "Explora oportunidades de becas, revisa requisitos clave y activa una ruta de orientacion para preparar tu postulacion.",
      deadlineLabel: hero.deadlineLabel || "Aplica hasta el:",
      deadline: hero.deadline || "Consulta el calendario vigente",
      primaryCta: hero.primaryCta || "Ver convocatoria",
      secondaryCta: hero.secondaryCta || "Abrir orientacion",
    },
    stats: Array.isArray(raw.stats) ? raw.stats : [],
    featuredConvocation: raw.featuredConvocation || {
      id: fallbackFeatured.id,
      title: fallbackFeatured.title || fallbackFeatured.name,
      deadline: fallbackFeatured.deadline,
      type: fallbackFeatured.type,
      level: fallbackFeatured.level,
      summary: fallbackFeatured.summary || fallbackFeatured.description,
      defaultMode: fallbackFeatured.defaultMode,
      prefill: fallbackFeatured.prefill,
    },
    convocationFilters:
      Array.isArray(raw.convocationFilters) && raw.convocationFilters.length
        ? raw.convocationFilters
        : fallbackFilters,
    convocations:
      Array.isArray(raw.convocations) && raw.convocations.length ? raw.convocations : derivedConvocations,
    videoSection: raw.videoSection || {
      titleLines: [
        "Dale a play y conoce",
        "todas las opciones que",
        "Beca tu Futuro trae para ti",
      ],
      button: "Ver video explicativo",
      url: "https://www.youtube.com/watch?v=BoCf3tIuzy4",
    },
    tools:
      Array.isArray(raw.tools) && raw.tools.length
        ? raw.tools
        : [
            {
              id: "assistant",
              title: "Asistente de orientacion",
              description: "Haz preguntas sobre requisitos, documentos, tipos de beca y proximos pasos.",
              button: "Abrir asistente",
            },
            {
              id: "quick",
              title: "Evaluacion rapida",
              description: "Recibe una lectura orientativa de tu perfil en pocos pasos.",
              button: "Iniciar evaluacion",
            },
            {
              id: "full",
              title: "Postulacion guiada",
              description: "Organiza un expediente mas completo y prepara mejor tu aplicacion.",
              button: "Abrir postulacion",
            },
          ],
    assistant: {
      ...assistant,
      entryTitle:
        assistant.entryTitle ||
        "Haz tus preguntas y recibe orientacion clara antes de empezar a llenar formularios.",
      entryBody:
        assistant.entryBody ||
        "El asistente te ayuda a entender convocatorias, requisitos, documentos y la ruta recomendada segun tu caso.",
      entryPrompts:
        Array.isArray(assistant.entryPrompts) && assistant.entryPrompts.length
          ? assistant.entryPrompts
          : fallbackPrompts,
      capabilities:
        Array.isArray(assistant.capabilities) && assistant.capabilities.length
          ? assistant.capabilities
          : fallbackCapabilities,
      greeting:
        assistant.greeting ||
        "Hola. Soy tu asistente de orientacion para becas. Puedo ayudarte a entender convocatorias, requisitos, documentos y la mejor ruta para empezar.",
    },
    footer: raw.footer || {
      helpLinks: ["Terminos de uso", "Politica de privacidad", "Preguntas frecuentes"],
      infoTitle: "Informacion",
      infoBody: "Ministerio de Educacion Superior, Ciencia y Tecnologia. Republica Dominicana.",
      contactTitle: "Contactanos",
      contactItems: ["Tel: (809) 731 1100", "Fax: (809) 731-1101", "info@mescyt.gob.do"],
      addressTitle: "Buscanos",
      addressBody: "Av. Maximo Gomez No. 31, esq. Pedro Henriquez Urena, Santo Domingo, Republica Dominicana.",
      social: ["Facebook", "Youtube", "Twitter", "Instagram"],
      copyright: "© 2024 Todos los Derechos Reservados.",
    },
  };
}

function cacheElements() {
  elements.govBannerText = document.getElementById("govBannerText");
  elements.govBannerHelper = document.getElementById("govBannerHelper");
  elements.brandSubtitle = document.getElementById("brandSubtitle");
  elements.headerNav = document.getElementById("headerNav");
  elements.headerPrimaryButton = document.getElementById("headerPrimaryButton");
  elements.headerSecondaryButton = document.getElementById("headerSecondaryButton");
  elements.heroStatus = document.getElementById("heroStatus");
  elements.heroHeadline = document.getElementById("heroHeadline");
  elements.heroDeadlineLabel = document.getElementById("heroDeadlineLabel");
  elements.heroDeadline = document.getElementById("heroDeadline");
  elements.heroBody = document.getElementById("heroBody");
  elements.heroPrimaryButton = document.getElementById("heroPrimaryButton");
  elements.heroSecondaryButton = document.getElementById("heroSecondaryButton");
  elements.heroStats = document.getElementById("heroStats");
  elements.convocationFilterStrip = document.getElementById("convocationFilterStrip");
  elements.convocationGrid = document.getElementById("convocationGrid");
  elements.viewAllConvocationsButton = document.getElementById("viewAllConvocationsButton");
  elements.videoTitleLines = document.getElementById("videoTitleLines");
  elements.videoButton = document.getElementById("videoButton");
  elements.assistantEntryTitle = document.getElementById("assistantEntryTitle");
  elements.assistantEntryBody = document.getElementById("assistantEntryBody");
  elements.chatMessages = document.getElementById("chatMessages");
  elements.chatForm = document.getElementById("chatForm");
  elements.chatInput = document.getElementById("chatInput");
  elements.chatSubmitButton = document.getElementById("chatSubmitButton");
  elements.suggestionStrip = document.getElementById("suggestionStrip");
  elements.toolCards = document.getElementById("toolCards");
  elements.assistantCapabilities = document.getElementById("assistantCapabilities");
  elements.modeSwitch = document.getElementById("modeSwitch");
  elements.stepProgress = document.getElementById("stepProgress");
  elements.wizardHeader = document.getElementById("wizardHeader");
  elements.wizardForm = document.getElementById("wizardForm");
  elements.backStepButton = document.getElementById("backStepButton");
  elements.nextStepButton = document.getElementById("nextStepButton");
  elements.resultPanel = document.getElementById("resultPanel");
  elements.footerHelpLinks = document.getElementById("footerHelpLinks");
  elements.footerInfoTitle = document.getElementById("footerInfoTitle");
  elements.footerInfoBody = document.getElementById("footerInfoBody");
  elements.footerContactTitle = document.getElementById("footerContactTitle");
  elements.footerContactItems = document.getElementById("footerContactItems");
  elements.footerAddressTitle = document.getElementById("footerAddressTitle");
  elements.footerAddressBody = document.getElementById("footerAddressBody");
  elements.footerCopyright = document.getElementById("footerCopyright");
  elements.footerSocials = document.getElementById("footerSocials");
  elements.messageTemplate = document.getElementById("messageTemplate");
}

function attachEventListeners() {
  elements.backStepButton.addEventListener("click", handleBackStep);
  elements.nextStepButton.addEventListener("click", handleNextStep);
  elements.chatForm.addEventListener("submit", handleChatSubmit);
  elements.headerPrimaryButton.addEventListener("click", () => {
    state.convocationFilter = "all";
    renderConvocationFilters();
    renderConvocations();
    focusSection("convocatorias");
  });
  elements.headerSecondaryButton.addEventListener("click", focusAssistant);
  elements.heroPrimaryButton.addEventListener("click", () => openFeaturedConvocation(true));
  elements.heroSecondaryButton.addEventListener("click", focusAssistant);
  elements.viewAllConvocationsButton.addEventListener("click", () => {
    state.convocationFilter = "all";
    renderConvocationFilters();
    renderConvocations();
    focusSection("convocatorias");
  });
}

function renderStaticSections() {
  const { govBanner, brand, header, hero, stats, videoSection, assistant, footer } = state.bootstrap;

  elements.govBannerText.textContent = govBanner.text;
  elements.govBannerHelper.textContent = govBanner.helper;
  elements.govBannerHelper.addEventListener("click", () => {
    window.open("https://www.gob.do/", "_blank", "noopener,noreferrer");
  });

  elements.brandSubtitle.textContent = brand.subtitle || "";
  elements.headerNav.innerHTML = header.nav
    .map((item) => `<a href="${escapeAttribute(item.href)}">${escapeHtml(item.label)}</a>`)
    .join("");
  elements.headerPrimaryButton.textContent = header.primaryCta;
  elements.headerSecondaryButton.textContent = header.secondaryCta;

  elements.heroStatus.textContent = hero.status;
  elements.heroHeadline.textContent = hero.headline;
  elements.heroDeadlineLabel.textContent = hero.deadlineLabel;
  elements.heroDeadline.textContent = hero.deadline;
  elements.heroBody.textContent = hero.body;
  elements.heroPrimaryButton.textContent = hero.primaryCta;
  elements.heroSecondaryButton.textContent = hero.secondaryCta;
  elements.heroStats.innerHTML = stats
    .map(
      (item) => `
        <article class="stat-card">
          <h4>${escapeHtml(item.value)}</h4>
          <p><strong>${escapeHtml(item.label)}</strong><br />${escapeHtml(item.detail || "")}</p>
        </article>
      `
    )
    .join("");

  elements.videoTitleLines.innerHTML = videoSection.titleLines
    .map(
      (line, index) => `
        <p class="${index < 2 ? "is-light" : ""}">
          ${escapeHtml(line)}
        </p>
      `
    )
    .join("");
  elements.videoButton.textContent = videoSection.button;
  elements.videoButton.href = videoSection.url;

  elements.assistantEntryTitle.textContent = assistant.entryTitle;
  elements.assistantEntryBody.textContent = assistant.entryBody;
  elements.assistantCapabilities.innerHTML = assistant.capabilities
    .map(
      (item) => `
        <article class="assistant-capability">
          <h4>${escapeHtml(shortCapabilityHeading(item))}</h4>
          <p>${escapeHtml(item)}</p>
        </article>
      `
    )
    .join("");

  elements.toolCards.innerHTML = state.bootstrap.tools
    .map(
      (item) => `
        <article class="tool-card">
          <h3>${escapeHtml(item.title)}</h3>
          <p>${escapeHtml(item.description)}</p>
          <button
            type="button"
            class="tool-card-button"
            data-tool-action="${escapeAttribute(item.id)}"
          >
            ${escapeHtml(item.button)}
          </button>
        </article>
      `
    )
    .join("");
  bindToolCardEvents();

  elements.footerHelpLinks.innerHTML = `
    <div class="footer-link-list">
      ${footer.helpLinks.map((item) => `<a href="#">${escapeHtml(item)}</a>`).join("")}
    </div>
  `;
  elements.footerInfoTitle.textContent = footer.infoTitle;
  elements.footerInfoBody.textContent = footer.infoBody;
  elements.footerContactTitle.textContent = footer.contactTitle;
  elements.footerContactItems.innerHTML = `
    <div class="footer-contact-list">
      ${footer.contactItems.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
    </div>
  `;
  elements.footerAddressTitle.textContent = footer.addressTitle;
  elements.footerAddressBody.textContent = footer.addressBody;
  elements.footerCopyright.textContent = footer.copyright;
  elements.footerSocials.innerHTML = footer.social
    .map((item) => `<span class="social-chip">${escapeHtml(shortSocialLabel(item))}</span>`)
    .join("");
}

function renderInteractiveSections() {
  renderConvocationFilters();
  renderConvocations();
  renderModeSwitch();
  renderWizard();
  renderResult();
  renderChatSuggestions();
  renderChatMessages();
}

function renderConvocationFilters() {
  elements.convocationFilterStrip.innerHTML = state.bootstrap.convocationFilters
    .map(
      (filter) => `
        <button
          type="button"
          class="filter-chip ${state.convocationFilter === filter.id ? "is-active" : ""}"
          data-filter-id="${escapeAttribute(filter.id)}"
        >
          ${escapeHtml(filter.label)}
        </button>
      `
    )
    .join("");

  elements.convocationFilterStrip.querySelectorAll("[data-filter-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.convocationFilter = button.dataset.filterId;
      renderConvocationFilters();
      renderConvocations();
    });
  });
}

function renderConvocations() {
  const cards = getVisibleConvocations();

  if (!cards.length) {
    elements.convocationGrid.innerHTML = `
      <article class="convocation-card">
        <span class="convocation-card-status">Sin resultados</span>
        <h3>No hay convocatorias para este filtro.</h3>
        <p>Prueba con otra categoria o revisa todas las convocatorias disponibles.</p>
      </article>
    `;
    return;
  }

  elements.convocationGrid.innerHTML = cards
    .map(
      (item) => `
        <article class="convocation-card">
          <span class="convocation-card-status">${escapeHtml(item.status)}</span>
          <h3>${escapeHtml(item.name)}</h3>
          <p>${escapeHtml(item.description)}</p>
          <div class="convocation-meta">
            <span><strong>Tipo:</strong> ${escapeHtml(formatType(item.type))}</span>
            <span><strong>Nivel:</strong> ${escapeHtml(formatLevel(item.level))}</span>
            <span><strong>Cierre:</strong> ${escapeHtml(item.deadline)}</span>
          </div>
          <button
            type="button"
            class="button button-outline button-wide"
            data-convocation-id="${escapeAttribute(item.id)}"
          >
            Iniciar orientacion
          </button>
        </article>
      `
    )
    .join("");

  elements.convocationGrid.querySelectorAll("[data-convocation-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const convocation = getAllConvocations().find((item) => item.id === button.dataset.convocationId);
      if (convocation) {
        activateConvocation(convocation);
      }
    });
  });
}

function getAllConvocations() {
  const featured = {
    id: state.bootstrap.featuredConvocation.id,
    name: state.bootstrap.featuredConvocation.title,
    description: state.bootstrap.featuredConvocation.summary,
    type: state.bootstrap.featuredConvocation.type,
    level: state.bootstrap.featuredConvocation.level,
    deadline: state.bootstrap.featuredConvocation.deadline,
    status: "Destacada",
    defaultMode: state.bootstrap.featuredConvocation.defaultMode,
    prefill: state.bootstrap.featuredConvocation.prefill,
  };

  return [featured, ...state.bootstrap.convocations];
}

function getVisibleConvocations() {
  const filterId = state.convocationFilter;
  return getAllConvocations().filter((item) => {
    if (filterId === "all") {
      return true;
    }

    if (filterId === "nacional" || filterId === "internacional") {
      if (item.type === "mixta") {
        return true;
      }
      return item.type === filterId;
    }

    return String(item.level || "").includes(filterId);
  });
}

function bindToolCardEvents() {
  elements.toolCards.querySelectorAll("[data-tool-action]").forEach((button) => {
    button.addEventListener("click", () => {
      const action = button.dataset.toolAction;
      if (action === "assistant") {
        focusAssistant();
        return;
      }
      if (action === "quick" || action === "full") {
        activateMode(action, { scrollToWizard: true, resetStep: true });
      }
    });
  });
}

function openFeaturedConvocation(scrollToList) {
  state.convocationFilter = "all";
  renderConvocationFilters();
  renderConvocations();

  if (scrollToList) {
    focusSection("convocatorias");
  }
}

function activateConvocation(convocation) {
  const mode = convocation.defaultMode || "quick";
  const prefill = convocation.prefill || {};
  const nextData = { ...state.formData[mode], ...prefill };
  state.selectedConvocationId = convocation.id;

  if (nextData.tipo_beca && nextData.nivel_estudio) {
    const validLevels = getFieldOptions("nivel_estudio", nextData).map((item) => item.value);
    if (!validLevels.includes(nextData.nivel_estudio)) {
      nextData.nivel_estudio = "";
    }
  }

  state.formData[mode] = nextData;
  state.results[mode] = null;
  activateMode(mode, { scrollToWizard: true, resetStep: true });
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
          <strong>${escapeHtml(config.label)}</strong>
          <span>${escapeHtml(config.summary)}</span>
        </button>
      `
    )
    .join("");

  elements.modeSwitch.querySelectorAll("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      activateMode(button.dataset.mode, { scrollToWizard: false, resetStep: false });
    });
  });
}

function activateMode(mode, options = {}) {
  const { scrollToWizard = false, resetStep = false } = options;
  const changed = state.mode !== mode;

  if (changed) {
    syncSharedData(state.mode, mode);
    state.mode = mode;
  }

  if (changed || resetStep) {
    state.currentStepIndex = 0;
  }

  state.errors = {};
  renderInteractiveSections();

  if (scrollToWizard) {
    focusWizard();
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
  const stepFields = getVisibleFieldsForStep(step);
  const formLevelError = state.errors._form ? `<p class="field-error">${escapeHtml(state.errors._form)}</p>` : "";

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
    <p class="section-eyebrow">${escapeHtml(step.eyebrow)}</p>
    <h3>${escapeHtml(step.title)}</h3>
    <p>${escapeHtml(step.description)}</p>
    <p class="wizard-intro-copy">Paso ${state.currentStepIndex + 1} de ${wizard.steps.length}. ${escapeHtml(
      wizard.summary
    )}</p>
    ${formLevelError}
  `;

  elements.wizardForm.innerHTML = stepFields.map(renderFieldCard).join("");
  bindFieldEvents(stepFields);

  elements.backStepButton.disabled = state.currentStepIndex === 0 || state.busy.wizard;
  elements.nextStepButton.disabled = state.busy.wizard;
  elements.nextStepButton.textContent =
    state.currentStepIndex === wizard.steps.length - 1
      ? state.busy.wizard
        ? "Calculando..."
        : "Ver mi resultado"
      : "Continuar";
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
    control = `
      <select name="${fieldName}" data-field="${fieldName}">
        <option value="">Selecciona una opcion</option>
        ${getFieldOptions(fieldName)
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
    if (!input) {
      return;
    }

    input.addEventListener("change", handleFieldChange);
    if (input.tagName === "INPUT" || input.tagName === "TEXTAREA") {
      input.addEventListener("input", handleFieldInput);
    }
  });

  elements.wizardForm.querySelectorAll("[data-toggle-field]").forEach((button) => {
    button.addEventListener("click", () => {
      updateFieldValue(button.dataset.toggleField, button.dataset.value, { render: true });
    });
  });
}

function handleFieldInput(event) {
  updateFieldValue(event.target.dataset.field, event.target.value, { render: false });
}

function handleFieldChange(event) {
  updateFieldValue(event.target.dataset.field, event.target.value, { render: true });
}

function updateFieldValue(fieldName, rawValue, options = {}) {
  const { render = false } = options;
  const definition = state.bootstrap.fields[fieldName];
  let value = rawValue;

  if (definition.type === "number") {
    value = rawValue === "" ? "" : Number(rawValue);
  }

  if (definition.type === "boolean") {
    value = Number(rawValue);
  }

  const currentData = getCurrentData();
  const nextData = { ...currentData, [fieldName]: value };

  if (fieldName === "tipo_beca") {
    const validOptions = getFieldOptions("nivel_estudio", nextData).map((option) => option.value);
    if (nextData.nivel_estudio && !validOptions.includes(nextData.nivel_estudio)) {
      nextData.nivel_estudio = "";
    }
  }

  const changed = String(currentData[fieldName] ?? "") !== String(value ?? "");
  state.formData[state.mode] = nextData;
  state.errors = { ...state.errors, [fieldName]: undefined, _form: undefined };

  if (changed && state.results[state.mode]) {
    state.results[state.mode] = null;
  }

  if (render || fieldName === "tipo_beca") {
    renderWizard();
    renderResult();
    renderChatSuggestions();
  }
}

function handleBackStep() {
  state.currentStepIndex = Math.max(0, state.currentStepIndex - 1);
  state.errors = {};
  renderWizard();
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
    return;
  }

  await submitPrediction();
}

async function submitPrediction() {
  state.busy.wizard = true;
  renderWizard();

  try {
    const response = await api("/api/eligibility/predict", {
      method: "POST",
      body: { mode: state.mode, applicant: getCurrentData() },
    });
    state.results[state.mode] = response;
    state.chatSuggestions = [
      "Interpretame mi resultado y dime mis proximos pasos.",
      "Que documentos debo priorizar primero?",
      "Como puedo fortalecer mi perfil antes de aplicar?",
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

  if (!result) {
    elements.resultPanel.classList.add("hidden");
    elements.resultPanel.innerHTML = "";
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
  const nextStepsMarkup = result.next_steps.map((item) => `<li>${escapeHtml(item)}</li>`).join("");

  elements.resultPanel.classList.remove("hidden");
  elements.resultPanel.innerHTML = `
    <div class="result-card">
      <div class="result-topline">
        <div>
          <p class="section-eyebrow">RESULTADO ORIENTATIVO</p>
          <h3>${escapeHtml(getCurrentWizard().label)}</h3>
        </div>
        <span class="priority-chip ${escapeAttribute(result.prediction.priority_label)}">
          Prioridad ${escapeHtml(result.prediction.priority_label)}
        </span>
      </div>

      <section class="result-summary">
        <div>
          <h4>${escapeHtml(result.prediction.explanation)}</h4>
          <p class="result-copy">${escapeHtml(result.disclaimer)}</p>
        </div>
        <div class="result-metric">
          <strong>${probabilityPercent}%</strong>
          <span>probabilidad orientativa</span>
          <div class="meter"><span style="width: ${probabilityPercent}%"></span></div>
        </div>
      </section>

      <section>
        <p class="section-eyebrow">LECTURA RAPIDA</p>
        <div class="signal-grid">
          ${signalMarkup || '<div class="signal-chip positive">Perfil capturado correctamente.</div>'}
        </div>
      </section>

      <section>
        <p class="section-eyebrow">CHECKLIST DOCUMENTAL</p>
        <div class="document-grid">${documentMarkup}</div>
      </section>

      <section>
        <p class="section-eyebrow">PROXIMOS PASOS</p>
        <ol class="next-step-list">${nextStepsMarkup}</ol>
      </section>

      <div class="hero-actions">
        <button type="button" class="button button-outline" id="resultAskAssistant">Llevar esto al asistente</button>
        <button type="button" class="button button-solid" id="downloadSummaryButton">Descargar resumen</button>
      </div>
    </div>
  `;

  const askAssistant = document.getElementById("resultAskAssistant");
  if (askAssistant) {
    askAssistant.addEventListener("click", () => {
      focusAssistant();
      elements.chatInput.value = "Interpretame mi resultado y dime mis proximos pasos.";
      elements.chatInput.focus();
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
    node.querySelector(".message-role").textContent = message.role === "user" ? "Tu consulta" : "Asistente";
    node.querySelector(".message-body").innerHTML = renderMessageBody(message);
    fragment.appendChild(node);
  });

  elements.chatMessages.appendChild(fragment);
  elements.chatMessages.querySelectorAll("[data-chat-convocation]").forEach((button) => {
    button.addEventListener("click", () => {
      const convocation = getAllConvocations().find((item) => item.id === button.dataset.chatConvocation);
      if (convocation) {
        activateConvocation(convocation);
      }
    });
  });
  elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
  elements.chatSubmitButton.disabled = state.busy.chat;
  elements.chatSubmitButton.textContent = state.busy.chat ? "Consultando..." : "Enviar consulta";
}

function renderChatSuggestions() {
  const defaults = state.bootstrap.assistant.entryPrompts || [];
  const result = state.results[state.mode];
  const merged = Array.from(
    new Set(
      [
        ...(state.chatSuggestions.length ? state.chatSuggestions : defaults),
        ...(result ? ["Interpretame mi resultado y dime mis proximos pasos."] : []),
        "Que documentos me faltan para postular?",
      ].filter(Boolean)
    )
  ).slice(0, 5);

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
    button.addEventListener("click", () => {
      sendChatQuestion(button.dataset.suggestion);
    });
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
    const response = await api("/api/assistant/chat", {
      method: "POST",
      body: {
        question,
        history: state.chatMessages
          .slice(0, -1)
          .slice(-6)
          .map((item) => ({ role: item.role, body: item.body })),
        applicant_context: getCurrentData(),
        prediction: state.results[state.mode]?.prediction || null,
        step_context: { mode: state.mode, step_id: step.id, step_title: step.title },
        selected_convocation_id: state.selectedConvocationId,
        allow_prediction: false,
      },
    });

    state.chatMessages.push({
      role: "assistant",
      body: response.answer,
      references: response.references || [],
      recommendations: response.recommendations || [],
      intent: response.intent || "",
      provider: response.provider || "local_fallback",
    });
    state.chatSuggestions = response.suggestions || state.chatSuggestions;

    const normalized = question.toLowerCase();
    if (
      normalized.includes("evaluacion") ||
      normalized.includes("postulacion") ||
      normalized.includes("empezar") ||
      response.intent === "recommendation"
    ) {
      focusWizard();
    }
  } catch (error) {
    state.chatMessages.push({
      role: "assistant",
      body: `No pude responder ahora mismo. ${error.message || "Intenta de nuevo en unos segundos."}`,
    });
  } finally {
    state.busy.chat = false;
    renderChatSuggestions();
    renderChatMessages();
  }
}

function renderMessageBody(message) {
  const body = `<p>${formatMessageText(message.body || "")}</p>`;
  if (message.role !== "assistant") {
    return body;
  }

  const recommendations = Array.isArray(message.recommendations) ? message.recommendations : [];
  const references = Array.isArray(message.references) ? message.references : [];
  const provider = message.provider
    ? `<span class="message-provider">${escapeHtml(formatProviderLabel(message.provider))}</span>`
    : "";

  const recommendationMarkup = recommendations.length
    ? `
      <section class="message-meta-block">
        <p class="message-meta-title">Becas recomendadas</p>
        <div class="message-recommendation-list">
          ${recommendations
            .map(
              (item) => `
                <article class="message-recommendation">
                  <div class="message-recommendation-topline">
                    <strong>${escapeHtml(item.title)}</strong>
                    <span class="recommendation-fit ${escapeAttribute(slugify(item.fit_label || "media"))}">
                      ${escapeHtml(item.fit_label || "afinidad media")}
                    </span>
                  </div>
                  <p>${escapeHtml((item.reasons || [])[0] || "Afinidad parcial detectada.")}</p>
                  ${
                    item.gaps && item.gaps.length
                      ? `<p class="recommendation-gap">Atencion: ${escapeHtml(item.gaps[0])}</p>`
                      : ""
                  }
                  <button
                    type="button"
                    class="text-link message-action-link"
                    data-chat-convocation="${escapeAttribute(item.scholarship_id)}"
                  >
                    Abrir esta beca
                  </button>
                </article>
              `
            )
            .join("")}
        </div>
      </section>
    `
    : "";

  const referenceMarkup = references.length
    ? `
      <section class="message-meta-block">
        <p class="message-meta-title">Fuentes usadas</p>
        <div class="message-reference-list">
          ${references
            .map(
              (item) => `
                <span class="message-reference-chip">
                  ${escapeHtml(formatReferenceLabel(item))}
                </span>
              `
            )
            .join("")}
        </div>
      </section>
    `
    : "";

  return `
    ${body}
    ${provider}
    ${recommendationMarkup}
    ${referenceMarkup}
  `;
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
    state.bootstrap.brand.title,
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
  anchor.download = `beca-tu-futuro-${state.mode}-resumen.txt`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function focusAssistant() {
  focusSection("orientacion");
  elements.chatInput.focus();
}

function focusWizard() {
  focusSection("herramientas");
}

function focusSection(id) {
  const node = document.getElementById(id);
  if (node) {
    node.scrollIntoView({ behavior: "smooth", block: "start" });
  }
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
    <main style="display:grid;place-items:center;min-height:100vh;padding:24px;background:#eef6ff;color:#0b2e4f;font-family:Poppins, Arial, sans-serif;">
      <section style="max-width:720px;border:1px solid #d2e1f1;border-radius:24px;padding:28px;background:#ffffff;">
        <p style="letter-spacing:0.08em;text-transform:uppercase;color:#0099ff;font-size:0.82rem;font-weight:700;">Error de inicio</p>
        <h1 style="font-weight:800;">No fue posible cargar el portal</h1>
        <p style="color:#546b85;line-height:1.7;">${escapeHtml(message)}</p>
      </section>
    </main>
  `;
}

function shortCapabilityHeading(copy) {
  if (copy.includes("interpretar")) {
    return "Entiende convocatorias";
  }
  if (copy.includes("ruta")) {
    return "Sugiere la mejor via";
  }
  return "Convierte en acciones";
}

function shortSocialLabel(name) {
  const key = String(name).toLowerCase();
  if (key.includes("facebook")) {
    return "FB";
  }
  if (key.includes("youtube")) {
    return "YT";
  }
  if (key.includes("instagram")) {
    return "IG";
  }
  if (key.includes("twitter")) {
    return "TW";
  }
  return name.slice(0, 2).toUpperCase();
}

function formatType(value) {
  if (value === "nacional") {
    return "Nacional";
  }
  if (value === "internacional") {
    return "Internacional";
  }
  if (value === "mixta") {
    return "Nacional e internacional";
  }
  return String(value || "");
}

function formatLevel(value) {
  if (value === "grado") {
    return "Grado";
  }
  if (value === "maestria") {
    return "Maestria";
  }
  if (value === "doctorado") {
    return "Doctorado";
  }
  if (value === "maestria-doctorado") {
    return "Maestria y doctorado";
  }
  return String(value || "");
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

function formatMessageText(value) {
  return escapeHtml(value).replaceAll("\n", "<br />");
}

function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .replaceAll(" ", "-")
    .replaceAll("á", "a")
    .replaceAll("é", "e")
    .replaceAll("í", "i")
    .replaceAll("ó", "o")
    .replaceAll("ú", "u")
    .replaceAll("ñ", "n");
}

function formatProviderLabel(value) {
  if (value === "openai") {
    return "OpenAI";
  }
  if (value === "local_fallback") {
    return "Fallback local";
  }
  return value;
}

function formatReferenceLabel(item) {
  const source = String(item.source || "");
  const label = String(item.label || "");
  const sourceLabel = source === "catalogo_becas_portal" ? "Portal" : source.replaceAll(".md", "");
  return label ? `${sourceLabel} · ${label}` : sourceLabel;
}
