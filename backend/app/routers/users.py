import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Skill, User
from app.schemas import PublicUserProfile, SkillSummary, UserMe, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserMe, summary="Get Current User Profile")
def read_me(current: User = Depends(get_current_user)):
    """
    Retrieves the full profile of the currently authenticated user.
    
    This endpoint uses the JWT token (via the `get_current_user` dependency) 
    to identify the user. It returns private information such as their email 
    and current Time Wallet credit balance, which should never be exposed publicly.
    """
    return UserMe(
        id=current.id,
        email=current.email,
        first_name=current.first_name,
        last_name=current.last_name,
        bio=current.bio,
        credit=current.credit,
        rating=current.rating,
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
    # 1. Selectively update fields only if they were provided in the request body
    if body.first_name is not None:
        current.first_name = body.first_name
    if body.last_name is not None:
        current.last_name = body.last_name
    if body.bio is not None:
        current.bio = body.bio
        
    # 2. Save changes to the database
    db.commit()
    
    # 3. Refresh the object to ensure we have the latest data before returning
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


@router.get("/{user_id}", response_model=PublicUserProfile, summary="Get Public User Profile")
def read_public_profile(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieves the public-facing profile of any user by their UUID.
    
    This is used when a student clicks on a teacher's name to see their profile.
    It intentionally omits sensitive data like email and wallet credits, but 
    includes a list of all the skills that this specific user teaches.
    """
    # 1. Fetch the requested user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Fetch all skills associated with this user
    skills = db.query(Skill).filter(Skill.user_id == user_id).all()
    
    # 3. Format the response, combining user data with their list of skills
    return PublicUserProfile(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        bio=user.bio,
        rating=user.rating,
        # Use a list comprehension to quickly format the skills into the expected schema
        skills=[SkillSummary(id=s.id, skill_name=s.skill_name) for s in skills],
    )