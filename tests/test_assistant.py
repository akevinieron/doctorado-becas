from pathlib import Path

from becas_rd.assistant import ScholarshipAssistant
from becas_rd.portal import get_portal_scholarships


def test_assistant_recommends_portal_scholarships_without_llm(tmp_path: Path):
    doc1 = tmp_path / "a.md"
    doc2 = tmp_path / "b.md"
    doc1.write_text(
        "Las becas internacionales suelen requerir evidencia de idioma, admision o preadmision y presupuesto.",
        encoding="utf-8",
    )
    doc2.write_text(
        "Las maestrias internacionales en STEM y salud publica priorizan perfiles con buena base academica.",
        encoding="utf-8",
    )

    assistant = ScholarshipAssistant([doc1, doc2], scholarships=get_portal_scholarships(), llm_client=None)
    response = assistant.answer(
        "Que becas del portal encajan con mi perfil?",
        applicant_context={
            "tipo_beca": "internacional",
            "nivel_estudio": "maestria",
            "programa_interes": "ingenieria de datos y salud publica",
            "promedio_academico": 89,
            "puntaje_ingles": 82,
            "score_documental": 74,
        },
    )

    assert response.recommendations
    assert response.recommendations[0].scholarship_id == "conv-int-maestria-stem-salud-2026"
    assert response.provider == "local_fallback"
    assert "portal" in response.answer.lower() or "beca" in response.answer.lower()


def test_assistant_uses_llm_client_when_available(tmp_path: Path):
    class FakeResponses:
        def create(self, **_: object):
            return type("FakeResponse", (), {"output_text": "Respuesta premium del modelo"})()

    class FakeClient:
        responses = FakeResponses()

    doc = tmp_path / "a.md"
    doc.write_text("Regla: toda beca internacional requiere idioma y admision.", encoding="utf-8")

    assistant = ScholarshipAssistant([doc], scholarships=get_portal_scholarships(), llm_client=FakeClient())
    response = assistant.answer(
        "Quiero una beca internacional para maestria.",
        applicant_context={"tipo_beca": "internacional", "nivel_estudio": "maestria"},
        history=[{"role": "user", "body": "Hola"}],
    )

    assert response.provider == "openai"
    assert response.answer == "Respuesta premium del modelo"
