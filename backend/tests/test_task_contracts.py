import pytest
from pydantic import ValidationError

from app.ai_service import AIServiceError, _validate_stage2, analyze_draft
from app.schemas import DraftCreate, Stage1Result
from app.task_rating import calculate_task_rating

def full_card(value="достаточно длинное значение поля"):
    return {field: value for field in (
        "context_and_need", "data_and_materials", "expected_result",
        "success_criteria", "limitations", "target_users",
        "business_contact", "interaction_format"
    )}

def test_stub_stage1_has_three_questions(monkeypatch):
    monkeypatch.setenv("USE_AI_STUB", "true")
    result = Stage1Result.model_validate(analyze_draft("Описание задачи"))
    assert 3 <= len(result.questions) <= 5

def test_whitespace_draft_is_rejected():
    with pytest.raises(ValidationError):
        DraftCreate(draft_text="   ")

def test_extra_draft_field_is_rejected():
    with pytest.raises(ValidationError):
        DraftCreate(draft_text="Описание", status="priority")

def test_stage1_target_field_is_restricted():
    with pytest.raises(ValidationError):
        Stage1Result.model_validate({
            "analyzed_draft": "x",
            "missing_aspects": [],
            "questions": [
                {"id": "q1", "target_field": "unknown", "question": "q"},
                {"id": "q2", "target_field": "data_and_materials", "question": "q"},
                {"id": "q3", "target_field": "success_criteria", "question": "q"},
            ],
        })

def test_stage2_validation_rejects_unknown_or_missing_fields():
    card = full_card()
    card.pop("interaction_format")
    with pytest.raises(ValueError):
        _validate_stage2(card)
    card = full_card()
    card["status"] = "priority"
    with pytest.raises(ValueError):
        _validate_stage2(card)

def test_rating_zero():
    result = calculate_task_rating({})
    assert result["rating_total"] == 0
    assert result["status"] == "draft"
    assert len(result["rating_breakdown"]) == 7

def test_rating_one_hundred():
    result = calculate_task_rating(full_card())
    assert result["rating_total"] == 100
    assert result["status"] == "priority"
    assert sum(result["rating_breakdown"].values()) == 100

def test_contact_requires_interaction_format():
    card = full_card()
    card["interaction_format"] = ""
    result = calculate_task_rating(card)
    assert result["rating_breakdown"]["business_contact_and_interaction_format"] == 0
    assert result["rating_total"] == 90

def test_stage2_marker_is_allowed_but_empty_is_not():
    card = full_card()
    card["data_and_materials"] = "Не указано (требуется уточнение)"
    assert _validate_stage2(card)["data_and_materials"].startswith("Не указано")
    card["data_and_materials"] = ""
    with pytest.raises(ValueError):
        _validate_stage2(card)

def test_ai_service_error_type_exists():
    assert issubclass(AIServiceError, RuntimeError)
