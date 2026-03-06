from __future__ import annotations

from copy import deepcopy
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
        "placeholder": "Ej. ingenieria, medicina, educacion, datos, arquitectura...",
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
        "label": "Ingreso mensual aproximado del hogar (DOP)",
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
        "label": "Que tan listo esta tu expediente hoy?",
        "type": "number",
        "required": True,
        "min": 0,
        "max": 100,
        "step": 0.1,
        "hint": "Piensa en cartas, record, identificacion y evidencias ya reunidas.",
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
        "label": "Puntaje o nivel estimado de ingles",
        "type": "number",
        "required": True,
        "min": 0,
        "max": 100,
        "step": 0.1,
        "showWhen": {"field": "tipo_beca", "equals": "internacional"},
        "hint": "Si aun no tienes examen, usa una estimacion realista de tu nivel actual.",
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
        "eyebrow": "Evaluacion rapida",
        "title": "Que quieres estudiar y por donde quieres empezar?",
        "description": "Definimos tu ruta academica para darte una orientacion inicial sin rodeos.",
        "fields": ["tipo_beca", "nivel_estudio", "programa_interes"],
    },
    {
        "id": "perfil",
        "eyebrow": "Perfil personal",
        "title": "Cuentanos tu contexto",
        "description": "Necesitamos una vista basica de tu realidad para orientar mejor la recomendacion.",
        "fields": ["edad", "genero", "provincia", "zona"],
    },
    {
        "id": "academico",
        "eyebrow": "Base academica",
        "title": "Como va tu preparacion hasta ahora?",
        "description": "Aqui estimamos fortaleza academica, avance documental y participacion extracurricular.",
        "fields": ["promedio_academico", "score_documental", "horas_voluntariado", "puntaje_ingles"],
    },
    {
        "id": "contexto",
        "eyebrow": "Entorno social",
        "title": "Como es tu realidad economica y familiar?",
        "description": "Este bloque ayuda a entender necesidad economica y barreras de acceso.",
        "fields": [
            "ingreso_hogar_mensual_dop",
            "miembros_hogar",
            "primera_generacion_universitaria",
            "discapacidad",
        ],
    },
    {
        "id": "costos",
        "eyebrow": "Cierre",
        "title": "Cerremos con el costo del programa",
        "description": "Con este dato calculamos tu resultado orientativo y te proponemos proximos pasos.",
        "fields": ["costo_anual_programa_dop"],
    },
]

