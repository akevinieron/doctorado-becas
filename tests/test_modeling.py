from pathlib import Path

from becas_rd.data_generation import GenerationConfig, generate_synthetic_data
from becas_rd.modeling import predict_eligibility, train_models


def test_train_models_and_predict(tmp_path: Path):
    df = generate_synthetic_data(GenerationConfig(n_samples=300, random_state=12))
    artifacts_dir = tmp_path / "artifacts"
    result = train_models(df, artifacts_dir=artifacts_dir)

    assert "main" in result.metrics
    assert (artifacts_dir / "model_bundle.joblib").exists()

    sample = df.drop(columns=["adjudicada", "applicant_id"]).iloc[0].to_dict()
    pred = predict_eligibility(sample, artifacts=result.bundle)

    assert 0.0 <= pred["probability"] <= 1.0
    assert pred["priority_label"] in {"alta", "media", "baja"}
