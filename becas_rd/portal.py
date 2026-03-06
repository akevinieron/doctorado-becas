from __future__ import annotations

from typing import Any, Dict, List

from .data_generation import REGION_BY_PROVINCE

MODEL_FIELDS: List[str] = [
    "edad",
    "genero",
    "provincia",
    "region",
    "zona",
    "tipo_beca",
    "nivel_estudio",
    "ingreso_hogar_mensual_dop",
    "miembros_hogar",
    "promedio_academico",
    "score_documental",
    "horas_voluntariado",
    "puntaje_ingles",
    "costo_anual_programa_dop",
    "primera_generacion_universitaria",
    "discapacidad",
]

BOOLEAN_FIELDS = {
    "primera_generacion_universitaria",
    "discapacidad",
    "record_academico_listo",
    "identificacion_vigente",
    "carta_motivacion_lista",
    "plan_estudios_listo",
    "evidencia_socioeconomica_lista",
    "carta_admision",
    "presupuesto_estimado_listo",
    "evidencia_idioma_lista",
}

NUMERIC_FIELDS = {
    "edad",
    "ingreso_hogar_mensual_dop",
    "miembros_hogar",
    "promedio_academico",
    "score_documental",
    "horas_voluntariado",
    "puntaje_ingles",
    "costo_anual_programa_dop",
}

FIELD_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "nombre_completo": {
        "label": "Nombre completo",
        "type": "text",
        "placeholder": "Como aparece en tu cedula o pasaporte",
        "required": True,
    },
    "correo": {
        "label": "Correo electronico",
        "type": "email",
        "placeholder": "persona@ejemplo.com",
        "required": True,
    },
    "telefono": {
        "label": "Telefono",
        "type": "text",
        "placeholder": "809-555-0000",
        "required": False,
    },
    "programa_interes": {
        "label": "Programa de interes",
        "type": "text",
        "placeholder": "Ingenieria de datos, educacion, salud publica...",
        "required": False,
    },
    "universidad_destino": {
        "label": "Universidad o centro de destino",
        "type": "text",
        "placeholder": "Universidad de interes o institucion objetivo",
        "required": False,
    },
    "objetivo_profesional": {
        "label": "Objetivo profesional",
        "type": "textarea",
        "placeholder": "Describe como esta beca se conecta con tu impacto profesional y social.",
        "required": False,
    },
    "tipo_beca": {
        "label": "Tipo de beca",
        "type": "select",
        "required": True,
        "options": [
            {"value": "nacional", "label": "Nacional"},
            {"value": "internacional", "label": "Internacional"},
        ],
    },
    "nivel_estudio": {
        "label": "Nivel de estudio",
        "type": "select",
        "required": True,
        "options": [
            {"value": "grado", "label": "Grado"},
            {"value": "maestria", "label": "Maestria"},
            {"value": "doctorado", "label": "Doctorado"},
        ],
        "optionsByValue": {
            "nacional": [
                {"value": "grado", "label": "Grado"},
                {"value": "maestria", "label": "Maestria"},
            ],
            "internacional": [
                {"value": "maestria", "label": "Maestria"},
                {"value": "doctorado", "label": "Doctorado"},
            ],
        },
        "dependsOn": "tipo_beca",
    },
    "edad": {
        "label": "Edad",
        "type": "number",
        "required": True,
        "min": 17,
        "max": 60,
        "step": 1,
    },
    "genero": {
        "label": "Genero",
        "type": "select",
        "required": True,
        "options": [
            {"value": "femenino", "label": "Femenino"},
            {"value": "masculino", "label": "Masculino"},
            {"value": "otro", "label": "Otro"},
        ],
    },
    "provincia": {
        "label": "Provincia",
        "type": "select",
        "required": True,
        "options": [{"value": province, "label": province} for province in sorted(REGION_BY_PROVINCE)],
    },
    "zona": {
        "label": "Zona",
        "type": "select",
        "required": True,
        "options": [
            {"value": "urbana", "label": "Urbana"},
            {"value": "rural", "label": "Rural"},
        ],
    },
    "ingreso_hogar_mensual_dop": {
        "label": "Ingreso mensual del hogar (DOP)",
        "type": "number",
        "required": True,
        "min": 12000,
        "max": 500000,
        "step": 1000,
    },
    "miembros_hogar": {
        "label": "Miembros del hogar",
        "type": "number",
        "required": True,
        "min": 1,
        "max": 12,
        "step": 1,
    },
    "promedio_academico": {
        "label": "Promedio academico",
        "type": "number",
        "required": True,
        "min": 60,
        "max": 100,
        "step": 0.1,
    },
    "score_documental": {
        "label": "Preparacion documental",
        "type": "number",
        "required": True,
        "min": 0,
        "max": 100,
        "step": 0.1,
        "hint": "Evalua que tan listo esta tu expediente hoy.",
    },
    "horas_voluntariado": {
        "label": "Horas de voluntariado",
        "type": "number",
        "required": True,
        "min": 0,
        "max": 400,
        "step": 1,
    },
    "puntaje_ingles": {
        "label": "Nivel de ingles",
        "type": "number",
        "required": True,
        "min": 0,
        "max": 100,
        "step": 0.1,
        "showWhen": {"field": "tipo_beca", "equals": "internacional"},
        "hint": "Usa tu puntaje o una autoestimacion razonable si aun no tienes examen.",
    },
    "costo_anual_programa_dop": {
        "label": "Costo anual estimado del programa (DOP)",
        "type": "number",
        "required": True,
        "min": 50000,
        "max": 3500000,
        "step": 1000,
    },
    "primera_generacion_universitaria": {
        "label": "Primera generacion universitaria",
        "type": "boolean",
        "required": True,
    },
    "discapacidad": {
        "label": "Condicion de discapacidad declarada",
        "type": "boolean",
        "required": True,
    },
    "record_academico_listo": {
        "label": "Record academico oficial disponible",
        "type": "boolean",
        "required": False,
    },
    "identificacion_vigente": {
        "label": "Cedula o pasaporte vigente",
        "type": "boolean",
        "required": False,
    },
    "carta_motivacion_lista": {
        "label": "Carta de motivacion lista",
        "type": "boolean",
        "required": False,
    },
    "plan_estudios_listo": {
        "label": "Plan de estudios definido",
        "type": "boolean",
        "required": False,
    },
    "evidencia_socioeconomica_lista": {
        "label": "Evidencia socioeconomica disponible",
        "type": "boolean",
        "required": False,
    },
    "carta_admision": {
        "label": "Carta de admision o preadmision",
        "type": "boolean",
        "required": False,
        "showWhen": {"field": "tipo_beca", "equals": "internacional"},
    },
    "presupuesto_estimado_listo": {
        "label": "Presupuesto anual estimado listo",
        "type": "boolean",
        "required": False,
        "showWhen": {"field": "tipo_beca", "equals": "internacional"},
    },
    "evidencia_idioma_lista": {
        "label": "Evidencia de idioma disponible",
        "type": "boolean",
        "required": False,
        "showWhen": {"field": "tipo_beca", "equals": "internacional"},
    },
}

