CHECKS = [
    ("context_and_need", 20),
    ("data_and_materials", 20),
    ("expected_result", 15),
    ("success_criteria", 15),
    ("limitations", 10),
    ("target_users", 10),
]

def _valid(value: str | None) -> bool:
    return bool(value and len(value.strip()) > 15 and "Не указано" not in value)

def calculate_task_rating(card: dict) -> dict:
    rating = 0
    missing = []
    breakdown = {}
    for field, weight in CHECKS:
        ok = _valid(card.get(field))
        breakdown[field] = weight if ok else 0
        if ok:
            rating += weight
        else:
            missing.append(field)
    contact_ok = _valid(card.get("business_contact"))
    format_ok = _valid(card.get("interaction_format"))
    breakdown["business_contact_and_interaction_format"] = 10 if contact_ok and format_ok else 0
    if contact_ok and format_ok:
        rating += 10
    else:
        missing.append("business_contact_and_interaction_format")
    status = "priority" if rating >= 90 else "ready" if rating >= 70 else "working" if rating >= 40 else "draft"
    return {"rating_total": rating, "status": status, "rating_breakdown": breakdown, "missing_fields": missing}
