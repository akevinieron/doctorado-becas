from becas_rd.portal import build_bootstrap_payload, build_required_documents, get_portal_scholarships, normalize_portal_payload


def test_normalize_portal_payload_infers_region_and_types():
    payload = {
        "provincia": "San Juan",
        "edad": "24",
        "ingreso_hogar_mensual_dop": "42000",
        "primera_generacion_universitaria": "1",
        "discapacidad": "0",
    }

    normalized = normalize_portal_payload(payload)

    assert normalized["region"] == "El Valle"
    assert normalized["edad"] == 24
    assert normalized["ingreso_hogar_mensual_dop"] == 42000.0
    assert normalized["primera_generacion_universitaria"] == 1
    assert normalized["discapacidad"] == 0


def test_required_documents_include_international_items():
    profile = normalize_portal_payload(
        {
            "tipo_beca": "internacional",
            "record_academico_listo": 1,
            "identificacion_vigente": 1,
            "carta_motivacion_lista": 1,
            "plan_estudios_listo": 1,
            "evidencia_socioeconomica_lista": 0,
            "carta_admision": 1,
            "presupuesto_estimado_listo": 0,
            "evidencia_idioma_lista": 1,
        }
    )

    documents = build_required_documents(profile, mode="full")
    labels = {item["label"] for item in documents}

    assert "Carta de admision o preadmision" in labels
    assert "Evidencia de idioma" in labels
    assert any(item["status"] == "listo" for item in documents)
    assert any(item["status"] == "pendiente" for item in documents)


def test_bootstrap_exposes_two_wizard_modes():
    payload = build_bootstrap_payload()

    assert "quick" in payload["wizards"]
    assert "full" in payload["wizards"]
    assert payload["hero"]["primaryCta"]
    assert payload["convocations"]
    assert get_portal_scholarships()