QUICK_WIZARD_STEPS: List[Dict[str, Any]] = [
    {
        "id": "ruta",
        "eyebrow": "Modo rapido",
        "title": "Define tu ruta academica",
        "description": "Ubicamos el tipo de beca, nivel y programa para orientar la evaluacion inicial.",
        "fields": ["tipo_beca", "nivel_estudio", "programa_interes"],
    },
    {
        "id": "perfil",
        "eyebrow": "Ciudadania",
        "title": "Cuadro personal y territorial",
        "description": "Usamos estos datos para aproximar contexto, region y trayectoria de acceso.",
        "fields": ["edad", "genero", "provincia", "zona"],
    },
    {
        "id": "academico",
        "eyebrow": "Merito",
        "title": "Tu base academica y documental",
        "description": "Este bloque captura preparacion academica, documental y experiencia solidaria.",
        "fields": ["promedio_academico", "score_documental", "horas_voluntariado", "puntaje_ingles"],
    },
    {
        "id": "contexto",
        "eyebrow": "Contexto social",
        "title": "Capacidad economica y entorno familiar",
        "description": "Esto nos ayuda a perfilar nivel de necesidad economica y responsabilidad familiar.",
        "fields": [
            "ingreso_hogar_mensual_dop",
            "miembros_hogar",
            "primera_generacion_universitaria",
            "discapacidad",
        ],
    },
    {
        "id": "costos",
        "eyebrow": "Viabilidad",
        "title": "Costo estimado del programa",
        "description": "Con esto cerramos la orientacion y calculamos una pre-evaluacion inmediata.",
        "fields": ["costo_anual_programa_dop"],
    },
]

