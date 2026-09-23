from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

Status = Literal["draft", "working", "ready", "priority"]
ProposalStatus = Literal["submitted", "accepted", "rejected"]
ProfileRole = Literal["business", "freelancer"]
TaskField = Literal[
    "context_and_need", "data_and_materials", "expected_result",
    "success_criteria", "limitations", "target_users",
    "business_contact", "interaction_format",
]
CARD_FIELDS = (
    "title", "context_and_need", "data_and_materials", "expected_result",
    "success_criteria", "limitations", "target_users",
    "business_contact", "interaction_format",
)
UNKNOWN_VALUE = "Не указано (требуется уточнение)"

class DraftCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    draft_text: str = Field(min_length=1)

    @field_validator("draft_text")
    @classmethod
    def draft_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("draft_text не может быть пустым")
        return value

class Stage1Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    target_field: TaskField
    question: str = Field(min_length=1)

class Stage1Result(BaseModel):
    model_config = ConfigDict(extra="forbid")
    analyzed_draft: str
    missing_aspects: list[str]
    questions: list[Stage1Question] = Field(min_length=3, max_length=5)

class TaskPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(default=None, max_length=100)
    context_and_need: str | None = None
    data_and_materials: str | None = None
    expected_result: str | None = None
    success_criteria: str | None = None
    limitations: str | None = None
    target_users: str | None = None
    business_contact: str | None = None
    interaction_format: str | None = None
    answers: dict[TaskField, str] | None = None
    confirmed: bool = False

class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
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
    confirmed: bool
    rating_total: int
    rating_breakdown: dict
    missing_fields: list[str]
    original_draft: str
    stage1_result: dict
    created_at: datetime
    updated_at: datetime


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    members: list
    contacts: dict
    interests: list[str]
    skills: list[str]
    technologies: list[str]


class ProposalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str
    team_id: str
    idea: str = Field(min_length=1)
    plan: str = Field(min_length=1)
    deadline: str = Field(min_length=1)
    prototype_link: str = ""


class ProposalPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: ProposalStatus


class ProposalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    task_id: str
    team_id: str
    idea: str
    plan: str
    deadline: str
    prototype_link: str
    status: ProposalStatus
    created_at: datetime
    updated_at: datetime


class ProfileCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: ProfileRole
    name: str = Field(min_length=1)
    company: str = ""
    headline: str = ""
    description: str = ""
    industry: str = ""
    skills: list[str] = []
    experience: str = ""
    city: str = ""
    contacts: dict = {}
    avatar: str = ""


class ProfilePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    company: str | None = None
    headline: str | None = None
    description: str | None = None
    industry: str | None = None
    skills: list[str] | None = None
    experience: str | None = None
    city: str | None = None
    contacts: dict | None = None
    avatar: str | None = None


class ProfileRead(ProfileCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
