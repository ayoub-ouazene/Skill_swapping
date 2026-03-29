import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import DesiredSkill, Session as LearningSession, Skill, User
from app.schemas import (
    DesiredSkillCreate,
    DesiredSkillItem,
    PublicUserProfile,
    SkillSummary,
    UserMe,
    UserUpdate,
)
from app.services.user_handle import build_user_handle, user_for_handle

router = APIRouter(prefix="/users", tags=["Users"])


def _me_payload(db: Session, current: User) -> UserMe:
    skills = db.query(Skill).filter(Skill.user_id == current.id).order_by(Skill.skill_name).all()
    desired = (
        db.query(DesiredSkill)
        .filter(DesiredSkill.user_id == current.id)
        .order_by(DesiredSkill.skill_name)
        .all()
    )
    sessions_total = (
        db.query(func.count(LearningSession.id))
        .filter(
            or_(
                LearningSession.teacher_id == current.id,
                LearningSession.student_id == current.id,
            )
        )
        .scalar()
        or 0
    )
    return UserMe(
        id=current.id,
        email=current.email,
        first_name=current.first_name,
        last_name=current.last_name,
        handle=build_user_handle(current),
        bio=current.bio,
        credit=current.credit,
        rating=current.rating,
        skills=[SkillSummary(id=s.id, skill_name=s.skill_name) for s in skills],
        desired_skills=[
            DesiredSkillItem(id=d.id, skill_name=d.skill_name) for d in desired
        ],
        sessions_total=int(sessions_total),
    )


@router.get("/me", response_model=UserMe, summary="Get Current User Profile")
def read_me(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    Retrieves the full profile of the currently authenticated user.
    
    This endpoint uses the JWT token (via the `get_current_user` dependency) 
    to identify the user. It returns private information such as their email 
    and current Time Wallet credit balance, which should never be exposed publicly.
    """
    return _me_payload(db, current)


@router.get("/by-handle/{handle}", response_model=PublicUserProfile, summary="Public profile by @handle")
def read_public_by_handle(handle: str, db: Session = Depends(get_db)):
    user = user_for_handle(db, handle)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    skills = db.query(Skill).filter(Skill.user_id == user.id).all()
    return PublicUserProfile(
        id=user.id,
        handle=build_user_handle(user),
        first_name=user.first_name,
        last_name=user.last_name,
        bio=user.bio,
        rating=user.rating,
        skills=[SkillSummary(id=s.id, skill_name=s.skill_name) for s in skills],
    )


@router.put("/me", response_model=UserMe, summary="Update Current User Profile")
def update_me(
    body: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    Allows the authenticated user to update their own profile information.
    
    Clients only need to send the fields they actually want to change. 
    If a field is omitted (is None), it will simply be ignored and retain 
    its current value in the database.
    """
    if body.first_name is not None:
        current.first_name = body.first_name
    if body.last_name is not None:
        current.last_name = body.last_name
    if body.bio is not None:
        current.bio = body.bio

    db.commit()
    db.refresh(current)

    return _me_payload(db, current)


@router.post("/me/desired-skills", response_model=UserMe, summary="Add a skill you want to learn")
def add_desired_skill(
    body: DesiredSkillCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    name = body.skill_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="skill_name is empty")
    dup = (
        db.query(DesiredSkill)
        .filter(
            DesiredSkill.user_id == current.id,
            func.lower(DesiredSkill.skill_name) == name.lower(),
        )
        .first()
    )
    if dup:
        raise HTTPException(status_code=400, detail="This skill is already in your list")
    row = DesiredSkill(id=uuid.uuid4(), user_id=current.id, skill_name=name)
    db.add(row)
    db.commit()
    return _me_payload(db, current)


@router.delete("/me/desired-skills/{desired_skill_id}", response_model=UserMe, summary="Remove a wanted skill")
def remove_desired_skill(
    desired_skill_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    row = (
        db.query(DesiredSkill)
        .filter(
            DesiredSkill.id == desired_skill_id,
            DesiredSkill.user_id == current.id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Desired skill not found")
    db.delete(row)
    db.commit()
    return _me_payload(db, current)


@router.get("/{user_id}", response_model=PublicUserProfile, summary="Get Public User Profile")
def read_public_profile(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieves the public-facing profile of any user by their UUID.
    
    This is used when a student clicks on a teacher's name to see their profile.
    It intentionally omits sensitive data like email and wallet credits, but 
    includes a list of all the skills that this specific user teaches.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skills = db.query(Skill).filter(Skill.user_id == user_id).all()

    return PublicUserProfile(
        id=user.id,
        handle=build_user_handle(user),
        first_name=user.first_name,
        last_name=user.last_name,
        bio=user.bio,
        rating=user.rating,
        skills=[SkillSummary(id=s.id, skill_name=s.skill_name) for s in skills],
    )