FULL_WIZARD_STEPS: List[Dict[str, Any]] = [
    {
        "id": "identidad",
        "eyebrow": "Postulacion guiada",
        "title": "Empecemos con tus datos base",
        "description": "Abrimos una ficha clara para acompanarte durante toda la preparacion.",
        "fields": ["nombre_completo", "correo", "telefono", "tipo_beca", "nivel_estudio"],
    },
    {
        "id": "trayectoria",
        "eyebrow": "Proyeccion",
        "title": "A donde quieres llegar?",
        "description": "Define tu meta academica y el impacto profesional que quieres construir.",
        "fields": ["programa_interes", "universidad_destino", "objetivo_profesional"],
    },
    {
        "id": "territorio",
        "eyebrow": "Contexto",
        "title": "Tu realidad hoy",
        "description": "Recogemos informacion personal y territorial para orientar tu ruta con mas precision.",
        "fields": ["edad", "genero", "provincia", "zona", "ingreso_hogar_mensual_dop", "miembros_hogar"],
    },
    {
        "id": "academico",
        "eyebrow": "Preparacion",
        "title": "Fortaleza academica y avance del expediente",
        "description": "Profundizamos en tu desempeno, evidencia disponible y experiencia complementaria.",
        "fields": ["promedio_academico", "score_documental", "horas_voluntariado", "puntaje_ingles"],
    },
    {
        "id": "inclusion",
        "eyebrow": "Acceso",
        "title": "Barreras, inclusion y viabilidad economica",
        "description": "Esto nos ayuda a leer mejor tus condiciones de acceso y el costo total del programa.",
        "fields": ["primera_generacion_universitaria", "discapacidad", "costo_anual_programa_dop"],
    },
    {
        "id": "documentos",
        "eyebrow": "Documentos",
        "title": "Que tienes listo y que te falta?",
        "description": "Cerramos la sesion armando un mapa claro de tu expediente documental.",
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

PORTAL_SCHOLARSHIP_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "conv-nac-grado-stem-2026",
        "title": "Becas nacionales de grado en STEM y educacion",
        "type": "nacional",
        "level": "grado",
        "areas": ["ingenieria", "tecnologia", "matematicas", "ciencias", "educacion"],
        "keywords": ["stem", "ingenieria", "ciencias", "docencia", "tecnologia", "educacion"],
        "modality": "presencial",
        "coverage": "Republica Dominicana",
        "country": "Republica Dominicana",
        "description": (
            "Programas de grado en universidades dominicanas para perfiles con vocacion academica, "
            "interes en STEM y disposicion para impacto social o educativo."
        ),
        "requirements": [
            "Promedio academico recomendado de 80 o mas.",
            "Expediente documental basico completo.",
            "Interes claro en areas STEM o educacion.",
        ],
        "documents": [
            "Record academico oficial",
            "Cedula vigente",
            "Carta de motivacion",
            "Evidencia socioeconomica del hogar",
        ],
        "priorities": [
            "Carreras STEM",
            "Formacion docente",
            "Impacto comunitario",
        ],
        "status": "Abierta",
        "deadline": "15 de mayo de 2026",
        "defaultMode": "quick",
        "prefill": {"tipo_beca": "nacional", "nivel_estudio": "grado"},
        "eligibility": {
            "min_average": 80.0,
            "min_document_score": 55.0,
            "min_english": None,
            "requires_international_admission": False,
        },
    },
    {
        "id": "conv-nac-maestria-gestion-publica-2026",
        "title": "Becas nacionales de maestria en gestion publica, educacion y salud",
        "type": "nacional",
        "level": "maestria",
        "areas": ["gestion publica", "educacion", "salud publica", "politicas publicas"],
        "keywords": ["gestion", "politicas", "educacion", "salud", "servicio publico"],
        "modality": "mixta",
        "coverage": "Republica Dominicana",
        "country": "Republica Dominicana",
        "description": (
            "Oferta de maestrias nacionales para fortalecer liderazgos profesionales en gestion publica, "
            "educacion y salud, con foco en impacto territorial."
        ),
        "requirements": [
            "Promedio academico recomendado de 82 o mas.",
            "Narrativa profesional alineada con servicio publico.",
            "Documentacion personal y academica consistente.",
        ],
        "documents": [
            "Record academico oficial",
            "Carta de motivacion",
            "Plan de estudios o propuesta academica",
            "Evidencia socioeconomica",
        ],
        "priorities": [
            "Servicio publico",
            "Transformacion educativa",
            "Salud territorial",
        ],
        "status": "Abierta",
        "deadline": "20 de mayo de 2026",
        "defaultMode": "full",
        "prefill": {"tipo_beca": "nacional", "nivel_estudio": "maestria"},
        "eligibility": {
            "min_average": 82.0,
            "min_document_score": 60.0,
            "min_english": None,
            "requires_international_admission": False,
        },
    },
    {
        "id": "conv-int-maestria-stem-salud-2026",
        "title": "Maestrias internacionales en STEM y salud publica",
        "type": "internacional",
        "level": "maestria",
        "areas": ["ingenieria", "datos", "tecnologia", "salud publica", "innovacion"],
        "keywords": ["maestria", "internacional", "stem", "salud", "datos", "innovacion"],
        "modality": "presencial",
        "coverage": "Internacional",
        "country": "Multipaís",
        "description": (
            "Convocatoria internacional priorizada para perfiles con base academica solida en STEM, analitica, "
            "innovacion o salud publica y con potencial de retorno e impacto nacional."
        ),
        "requirements": [
            "Promedio academico recomendado de 85 o mas.",
            "Puntaje o nivel de ingles recomendado de 72 o mas.",
            "Plan de estudios y narrativa internacional convincentes.",
        ],
        "documents": [
            "Carta de admision o preadmision",
            "Evidencia de idioma",
            "Presupuesto anual estimado",
            "Carta de motivacion",
        ],
        "priorities": [
            "Innovacion",
            "Transformacion digital",
            "Salud publica",
        ],
        "status": "Abierta",
        "deadline": "22 de mayo de 2026",
        "defaultMode": "full",
        "prefill": {"tipo_beca": "internacional", "nivel_estudio": "maestria"},
        "eligibility": {
            "min_average": 85.0,
            "min_document_score": 65.0,
            "min_english": 72.0,
            "requires_international_admission": True,
        },
    },
    {
        "id": "conv-int-doctorado-impacto-2026",
        "title": "Doctorados internacionales de alto impacto",
        "type": "internacional",
        "level": "doctorado",
        "areas": ["investigacion", "ingenieria", "salud", "educacion", "ciencias sociales"],
        "keywords": ["doctorado", "investigacion", "publicaciones", "academia", "impacto"],
        "modality": "presencial",
        "coverage": "Internacional",
        "country": "Multipaís",
        "description": (
            "Doctorados internacionales orientados a investigacion aplicada y formacion avanzada para perfiles "
            "con trayectoria academica fuerte, potencial de liderazgo y alto compromiso de retorno."
        ),
        "requirements": [
            "Promedio academico recomendado de 88 o mas.",
            "Puntaje o nivel de ingles recomendado de 78 o mas.",
            "Perfil academico y documental robusto.",
        ],
        "documents": [
            "Carta de admision o preadmision",
            "Evidencia de idioma",
            "Plan de investigacion",
            "Presupuesto anual estimado",
        ],
        "priorities": [
            "Investigacion aplicada",
            "Innovacion cientifica",
            "Impacto nacional",
        ],
        "status": "Proxima a cerrar",
        "deadline": "03 de junio de 2026",
        "defaultMode": "full",
        "prefill": {"tipo_beca": "internacional", "nivel_estudio": "doctorado"},
        "eligibility": {
            "min_average": 88.0,
            "min_document_score": 72.0,
            "min_english": 78.0,
            "requires_international_admission": True,
        },
    },
]


