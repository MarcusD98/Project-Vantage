from services.taxonomy_service import (
    canonicalize_sector,
    normalize_sector_text,
)


def test_normalizes_sector_text():
    assert (
        normalize_sector_text(
            "  AI-Infrastructure  "
        )
        == "ai infrastructure"
    )


def test_maps_ai_sector():
    assert (
        canonicalize_sector(
            "Artificial Intelligence"
        )
        == "Artificial Intelligence"
    )


def test_maps_ai_variant():
    assert (
        canonicalize_sector(
            "Generative AI"
        )
        == "Artificial Intelligence"
    )


def test_maps_long_ai_description():
    assert (
        canonicalize_sector(
            "Enterprise AI infrastructure software"
        )
        == "Artificial Intelligence"
    )


def test_maps_fintech_variant():
    assert (
        canonicalize_sector(
            "Embedded Finance"
        )
        == "Fintech"
    )


def test_maps_debt_collection_to_fintech():
    assert (
        canonicalize_sector(
            "Debt collection technology"
        )
        == "Fintech"
    )


def test_ai_accounting_prefers_fintech():
    assert (
        canonicalize_sector(
            "AI accounting software"
        )
        == "Fintech"
    )


def test_maps_employee_experience_to_enterprise_software():
    assert (
        canonicalize_sector(
            "Employee experience software"
        )
        == "Enterprise Software"
    )


def test_maps_data_platform_to_enterprise_software():
    assert (
        canonicalize_sector(
            "Data platform"
        )
        == "Enterprise Software"
    )


def test_maps_legal_ai_to_legal_tech():
    assert (
        canonicalize_sector(
            "Legal AI"
        )
        == "Legal Tech"
    )


def test_maps_defence_spelling():
    assert (
        canonicalize_sector(
            "Defense Tech"
        )
        == "Defence"
    )


def test_maps_climate_variant():
    assert (
        canonicalize_sector(
            "Climate Technology"
        )
        == "Climate Tech"
    )


def test_maps_health_variant():
    assert (
        canonicalize_sector(
            "Digital Health"
        )
        == "Health Tech"
    )


def test_maps_agritech():
    assert (
        canonicalize_sector(
            "Agritech"
        )
        == "Agritech"
    )


def test_maps_edtech():
    assert (
        canonicalize_sector(
            "Edtech"
        )
        == "Edtech"
    )


def test_maps_consumer_food():
    assert (
        canonicalize_sector(
            "Consumer food"
        )
        == "Consumer"
    )


def test_maps_food_technology():
    assert (
        canonicalize_sector(
            "Food technology"
        )
        == "Consumer"
    )


def test_maps_marketplace():
    assert (
        canonicalize_sector(
            "B2B marketplace"
        )
        == "Marketplaces"
    )


def test_maps_robotics():
    assert (
        canonicalize_sector(
            "Industrial Robotics"
        )
        == "Robotics"
    )


def test_maps_fiber_optics_to_deep_tech():
    assert (
        canonicalize_sector(
            "fiber optic technology"
        )
        == "Deep Tech"
    )


def test_does_not_match_ai_inside_word():
    assert (
        canonicalize_sector(
            "Retail commerce"
        )
        == "Other"
    )


def test_unknown_sector_maps_to_other():
    assert (
        canonicalize_sector(
            "Underwater basket technology"
        )
        == "Other"
    )


def test_empty_sector_returns_none():
    assert canonicalize_sector(None) is None