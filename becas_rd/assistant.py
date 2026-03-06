from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .portal import get_portal_scholarships, get_scholarship_by_id


@dataclass
class RetrievalChunk:
    source: str
    text: str
    score: float
    kind: str = "doc"
    label: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScholarshipRecommendation:
    scholarship_id: str
    title: str
    score: float
    fit_label: str
    reasons: List[str]
    gaps: List[str]
    next_step: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scholarship_id": self.scholarship_id,
            "title": self.title,
            "score": round(self.score, 2),
            "fit_label": self.fit_label,
            "reasons": self.reasons,
            "gaps": self.gaps,
            "next_step": self.next_step,
        }


@dataclass
class AssistantAnswer:
    answer: str
    intent: str
    references: List[RetrievalChunk]
    recommendations: List[ScholarshipRecommendation]
    suggestions: List[str]
    provider: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "intent": self.intent,
            "references": [
                {
                    "source": item.source,
                    "label": item.label,
                    "kind": item.kind,
                    "score": round(item.score, 4),
                }
                for item in self.references
            ],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "suggestions": self.suggestions,
            "provider": self.provider,
        }


class ScholarshipAssistant:
    """Asistente de orientacion para becas con grounding local y generacion LLM."""

    def __init__(
        self,
        docs_paths: Sequence[str | Path],
        scholarships: Sequence[Dict[str, Any]] | None = None,
        llm_client: Any | None = None,
        model: str | None = None,
    ):
        self.docs_paths = [Path(p) for p in docs_paths]
        self.scholarships = list(scholarships or get_portal_scholarships())
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.llm_client = llm_client if llm_client is not None else self._build_llm_client()
        self.chunks: List[RetrievalChunk] = []
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            stop_words=None,
            lowercase=True,
            strip_accents="unicode",
            sublinear_tf=True,
        )
        self._fit_index()

    def _build_llm_client(self) -> Any | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            from openai import OpenAI
        except Exception:
            return None
        return OpenAI(api_key=api_key)

    def _read_chunks(self) -> List[RetrievalChunk]:
        items: List[RetrievalChunk] = []

        for path in self.docs_paths:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            items.extend(self._chunk_markdown(path.name, text))

        for scholarship in self.scholarships:
            scholarship_text = " ".join(
                [
                    scholarship["title"],
                    scholarship["description"],
                    f"Tipo: {scholarship['type']}. Nivel: {scholarship['level']}.",
                    f"Areas: {', '.join(scholarship.get('areas', []))}.",
                    f"Prioridades: {', '.join(scholarship.get('priorities', []))}.",
                    f"Requisitos: {' '.join(scholarship.get('requirements', []))}.",
                    f"Documentos: {' '.join(scholarship.get('documents', []))}.",
                ]
            )
            items.append(
                RetrievalChunk(
                    source="catalogo_becas_portal",
                    label=scholarship["title"],
                    text=scholarship_text,
                    score=0.0,
                    kind="scholarship",
                    metadata={"scholarship_id": scholarship["id"]},
                )
            )

        return items

    def _chunk_markdown(self, source: str, text: str) -> List[RetrievalChunk]:
        chunks: List[RetrievalChunk] = []
        current_section = "General"
        buffer: List[str] = []

        def flush() -> None:
            nonlocal buffer
            if not buffer:
                return
            block = " ".join(part.strip() for part in buffer if part.strip())
            if len(block) < 35:
                buffer = []
                return
            chunks.append(
                RetrievalChunk(
                    source=source,
                    label=current_section,
                    text=block,
                    score=0.0,
                    kind="doc",
                    metadata={"section": current_section},
                )
            )
            buffer = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                flush()
                continue
            if line.startswith("#"):
                flush()
                current_section = re.sub(r"^#+\s*", "", line).strip() or current_section
                continue
            buffer.append(line)

        flush()
        return chunks

    def _fit_index(self) -> None:
        self.chunks = self._read_chunks()
        if not self.chunks:
            self._matrix = None
            return
        corpus = [chunk.text for chunk in self.chunks]
        self._matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(
        self,
        question: str,
        top_k: int = 4,
        min_score: float = 0.05,
        kinds: Sequence[str] | None = None,
    ) -> List[RetrievalChunk]:
        if self._matrix is None or not self.chunks:
            return []
        q_vec = self.vectorizer.transform([question])
        scores = (self._matrix @ q_vec.T).toarray().ravel()
        if not np.any(scores):
            return []
        order = np.argsort(scores)[::-1]
        out: List[RetrievalChunk] = []
        allowed = set(kinds or [])

        for idx in order:
            score = float(scores[idx])
            if score < min_score:
                continue
            chunk = self.chunks[idx]
            if allowed and chunk.kind not in allowed:
                continue
            out.append(
                RetrievalChunk(
                    source=chunk.source,
                    label=chunk.label,
                    text=chunk.text,
                    score=score,
                    kind=chunk.kind,
                    metadata=chunk.metadata,
                )
            )
            if len(out) >= top_k:
                break
        return out

    def detect_intent(self, question: str, selected_convocation_id: str | None = None) -> str:
        q = _normalize_text(question)

        if any(word in q for word in ["recomienda", "recomiendas", "cual beca", "que beca", "encaja", "encajan"]):
            return "recommendation"
        if any(word in q for word in ["documento", "documentos", "requisito", "requisitos", "papeles"]):
            return "documents"
        if any(word in q for word in ["paso", "pasos", "proceso", "postular", "aplicar"]):
            return "process"
        if any(word in q for word in ["elegible", "elegibilidad", "probabilidad", "califico", "califica"]):
            return "eligibility"
        if selected_convocation_id or any(word in q for word in ["convocatoria", "beca", "maestria", "doctorado"]):
            return "catalog"
        return "general"

    def recommend_scholarships(
        self,
        question: str,
        applicant_context: Dict[str, Any] | None = None,
        prediction: Dict[str, Any] | None = None,
        selected_convocation_id: str | None = None,
        top_k: int = 3,
    ) -> List[ScholarshipRecommendation]:
        profile = applicant_context or {}
        desired_type = profile.get("tipo_beca")
        desired_level = profile.get("nivel_estudio")
        average = _to_float(profile.get("promedio_academico"))
        english = _to_float(profile.get("puntaje_ingles"))
        document_score = _to_float(profile.get("score_documental"))
        interest_terms = _extract_interest_terms(question, profile)
        priority_label = (prediction or {}).get("priority_label")

        recommendations: List[ScholarshipRecommendation] = []

        for scholarship in self.scholarships:
            score = 0.0
            reasons: List[str] = []
            gaps: List[str] = []
            eligibility = scholarship.get("eligibility", {})

            if selected_convocation_id and scholarship["id"] == selected_convocation_id:
                score += 18
                reasons.append("Ya estas explorando esta convocatoria en el portal.")

            if desired_type:
                if scholarship["type"] == desired_type:
                    score += 24
                    reasons.append(f"Coincide con tu interes en beca {desired_type}.")
                else:
                    score -= 10
                    gaps.append(f"Tu tipo de beca actual apunta a {desired_type} y esta oferta es {scholarship['type']}.")

            if desired_level:
                if scholarship["level"] == desired_level:
                    score += 24
                    reasons.append(f"Corresponde a tu nivel de estudio objetivo: {desired_level}.")
                else:
                    score -= 8
                    gaps.append(f"Tu nivel objetivo actual es {desired_level} y esta beca es para {scholarship['level']}.")

            area_matches = sorted(
                set(interest_terms)
                & {term for term in scholarship.get("areas", []) + scholarship.get("keywords", [])}
            )
            if area_matches:
                score += 18
                reasons.append(f"Tu interes academico se alinea con {', '.join(area_matches[:3])}.")

            if average is not None:
                min_average = _to_float(eligibility.get("min_average"))
                if min_average is not None and average >= min_average:
                    score += 14
                    reasons.append(f"Tu promedio actual ({average:.1f}) supera el recomendado.")
                elif min_average is not None:
                    gaps.append(f"El promedio recomendado ronda {min_average:.0f} y tu perfil actual queda por debajo.")

            if document_score is not None:
                min_document_score = _to_float(eligibility.get("min_document_score"))
                if min_document_score is not None and document_score >= min_document_score:
                    score += 10
                    reasons.append("Tu nivel documental ya es razonable para esta oferta.")
                elif min_document_score is not None:
                    gaps.append("Conviene reforzar tu expediente documental antes de priorizar esta beca.")

            min_english = _to_float(eligibility.get("min_english"))
            if min_english is not None:
                if english is not None and english >= min_english:
                    score += 10
                    reasons.append("Tu nivel de idioma luce competitivo para esta convocatoria internacional.")
                elif english is not None:
                    gaps.append(f"Necesitas mejorar el nivel de ingles hacia una referencia cercana a {min_english:.0f}.")
                else:
                    gaps.append("Aun no hay evidencia suficiente de idioma para esta convocatoria internacional.")

            if eligibility.get("requires_international_admission") and profile.get("carta_admision") != 1:
                gaps.append("Todavia te faltaria carta de admision o preadmision para volverla prioritaria.")

            if priority_label == "alta":
                score += 5
            elif priority_label == "media":
                score += 2
            elif priority_label == "baja":
                gaps.append("Tu lectura orientativa actual sugiere fortalecer el perfil antes de aplicar.")

            score = max(score, 0.0)
            fit_label = _fit_label_for_score(score, gaps)
            next_step = _next_step_for_recommendation(fit_label, scholarship, gaps)

            recommendations.append(
                ScholarshipRecommendation(
                    scholarship_id=scholarship["id"],
                    title=scholarship["title"],
                    score=score,
                    fit_label=fit_label,
                    reasons=reasons[:3] or ["Tiene cierta afinidad con tu consulta, pero faltan mas datos para afinar."],
                    gaps=gaps[:3],
                    next_step=next_step,
                )
            )

        ranked = sorted(recommendations, key=lambda item: (-item.score, item.title))
        return ranked[:top_k]

    def answer(
        self,
        question: str,
        applicant_context: Dict[str, Any] | None = None,
        prediction: Dict[str, Any] | None = None,
        history: Sequence[Dict[str, Any]] | None = None,
        step_context: Dict[str, Any] | None = None,
        selected_convocation_id: str | None = None,
    ) -> AssistantAnswer:
        intent = self.detect_intent(question, selected_convocation_id=selected_convocation_id)
        recommendations = self.recommend_scholarships(
            question=question,
            applicant_context=applicant_context,
            prediction=prediction,
            selected_convocation_id=selected_convocation_id,
            top_k=3,
        )
        retrieval_query = self._build_retrieval_query(question, applicant_context, recommendations, selected_convocation_id)
        references = self.retrieve(retrieval_query, top_k=4, min_score=0.04)
        suggestions = self.build_suggestions(intent, applicant_context, recommendations, bool(prediction))

        provider = "local_fallback"
        answer = self._build_fallback_answer(
            question=question,
            intent=intent,
            applicant_context=applicant_context,
            prediction=prediction,
            recommendations=recommendations,
            references=references,
            selected_convocation_id=selected_convocation_id,
        )

        if self.llm_client is not None:
            try:
                answer = self._generate_with_llm(
                    question=question,
                    applicant_context=applicant_context,
                    prediction=prediction,
                    history=history,
                    step_context=step_context,
                    recommendations=recommendations,
                    references=references,
                    selected_convocation_id=selected_convocation_id,
                )
                provider = "openai"
            except Exception:
                provider = "local_fallback"

        return AssistantAnswer(
            answer=answer,
            intent=intent,
            references=references[:3],
            recommendations=recommendations[:3],
            suggestions=suggestions,
            provider=provider,
        )

    def respond(
        self,
        question: str,
        applicant_context: Dict[str, Any] | None = None,
        prediction: Dict[str, Any] | None = None,
        history: Sequence[Dict[str, Any]] | None = None,
        step_context: Dict[str, Any] | None = None,
        selected_convocation_id: str | None = None,
    ) -> str:
        return self.answer(
            question=question,
            applicant_context=applicant_context,
            prediction=prediction,
            history=history,
            step_context=step_context,
            selected_convocation_id=selected_convocation_id,
        ).answer

    def build_suggestions(
        self,
        intent: str,
        applicant_context: Dict[str, Any] | None,
        recommendations: Sequence[ScholarshipRecommendation],
        has_prediction: bool,
    ) -> List[str]:
        tipo_beca = (applicant_context or {}).get("tipo_beca")
        suggestions = [
            "Que documentos me faltan para la beca que mejor encaja conmigo?",
            "Que becas del portal encajan con mi perfil?",
            "Explicame el proceso paso a paso.",
        ]

        if intent in {"recommendation", "catalog"}:
            suggestions.insert(0, "Comparame las dos becas que mejor encajan conmigo.")
        if tipo_beca == "internacional":
            suggestions.insert(0, "Que necesito reforzar para una beca internacional?")
        if has_prediction:
            suggestions.insert(0, "Interpretame mi resultado y dime cual beca deberia priorizar.")
        if recommendations:
            suggestions.insert(0, f"Que tan preparada estoy para {recommendations[0].title}?")

        deduped: List[str] = []
        for item in suggestions:
            if item not in deduped:
                deduped.append(item)
        return deduped[:5]

    def _build_retrieval_query(
        self,
        question: str,
        applicant_context: Dict[str, Any] | None,
        recommendations: Sequence[ScholarshipRecommendation],
        selected_convocation_id: str | None,
    ) -> str:
        profile = applicant_context or {}
        selected = get_scholarship_by_id(selected_convocation_id)
        parts = [question]

        if profile.get("tipo_beca"):
            parts.append(str(profile["tipo_beca"]))
        if profile.get("nivel_estudio"):
            parts.append(str(profile["nivel_estudio"]))
        if profile.get("programa_interes"):
            parts.append(str(profile["programa_interes"]))
        if selected:
            parts.append(selected["title"])
        elif recommendations:
            parts.append(recommendations[0].title)

        return " ".join(parts)

    def _generate_with_llm(
        self,
        question: str,
        applicant_context: Dict[str, Any] | None,
        prediction: Dict[str, Any] | None,
        history: Sequence[Dict[str, Any]] | None,
        step_context: Dict[str, Any] | None,
        recommendations: Sequence[ScholarshipRecommendation],
        references: Sequence[RetrievalChunk],
        selected_convocation_id: str | None,
    ) -> str:
        selected = get_scholarship_by_id(selected_convocation_id)
        prompt_parts = [
            "Consulta actual:",
            question,
            "",
            "Perfil del ciudadano:",
            _summarize_profile(applicant_context),
            "",
            "Resultado orientativo:",
            _summarize_prediction(prediction),
            "",
            "Paso actual del flujo:",
            _summarize_step_context(step_context),
            "",
            "Convocatoria seleccionada actualmente:",
            selected["title"] if selected else "No hay convocatoria seleccionada.",
            "",
            "Becas candidatas del portal:",
            _summarize_recommendations(recommendations),
            "",
            "Evidencia documental disponible:",
            _summarize_references(references),
            "",
            "Instrucciones de salida:",
            (
                "Responde en espanol, con tono mixto: claro, profesional y ligeramente empatico. "
                "No inventes becas ni requisitos fuera de la informacion provista. "
                "Si faltan datos, dilo y pide solo el dato minimo necesario. "
                "Si hay recomendaciones, menciona maximo 3 y explica por que encajan. "
                "Cierra con un siguiente paso concreto."
            ),
        ]

        messages: List[Dict[str, Any]] = []
        for item in (history or [])[-6:]:
            role = str(item.get("role") or "").strip()
            content = str(item.get("body") or item.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content[:2000]})

        messages.append({"role": "user", "content": "\n".join(prompt_parts)})

        response = self.llm_client.responses.create(
            model=self.model,
            instructions=(
                "Eres un orientador de becas del portal Beca tu Futuro. "
                "Solo debes recomendar becas del portal provistas en el contexto. "
                "No prometas adjudicacion oficial. No inventes requisitos ni fechas."
            ),
            input=messages,
        )

        answer = getattr(response, "output_text", "") or self._extract_output_text(response)
        if not answer or not answer.strip():
            raise ValueError("El proveedor LLM no devolvio texto util.")
        return answer.strip()

    def _extract_output_text(self, response: Any) -> str:
        output_items = getattr(response, "output", None) or []
        texts: List[str] = []
        for item in output_items:
            content_items = getattr(item, "content", None) or []
            for content in content_items:
                text = getattr(content, "text", None)
                if text:
                    texts.append(str(text))
        return "\n".join(texts).strip()

    def _build_fallback_answer(
        self,
        question: str,
        intent: str,
        applicant_context: Dict[str, Any] | None,
        prediction: Dict[str, Any] | None,
        recommendations: Sequence[ScholarshipRecommendation],
        references: Sequence[RetrievalChunk],
        selected_convocation_id: str | None,
    ) -> str:
        selected = get_scholarship_by_id(selected_convocation_id)

        if intent in {"recommendation", "catalog"}:
            if recommendations:
                lead = recommendations[0]
                alternatives = ", ".join(item.title for item in recommendations[1:3])
                alt_text = f" Otras opciones viables son {alternatives}." if alternatives else ""
                gap_text = f" Lo que deberias reforzar primero: {lead.gaps[0]}" if lead.gaps else ""
                reason_sentence = " ".join(reason.rstrip(".") for reason in lead.reasons[:2]).strip()
                return (
                    f"Por lo que compartes, la beca del portal que mejor encaja ahora mismo es {lead.title}. "
                    f"Encaja porque {reason_sentence.lower()}"
                    + "."
                    + alt_text
                    + gap_text
                    + f" Siguiente paso recomendado: {lead.next_step}"
                )
            return (
                "Todavia no tengo suficientes datos para recomendar una beca del portal con precision. "
                "Dime tu nivel de estudio, si buscas beca nacional o internacional y tu area de interes."
            )

        if intent == "documents":
            if selected:
                docs = ", ".join(selected.get("documents", [])[:4])
                return (
                    f"Para {selected['title']} deberias priorizar estos documentos: {docs}. "
                    "Si quieres, tambien te digo cuales te faltan segun tu perfil actual."
                )
            if recommendations:
                lead = recommendations[0]
                return (
                    f"Para la beca que mejor te encaja ahora mismo, {lead.title}, "
                    f"deberias revisar primero: {lead.next_step}"
                )

        if intent == "eligibility" and prediction is not None:
            priority = prediction.get("priority_label", "media")
            explanation = prediction.get("explanation", "Tu perfil tiene una lectura orientativa disponible.")
            if recommendations:
                return (
                    f"Tu lectura orientativa actual es de prioridad {priority}. {explanation} "
                    f"Con ese panorama, yo priorizaria {recommendations[0].title}. {recommendations[0].next_step}"
                )
            return (
                f"Tu lectura orientativa actual es de prioridad {priority}. {explanation} "
                "Usa esta referencia para decidir si conviene aplicar ya o reforzar el perfil."
            )

        if intent == "process":
            reference_text = references[0].text if references else ""
            trimmed = _trim_sentence(reference_text, 220)
            return (
                "La ruta mas segura es: revisar convocatoria, confirmar requisitos, organizar documentos y luego pasar a la postulacion guiada. "
                + (trimmed + " " if trimmed else "")
                + "Si quieres, te lo convierto en un checklist segun tu perfil."
            )

        if references:
            snippet = _trim_sentence(references[0].text, 260)
            return (
                f"Esto es lo mas relevante que encontre para tu consulta: {snippet} "
                "Si quieres, lo reformulo como recomendacion de becas, requisitos o siguientes pasos."
            )

        return (
            "Puedo ayudarte mejor si me dices tu nivel de estudio, si buscas beca nacional o internacional "
            "y el area que quieres estudiar. Con eso te recomiendo opciones del portal y te digo por que encajan."
        )


