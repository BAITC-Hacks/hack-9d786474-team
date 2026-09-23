from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Proposal, Task, Team, now_utc
from ..schemas import ProposalCreate, ProposalPatch, ProposalRead

router = APIRouter(prefix="/proposals", tags=["proposals"])
task_proposals_router = APIRouter(prefix="/tasks", tags=["proposals"])


@router.post("", response_model=ProposalRead, status_code=201)
def create_proposal(payload: ProposalCreate, db: Session = Depends(get_db)):
    if not db.get(Task, payload.task_id):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if not db.get(Team, payload.team_id):
        raise HTTPException(status_code=404, detail="Команда не найдена")
    proposal = Proposal(**payload.model_dump())
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


@task_proposals_router.get("/{task_id}/proposals", response_model=list[ProposalRead])
def list_task_proposals(task_id: str, db: Session = Depends(get_db)):
    if not db.get(Task, task_id):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return db.query(Proposal).filter(Proposal.task_id == task_id).order_by(Proposal.created_at.desc()).all()


@router.patch("/{proposal_id}", response_model=ProposalRead)
def update_proposal(proposal_id: str, payload: ProposalPatch, db: Session = Depends(get_db)):
    proposal = db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Предложение не найдено")
    proposal.status = payload.status
    proposal.updated_at = now_utc()
    db.commit()
    db.refresh(proposal)
    return proposal
