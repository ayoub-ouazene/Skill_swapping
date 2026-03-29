import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Skill, User
from app.schemas import SkillDetail, SkillListItem
from app.services.user_handle import build_user_handle

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("", summary="List All Available Skills")
def list_skills(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    Retrieves a paginated list of all skills offered on the platform, 
    along with basic information about the teacher offering each skill.

    **Query Parameters:**
    - **skip**: The number of records to skip (useful for pagination). Defaults to 0.
    - **limit**: The maximum number of records to return. Clamped between 1 and 100. Defaults to 20.

    **Returns:**
    A dictionary containing the list of skills (`items`) and pagination metadata (`total`, `skip`, `limit`).
    """
    # Enforce safe boundaries for pagination to prevent database overload
    limit = min(max(limit, 1), 100)
    skip = max(skip, 0)

    # 1. Get the total count of skills for the frontend to calculate total pages
    total = db.query(func.count(Skill.id)).scalar() or 0
    
    # 2. Fetch the paginated skills and join with the User table to get teacher details
    rows = (
        db.query(Skill, User)
        .join(User, Skill.user_id == User.id)
        .order_by(Skill.skill_name.asc()) # Alphabetical order makes UI browsing easier
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 3. Format the raw database rows into our Pydantic schema
    items = [
        SkillListItem(
            id=skill.id,
            skill_name=skill.skill_name,
            teacher_id=user.id,
            teacher_handle=build_user_handle(user),
            teacher_first_name=user.first_name,
            teacher_last_name=user.last_name,
            teacher_rating=user.rating,
        )
        for skill, user in rows
    ]
    
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{skill_id}", response_model=SkillDetail, summary="Get Skill Details")
def get_skill(skill_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieves the full, detailed profile of a specific skill by its UUID.
    
    This endpoint is typically used when a user clicks on a skill card from the list view
    to see more details, including the teacher's full biography, before deciding to enroll.

    **Path Parameters:**
    - **skill_id**: The UUID of the specific skill.

    **Returns:**
    A detailed JSON object (`SkillDetail`) containing the skill name, teacher info, and teacher bio.
    Raises a 404 error if the skill ID does not exist.
    """
    # Query the database for the specific skill and join the associated user (teacher)
    row = (
        db.query(Skill, User)
        .join(User, Skill.user_id == User.id)
        .filter(Skill.id == skill_id)
        .first()
    )
    
    # Handle the case where the skill doesn't exist
    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    skill, user = row
    
    # Return the expanded detail view (notice this includes `teacher_bio` which the list view does not)
    return SkillDetail(
        id=skill.id,
        skill_name=skill.skill_name,
        teacher_id=user.id,
        teacher_handle=build_user_handle(user),
        teacher_first_name=user.first_name,
        teacher_last_name=user.last_name,
        teacher_rating=user.rating,
        teacher_bio=user.bio,
    )