from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class ModelTrainingResult:
    bundle: Dict[str, Any]
    metrics: Dict[str, Any]
    fairness: Dict[str, Any]


def _build_preprocessor(df_features: pd.DataFrame) -> Tuple[List[str], List[str], ColumnTransformer]:
    numeric_cols = df_features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_cols = [c for c in df_features.columns if c not in numeric_cols]

    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ]
    )
    return numeric_cols, categorical_cols, preprocessor


def _build_main_estimator(random_state: int) -> Tuple[Any, str]:
    try:
        from xgboost import XGBClassifier

        model = XGBClassifier(
            n_estimators=260,
            max_depth=6,
            learning_rate=0.06,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.2,
            random_state=random_state,
            eval_metric="logloss",
        )
        return model, "xgboost"
    except Exception:
        return RandomForestClassifier(
            n_estimators=320,
            max_depth=12,
            min_samples_leaf=4,
            random_state=random_state,
            n_jobs=-1,
        ), "random_forest"


def _find_best_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    thresholds = np.linspace(0.25, 0.75, 51)
    best = (0.5, -1.0)
    for t in thresholds:
        score = f1_score(y_true, (y_prob >= t).astype(int))
        if score > best[1]:
            best = (float(t), float(score))
    return best[0]


def _classification_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> Dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "threshold": float(threshold),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def audit_regional_parity(y_true: np.ndarray, y_pred: np.ndarray, regions: Iterable[str]) -> pd.DataFrame:
    frame = pd.DataFrame({"y_true": y_true, "y_pred": y_pred, "region": list(regions)})
    rows = []
    for region, group in frame.groupby("region"):
        tp = ((group["y_true"] == 1) & (group["y_pred"] == 1)).sum()
        fn = ((group["y_true"] == 1) & (group["y_pred"] == 0)).sum()
        tpr = tp / (tp + fn) if (tp + fn) else 0.0
        rows.append(
            {
                "region": region,
                "n": int(len(group)),
                "positive_rate": float(group["y_pred"].mean()),
                "tpr": float(tpr),
            }
        )
    return pd.DataFrame(rows).sort_values("region").reset_index(drop=True)


def apply_regional_parity(
    y_prob: np.ndarray,
    regions: Iterable[str],
    base_threshold: float,
    min_ratio: float = 0.85,
    min_threshold: float = 0.35,
) -> Tuple[np.ndarray, Dict[str, float]]:
    regions = pd.Series(list(regions), name="region")
    thresholds = {region: float(base_threshold) for region in regions.unique()}

    def _pred_with_thresholds() -> np.ndarray:
        th = regions.map(thresholds).to_numpy()
        return (y_prob >= th).astype(int)

    y_pred = _pred_with_thresholds()
    frame = pd.DataFrame({"region": regions, "pred": y_pred})
    rates = frame.groupby("region")["pred"].mean()

    if rates.empty:
        return y_pred, thresholds

    target_min_rate = rates.max() * min_ratio
    for region in rates.index:
        current = rates.loc[region]
        while current < target_min_rate and thresholds[region] > min_threshold:
            thresholds[region] = round(max(min_threshold, thresholds[region] - 0.02), 4)
            y_pred = _pred_with_thresholds()
            frame = pd.DataFrame({"region": regions, "pred": y_pred})
            rates = frame.groupby("region")["pred"].mean()
            current = float(rates.loc[region])

    return _pred_with_thresholds(), thresholds


