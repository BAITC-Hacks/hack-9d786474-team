import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

class Task(Base):
    __tablename__ = "tasks"

    def __init__(self, **kwargs):
        kwargs.setdefault("confirmed", False)
        super().__init__(**kwargs)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(100), default="")
    context_and_need: Mapped[str] = mapped_column(Text, default="")
    data_and_materials: Mapped[str] = mapped_column(Text, default="")
    expected_result: Mapped[str] = mapped_column(Text, default="")
    success_criteria: Mapped[str] = mapped_column(Text, default="")
    limitations: Mapped[str] = mapped_column(Text, default="")
    target_users: Mapped[str] = mapped_column(Text, default="")
    business_contact: Mapped[str] = mapped_column(Text, default="")
    interaction_format: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    confirmed: Mapped[bool] = mapped_column(default=False, nullable=False)
    rating_total: Mapped[int] = mapped_column(Integer, default=0)
    rating_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    missing_fields: Mapped[list] = mapped_column(JSON, default=list)
    original_draft: Mapped[str] = mapped_column(Text, default="")
    stage1_result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    members: Mapped[list] = mapped_column(JSON, default=list)
    contacts: Mapped[dict] = mapped_column(JSON, default=dict)


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    idea: Mapped[str] = mapped_column(Text, nullable=False)
    plan: Mapped[str] = mapped_column(Text, nullable=False)
    deadline: Mapped[str] = mapped_column(String(120), nullable=False)
    prototype_link: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(20), default="submitted", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
