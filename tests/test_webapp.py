from becas_rd.data_generation import GenerationConfig, generate_synthetic_data
from becas_rd.webapp import PortalApp


def _sample_applicant():
    df = generate_synthetic_data(GenerationConfig(n_samples=40, random_state=21))
    return df.drop(columns=["adjudicada", "applicant_id"]).iloc[0].to_dict()


def test_portal_app_predict_and_chat():
    app = PortalApp()
    applicant = _sample_applicant()

    prediction = app.predict({"mode": "quick", "applicant": applicant})
    chat = app.answer_chat(
        {
            "question": "Que documentos necesito para una beca internacional?",
            "applicant_context": applicant,
            "prediction": prediction["prediction"],
            "step_context": {"step_id": "documentos"},
        }
    )

    assert "prediction" in prediction
    assert prediction["documents"]
    assert "answer" in chat
    assert "recommendations" in chat
    assert "intent" in chat


def test_portal_app_exposes_bootstrap_and_static_assets():
    app = PortalApp()
    bootstrap = app.get_bootstrap()

    assert bootstrap["brand"]["title"] == "Beca tu Futuro"
    assert bootstrap["govBanner"]["text"]
    assert bootstrap["convocations"]
    assert bootstrap["assistant"]["entryPrompts"]
    assert (app.static_dir / "index.html").exists()
    assert (app.static_dir / "app.js").exists()
    assert (app.static_dir / "styles.css").exists()