def train_models(
    df: pd.DataFrame,
    target_col: str = "adjudicada",
    regional_col: str = "region",
    random_state: int = 42,
    artifacts_dir: str | Path = "artifacts",
) -> ModelTrainingResult:
    """Entrena baseline y modelo principal para elegibilidad de becas."""
    work_df = df.copy()
    if target_col not in work_df.columns:
        raise ValueError(f"Missing target column: {target_col}")

    y = work_df[target_col].astype(int)
    X = work_df.drop(columns=[target_col]).copy()
    if "applicant_id" in X.columns:
        X = X.drop(columns=["applicant_id"])

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.25,
        random_state=random_state,
        stratify=y_train_val,
    )

    numeric_cols, categorical_cols, preprocessor = _build_preprocessor(X_train)

    baseline = Pipeline(
        steps=[
            ("prep", preprocessor),
            (
                "model",
                LogisticRegression(
                    max_iter=1800,
                    class_weight="balanced",
                    random_state=random_state,
                ),
            ),
        ]
    )
    main_estimator, model_name = _build_main_estimator(random_state)
    main = Pipeline(steps=[("prep", preprocessor), ("model", main_estimator)])

    baseline.fit(X_train, y_train)
    main.fit(X_train, y_train)

    base_val_prob = baseline.predict_proba(X_val)[:, 1]
    main_val_prob = main.predict_proba(X_val)[:, 1]
    baseline_threshold = _find_best_threshold(y_val.to_numpy(), base_val_prob)
    main_threshold = _find_best_threshold(y_val.to_numpy(), main_val_prob)

    base_test_prob = baseline.predict_proba(X_test)[:, 1]
    main_test_prob = main.predict_proba(X_test)[:, 1]

    baseline_metrics = _classification_metrics(y_test.to_numpy(), base_test_prob, baseline_threshold)
    main_metrics = _classification_metrics(y_test.to_numpy(), main_test_prob, main_threshold)

    y_main_pred = (main_test_prob >= main_threshold).astype(int)
    fairness_before = audit_regional_parity(y_test.to_numpy(), y_main_pred, X_test[regional_col])

    y_adjusted_pred, regional_thresholds = apply_regional_parity(
        y_prob=main_test_prob,
        regions=X_test[regional_col],
        base_threshold=main_threshold,
        min_ratio=0.85,
    )
    fairness_after = audit_regional_parity(y_test.to_numpy(), y_adjusted_pred, X_test[regional_col])
    adjusted_metrics = {
        "accuracy": float(accuracy_score(y_test, y_adjusted_pred)),
        "precision": float(precision_score(y_test, y_adjusted_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_adjusted_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_adjusted_pred, zero_division=0)),
    }

    bundle = {
        "baseline_pipeline": baseline,
        "main_pipeline": main,
        "feature_columns": X.columns.tolist(),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "baseline_threshold": baseline_threshold,
        "main_threshold": main_threshold,
        "regional_thresholds": regional_thresholds,
        "target_col": target_col,
        "regional_col": regional_col,
        "model_name": model_name,
    }

    metrics = {
        "baseline": baseline_metrics,
        "main": main_metrics,
        "main_adjusted_for_parity": adjusted_metrics,
    }

    fairness = {
        "before": fairness_before.to_dict(orient="records"),
        "after": fairness_after.to_dict(orient="records"),
    }

    artifacts_dir = Path(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, artifacts_dir / "model_bundle.joblib")
    (artifacts_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (artifacts_dir / "fairness.json").write_text(json.dumps(fairness, indent=2), encoding="utf-8")

    return ModelTrainingResult(bundle=bundle, metrics=metrics, fairness=fairness)


def load_artifacts(path: str | Path = "artifacts/model_bundle.joblib") -> Dict[str, Any]:
    return joblib.load(path)


def _explain_prediction(applicant: Dict[str, Any], probability: float) -> str:
    positives: List[str] = []
    cautions: List[str] = []

    if float(applicant.get("promedio_academico", 0)) >= 85:
        positives.append("promedio academico alto")
    if float(applicant.get("score_documental", 0)) >= 80:
        positives.append("documentacion solida")
    if float(applicant.get("horas_voluntariado", 0)) >= 80:
        positives.append("buen historial de voluntariado")
    if float(applicant.get("ingreso_hogar_mensual_dop", 9e9)) <= 50000:
        positives.append("alto nivel de necesidad economica")

    if float(applicant.get("promedio_academico", 0)) < 75:
        cautions.append("promedio academico por debajo de lo esperado")
    if float(applicant.get("score_documental", 0)) < 65:
        cautions.append("expediente documental incompleto o debil")
    if applicant.get("tipo_beca") == "internacional" and float(applicant.get("puntaje_ingles", 0)) < 70:
        cautions.append("nivel de ingles bajo para postulacion internacional")

    base = f"Probabilidad estimada: {probability:.3f}. "
    if positives:
        base += "Factores favorables: " + ", ".join(positives) + ". "
    if cautions:
        base += "Puntos a mejorar: " + ", ".join(cautions) + "."
    if not positives and not cautions:
        base += "Sin factores dominantes en este perfil."
    return base


def predict_eligibility(
    applicant: Dict[str, Any],
    artifacts: Dict[str, Any] | None = None,
    artifacts_path: str | Path = "artifacts/model_bundle.joblib",
) -> Dict[str, Any]:
    """Predice probabilidad de adjudicacion para un postulante individual."""
    if artifacts is None:
        artifacts = load_artifacts(artifacts_path)

    feature_columns = artifacts["feature_columns"]
    payload = {k: applicant.get(k) for k in feature_columns}
    df_one = pd.DataFrame([payload])

    prob = float(artifacts["main_pipeline"].predict_proba(df_one)[:, 1][0])
    threshold = float(artifacts["main_threshold"])
    label = "alta" if prob >= max(threshold + 0.1, 0.65) else "media" if prob >= threshold else "baja"

    return {
        "probability": prob,
        "threshold": threshold,
        "priority_label": label,
        "explanation": _explain_prediction(payload, prob),
        "model_name": artifacts.get("model_name", "unknown"),
    }
