from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

Status = Literal["draft", "working", "ready", "priority"]

class DraftCreate(BaseModel):
    draft_text: str = Field(min_length=1)

class Stage1Question(BaseModel):
    id: str
    target_field: str
    question: str

class Stage1Result(BaseModel):
    analyzed_draft: str
    missing_aspects: list[str]
    questions: list[Stage1Question] = Field(min_length=3, max_length=5)

class TaskPatch(BaseModel):
    title: str | None = Field(default=None, max_length=100)
    context_and_need: str | None = None
    data_and_materials: str | None = None
    expected_result: str | None = None
    success_criteria: str | None = None
    limitations: str | None = None
    target_users: str | None = None
    business_contact: str | None = None
    interaction_format: str | None = None
    answers: dict[str, str] | None = None
    confirmed: bool = False

class TaskRead(BaseModel):
    id: str
    title: str
    context_and_need: str
    data_and_materials: str
    expected_result: str
    success_criteria: str
    limitations: str
    target_users: str
    business_contact: str
    interaction_format: str
    status: Status
    rating_total: int
    rating_breakdown: dict
    missing_fields: list[str]
    original_draft: str
    stage1_result: dict
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
