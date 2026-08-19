import re

def extract_funding_data(title):
    company_name = extract_company_name(title)
    amount, currency = extract_amount(title)
    round_type = extract_round_type(title)

    if company_name is None or amount is None:
        return None

    return {
        "company_name": company_name,
        "amount": amount,
        "currency": currency,
        "round_type": round_type,        
    }

def extract_company_name(title):
    match = re.match(
        r"^(.+?)\s+(?:raises|raised)\s+",
        title,
        re.IGNORECASE,
    )

    if match is None:
        return None

    return match.group(1).strip()


def extract_amount(title):
    match = re.search(
        r"([$€£])\s*(\d+(?:\.\d+)?)\s*([KMB])",
        title,
        re.IGNORECASE,
    )

    if match is None:
        return None, None

    symbol = match.group(1)
    number = float(match.group(2))
    magnitude = match.group(3).upper()

    multipliers = {
        "K": 1_000,
        "M": 1_000_000,
        "B": 1_000_000_000,
    }

    currencies = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
    }

    amount = number * multipliers[magnitude]
    currency = currencies[symbol]

    return amount, currency


def extract_round_type(title):
    match = re.search(
        r"\b(Series [A-E]|Seed)\b",
        title,
        re.IGNORECASE,
    )

    if match is None:
        return None

    return match.group(1).title()