def get_portal_scholarships() -> List[Dict[str, Any]]:
    return deepcopy(PORTAL_SCHOLARSHIP_CATALOG)


def get_scholarship_by_id(scholarship_id: str | None) -> Dict[str, Any] | None:
    if not scholarship_id:
        return None
    for scholarship in PORTAL_SCHOLARSHIP_CATALOG:
        if scholarship["id"] == scholarship_id:
            return deepcopy(scholarship)
    return None


def build_convocation_cards() -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for scholarship in PORTAL_SCHOLARSHIP_CATALOG:
        cards.append(
            {
                "id": scholarship["id"],
                "name": scholarship["title"],
                "description": scholarship["description"],
                "type": scholarship["type"],
                "level": scholarship["level"],
                "deadline": scholarship["deadline"],
                "status": scholarship["status"],
                "defaultMode": scholarship["defaultMode"],
                "prefill": scholarship["prefill"],
            }
        )
    return cards


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
        "Que becas del portal encajan con mi perfil?",
        "Que documentos me faltan para postular?",
        "Explicame el proceso paso a paso.",
        "Como se evalua mi perfil?",
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
    scholarships = get_portal_scholarships()
    featured = scholarships[2]
    return {
        "brand": {
            "title": "Beca tu Futuro",
            "subtitle": "Una plataforma que concentra oportunidades, orientacion y herramientas de preparacion para becas dominicanas.",
            "badge": "Portal oficial de becas",
        },
        "govBanner": {
            "text": "Esta es una web oficial del Gobierno de la Republica Dominicana.",
            "helper": "Asi es como puedes saberlo",
        },
        "header": {
            "nav": [
                {"label": "Inicio", "href": "#inicio"},
                {"label": "Convocatorias", "href": "#convocatorias"},
                {"label": "Orientacion IA", "href": "#orientacion"},
                {"label": "Postulacion", "href": "#herramientas"},
            ],
            "primaryCta": "Ver convocatorias",
            "secondaryCta": "Iniciar orientacion",
        },
        "hero": {
            "status": "Ya esta disponible",
            "headline": featured["title"],
            "body": (
                "Explora oportunidades de becas, revisa requisitos clave y recibe orientacion inteligente basada en tu perfil y tus metas academicas."
            ),
            "deadlineLabel": "Aplica hasta el:",
            "deadline": featured["deadline"],
            "primaryCta": "Ver convocatoria",
            "secondaryCta": "Abrir orientacion",
        },
        "featuredConvocation": {
            "id": featured["id"],
            "title": featured["title"],
            "deadline": featured["deadline"],
            "type": featured["type"],
            "level": featured["level"],
            "summary": featured["description"],
            "defaultMode": featured["defaultMode"],
            "prefill": featured["prefill"],
        },
        "stats": [
            {
                "value": "1 portal",
                "label": "todo en un solo lugar",
                "detail": "Consulta convocatorias, orientate y organiza tu expediente en la misma plataforma.",
            },
            {
                "value": "2 rutas",
                "label": "rapida o guiada",
                "detail": "Elige entre una lectura breve de tu perfil o una postulacion paso a paso.",
            },
            {
                "value": "IA + datos",
                "label": "acompanamiento orientativo",
                "detail": "El asistente te explica requisitos, documentos y siguientes pasos con base en el proyecto.",
            },
        ],
        "convocationFilters": [
            {"id": "all", "label": "Todas"},
            {"id": "nacional", "label": "Nacionales"},
            {"id": "internacional", "label": "Internacionales"},
            {"id": "grado", "label": "Grado"},
            {"id": "maestria", "label": "Maestria"},
            {"id": "doctorado", "label": "Doctorado"},
        ],
        "convocations": build_convocation_cards(),
        "videoSection": {
            "titleLines": [
                "Dale a play y conoce",
                "todas las opciones que",
                "Beca tu Futuro trae para ti",
            ],
            "button": "Ver video explicativo",
            "url": "https://www.youtube.com/watch?v=BoCf3tIuzy4",
        },
        "tools": [
            {
                "id": "assistant",
                "title": "Asistente de orientacion",
                "description": "Haz preguntas, recibe becas recomendadas para tu perfil y entiende por que encajan contigo.",
                "button": "Abrir asistente",
            },
            {
                "id": "quick",
                "title": "Evaluacion rapida",
                "description": "Recibe una lectura orientativa de tu perfil en pocos pasos.",
                "button": "Iniciar evaluacion",
            },
            {
                "id": "full",
                "title": "Postulacion guiada",
                "description": "Organiza un expediente mas completo y prepara mejor tu aplicacion.",
                "button": "Abrir postulacion",
            },
        ],
        "timeline": [
            {"step": "01", "title": "Explora oportunidades", "body": "Revisa convocatorias y decide cual se ajusta mejor a tu meta academica."},
            {"step": "02", "title": "Orientate", "body": "Usa el asistente para entender requisitos, documentos y prioridades."},
            {"step": "03", "title": "Prepara tu perfil", "body": "Activa una evaluacion rapida o una postulacion guiada segun tu avance."},
            {"step": "04", "title": "Fortalece tu expediente", "body": "Recibe una lista clara de proximos pasos antes de aplicar."},
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
            "entryTitle": "Haz tus preguntas y recibe orientacion inteligente basada en tu perfil antes de empezar a llenar formularios.",
            "entryBody": (
                "El asistente te ayuda a entender convocatorias, recomendar becas del portal, revisar documentos y definir la ruta recomendada segun tu caso."
            ),
            "entryPrompts": [
                "No se por donde empezar. Que me recomiendas?",
                "Que becas del portal encajan con mi perfil?",
                "Quiero una beca internacional. Que necesito primero?",
                "Que documentos debo reunir antes de aplicar?",
            ],
            "capabilities": [
                "Te recomienda becas del portal segun tu nivel, interes y preparacion actual.",
                "Te ayuda a interpretar convocatorias, requisitos y documentos en lenguaje simple.",
                "Traduce tu resultado orientativo en acciones concretas y siguientes pasos.",
            ],
            "greeting": (
                "Hola. Soy tu asistente de orientacion para becas. "
                "Puedo ayudarte a entender convocatorias, recomendar becas del portal para tu perfil, revisar documentos y decirte la mejor ruta para empezar."
            ),
        },
        "footer": {
            "helpLinks": ["Terminos de uso", "Politica de privacidad", "Preguntas frecuentes"],
            "infoTitle": "Informacion",
            "infoBody": "Ministerio de Educacion Superior, Ciencia y Tecnologia. Republica Dominicana.",
            "contactTitle": "Contactanos",
            "contactItems": ["Tel: (809) 731 1100", "Fax: (809) 731-1101", "info@mescyt.gob.do"],
            "addressTitle": "Buscanos",
            "addressBody": "Av. Maximo Gomez No. 31, esq. Pedro Henriquez Urena, Santo Domingo, Republica Dominicana.",
            "social": ["Facebook", "Youtube", "Twitter", "Instagram"],
            "copyright": "© 2024 Todos los Derechos Reservados.",
        },
        "fields": FIELD_DEFINITIONS,
        "wizards": {
            "quick": {
                "label": "Evaluacion rapida",
                "summary": "Ruta breve para obtener una lectura inicial de tu perfil.",
                "steps": QUICK_WIZARD_STEPS,
            },
            "full": {
                "label": "Postulacion guiada",
                "summary": "Ruta completa para organizar mejor tu caso y tu expediente.",
                "steps": FULL_WIZARD_STEPS,
            },
        },
    }
