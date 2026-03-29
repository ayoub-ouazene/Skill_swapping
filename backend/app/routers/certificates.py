import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Skill, ExternalCertificate, User
from app.services.ai_vision import analyze_external_certificate
from app.services.ai_embeddings import generate_embedding

router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"]
)

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)


# adding new skill by uploading certificate 

@router.post("/skills/add")
async def analyze_and_store_external(
    user_id: uuid.UUID = Form(...), # We get the user ID from the form data
    file: UploadFile = File(...),
    db: Session = Depends(get_db)   # We inject the database session here
):
    """
    adding new skill by uploading certificate 
    Full Pipeline: Upload -> Gemini Validation -> Vectorize Skill -> Save to DB
    """
    # 1. Verify User Exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in database.")

    # 2. File Setup
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    temp_file_path = os.path.join(TEMP_DIR, file.filename)

    try:
        # Save file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Call Gemini Vision
        ai_result = analyze_external_certificate(temp_file_path)

        # 4. Check if Valid
        if ai_result.get("status") != "VALID" or not ai_result.get("skill_name"):
            return {
                "success": False, 
                "message": "Certificate was rejected by AI or unreadable.",
                "ai_status": ai_result.get("status")
            }

        extracted_skill = ai_result["skill_name"]

        # 5. Generate Vector Embedding using HuggingFace
        skill_vector = generate_embedding(extracted_skill)
        if not skill_vector:
            raise HTTPException(status_code=500, detail="Failed to generate AI embedding.")

        # 6. Save the Skill to the Database (with the vector!)
        new_skill = Skill(
            user_id=user_id,
            skill_name=extracted_skill,
            embedding=skill_vector
        )
        db.add(new_skill)
        db.commit()
        db.refresh(new_skill) # Get the new skill's generated ID

        # 7. Save the Certificate Record
        new_cert = ExternalCertificate(
            user_id=user_id,
            skill_id=new_skill.id,
            # document_url=... (We leave this null for now as agreed,  we need to use cloudinary)  
        )
        db.add(new_cert)
        db.commit()

        # 8. Success Response
        return {
            "success": True,
            "message": "Certificate approved and skill registered!",
            "data": {
                "skill_name": new_skill.skill_name,
                "skill_id": new_skill.id
            }
        }

    except Exception as e:
        db.rollback() # Cancel DB changes if something crashes
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)