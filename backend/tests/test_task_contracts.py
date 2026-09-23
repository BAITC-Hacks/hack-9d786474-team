import json
import pytest
from pydantic import ValidationError

from app.ai_service import AIServiceError, _validate_stage2, analyze_draft, assemble_card
from app.models import Task
from app.schemas import DraftCreate, Stage1Result, TaskPatch
from app.task_rating import calculate_task_rating

def full_card(value="достаточно длинное значение поля"):
    return {field: value for field in (
        "title", "context_and_need", "data_and_materials", "expected_result",
        "success_criteria", "limitations", "target_users",
        "business_contact", "interaction_format"
    )}

def test_valid_stub_stage1_has_three_questions(monkeypatch):
    monkeypatch.setenv("USE_AI_STUB", "true")
    result = Stage1Result.model_validate(analyze_draft("Описание задачи"))
    assert 3 <= len(result.questions) <= 5

def test_invalid_stage1_json_and_target_field():
    with pytest.raises(ValidationError):
        Stage1Result.model_validate_json('{"analyzed_draft":"x","missing_aspects":[],"questions":[]}')
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

def test_whitespace_draft_is_rejected():
    with pytest.raises(ValidationError):
        DraftCreate(draft_text="   ")

def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        DraftCreate(draft_text="Описание", status="priority")
    with pytest.raises(ValidationError):
        TaskPatch(confirmed=False, rating_total=100)

def test_valid_stage2():
    assert _validate_stage2(json.dumps(full_card(), ensure_ascii=False))["title"]

@pytest.mark.parametrize("payload", [
    "{}",
    "{not-json}",
    json.dumps({**full_card(), "extra": "no"}),
    json.dumps({**full_card(), "title": 123}),
    json.dumps({**full_card(), "title": "x" * 101}),
])
def test_invalid_stage2(payload):
    with pytest.raises(ValueError):
        _validate_stage2(payload)

def test_rating_zero():
    result = calculate_task_rating({})
    assert result["rating_total"] == 0
    assert result["status"] == "draft"
    assert len(result["rating_breakdown"]) == 7

def test_rating_one_hundred():
    result = calculate_task_rating({key: value for key, value in full_card().items() if key != "title"})
    assert result["rating_total"] == 100
    assert result["status"] == "priority"
    assert sum(result["rating_breakdown"].values()) == 100

def test_contact_requires_interaction_format():
    card = {key: value for key, value in full_card().items() if key != "title"}
    card["interaction_format"] = ""
    result = calculate_task_rating(card)
    assert result["rating_breakdown"]["business_contact_and_interaction_format"] == 0
    assert result["rating_total"] == 90

def test_contact_and_interaction_format_both_score_ten():
    card = {key: value for key, value in full_card().items() if key != "title"}
    result = calculate_task_rating(card)
    assert result["rating_breakdown"]["business_contact_and_interaction_format"] == 10

def test_marker_is_allowed_but_empty_is_not():
    card = full_card()
    card["data_and_materials"] = "Не указано (требуется уточнение)"
    assert _validate_stage2(json.dumps(card, ensure_ascii=False))["data_and_materials"].startswith("Не указано")
    card["data_and_materials"] = ""
    with pytest.raises(ValueError):
        _validate_stage2(json.dumps(card, ensure_ascii=False))

def test_confirmed_defaults_false_and_can_be_explicit():
    assert Task().confirmed is False
    assert TaskPatch().confirmed is False
    assert TaskPatch(confirmed=True).confirmed is True

def test_ai_service_error_type_exists():
    assert issubclass(AIServiceError, RuntimeError)
