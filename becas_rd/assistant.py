from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass
class RetrievalChunk:
    source: str
    text: str
    score: float


class ScholarshipAssistant:
    """Asistente de orientacion para becas usando RAG simple y reglas."""

    def __init__(self, docs_paths: Sequence[str | Path]):
        self.docs_paths = [Path(p) for p in docs_paths]
        self.chunks: List[RetrievalChunk] = []
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words=None)
        self._fit_index()

    def _read_chunks(self) -> List[tuple[str, str]]:
        items: List[tuple[str, str]] = []
        for path in self.docs_paths:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
            for block in blocks:
                if len(block) < 25:
                    continue
                items.append((path.name, block.replace("\n", " ")))
        return items

    def _fit_index(self) -> None:
        raw = self._read_chunks()
        if not raw:
            self._matrix = None
            return
        corpus = [txt for _, txt in raw]
        self._matrix = self.vectorizer.fit_transform(corpus)
        self.chunks = [RetrievalChunk(source=src, text=txt, score=0.0) for src, txt in raw]

    def retrieve(self, question: str, top_k: int = 3) -> List[RetrievalChunk]:
        if self._matrix is None or not self.chunks:
            return []
        q_vec = self.vectorizer.transform([question])
        scores = (self._matrix @ q_vec.T).toarray().ravel()
        if not np.any(scores):
            return []
        order = np.argsort(scores)[::-1][:top_k]
        out: List[RetrievalChunk] = []
        for idx in order:
            out.append(
                RetrievalChunk(
                    source=self.chunks[idx].source,
                    text=self.chunks[idx].text,
                    score=float(scores[idx]),
                )
            )
        return out

    def respond(
        self,
        question: str,
        applicant_context: Dict[str, Any] | None = None,
        prediction: Dict[str, Any] | None = None,
    ) -> str:
        q = question.lower().strip()

        if any(k in q for k in ["hola", "saludos", "buenas"]):
            return (
                "Hola. Soy un asistente de orientacion para becas RD. "
                "Puedo ayudarte con requisitos, documentos, pasos de postulacion y una pre-evaluacion orientativa."
            )

        if prediction is not None and any(
            k in q for k in ["elegible", "elegibilidad", "probabilidad", "califico", "califica"]
        ):
            return (
                f"Resultado orientativo: prioridad {prediction['priority_label']} "
                f"(prob={prediction['probability']:.3f}, umbral={prediction['threshold']:.3f}). "
                f"{prediction['explanation']} "
                "Nota: esta estimacion no sustituye la decision oficial del programa."
            )

        if applicant_context and any(k in q for k in ["documento", "requisito", "paso", "aplicar", "postular"]):
            retrieved = self.retrieve(question, top_k=2)
            if retrieved:
                context = " ".join([f"[{r.source}] {r.text}" for r in retrieved])
                return (
                    "Segun la normativa disponible, estos son los puntos mas relevantes: "
                    f"{context} "
                    "Si quieres, te doy checklist personalizado con tus datos."
                )

        retrieved = self.retrieve(question, top_k=3)
        if retrieved:
            stitched = " ".join([f"[{r.source}] {r.text}" for r in retrieved])
            return (
                f"Encontre informacion relevante: {stitched} "
                "Si deseas, reformulo esta respuesta como pasos accionables."
            )

        return (
            "No tengo evidencia suficiente en la base documental para responder con precision. "
            "Prueba con una pregunta mas especifica sobre requisitos, fechas o criterios de evaluacion."
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
