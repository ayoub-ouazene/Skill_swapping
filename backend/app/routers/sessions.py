import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.deps import get_current_user
from app.models import Session as LearningSession, Skill, User
from app.schemas import SessionDetail, SessionItem , EnrollRequest

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("", summary="List Past Sessions")
def list_my_past_sessions(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    Retrieves a list of all historical (non-ongoing) sessions for the authenticated user.
    The user can be either the student or the teacher in these sessions.
    """
    # Build the query: Join Session with Skill to get the skill name
    q = (
        db.query(LearningSession, Skill.skill_name)
        .outerjoin(Skill, LearningSession.skill_id == Skill.id)
        .filter(LearningSession.status != "ONGOING") # FIXED: changed '!' to '!='
        .filter(
            or_(
                LearningSession.student_id == current.id,
                LearningSession.teacher_id == current.id
            )
        )
        .order_by(LearningSession.id.desc())
    )
    
    rows = q.all()
    
    # Format the response list
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


@router.get("/ongoing", summary="List Ongoing Sessions")
def list_my_ongoing_sessions(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    Retrieves a list of all currently active (ONGOING) sessions for the authenticated user.
    This is useful for the frontend to show the user what courses they are currently taking or teaching.
    to be able to end up a course
    """
    q = (
        db.query(LearningSession, Skill.skill_name)
        .outerjoin(Skill, LearningSession.skill_id == Skill.id)
        .filter(LearningSession.status == "ONGOING")
        .filter(
            or_(
                LearningSession.student_id == current.id,
                LearningSession.teacher_id == current.id
            )
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


@router.get("/{session_id}", response_model=SessionDetail, summary="Get Session Details")
def get_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    Fetches the full details of a specific session by its UUID.
    Includes security checks to ensure only the participating student or teacher can view it.
    """
    row = (
        db.query(LearningSession, Skill.skill_name)
        .outerjoin(Skill, LearningSession.skill_id == Skill.id)
        .filter(LearningSession.id == session_id)
        .first()
    )
    
    # 1. Check if the session exists at all
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
        
    s, skill_name = row
    
    # 2. Security Check: Prevent users from viewing sessions they aren't part of
    if s.student_id != current.id and s.teacher_id != current.id:
        raise HTTPException(status_code=403, detail="Not a participant in this session")
        
    # 3. Return the formatted detail view
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


# creating a new session 

@router.post("/enroll", summary="Enroll with a Teacher")
def enroll_in_session(
    request: EnrollRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    STUDENT FLOW: Creates a new ONGOING session where a student chooses to enroll 
    with a specific teacher for a specific skill.
    """
    
    # 1. Sanity Check: Prevent users from enrolling with themselves
    if request.teacher_id == current.id:
        raise HTTPException(
            status_code=400, 
            detail="You cannot enroll in a session with yourself."
        )

    # 2. Verify the Teacher exists
    teacher = db.query(User).filter(User.id == request.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    # 3. Verify the Skill exists
    skill = db.query(Skill).filter(Skill.id == request.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found.")

    try:
        # 4. Create the new Learning Session
        new_session = LearningSession(
            student_id=current.id,
            teacher_id=request.teacher_id,
            skill_id=request.skill_id,
            status="ONGOING",
            duration_hours=0.0, # Will be updated when the session is completed
            rating=0            # Will be updated when the session is completed
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return {
            "success": True,
            "message": f"Successfully enrolled with {teacher.first_name} for {skill.skill_name}!",
            "session_id": new_session.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")