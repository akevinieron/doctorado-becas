from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import pandas as pd


def _load_json(path: str | Path) -> Dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def export_report_assets(
    metrics_path: str | Path = "artifacts/metrics.json",
    fairness_path: str | Path = "artifacts/fairness.json",
    output_dir: str | Path = "report/assets",
) -> Dict[str, Path]:
    """Exporta tablas CSV y resumen markdown para el informe."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics = _load_json(metrics_path)
    fairness = _load_json(fairness_path)

    metrics_df = pd.DataFrame(metrics).T.reset_index().rename(columns={"index": "model"})
    fairness_before_df = pd.DataFrame(fairness.get("before", []))
    fairness_after_df = pd.DataFrame(fairness.get("after", []))

    metrics_csv = output_dir / "metrics_summary.csv"
    fairness_before_csv = output_dir / "fairness_before.csv"
    fairness_after_csv = output_dir / "fairness_after.csv"

    metrics_df.to_csv(metrics_csv, index=False)
    fairness_before_df.to_csv(fairness_before_csv, index=False)
    fairness_after_df.to_csv(fairness_after_csv, index=False)

    md = output_dir / "results_summary.md"
    md.write_text(
        "\n".join(
            [
                "# Resultados del MVP de Becas RD",
                "",
                "## Metricas globales",
                metrics_df.to_markdown(index=False),
                "",
                "## Equidad regional antes del ajuste",
                fairness_before_df.to_markdown(index=False) if not fairness_before_df.empty else "Sin datos.",
                "",
                "## Equidad regional despues del ajuste",
                fairness_after_df.to_markdown(index=False) if not fairness_after_df.empty else "Sin datos.",
                "",
                "## Nota metodologica",
                "Se aplico ajuste de umbrales por region para aproximar paridad de tasa positiva minima.",
            ]
        ),
        encoding="utf-8",
    )

    return {
        "metrics_csv": metrics_csv,
        "fairness_before_csv": fairness_before_csv,
        "fairness_after_csv": fairness_after_csv,
        "results_md": md,
    }
