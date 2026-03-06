# Sistema de Becas RD (Modalidad B)

MVP academico para doctorado: prediccion de adjudicacion de becas (nacional/internacional) en Republica Dominicana + asistente conversacional de orientacion.

## Plan y seguimiento

- Plan funcional del portal ciudadano: `docs/portal_ciudadano_plan.md`
- Lista viva de tareas: `PLANS.md`
- Instrucciones para agentes y seguimiento operativo: `AGENTS.md`

## Estructura

- `becas_rd/`: modulos de datos, modelado, asistente y assets de reporte.
- `becas_rd/web/`: SPA estatica del portal ciudadano.
- `becas_rd/portal.py`: contrato del portal, wizard, checklist y copy estructurado.
- `becas_rd/webapp.py`: API HTTP ligera y servidor del portal.
- `scripts/`: ejecucion end-to-end y demos.
- `notebooks/`: notebooks para flujo en Colab.
- `docs/`: reglamento simulado, FAQ, log de prompts y plan funcional del portal ciudadano.
- `PLANS.md`: checklist operativo y seguimiento del avance.
- `AGENTS.md`: pautas para consultar y mantener actualizado el avance.
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

## Ejecutar portal ciudadano

```bash
python3 scripts/serve_portal.py --host 127.0.0.1 --port 8000
```

Luego abre `http://127.0.0.1:8000`.

Endpoints disponibles:

- `GET /api/health`
- `GET /api/bootstrap`
- `POST /api/eligibility/predict`
- `POST /api/assistant/chat`

## Funciones principales

- `generate_synthetic_data(config) -> DataFrame`
- `train_models(df) -> ModelTrainingResult`
- `predict_eligibility(applicant) -> dict`
- `chat_assistant(question, applicant_context=None) -> str`
- `run_server(host, port) -> None`

## Nota etica

El sistema es de apoyo a decisiones. No reemplaza la evaluacion oficial del comite de becas.
