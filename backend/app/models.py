import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    bio = Column(String(2000), nullable=True)
    credit = Column(Float, default=2.0)
    rating = Column(Float, default=0.0)
    hashed_password = Column(String, nullable=False)

    # Relationships (makes it easy to query e.g. user.skills)
    skills = relationship("Skill", back_populates="owner", cascade="all, delete-orphan")
    external_certificates = relationship("ExternalCertificate", back_populates="owner", cascade="all, delete-orphan")
    chat_conversations = relationship(
        "ChatConversation", back_populates="owner", cascade="all, delete-orphan"
    )

class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    skill_name = Column(String(255), nullable=False)
    
    # This is the magic AI column! 384 dimensions matches our free HuggingFace model.
    embedding = Column(Vector(384))

    # Relationships
    owner = relationship("User", back_populates="skills")
    certificates = relationship("ExternalCertificate", back_populates="skill", cascade="all, delete-orphan")

class ExternalCertificate(Base):
    __tablename__ = "external_certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"))
    document_url = Column(String, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="external_certificates")
    skill = relationship("Skill", back_populates="certificates")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"))
    status = Column(String(50), default="ONGOING")
    duration_hours = Column(Float, nullable=True)
    rating = Column(Integer, nullable=True)

class InternalCertificate(Base):
    __tablename__ = "internal_certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    duration_hours = Column(Float, nullable=False)


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="chat_conversations")
    messages = relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("ChatConversation", back_populates="messages")
