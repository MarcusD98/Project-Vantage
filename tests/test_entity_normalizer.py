from services.entity_normalizer import clean_entity_name


def test_removes_exclusive_prefix():
    assert clean_entity_name(
        "Exclusive: ClearJet"
    ) == "ClearJet"


def test_removes_country_prefix():
    assert clean_entity_name(
        "Brazil’s Kesh"
    ) == "Kesh"


def test_removes_context_prefix():
    assert clean_entity_name(
        "Revolut founder’s QuantumLight"
    ) == "QuantumLight"


def test_keeps_clean_name():
    assert clean_entity_name(
        "Computomics"
    ) == "Computomics"