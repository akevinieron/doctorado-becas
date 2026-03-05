from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


REGION_BY_PROVINCE: Dict[str, str] = {
    "Distrito Nacional": "Ozama",
    "Santo Domingo": "Ozama",
    "Santiago": "Cibao Norte",
    "La Vega": "Cibao Sur",
    "Puerto Plata": "Cibao Norte",
    "Duarte": "Cibao Nordeste",
    "Monsenor Nouel": "Cibao Sur",
    "San Cristobal": "Valdesia",
    "San Pedro de Macoris": "Higuamo",
    "La Romana": "Yuma",
    "La Altagracia": "Yuma",
    "Azua": "Valdesia",
    "Peravia": "Valdesia",
    "San Juan": "El Valle",
    "Barahona": "Enriquillo",
    "Monte Cristi": "Cibao Noroeste",
}


@dataclass(frozen=True)
class GenerationConfig:
    n_samples: int = 3000
    random_state: int = 42


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def generate_synthetic_data(config: GenerationConfig = GenerationConfig()) -> pd.DataFrame:
    """Genera un dataset sintetico de postulantes para becas en RD."""
    rng = np.random.default_rng(config.random_state)

    provinces: List[str] = list(REGION_BY_PROVINCE.keys())
    p_provinces = np.array(
        [0.11, 0.16, 0.10, 0.06, 0.05, 0.05, 0.03, 0.07, 0.05, 0.04, 0.04, 0.04, 0.03, 0.04, 0.02, 0.01]
    )
    p_provinces = p_provinces / p_provinces.sum()

    n = config.n_samples
    provincia = rng.choice(provinces, size=n, p=p_provinces)
    region = np.array([REGION_BY_PROVINCE[p] for p in provincia])

    tipo_beca = rng.choice(["nacional", "internacional"], size=n, p=[0.72, 0.28])
    nivel_estudio = np.where(
        tipo_beca == "nacional",
        rng.choice(["grado", "maestria"], size=n, p=[0.85, 0.15]),
        rng.choice(["maestria", "doctorado"], size=n, p=[0.75, 0.25]),
    )

    ingreso_hogar_mensual_dop = np.clip(rng.lognormal(mean=10.65, sigma=0.55, size=n), 12000, 420000)
    miembros_hogar = rng.integers(1, 8, size=n)
    edad = np.where(nivel_estudio == "grado", rng.integers(17, 27, size=n), rng.integers(22, 45, size=n))

    promedio_academico = np.clip(rng.normal(loc=84, scale=8, size=n), 60, 100)
    score_documental = np.clip(rng.normal(loc=78, scale=12, size=n), 30, 100)
    horas_voluntariado = np.clip(rng.normal(loc=60, scale=45, size=n), 0, 300)

    puntaje_ingles = np.where(
        tipo_beca == "internacional",
        np.clip(rng.normal(loc=78, scale=11, size=n), 20, 100),
        np.clip(rng.normal(loc=52, scale=15, size=n), 0, 100),
    )

    genero = rng.choice(["femenino", "masculino", "otro"], size=n, p=[0.50, 0.48, 0.02])
    zona = rng.choice(["urbana", "rural"], size=n, p=[0.77, 0.23])
    primera_generacion = rng.choice([0, 1], size=n, p=[0.63, 0.37])
    discapacidad = rng.choice([0, 1], size=n, p=[0.93, 0.07])

    costo_anual_programa_dop = np.where(
        tipo_beca == "internacional",
        np.clip(rng.normal(loc=1_450_000, scale=420_000, size=n), 550_000, 3_200_000),
        np.clip(rng.normal(loc=240_000, scale=95_000, size=n), 80_000, 650_000),
    )

    # Crea una probabilidad latente con relacion clara entre variables y target.
    merit_z = (promedio_academico - 82.0) / 7.0
    docs_z = (score_documental - 75.0) / 10.0
    volunteer_z = (horas_voluntariado - 60.0) / 45.0
    need_z = np.clip((85_000 - ingreso_hogar_mensual_dop) / 45_000, -3.0, 3.0)
    cost_z = np.clip((500_000 - costo_anual_programa_dop) / 450_000, -3.0, 3.0)
    english_z = np.where(tipo_beca == "internacional", (puntaje_ingles - 70.0) / 11.0, 0.0)

    region_bonus = np.select(
        [region == "El Valle", region == "Enriquillo", region == "Cibao Noroeste"],
        [0.14, 0.11, 0.08],
        default=0.0,
    )
    urban_bias = np.where(zona == "urbana", 0.10, -0.10)

    logit = (
        -0.55
        + 0.95 * merit_z
        + 0.65 * docs_z
        + 0.80 * need_z
        + 0.45 * volunteer_z
        + 0.55 * english_z
        + 0.50 * cost_z
        + region_bonus
        + urban_bias
        + 0.16 * primera_generacion
        + 0.06 * discapacidad
        + rng.normal(0, 0.42, size=n)
    )

    prob_adjudicacion = _sigmoid(logit)
    adjudicada = rng.binomial(1, prob_adjudicacion)

    df = pd.DataFrame(
        {
            "applicant_id": [f"RD-{i:06d}" for i in range(1, n + 1)],
            "edad": edad,
            "genero": genero,
            "provincia": provincia,
            "region": region,
            "zona": zona,
            "tipo_beca": tipo_beca,
            "nivel_estudio": nivel_estudio,
            "ingreso_hogar_mensual_dop": ingreso_hogar_mensual_dop.round(2),
            "miembros_hogar": miembros_hogar,
            "promedio_academico": promedio_academico.round(2),
            "score_documental": score_documental.round(2),
            "horas_voluntariado": horas_voluntariado.round(1),
            "puntaje_ingles": puntaje_ingles.round(2),
            "costo_anual_programa_dop": costo_anual_programa_dop.round(2),
            "primera_generacion_universitaria": primera_generacion,
            "discapacidad": discapacidad,
            "adjudicada": adjudicada,
        }
    )

    return df


def save_synthetic_dataset(output_path: str | Path, config: GenerationConfig = GenerationConfig()) -> pd.DataFrame:
    """Genera y guarda dataset sintetico en CSV."""
    df = generate_synthetic_data(config)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df
