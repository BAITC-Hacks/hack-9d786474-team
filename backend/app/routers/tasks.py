from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..ai_service import analyze_draft, assemble_card
from ..database import get_db
from ..models import Task, now_utc
from ..schemas import DraftCreate, TaskPatch, TaskRead
from ..task_rating import calculate_task_rating

router = APIRouter(prefix="/tasks", tags=["tasks"])

def _recalculate(task: Task) -> None:
    result = calculate_task_rating({field: getattr(task, field) for field, _ in [
        ("context_and_need", 0), ("data_and_materials", 0), ("expected_result", 0),
        ("success_criteria", 0), ("limitations", 0), ("target_users", 0),
        ("business_contact", 0), ("interaction_format", 0)]})
    task.rating_total = result["rating_total"]
    task.status = result["status"]
    task.rating_breakdown = result["rating_breakdown"]
    task.missing_fields = result["missing_fields"]

@router.post("/draft", response_model=TaskRead, status_code=201)
def create_draft(payload: DraftCreate, db: Session = Depends(get_db)):
    try:
        stage1 = analyze_draft(payload.draft_text)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    task = Task(original_draft=payload.draft_text, stage1_result=stage1)
    _recalculate(task)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: str, payload: TaskPatch, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    data = payload.model_dump(exclude_none=True)
    answers = data.pop("answers", None) or {}
    if answers:
        data.update(assemble_card(task.original_draft, answers))
    data.pop("confirmed", None)
    for key, value in data.items():
        if hasattr(task, key):
            setattr(task, key, value)
    _recalculate(task)
    task.updated_at = now_utc()
    db.commit()
    db.refresh(task)
    return task

@router.get("/{task_id}/rating")
def get_rating(task_id: str, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"rating_total": task.rating_total, "rating_breakdown": task.rating_breakdown, "missing_fields": task.missing_fields}
