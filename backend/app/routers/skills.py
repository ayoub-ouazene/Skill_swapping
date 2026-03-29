import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Skill, User
from app.schemas import SkillDetail, SkillListItem

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("")
def list_skills(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    limit = min(max(limit, 1), 100)
    skip = max(skip, 0)

    total = db.query(func.count(Skill.id)).scalar() or 0
    rows = (
        db.query(Skill, User)
        .join(User, Skill.user_id == User.id)
        .order_by(Skill.skill_name.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = [
        SkillListItem(
            id=skill.id,
            skill_name=skill.skill_name,
            teacher_id=user.id,
            teacher_first_name=user.first_name,
            teacher_last_name=user.last_name,
            teacher_rating=user.rating,
        )
        for skill, user in rows
    ]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{skill_id}", response_model=SkillDetail)
def get_skill(skill_id: uuid.UUID, db: Session = Depends(get_db)):
    row = (
        db.query(Skill, User)
        .join(User, Skill.user_id == User.id)
        .filter(Skill.id == skill_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill, user = row
    return SkillDetail(
        id=skill.id,
        skill_name=skill.skill_name,
        teacher_id=user.id,
        teacher_first_name=user.first_name,
        teacher_last_name=user.last_name,
        teacher_rating=user.rating,
        teacher_bio=user.bio,
    )
