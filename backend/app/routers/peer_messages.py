from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import PeerMessage, PeerThread, Skill, User
from app.schemas import PeerMessageCreate, PeerMessageOut, PeerThreadCreate, PeerThreadOut
from app.services.user_handle import build_user_handle

router = APIRouter(prefix="/peer-messages", tags=["Peer messaging"])

PREVIEW_LEN = 280


def _ordered_pair(a: uuid.UUID, b: uuid.UUID) -> tuple[uuid.UUID, uuid.UUID]:
    if a == b:
        raise HTTPException(status_code=400, detail="Cannot message yourself")
    return (a, b) if str(a) < str(b) else (b, a)


def _other_user_id(thread: PeerThread, me_id: uuid.UUID) -> uuid.UUID:
    return thread.user_b_id if thread.user_a_id == me_id else thread.user_a_id


def _require_thread_participant(db: Session, thread_id: uuid.UUID, me_id: uuid.UUID) -> PeerThread:
    t = db.query(PeerThread).filter(PeerThread.id == thread_id).first()
    if not t or (t.user_a_id != me_id and t.user_b_id != me_id):
        raise HTTPException(status_code=404, detail="Thread not found")
    return t


def _thread_to_out(db: Session, thread: PeerThread, me: User) -> PeerThreadOut:
    oid = _other_user_id(thread, me.id)
    other = db.query(User).filter(User.id == oid).first()
    if not other:
        raise HTTPException(status_code=500, detail="Peer user missing")
    skill_name = None
    if thread.skill_id:
        sk = db.query(Skill.skill_name).filter(Skill.id == thread.skill_id).first()
        skill_name = sk[0] if sk else None
    return PeerThreadOut(
        id=thread.id,
        other_user_id=oid,
        other_handle=build_user_handle(other),
        other_first_name=other.first_name,
        other_last_name=other.last_name,
        skill_id=thread.skill_id,
        skill_name=skill_name,
        last_message_at=thread.last_message_at,
        last_message_preview=thread.last_message_preview,
    )


@router.post("/threads", response_model=PeerThreadOut, status_code=201)
def create_or_get_thread(
    body: PeerThreadCreate,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    other = db.query(User).filter(User.id == body.other_user_id).first()
    if not other:
        raise HTTPException(status_code=404, detail="User not found")
    if body.skill_id is not None:
        sk = (
            db.query(Skill)
            .filter(Skill.id == body.skill_id, Skill.user_id == other.id)
            .first()
        )
        if not sk:
            raise HTTPException(
                status_code=400,
                detail="skill_id must be a skill taught by the other user",
            )

    ua, ub = _ordered_pair(me.id, body.other_user_id)
    thread = (
        db.query(PeerThread)
        .filter(PeerThread.user_a_id == ua, PeerThread.user_b_id == ub)
        .first()
    )

    if thread:
        if body.skill_id and thread.skill_id is None:
            thread.skill_id = body.skill_id
            db.commit()
            db.refresh(thread)
        return _thread_to_out(db, thread, me)

    thread = PeerThread(
        id=uuid.uuid4(),
        user_a_id=ua,
        user_b_id=ub,
        skill_id=body.skill_id,
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return _thread_to_out(db, thread, me)


@router.get("/threads", response_model=list[PeerThreadOut])
def list_my_threads(
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    rows = (
        db.query(PeerThread)
        .filter(or_(PeerThread.user_a_id == me.id, PeerThread.user_b_id == me.id))
        .order_by(
            PeerThread.last_message_at.desc(),
            PeerThread.updated_at.desc(),
        )
        .all()
    )
    return [_thread_to_out(db, t, me) for t in rows]


@router.get("/threads/{thread_id}/messages", response_model=list[PeerMessageOut])
def list_messages(
    thread_id: uuid.UUID,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    _require_thread_participant(db, thread_id, me.id)
    rows = (
        db.query(PeerMessage)
        .filter(PeerMessage.thread_id == thread_id)
        .order_by(PeerMessage.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return rows


@router.post("/threads/{thread_id}/messages", response_model=PeerMessageOut)
def send_peer_message(
    thread_id: uuid.UUID,
    body: PeerMessageCreate,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    thread = _require_thread_participant(db, thread_id, me.id)

    msg = PeerMessage(
        id=uuid.uuid4(),
        thread_id=thread.id,
        sender_id=me.id,
        content=body.content,
    )
    db.add(msg)

    preview = body.content.strip().replace("\n", " ")[:PREVIEW_LEN]
    now = datetime.now(timezone.utc)
    thread.last_message_at = now
    thread.last_message_preview = preview
    thread.updated_at = now

    db.commit()
    db.refresh(msg)
    return msg
