from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Task
from ..schemas import TaskRead

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("", response_model=list[TaskRead])
def get_catalog(db: Session = Depends(get_db)):
    """Every explicitly confirmed task is visible, regardless of rating/status."""
    return (
        db.query(Task)
        .filter(Task.confirmed.is_(True))
        .order_by(Task.rating_total.desc(), Task.created_at.desc())
        .all()
    )