FULL_WIZARD_STEPS: List[Dict[str, Any]] = [
    {
        "id": "identidad",
        "eyebrow": "Postulacion guiada",
        "title": "Identidad y contacto",
        "description": "Preparamos una ficha ciudadana mas completa para una postulacion guiada en una sola sesion.",
        "fields": ["nombre_completo", "correo", "telefono", "tipo_beca", "nivel_estudio"],
    },
    {
        "id": "trayectoria",
        "eyebrow": "Proposito",
        "title": "Programa y trayectoria deseada",
        "description": "Definimos el destino academico y el impacto que esperas producir.",
        "fields": ["programa_interes", "universidad_destino", "objetivo_profesional"],
    },
    {
        "id": "territorio",
        "eyebrow": "Contexto",
        "title": "Perfil ciudadano y territorial",
        "description": "Capturamos ubicacion, edad y condiciones del hogar para orientar la priorizacion.",
        "fields": ["edad", "genero", "provincia", "zona", "ingreso_hogar_mensual_dop", "miembros_hogar"],
    },
    {
        "id": "academico",
        "eyebrow": "Merito",
        "title": "Base academica y evidencia de preparacion",
        "description": "Profundizamos en tu desempeno academico, nivel documental y experiencia social.",
        "fields": ["promedio_academico", "score_documental", "horas_voluntariado", "puntaje_ingles"],
    },
    {
        "id": "inclusion",
        "eyebrow": "Equidad",
        "title": "Condiciones de acceso e inclusion",
        "description": "Este bloque mejora la lectura de necesidades y barreras estructurales.",
        "fields": ["primera_generacion_universitaria", "discapacidad", "costo_anual_programa_dop"],
    },
    {
        "id": "documentos",
        "eyebrow": "Checklist",
        "title": "Estado documental",
        "description": "Marcamos lo que ya tienes listo y lo que debes reunir para postular con mas fuerza.",
        "fields": [
            "record_academico_listo",
            "identificacion_vigente",
            "carta_motivacion_lista",
            "plan_estudios_listo",
            "evidencia_socioeconomica_lista",
            "carta_admision",
            "presupuesto_estimado_listo",
            "evidencia_idioma_lista",
        ],
    },
]


def _coerce_number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_boolean_flag(value: Any) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "si", "true", "yes"}:
            return 1
        if lowered in {"0", "no", "false"}:
            return 0
    return None


def normalize_portal_payload(payload: Dict[str, Any] | None) -> Dict[str, Any]:
    source = payload or {}
    normalized: Dict[str, Any] = {}

    for field_name in set(FIELD_DEFINITIONS) | {"region"}:
        value = source.get(field_name)
        if field_name in BOOLEAN_FIELDS:
            normalized[field_name] = _coerce_boolean_flag(value)
        elif field_name in NUMERIC_FIELDS:
            number = _coerce_number(value)
            if number is None:
                normalized[field_name] = None
            elif field_name in {"edad", "miembros_hogar"}:
                normalized[field_name] = int(round(number))
            else:
                normalized[field_name] = round(number, 2)
        elif value is None:
            normalized[field_name] = None
        else:
            normalized[field_name] = str(value).strip() or None

    provincia = normalized.get("provincia")
    normalized["region"] = REGION_BY_PROVINCE.get(str(provincia), normalized.get("region"))
    return normalized


