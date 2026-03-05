from pathlib import Path

from becas_rd.assistant import ScholarshipAssistant


def test_assistant_retrieval(tmp_path: Path):
    doc1 = tmp_path / "a.md"
    doc2 = tmp_path / "b.md"
    doc1.write_text("Requisitos: record academico, cedula, carta de motivacion.", encoding="utf-8")
    doc2.write_text("Beca internacional requiere prueba de idioma.", encoding="utf-8")

    assistant = ScholarshipAssistant([doc1, doc2])
    answer = assistant.respond("Que requisitos necesito para beca internacional?")

    assert "informacion relevante" in answer.lower() or "puntos" in answer.lower()
