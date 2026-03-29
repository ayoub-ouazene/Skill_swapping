import os
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from groq import Groq

from app.database import get_db
from app.models import Skill, User
from app.services.ai_embeddings import generate_embedding


# Initialize Groq Client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter(
    prefix="/matching",
    tags=["Smart Matching Chatbot"]
)

class ChatRequest(BaseModel):
    user_query: str



# searching for specific skill by asking the chatbot 

@router.post("/Search_skills")
def smart_chatbot(request: ChatRequest, db: Session = Depends(get_db)):
    """
       the user search for skill by asking the chatbot , enter a prompt 
       the chatbot Detects if the user wants to chat or find a skill, and responds accordingly.
       the chatbot will return list of matchin users
    """
    try:
        # --- STEP 1: Intent Detection using Groq (Llama 3) ---
        # We force Groq to return a strict JSON object so our Python code can read it perfectly.
        system_prompt = """
        You are the AI assistant for SkillSwap. 
        Analyze the user's message. Determine if they are looking to LEARN A SKILL (find a teacher) 
        or if they are just asking a GENERAL QUESTION / CHATTING.
        
        You MUST respond in strictly valid JSON format.
        
        If they want to learn a skill, return:
        {"intent": "MATCHING", "extracted_skill": "The specific skill they want"}
        
        If it's a general question or greeting, return:
        {"intent": "GENERAL_CHAT", "bot_reply": "Your helpful, friendly response to their message"}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_query}
            ],
            model="llama-3.1-8b-instant", # new model not deprecated
            response_format={"type": "json_object"} # Forces JSON output
        )

        # Parse the JSON response from Groq
        ai_response = json.loads(chat_completion.choices[0].message.content)
        intent = ai_response.get("intent")

        # --- STEP 2: Handle GENERAL CHAT ---
        if intent == "GENERAL_CHAT":
            return {
                "response_type": "CHAT",
                "message": ai_response.get("bot_reply", "I'm here to help you find teachers for improving your skills!"),
                "data": None
            }

        # --- STEP 3: Handle MATCHING (Database Search) ---
        if intent == "MATCHING":
            target_skill = ai_response.get("extracted_skill")
            if not target_skill:
                return {
                    "response_type": "CHAT",
                    "message": "I understand you want to learn something, but I couldn't catch the exact skill. Could you clarify?",
                    "data": None
                }

            # Vectorize the extracted skill
            query_vector = generate_embedding(target_skill)
            if not query_vector:
                raise HTTPException(status_code=500, detail="Embedding generation failed.")


            distance_threshold = 0.5
            # Search Neon Database for the Top 5 matches
            closest_skills = (
                db.query(Skill)
                .filter(Skill.embedding.cosine_distance(query_vector) < distance_threshold)
                .order_by(Skill.embedding.cosine_distance(query_vector))
                .limit(5)
                .all()
            )

            if not closest_skills:
                return {
                    "response_type": "CHAT",
                    "message": f"I looked for '{target_skill}', but we don't have any teachers offering that right now. Try another skill!",
                    "data": []
                }

            # Build the rich dictionary of the 5 users as requested
            top_5_users = []
            for skill in closest_skills:
                teacher = skill.owner
                top_5_users.append({
                    "teacher_id": str(teacher.id),
                    "first_name": teacher.first_name,
                    "last_name": teacher.last_name,
                    "email": teacher.email,
                    "rating": teacher.rating,
                    "matched_skill": skill.skill_name,
                    # We can even add a "match_score" later if you want to calculate the raw distance!
                })

            return {
                "response_type": "MATCH_RESULTS",
                "message": f"Here are the top experts I found for {target_skill}!",
                "data": top_5_users
            }

    except Exception as e:
        print(f"Chatbot Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    



