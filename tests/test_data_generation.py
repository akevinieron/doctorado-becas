from becas_rd.data_generation import GenerationConfig, generate_synthetic_data


def test_generate_synthetic_data_shape_and_columns():
    df = generate_synthetic_data(GenerationConfig(n_samples=120, random_state=7))
    assert len(df) == 120
    expected = {
        "applicant_id",
        "edad",
        "genero",
        "provincia",
        "region",
        "zona",
        "tipo_beca",
        "nivel_estudio",
        "ingreso_hogar_mensual_dop",
        "miembros_hogar",
        "promedio_academico",
        "score_documental",
        "horas_voluntariado",
        "puntaje_ingles",
        "costo_anual_programa_dop",
        "primera_generacion_universitaria",
        "discapacidad",
        "adjudicada",
    }
    assert expected.issubset(set(df.columns))
    assert set(df["adjudicada"].unique()).issubset({0, 1})