def validate_applicant_payload(applicant: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    for field_name in MODEL_FIELDS:
        if field_name == "region":
            continue
        definition = FIELD_DEFINITIONS.get(field_name, {})
        required = definition.get("required", True)
        if not required:
            continue
        if definition.get("showWhen") and not _field_is_visible(definition, applicant):
            continue
        if applicant.get(field_name) in (None, ""):
            missing.append(field_name)

    if not applicant.get("region"):
        missing.append("region")
    return missing


def _field_is_visible(definition: Dict[str, Any], values: Dict[str, Any]) -> bool:
    rule = definition.get("showWhen")
    if not rule:
        return True
    return values.get(rule["field"]) == rule["equals"]


def build_required_documents(profile: Dict[str, Any], mode: str) -> List[Dict[str, str]]:
    quick_mode = mode == "quick"

    def status_from(flag_name: str) -> str:
        if quick_mode:
            return "pendiente"
        return "listo" if profile.get(flag_name) == 1 else "pendiente"

    documents = [
        {
            "label": "Formulario de postulacion completo y firmado",
            "status": "pendiente" if quick_mode else "en_preparacion",
            "detail": "Se genera con la informacion consolidada de la sesion.",
        },
        {
            "label": "Record academico oficial",
            "status": status_from("record_academico_listo"),
            "detail": "Debe venir emitido por la institucion educativa correspondiente.",
        },
        {
            "label": "Cedula o pasaporte vigente",
            "status": status_from("identificacion_vigente"),
            "detail": "Documento de identidad requerido para validar la postulacion.",
        },
        {
            "label": "Carta de motivacion",
            "status": status_from("carta_motivacion_lista"),
            "detail": "Explica metas, impacto esperado y alineacion con la beca.",
        },
        {
            "label": "Plan de estudios o propuesta academica",
            "status": status_from("plan_estudios_listo"),
            "detail": "Resume estructura del programa y objetivos de formacion.",
        },
        {
            "label": "Evidencia socioeconomica del hogar",
            "status": status_from("evidencia_socioeconomica_lista"),
            "detail": "Constancias de ingresos, dependientes y otras evidencias de necesidad.",
        },
    ]

    if profile.get("tipo_beca") == "internacional":
        documents.extend(
            [
                {
                    "label": "Carta de admision o preadmision",
                    "status": status_from("carta_admision"),
                    "detail": "Para beca internacional es uno de los documentos criticos.",
                },
                {
                    "label": "Evidencia de idioma",
                    "status": status_from("evidencia_idioma_lista"),
                    "detail": "Puede ser examen oficial o constancia aceptada por el programa.",
                },
                {
                    "label": "Presupuesto anual estimado",
                    "status": status_from("presupuesto_estimado_listo"),
                    "detail": "Incluye matricula, manutencion y otros costos asociados.",
                },
            ]
        )

    return documents


def build_profile_signals(profile: Dict[str, Any], prediction: Dict[str, Any]) -> List[Dict[str, str]]:
    signals: List[Dict[str, str]] = []

    if float(profile.get("promedio_academico") or 0) >= 88:
        signals.append({"tone": "positive", "label": "Merito academico fuerte"})
    elif float(profile.get("promedio_academico") or 0) < 75:
        signals.append({"tone": "caution", "label": "Promedio por debajo de la franja competitiva"})

    if float(profile.get("score_documental") or 0) >= 80:
        signals.append({"tone": "positive", "label": "Expediente documental robusto"})
    elif float(profile.get("score_documental") or 0) < 65:
        signals.append({"tone": "caution", "label": "Documentacion todavia vulnerable"})

    if float(profile.get("ingreso_hogar_mensual_dop") or 0) <= 50000:
        signals.append({"tone": "positive", "label": "Nivel de necesidad economica visible"})

    if profile.get("tipo_beca") == "internacional" and float(profile.get("puntaje_ingles") or 0) < 70:
        signals.append({"tone": "caution", "label": "Conviene reforzar evidencia de idioma"})

    if float(prediction.get("probability") or 0) >= 0.7:
        signals.append({"tone": "positive", "label": "Perfil con traccion competitiva"})
    elif prediction.get("priority_label") == "baja":
        signals.append({"tone": "caution", "label": "Ruta recomendable: fortalecer y volver a aplicar"})

    return signals[:5]


def build_next_steps(profile: Dict[str, Any], prediction: Dict[str, Any], mode: str) -> List[str]:
    next_steps = [
        "Revisa el checklist y completa primero los documentos con estado pendiente.",
        "Usa el chat para convertir tu diagnostico en una ruta de accion personalizada.",
    ]

    if prediction.get("priority_label") == "alta":
        next_steps.insert(0, "Tu perfil luce competitivo: prioriza cerrar expediente y fechas de convocatoria.")
    elif prediction.get("priority_label") == "media":
        next_steps.insert(0, "Tienes una base viable: fortalece documentos y narrativa antes de aplicar.")
    else:
        next_steps.insert(0, "Conviene fortalecer el perfil antes de una postulacion formal.")

    if profile.get("tipo_beca") == "internacional":
        next_steps.append("Verifica idioma, admision y presupuesto anual antes de avanzar con la convocatoria.")
    else:
        next_steps.append("Identifica universidades locales y costos reales para afinar tu plan de beca nacional.")

    if mode == "full":
        next_steps.append("Descarga el resumen de sesion para convertirlo en borrador de expediente.")

    return next_steps[:5]


def build_chat_suggestions(step_id: str | None, applicant: Dict[str, Any] | None, has_result: bool) -> List[str]:
    tipo_beca = (applicant or {}).get("tipo_beca")
    suggestions = [
        "Que documentos me faltan para postular?",
        "Como se evalua la necesidad economica?",
        "Explicame el proceso paso a paso.",
    ]

    if step_id == "academico":
        suggestions.insert(0, "Como puedo fortalecer mi perfil academico?")
    if tipo_beca == "internacional":
        suggestions.insert(0, "Que necesito para una beca internacional?")
    if has_result:
        suggestions.insert(0, "Interpretame mi resultado y dime mis proximos pasos.")

    deduped: List[str] = []
    for item in suggestions:
        if item not in deduped:
            deduped.append(item)
    return deduped[:4]


def build_bootstrap_payload() -> Dict[str, Any]:
    return {
        "brand": {
            "title": "Portal Ciudadano de Becas RD",
            "subtitle": "Orientacion dominicana para decidir, preparar y fortalecer una postulacion en una sola sesion.",
            "badge": "Asistente IA + ruta guiada",
        },
        "hero": {
            "headline": "Becas dominicanas con una experiencia pensada para quien postula, no para quien redacta el reglamento.",
            "body": (
                "Evalua tu caso, recorre una via rapida o una postulacion guiada completa, "
                "y conversa con un asistente que te ayuda a entender documentos, criterios y proximos pasos."
            ),
            "primaryCta": "Iniciar evaluacion rapida",
            "secondaryCta": "Abrir postulacion guiada",
        },
        "stats": [
            {"value": "16", "label": "provincias modeladas"},
            {"value": "2", "label": "rutas de navegacion"},
            {"value": "1", "label": "sesion continua"},
        ],
        "scholarshipTypes": [
            {
                "name": "Beca nacional",
                "description": "Cobertura parcial o total para programas en universidades de Republica Dominicana.",
            },
            {
                "name": "Beca internacional",
                "description": "Apoyo para estudios fuera del pais con foco en maestria y doctorado.",
            },
        ],
        "timeline": [
            {"step": "01", "title": "Diagnostica", "body": "Completa la via rapida o la postulacion guiada."},
            {"step": "02", "title": "Interpreta", "body": "Recibe prioridad, probabilidad y factores explicativos."},
            {"step": "03", "title": "Afina", "body": "Cierra documentos pendientes y fortalece el expediente."},
            {"step": "04", "title": "Consulta", "body": "Usa el chat para convertir dudas en acciones concretas."},
        ],
        "faq": [
            {
                "question": "Cuando debo postular?",
                "answer": "Las convocatorias suelen abrirse una o dos veces al ano. Debes revisar el calendario oficial.",
            },
            {
                "question": "Como se evalua la necesidad economica?",
                "answer": "Se revisa ingreso del hogar, dependientes y contexto territorial.",
            },
            {
                "question": "El asistente puede aprobar mi beca?",
                "answer": "No. El sistema orienta y explica, pero no reemplaza la decision oficial.",
            },
        ],
        "assistant": {
            "greeting": (
                "Hola. Soy tu asistente de orientacion para becas RD. "
                "Puedo explicarte requisitos, documentos, criterios y proximos pasos segun tu caso."
            )
        },
        "fields": FIELD_DEFINITIONS,
        "wizards": {
            "quick": {
                "label": "Evaluacion rapida",
                "summary": "Diagnostico orientativo de baja friccion con respuesta inmediata.",
                "steps": QUICK_WIZARD_STEPS,
            },
            "full": {
                "label": "Postulacion guiada",
                "summary": "Recorrido completo para construir un expediente orientativo en una sola interaccion.",
                "steps": FULL_WIZARD_STEPS,
            },
        },
    }
