#!/usr/bin/env python3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from becas_rd.assistant import chat_assistant
from becas_rd.data_generation import GenerationConfig, save_synthetic_dataset
from becas_rd.modeling import predict_eligibility, train_models
from becas_rd.report_assets import export_report_assets


def main() -> None:
    data_path = Path("data/synthetic_becas_rd.csv")
    cfg = GenerationConfig(n_samples=3000, random_state=42)
    df = save_synthetic_dataset(data_path, cfg)
    print(f"[1/4] Dataset generado: {len(df)} filas")

    result = train_models(df, artifacts_dir="artifacts")
    print("[2/4] Modelos entrenados")
    print(result.metrics)

    sample = df.drop(columns=["adjudicada", "applicant_id"]).iloc[0].to_dict()
    pred = predict_eligibility(sample)
    print("[3/4] Prediccion de ejemplo:")
    print(pred)

    answer = chat_assistant(
        "Quiero saber mi elegibilidad y documentos para postular.",
        applicant_context=sample,
    )
    print("[4/4] Respuesta del asistente:")
    print(answer)

    assets = export_report_assets(output_dir="report/assets")
    print("Assets exportados:")
    for k, v in assets.items():
        print(f"- {k}: {v}")

    # Snapshot limpio para inspeccion rapida
    pd.DataFrame([pred]).to_csv("report/assets/sample_prediction.csv", index=False)


if __name__ == "__main__":
    main()
