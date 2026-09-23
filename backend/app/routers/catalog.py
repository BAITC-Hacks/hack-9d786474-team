from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Task
from ..schemas import TaskRead

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("", response_model=list[TaskRead])
def get_catalog(db: Session = Depends(get_db)):
    """Published tasks are explicitly confirmed and ready or priority."""
    return (
        db.query(Task)
        .filter(Task.confirmed.is_(True), Task.status.in_(("ready", "priority")))
        .order_by(Task.rating_total.desc(), Task.created_at.desc())
        .all()
    )
