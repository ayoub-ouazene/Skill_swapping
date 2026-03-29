import os
import uuid
import shutil
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import func
from google import genai

from app.database import get_db
from app.models import Session, User, InternalCertificate, Skill
from app.services.rewards import generate_certificate_pdf, send_certificate_email

# Initialize Gemini for reading the uploaded PDF certificates
ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(
    prefix="/economy",
    tags=["Time Wallet & Certificates"]
)

# =====================================================================
# 1. STUDENT ACTION: FINALIZE SESSION & ISSUE REWARD PDF
# =====================================================================

class FinalizeSessionRequest(BaseModel):
    session_id: uuid.UUID
    student_rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    duration_hours: float = Field(..., gt=0, description="Actual time spent in hours")

@router.post("/finalize-session")
def finalize_session_and_issue_pdf(request: FinalizeSessionRequest, db: DbSession = Depends(get_db)):
    """
    STUDENT FLOW: Closes the session using the frontend-provided button,
    enter the duration of the course , then the rating , as inputs to the backend 
    the backend generates a PDF certificate, and emails it to the teacher.
    """
    try:
        learning_session = db.query(Session).filter(Session.id == request.session_id).first()
        if not learning_session or learning_session.status == "COMPLETED":
            raise HTTPException(status_code=400, detail="Session not found or already closed.")

        student = db.query(User).filter(User.id == learning_session.student_id).first()
        teacher = db.query(User).filter(User.id == learning_session.teacher_id).first()
        taught_skill = db.query(Skill).filter(Skill.id == learning_session.skill_id).first()
        
        actual_duration = request.duration_hours

        # 1. Deduct from Student
        if student.credit < actual_duration:
            raise HTTPException(status_code=400, detail="Student does not have enough Time Credits!")
        student.credit -= actual_duration

        # 2. Update Session Record
        learning_session.status = "COMPLETED"
        learning_session.rating = request.student_rating   #add rating to the course
        learning_session.duration_hours = actual_duration 

        # 3. Save the Certificate Record to DB
        new_certificate = InternalCertificate(
            session_id=learning_session.id,
            student_id=student.id,
            teacher_id=teacher.id,
            duration_hours=actual_duration
        )
        db.add(new_certificate)
        db.commit()

        # 4. Generate the Physical PDF Document
        pdf_path = generate_certificate_pdf(
            teacher_name=f"{teacher.first_name} {teacher.last_name}",
            student_name=f"{student.first_name} {student.last_name}",
            skill_name=taught_skill.skill_name,
            duration=actual_duration,
            cert_id=str(new_certificate.id) 
        )

        # 5. Email it to the teacher
        send_certificate_email(teacher.email, pdf_path)

        # 6. Cleanup the temp PDF from the server
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        return {
            "success": True, 
            "message": f"Session closed for {actual_duration} hours. PDF Certificate emailed to teacher."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# 2. TEACHER ACTION: UPLOAD PDF & CLAIM MARKET CREDITS
# =====================================================================

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/upload-internal-certificate")
async def claim_credits_via_upload(
    teacher_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: DbSession = Depends(get_db)
):
    """
    TEACHER FLOW: click on get credit button ,  Uploads the PDF of internel certificate 
      AI extracts the UUID, calculates Supply/Demand 
    via Vector Search, applies the rating multiplier, and adds credits to the wallet.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Must be a PDF file.")

    temp_file_path = os.path.join(TEMP_DIR, file.filename)

    try:
        # 1. Save uploaded PDF temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Use Gemini Vision to read the PDF and extract the "Secure Certificate ID"
        uploaded_file = ai_client.files.upload(file=temp_file_path)
        prompt = """
        Read this certificate document. Find the 'Secure Certificate ID' at the bottom.
        Return ONLY the UUID string, nothing else. If you cannot find it, return 'ERROR'.
        """
        ai_response = ai_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[uploaded_file, prompt]
        )
        extracted_uuid = ai_response.text.strip()

        if extracted_uuid == "ERROR":
            raise HTTPException(status_code=400, detail="Could not read a valid Certificate ID from this document.")

        # 3. Verify the Certificate in the Database
        certificate = db.query(InternalCertificate).filter(InternalCertificate.id == extracted_uuid).first()
        
        if not certificate:
            raise HTTPException(status_code=404, detail="Invalid Certificate ID. This certificate does not exist.")
        if certificate.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="This certificate does not belong to you.")
        
        # 4. Fetch the Session FIRST so we can check its status
        learning_session = db.query(Session).filter(Session.id == certificate.session_id).first()
        
        if learning_session.status == "CLAIMED":
            raise HTTPException(status_code=400, detail="The Time Credits for this certificate have already been claimed.")

        # 5. Fetch remaining associated Vector Data
        teacher = db.query(User).filter(User.id == teacher_id).first()
        taught_skill = db.query(Skill).filter(Skill.id == learning_session.skill_id).first()
        target_vector = taught_skill.embedding

        # --- THE ON-THE-FLY ECONOMIC CALCULATION ---
        
        # OFFER: How many teachers offer similar skills? (Cosine distance < 0.3)
        similar_skills_count = db.query(Skill).filter(
            Skill.embedding.cosine_distance(target_vector) < 0.3
        ).count()
        offer_score = max(similar_skills_count, 1)

        # DEMAND: How many completed sessions used similar skills?
        demand_score = db.query(Session).join(Skill, Session.skill_id == Skill.id).filter(
            Skill.embedding.cosine_distance(target_vector) < 0.3,
            Session.status == "COMPLETED"
        ).count()

        # Multipliers
        raw_multiplier = demand_score / offer_score
        market_multiplier = max(0.5, min(2.0, float(raw_multiplier))) # Clamp between 0.5x and 2.0x
        rating_multiplier = learning_session.rating / 5.0

        # Math
        final_credits_earned = certificate.duration_hours * market_multiplier * rating_multiplier

        # --- APPLY UPDATES ---
        teacher.credit += final_credits_earned
        learning_session.status = "CLAIMED"

        # Update Teacher Rating Average
        if teacher.rating == 0.0:
            teacher.rating = float(learning_session.rating)
        else:
            teacher.rating = (teacher.rating + learning_session.rating) / 2.0

        db.commit()

        return {
            "success": True,
            "message": "Certificate validated and market-adjusted credits deposited!",
            "receipt": {
                "base_hours": certificate.duration_hours,
                "market_demand_score": demand_score,
                "market_offer_score": offer_score,
                "market_multiplier": round(market_multiplier, 2),
                "rating_multiplier": round(rating_multiplier, 2),
                "final_credits_earned": round(final_credits_earned, 2),
                "new_wallet_balance": round(teacher.credit, 2)
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)