# Sistema de Becas RD (Modalidad B)

MVP academico para doctorado: prediccion de adjudicacion de becas (nacional/internacional) en Republica Dominicana + asistente conversacional de orientacion.

## Estructura

- `becas_rd/`: modulos de datos, modelado, asistente y assets de reporte.
- `scripts/`: ejecucion end-to-end y demos.
- `notebooks/`: notebooks para flujo en Colab.
- `docs/`: reglamento simulado, FAQ y log de prompts.
- `report/`: plantilla del informe y guion de video.

## Setup local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar pipeline completo

```bash
python scripts/run_pipeline.py
```

Esto genera:

- `data/synthetic_becas_rd.csv`
- `artifacts/model_bundle.joblib`
- `artifacts/metrics.json`
- `artifacts/fairness.json`
- `report/assets/*`

## Ejecutar pruebas

```bash
pytest -q
```

## Funciones principales

- `generate_synthetic_data(config) -> DataFrame`
- `train_models(df) -> ModelTrainingResult`
- `predict_eligibility(applicant) -> dict`
- `chat_assistant(question, applicant_context=None) -> str`

## Nota etica

El sistema es de apoyo a decisiones. No reemplaza la evaluacion oficial del comite de becas.
