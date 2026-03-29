import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
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
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    adding new skill by uploading certificate 
    the certificates should clearly mention the skill name 
    Full Pipeline: Upload -> Gemini Validation -> Vectorize Skill -> Save to DB
    """
    user_id = current.id

    # 1. File Setup
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    temp_file_path = None
    safe_name = file.filename or "upload.bin"

    try:
        temp_file_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}_{safe_name}")
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
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass