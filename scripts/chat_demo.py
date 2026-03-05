#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from becas_rd.assistant import chat_assistant


if __name__ == "__main__":
    applicant = {
        "edad": 24,
        "genero": "femenino",
        "provincia": "San Juan",
        "region": "El Valle",
        "zona": "rural",
        "tipo_beca": "internacional",
        "nivel_estudio": "maestria",
        "ingreso_hogar_mensual_dop": 38000,
        "miembros_hogar": 5,
        "promedio_academico": 91,
        "score_documental": 88,
        "horas_voluntariado": 110,
        "puntaje_ingles": 84,
        "costo_anual_programa_dop": 1500000,
        "primera_generacion_universitaria": 1,
        "discapacidad": 0,
    }
    question = "Soy elegible para una beca internacional y que documentos debo tener?"
    print(chat_assistant(question, applicant_context=applicant))
