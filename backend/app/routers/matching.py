import os
import json
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from groq import Groq
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_optional_user
from app.models import Skill, User
from app.services.ai_embeddings import generate_embedding
from app.services.chat_user_context import build_user_context
from app.services.user_handle import build_user_handle


groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter(
    prefix="/matching",
    tags=["Smart Matching Chatbot"]
)

MAX_HISTORY_TURNS = 28


class MatchChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=12000)


class ChatRequest(BaseModel):
    user_query: str = Field(..., max_length=12000)
    history: List[MatchChatTurn] = Field(
        default_factory=list,
        description="Prior turns in this AI Match chat (user + assistant), newest last.",
    )


def _intent_system_prompt() -> str:
    return """
        You are the AI assistant for SkillSwap.
        Decide: (A) they name or clearly imply ONE concrete skill to learn (find teachers), or
        (B) general chat, math, greeting, vague "show my matches" without a skill name, or unclear.

        If they only say "matching", "find matches", "my matching" WITHOUT naming what to learn, use GENERAL_CHAT
        and ask which skill or topic they want (e.g. Python, French).

        Use the conversation history and user profile (if provided) for context.

        You MUST respond in strictly valid JSON only.

        For (A) — specific skill to learn:
        {"intent": "MATCHING", "extracted_skill": "short skill phrase in English or user's language"}

        For (B) — everything else:
        {"intent": "GENERAL_CHAT", "bot_reply": "your concise helpful reply in the user's language"}
        """


def _build_intent_messages(request: ChatRequest, user_context_text: str) -> list[dict]:
    if user_context_text.strip() == "(No authenticated user — request had no valid JWT.)":
        user_block = "\n\n(No authenticated user — profile unknown.)\n"
    else:
        user_block = (
            "\n\n=== Logged-in user profile (SkillSwap) ===\n"
            + user_context_text.strip()
            + "\n=== End profile ===\n"
        )

    trimmed = request.history[-MAX_HISTORY_TURNS:] if request.history else []
    messages: list[dict] = [
        {"role": "system", "content": _intent_system_prompt().strip() + user_block},
    ]
    for turn in trimmed:
        messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": request.user_query})
    return messages


@router.post("/Search_skills")
def smart_chatbot(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Intent + optional vector search. Sends conversation `history` + optional JWT user profile to the model.
    """
    try:
        if current_user:
            user_context_text = build_user_context(db, current_user)
        else:
            user_context_text = "(No authenticated user — request had no valid JWT.)"

        chat_completion = groq_client.chat.completions.create(
            messages=_build_intent_messages(request, user_context_text),
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
        )

        ai_response = json.loads(chat_completion.choices[0].message.content)
        raw_intent = ai_response.get("intent") or ""
        intent = raw_intent.strip().upper().replace(" ", "_")
        if intent in ("MATCH", "FIND_TEACHER", "FIND_SKILL", "SKILL_SEARCH", "LEARN"):
            intent = "MATCHING"
        if intent in ("CHAT", "GENERAL", "CONVERSATION", "SMALLTALK"):
            intent = "GENERAL_CHAT"

        if intent == "GENERAL_CHAT":
            return {
                "response_type": "CHAT",
                "message": ai_response.get(
                    "bot_reply",
                    "I'm here to help you find teachers for improving your skills!",
                ),
                "data": None,
            }

        if intent == "MATCHING":
            target_skill = ai_response.get("extracted_skill")
            if not target_skill:
                return {
                    "response_type": "CHAT",
                    "message": "I understand you want to learn something, but I couldn't catch the exact skill. Could you clarify?",
                    "data": None,
                }

            query_vector = generate_embedding(target_skill)
            if not query_vector:
                raise HTTPException(status_code=500, detail="Embedding generation failed.")

            distance_threshold = 0.5
            closest_skills = (
                db.query(Skill)
                .options(joinedload(Skill.owner))
                .filter(Skill.embedding.isnot(None))
                .filter(Skill.embedding.cosine_distance(query_vector) < distance_threshold)
                .order_by(Skill.embedding.cosine_distance(query_vector))
                .limit(5)
                .all()
            )

            if not closest_skills:
                return {
                    "response_type": "CHAT",
                    "message": f"I looked for '{target_skill}', but we don't have any teachers offering that right now. Try another skill!",
                    "data": [],
                }

            top_5_users = []
            for skill in closest_skills:
                teacher = skill.owner
                if teacher is None:
                    continue
                try:
                    r = float(teacher.rating or 0.0)
                    if r != r:
                        r = 0.0
                except (TypeError, ValueError):
                    r = 0.0
                top_5_users.append({
                    "teacher_id": str(teacher.id),
                    "teacher_handle": build_user_handle(teacher),
                    "skill_id": str(skill.id),
                    "first_name": teacher.first_name,
                    "last_name": teacher.last_name,
                    "email": teacher.email,
                    "rating": r,
                    "matched_skill": skill.skill_name,

                    "skill_id": skill.id 
                    # We can even add a "match_score" later if you want to calculate the raw distance!

                })

            return {
                "response_type": "MATCH_RESULTS",
                "message": f"Here are the top experts I found for {target_skill}!",
                "data": top_5_users,
            }

        return {
            "response_type": "CHAT",
            "message": ai_response.get("bot_reply")
            or (
                "Pour chercher des profils pertinents, décrivez une compétence précise "
                "(ex. « je veux apprendre Python »). Pour une question générale, reformulez en une phrase claire."
            ),
            "data": None,
        }

    except Exception as e:
        print(f"Chatbot Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
