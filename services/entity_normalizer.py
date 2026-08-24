import re

from models.entity_alias import EntityAlias


def clean_entity_name(name):
    if not name:
        return None

    cleaned = name.strip()

    prefixes = [
        "exclusive:",
        "brazil’s",
        "brazil's",
        "sweden’s",
        "sweden's",
        "revolut founder’s",
        "revolut founder's",
    ]

    lower_name = cleaned.lower()

    for prefix in prefixes:
        if lower_name.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break

    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip()

    return cleaned or None


def normalize_entity_name(name, entity_type=None):
    cleaned = clean_entity_name(name)

    if not cleaned:
        return None

    if entity_type is None:
        return cleaned

    alias = EntityAlias.query.filter(
        EntityAlias.entity_type == entity_type,
        EntityAlias.alias.ilike(cleaned),
    ).first()

    if alias:
        return alias.canonical_name

    return cleaned