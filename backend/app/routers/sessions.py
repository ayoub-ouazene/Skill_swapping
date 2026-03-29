import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Session as LearningSession, Skill, User
from app.schemas import SessionDetail, SessionItem

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("")
def list_my_past_sessions(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    q = (
        db.query(LearningSession, Skill.skill_name)
        .outerjoin(Skill, LearningSession.skill_id == Skill.id)
        .filter(LearningSession.status == "COMPLETED")
        .filter(
            (LearningSession.student_id == current.id)
            | (LearningSession.teacher_id == current.id)
        )
        .order_by(LearningSession.id.desc())
    )
    rows = q.all()
    items = [
        SessionItem(
            id=s.id,
            teacher_id=s.teacher_id,
            student_id=s.student_id,
            skill_id=s.skill_id,
            skill_name=skill_name,
            status=s.status,
            duration_hours=s.duration_hours,
            rating=s.rating,
        )
        for s, skill_name in rows
    ]
    return {"items": items}


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    row = (
        db.query(LearningSession, Skill.skill_name)
        .outerjoin(Skill, LearningSession.skill_id == Skill.id)
        .filter(LearningSession.id == session_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    s, skill_name = row
    if s.student_id != current.id and s.teacher_id != current.id:
        raise HTTPException(status_code=403, detail="Not a participant in this session")
    return SessionDetail(
        id=s.id,
        teacher_id=s.teacher_id,
        student_id=s.student_id,
        skill_id=s.skill_id,
        skill_name=skill_name,
        status=s.status,
        duration_hours=s.duration_hours,
        rating=s.rating,
    )
