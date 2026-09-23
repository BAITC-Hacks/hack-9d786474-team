import json
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app import ai_service
from app.ai_service import AIServiceError, _call, _validate_stage2, analyze_draft
from app.models import Task
from app.schemas import DraftCreate, Stage1Result, TaskPatch
from app.task_rating import calculate_task_rating
from app.main import app

client = TestClient(app)

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


def test_openai_client_uses_configured_base_url_and_model(monkeypatch):
    captured = {}

    class FakeClient:
        pass

    def fake_openai(**kwargs):
        captured.update(kwargs)
        return FakeClient()

    monkeypatch.setattr(ai_service, "OpenAI", fake_openai)
    monkeypatch.setenv("OPENAI_API_KEY", "lm-studio")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1")
    monkeypatch.setenv("OPENAI_MODEL", "qwen/qwen3-vl-8b")

    client = ai_service._openai_client("lm-studio")

    assert client is not None
    assert captured == {
        "api_key": "lm-studio",
        "base_url": "http://127.0.0.1:1234/v1",
    }
    assert ai_service._model_name() == "qwen/qwen3-vl-8b"


def test_external_ai_exception_is_wrapped():
    class BrokenCompletions:
        def create(self, **kwargs):
            raise TimeoutError("network timeout")

    class BrokenClient:
        chat = type("Chat", (), {"completions": BrokenCompletions()})()

    with pytest.raises(AIServiceError):
        _call(BrokenClient(), [])


def test_catalog_teams_and_proposal_selection_flow():
    catalog = client.get("/catalog")
    assert catalog.status_code == 200
    assert catalog.json()
    assert all(item["confirmed"] and item["status"] in {"ready", "priority"} for item in catalog.json())

    teams = client.get("/teams")
    assert teams.status_code == 200
    assert len(teams.json()) == 5

    task_id = catalog.json()[0]["id"]
    team_id = teams.json()[0]["id"]
    proposal = client.post("/proposals", json={
        "task_id": task_id, "team_id": team_id, "idea": "Тестовая идея предложения",
        "plan": "Проверить прототип и собрать обратную связь.", "deadline": "1 неделя",
        "prototype_link": "https://example.test/test",
    })
    assert proposal.status_code == 201
    proposal_id = proposal.json()["id"]
    assert client.get(f"/tasks/{task_id}/proposals").json()

    updated = client.patch(f"/proposals/{proposal_id}", json={"status": "accepted"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "accepted"


@pytest.mark.parametrize("payload", [
    {"task_id": "missing", "team_id": "demo-team-1", "idea": "x", "plan": "y", "deadline": "z"},
    {"task_id": "demo-task-appointment", "team_id": "missing", "idea": "x", "plan": "y", "deadline": "z"},
])
def test_proposal_rejects_invalid_relationships(payload):
    assert client.post("/proposals", json=payload).status_code == 404


def test_profile_contract_and_editable_demo_profile():
    profile = client.get("/profiles/demo-business-1")
    assert profile.status_code == 200
    assert profile.json()["role"] == "business"
    updated = client.patch("/profiles/demo-business-1", json={"city": "Санкт-Петербург"})
    assert updated.status_code == 200
    assert updated.json()["city"] == "Санкт-Петербург"
    assert client.post("/profiles", json={"role": "invalid", "name": "Bad"}).status_code == 422