def _default_docs() -> List[Path]:
    return [
        Path("docs/reglamento_becas_rd.md"),
        Path("docs/faq_becas_rd.md"),
    ]


def chat_assistant(
    question: str,
    applicant_context: Dict[str, Any] | None = None,
    assistant: ScholarshipAssistant | None = None,
    artifacts_path: str | Path = "artifacts/model_bundle.joblib",
) -> str:
    """Interfaz funcional para conversar con el asistente."""
    if assistant is None:
        assistant = ScholarshipAssistant(_default_docs())

    prediction = None
    if applicant_context is not None:
        try:
            from .modeling import predict_eligibility

            prediction = predict_eligibility(applicant=applicant_context, artifacts_path=artifacts_path)
        except Exception:
            prediction = None

    return assistant.respond(question=question, applicant_context=applicant_context, prediction=prediction)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _trim_sentence(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_interest_terms(question: str, applicant_context: Dict[str, Any] | None) -> List[str]:
    profile = applicant_context or {}
    raw = " ".join(
        [
            question,
            str(profile.get("programa_interes") or ""),
            str(profile.get("objetivo_profesional") or ""),
            str(profile.get("universidad_destino") or ""),
        ]
    )
    tokens = re.findall(r"[a-záéíóúñ]{4,}", _normalize_text(raw))
    return list(dict.fromkeys(tokens))


def _fit_label_for_score(score: float, gaps: Sequence[str]) -> str:
    if score >= 58 and len(gaps) <= 1:
        return "alta afinidad"
    if score >= 34:
        return "afinidad media"
    return "todavia no recomendable"


def _next_step_for_recommendation(fit_label: str, scholarship: Dict[str, Any], gaps: Sequence[str]) -> str:
    if fit_label == "alta afinidad":
        return f"Abre la postulacion guiada de {scholarship['title']} y cierra documentos criticos."
    if gaps:
        return gaps[0]
    return f"Revisa requisitos y documentos de {scholarship['title']} antes de postular."


def _summarize_profile(applicant_context: Dict[str, Any] | None) -> str:
    profile = applicant_context or {}
    meaningful = {key: value for key, value in profile.items() if value not in (None, "", [])}
    if not meaningful:
        return "Aun no hay suficientes datos del ciudadano."
    parts = []
    ordered_fields = [
        "tipo_beca",
        "nivel_estudio",
        "programa_interes",
        "universidad_destino",
        "promedio_academico",
        "puntaje_ingles",
        "score_documental",
        "provincia",
    ]
    for field_name in ordered_fields:
        if field_name in meaningful:
            parts.append(f"{field_name}: {meaningful[field_name]}")
    return "; ".join(parts) if parts else "Perfil parcial disponible."


def _summarize_prediction(prediction: Dict[str, Any] | None) -> str:
    if not prediction:
        return "No hay resultado orientativo disponible."
    return (
        f"Prioridad {prediction.get('priority_label', 'media')}; "
        f"probabilidad {round(float(prediction.get('probability', 0.0)) * 100)}%; "
        f"{prediction.get('explanation', '')}"
    )


def _summarize_step_context(step_context: Dict[str, Any] | None) -> str:
    if not step_context:
        return "Sin contexto adicional del flujo."
    return (
        f"Modo {step_context.get('mode', 'quick')}; "
        f"paso {step_context.get('step_id', 'general')}; "
        f"titulo {step_context.get('step_title', 'sin titulo')}."
    )


def _summarize_recommendations(recommendations: Sequence[ScholarshipRecommendation]) -> str:
    if not recommendations:
        return "No hay recomendaciones de becas suficientemente fuertes."
    lines = []
    for item in recommendations[:3]:
        reason = item.reasons[0] if item.reasons else "Afinidad parcial."
        gap = item.gaps[0] if item.gaps else "Sin brechas criticas detectadas."
        lines.append(
            f"- {item.title} ({item.fit_label}, score {round(item.score, 1)}): {reason} Brecha principal: {gap}"
        )
    return "\n".join(lines)


def _summarize_references(references: Sequence[RetrievalChunk]) -> str:
    if not references:
        return "No se recupero evidencia documental fuerte."
    lines = []
    for item in references[:3]:
        label = item.label or item.source
        lines.append(f"- [{item.source} / {label}] {_trim_sentence(item.text, 220)}")
    return "\n".join(lines)
