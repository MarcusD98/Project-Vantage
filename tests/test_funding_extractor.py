from services.funding_extractor import extract_funding_data


def test_extract_funding_data():
    title = "Computomics raises €6.3M to scale climate-smart plant breeding"

    result = extract_funding_data(title)

    assert result["company_name"] == "Computomics"
    assert result["amount"] == 6_300_000
    assert result["currency"] == "EUR"
    assert result["round_type"] is None

def test_extract_series_round():
    title = "Acme raises $50M Series B to expand globally"

    result = extract_funding_data(title)

    assert result["company_name"] == "Acme"
    assert result["amount"] == 50_000_000
    assert result["currency"] == "USD"
    assert result["round_type"] == "Series B"

def test_returns_none_for_non_funding_article():
    title = "Startup ecosystem continues to grow across Europe"

    result = extract_funding_data(title)

    assert result is None