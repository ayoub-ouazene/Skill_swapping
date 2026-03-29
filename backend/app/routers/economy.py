import os
import uuid
import shutil
import json
import re
import base64
import pdfplumber
import fitz  # PyMuPDF for converting PDF to image
from groq import Groq
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import func
from dotenv import load_dotenv

from app.database import get_db
from app.models import Session, User, InternalCertificate, Skill
from app.services.rewards import generate_certificate_pdf, send_certificate_email

# Load environment variables
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter(
    prefix="/economy",
    tags=["Time Wallet & Certificates"]
)

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def pdf_to_base64_image(pdf_path: str) -> str:
    """Takes the first page of a PDF and converts it to a base64 PNG string."""
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  # Grab the first page
    pix = page.get_pixmap(dpi=150) # Render to image at 150 DPI
    img_bytes = pix.tobytes("png")
    doc.close()
    return base64.b64encode(img_bytes).decode('utf-8')

def groq_fallback_uuid_extraction(base64_image: str) -> str:
    """Sends the image to Groq Vision to find the UUID."""
    prompt = """
    Read this certificate document. Find the 'Secure Certificate ID' at the bottom.
    It will look like a standard UUID (e.g., 123e4567-e89b-12d3-a456-426614174000).
    Return ONLY the UUID string, nothing else. Do not add quotes or markdown.
    If you cannot find it, return 'ERROR'.
    """
    try:
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq Fallback Error: {e}")
        return "ERROR"

# =====================================================================
# 1. STUDENT ACTION: FINALIZE SESSION & ISSUE REWARD PDF
# =====================================================================

class FinalizeSessionRequest(BaseModel):
    session_id: uuid.UUID
    student_rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    duration_hours: float = Field(..., gt=0, description="Actual time spent in hours")

@router.post("/Complete_Course")
def finalize_session_and_issue_pdf(request: FinalizeSessionRequest, db: DbSession = Depends(get_db)):
    # ... (Keep your exact existing code for Complete_Course here) ...
    try:
        learning_session = db.query(Session).filter(Session.id == request.session_id).first()
        if not learning_session or learning_session.status == "COMPLETED":
            raise HTTPException(status_code=400, detail="Session not found or already closed.")

        student = db.query(User).filter(User.id == learning_session.student_id).first()
        teacher = db.query(User).filter(User.id == learning_session.teacher_id).first()
        taught_skill = db.query(Skill).filter(Skill.id == learning_session.skill_id).first()
        
        actual_duration = request.duration_hours

        if student.credit < actual_duration:
            raise HTTPException(status_code=400, detail="Student does not have enough Time Credits!")
        student.credit -= actual_duration

        learning_session.status = "COMPLETED"
        learning_session.rating = request.student_rating
        learning_session.duration_hours = actual_duration 

        new_certificate = InternalCertificate(
            session_id=learning_session.id,
            student_id=student.id,
            teacher_id=teacher.id,
            duration_hours=actual_duration
        )
        db.add(new_certificate)
        db.commit()

        pdf_path = generate_certificate_pdf(
            teacher_name=f"{teacher.first_name} {teacher.last_name}",
            student_name=f"{student.first_name} {student.last_name}",
            skill_name=taught_skill.skill_name,
            duration=actual_duration,
            cert_id=str(new_certificate.id) 
        )

        send_certificate_email(teacher.email, pdf_path)

        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        return {"success": True, "message": f"Session closed. PDF Certificate emailed."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# 2. TEACHER ACTION: UPLOAD PDF & CLAIM MARKET CREDITS
# =====================================================================

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/Claim_Credit")
async def claim_credits_via_upload(
    teacher_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: DbSession = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Must be a PDF file.")

    temp_file_path = os.path.join(TEMP_DIR, file.filename)
    extracted_uuid = None
    extraction_method = None

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # --- ATTEMPT 1: Local PDF Parsing (Fast & Free) ---
        extracted_text = ""
        with pdfplumber.open(temp_file_path) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""

        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        matches = re.findall(uuid_pattern, extracted_text.lower())

        if matches:
            extracted_uuid = matches[0]
            extraction_method = "local_pdf_parser"
        
        # --- ATTEMPT 2: Groq Vision Fallback (For flattened/scanned PDFs) ---
        else:
            print("pdfplumber failed. Trying Groq AI fallback...")
            base64_img = pdf_to_base64_image(temp_file_path)
            groq_result = groq_fallback_uuid_extraction(base64_img)
            
            # Double check that Groq actually returned a valid UUID format
            if groq_result != "ERROR" and re.match(uuid_pattern, groq_result.lower()):
                extracted_uuid = groq_result.lower()
                extraction_method = "groq_vision_ai"
            else:
                raise HTTPException(status_code=400, detail="Could not read a valid Certificate ID from this document, even with AI fallback.")

        # 3. Verify the Certificate in the Database
        certificate = db.query(InternalCertificate).filter(InternalCertificate.id == extracted_uuid).first()
        
        if not certificate:
            raise HTTPException(status_code=404, detail="Invalid Certificate ID. This certificate does not exist.")
        if certificate.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="This certificate does not belong to you.")
        
        learning_session = db.query(Session).filter(Session.id == certificate.session_id).first()
        
        if learning_session.status == "CLAIMED":
            raise HTTPException(status_code=400, detail="The Time Credits for this certificate have already been claimed.")

        # 5. Fetch remaining associated Vector Data
        teacher = db.query(User).filter(User.id == teacher_id).first()
        taught_skill = db.query(Skill).filter(Skill.id == learning_session.skill_id).first()
        target_vector = taught_skill.embedding

        # --- THE ON-THE-FLY ECONOMIC CALCULATION ---
        similar_skills_count = db.query(Skill).filter(
            Skill.embedding.cosine_distance(target_vector) < 0.3
        ).count()
        offer_score = max(similar_skills_count, 1)

        demand_score = db.query(Session).join(Skill, Session.skill_id == Skill.id).filter(
            Skill.embedding.cosine_distance(target_vector) < 0.3,
            Session.status == "COMPLETED"
        ).count()

        raw_multiplier = demand_score / offer_score
        market_multiplier = max(0.5, min(2.0, float(raw_multiplier))) 
        rating_multiplier = learning_session.rating / 5.0

        final_credits_earned = certificate.duration_hours * market_multiplier * rating_multiplier

        # --- APPLY UPDATES ---
        teacher.credit += final_credits_earned
        learning_session.status = "CLAIMED"

        if teacher.rating == 0.0:
            teacher.rating = float(learning_session.rating)
        else:
            teacher.rating = (teacher.rating + learning_session.rating) / 2.0

        db.commit()

        return {
            "success": True,
            "message": "Certificate validated and market-adjusted credits deposited!",
            "receipt": {
                "extracted_via": extraction_method,
                "base_hours": certificate.duration_hours,
                "market_demand_score": demand_score,
                "market_offer_score": offer_score,
                "market_multiplier": round(market_multiplier, 2),
                "rating_multiplier": round(rating_multiplier, 2),
                "final_credits_earned": round(final_credits_earned, 2),
                "new_wallet_balance": round(teacher.credit, 2)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)