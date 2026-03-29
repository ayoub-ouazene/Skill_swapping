import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Skill, User
from app.schemas import PublicUserProfile, SkillSummary, UserMe, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserMe)
def read_me(current: User = Depends(get_current_user)):
    return UserMe(
        id=current.id,
        email=current.email,
        first_name=current.first_name,
        last_name=current.last_name,
        bio=current.bio,
        credit=current.credit,
        rating=current.rating,
    )


@router.put("/me", response_model=UserMe)
def update_me(
    body: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if body.first_name is not None:
        current.first_name = body.first_name
    if body.last_name is not None:
        current.last_name = body.last_name
    if body.bio is not None:
        current.bio = body.bio
    db.commit()
    db.refresh(current)
    return UserMe(
        id=current.id,
        email=current.email,
        first_name=current.first_name,
        last_name=current.last_name,
        bio=current.bio,
        credit=current.credit,
        rating=current.rating,
    )


@router.get("/{user_id}", response_model=PublicUserProfile)
def read_public_profile(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skills = db.query(Skill).filter(Skill.user_id == user_id).all()
    return PublicUserProfile(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        bio=user.bio,
        rating=user.rating,
        skills=[SkillSummary(id=s.id, skill_name=s.skill_name) for s in skills],
    )
