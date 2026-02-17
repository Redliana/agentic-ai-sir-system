"""KG load mapping for critical materials entities and relations."""

from typing import Any, Dict, List


def load_to_kg(config: Dict[str, Any]) -> Dict[str, Any]:
    """Map structured records to a backend-agnostic KG fact payload."""
    config = config or {}
    records: List[Dict[str, Any]] = config.get("records", [])
    facts = []

    for record in records:
        material = record.get("material")
        country = record.get("country")
        stage = record.get("stage", "supply")
        if not material or not country:
            continue

        facts.append(
            {
                "subject_type": "Material",
                "subject_id": material,
                "predicate": "INVOLVES_COUNTRY",
                "object_type": "Country",
                "object_id": country,
                "properties": {"stage": stage},
            }
        )

    return {"status": "ok", "facts": facts, "fact_count": len(facts)}
