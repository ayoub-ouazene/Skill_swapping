from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from groq import Groq
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import ChatConversation, ChatMessage, User
from app.services.chat_user_context import build_user_context

router = APIRouter(prefix="/chat", tags=["Personal chat"])

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CHAT_MODEL = "llama-3.1-8b-instant"
MAX_HISTORY_MESSAGES = 40

SYSTEM_PROMPT = """You are SkillSwap Assistant — a friendly, concise personal helper for the SkillSwap platform.

SkillSwap is a peer-to-peer skill exchange: users teach and learn using Time Credits as the internal currency; sessions can be scheduled and completed; skills are listed and discoverable.

Rules:
- Use the user context block you receive: address them by first name when natural, reference their credits, skills, and session stats when relevant.
- Never invent bookings, payments, or other users' private details. If asked for another person's email or data, say you can only discuss their own account.
- If they want to find someone to teach them a skill, you can explain they can browse skills or use the app's matching features — stay accurate, don't promise features that don't exist.
- Keep replies helpful and short unless they ask for detail.
- Respond in the same language the user writes in when possible."""


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)


class ConversationOut(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ChatSendRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=12000)
    conversation_id: Optional[uuid.UUID] = None


class ChatSendResponse(BaseModel):
    reply: str
    conversation_id: uuid.UUID
    user_message_id: uuid.UUID
    assistant_message_id: uuid.UUID


def _require_conv_for_user(
    db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID
) -> ChatConversation:
    c = (
        db.query(ChatConversation)
        .filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == user_id,
        )
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return c


def _get_or_create_default_conversation(db: Session, user: User) -> ChatConversation:
    c = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user.id)
        .order_by(
            ChatConversation.updated_at.desc(),
            ChatConversation.created_at.desc(),
        )
        .first()
    )
    if c:
        return c
    c = ChatConversation(user_id=user.id, title="Main chat")
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.post("/conversations", response_model=ConversationOut, status_code=201)
def create_conversation(
    body: ConversationCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    c = ChatConversation(
        user_id=current.id,
        title=body.title or "Chat",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    rows = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == current.id)
        .order_by(
            ChatConversation.updated_at.desc(),
            ChatConversation.created_at.desc(),
        )
        .all()
    )
    return rows


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    _require_conv_for_user(db, current.id, conversation_id)
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return rows


@router.post("/messages", response_model=ChatSendResponse)
def send_chat_message(
    body: ChatSendRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured")

    if body.conversation_id:
        conv = _require_conv_for_user(db, current.id, body.conversation_id)
    else:
        conv = _get_or_create_default_conversation(db, current)

    user_msg = ChatMessage(
        id=uuid.uuid4(),
        conversation_id=conv.id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    db.flush()

    history = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.conversation_id == conv.id,
            ChatMessage.id != user_msg.id,
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
        .all()
    )
    history_chrono = list(reversed(history))

    user_context = build_user_context(db, current)

    groq_messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\n" + user_context,
        }
    ]
    for m in history_chrono:
        if m.role in ("user", "assistant"):
            groq_messages.append({"role": m.role, "content": m.content})
    groq_messages.append({"role": "user", "content": body.message})

    try:
        completion = groq_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=groq_messages,
        )
        reply = (completion.choices[0].message.content or "").strip()
        if not reply:
            reply = "I couldn't generate a reply. Please try again."
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Chat model error: {e!s}") from e

    assistant_msg = ChatMessage(
        id=uuid.uuid4(),
        conversation_id=conv.id,
        role="assistant",
        content=reply,
    )
    db.add(assistant_msg)

    now = datetime.now(timezone.utc)
    conv.updated_at = now

    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    return ChatSendResponse(
        reply=reply,
        conversation_id=conv.id,
        user_message_id=user_msg.id,
        assistant_message_id=assistant_msg.id,
    )
