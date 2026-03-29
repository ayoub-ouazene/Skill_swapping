import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)


class UserLogin(BaseModel):
    """Login accepts any reachable email string; strict EmailStr rejects some dev TLDs (e.g. .test)."""

    email: str = Field(..., min_length=3, max_length=320)
    password: str = Field(..., min_length=1, max_length=500)

    @field_validator("email")
    @classmethod
    def strip_email(cls, v: str) -> str:
        return v.strip().lower()


class SkillSummary(BaseModel):
    id: uuid.UUID
    skill_name: str

    model_config = {"from_attributes": True}


class DesiredSkillItem(BaseModel):
    id: uuid.UUID
    skill_name: str

    model_config = {"from_attributes": True}


class DesiredSkillCreate(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=255)


class UserMe(BaseModel):
    id: uuid.UUID
    email: str = Field(..., max_length=320)
    first_name: str
    last_name: str
    handle: str
    bio: Optional[str]
    credit: float
    rating: float
    skills: list[SkillSummary] = Field(default_factory=list)
    desired_skills: list[DesiredSkillItem] = Field(default_factory=list)
    sessions_total: int = 0

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=2000)


class PublicUserProfile(BaseModel):
    id: uuid.UUID
    handle: str
    first_name: str
    last_name: str
    bio: Optional[str]
    rating: float
    skills: list[SkillSummary]


class SkillListItem(BaseModel):
    id: uuid.UUID
    skill_name: str
    teacher_id: uuid.UUID
    teacher_handle: str
    teacher_first_name: str
    teacher_last_name: str
    teacher_rating: float


class SkillDetail(BaseModel):
    id: uuid.UUID
    skill_name: str
    teacher_id: uuid.UUID
    teacher_handle: str
    teacher_first_name: str
    teacher_last_name: str
    teacher_rating: float
    teacher_bio: Optional[str]


class SessionItem(BaseModel):
    id: uuid.UUID
    teacher_id: uuid.UUID
    student_id: uuid.UUID
    skill_id: uuid.UUID
    skill_name: Optional[str]
    status: str
    duration_hours: Optional[float]
    rating: Optional[int]


class SessionDetail(BaseModel):
    id: uuid.UUID
    teacher_id: uuid.UUID
    student_id: uuid.UUID
    skill_id: uuid.UUID
    skill_name: Optional[str]
    status: str
    duration_hours: Optional[float]
    rating: Optional[int]




# for booking / enrolling with specific teacher 

class EnrollRequest(BaseModel):
    teacher_id: uuid.UUID
    skill_id: uuid.UUID


# --- Peer-to-peer (user ↔ user) messaging ---


class PeerThreadCreate(BaseModel):
    other_user_id: uuid.UUID
    skill_id: Optional[uuid.UUID] = None


class PeerThreadOut(BaseModel):
    id: uuid.UUID
    other_user_id: uuid.UUID
    other_handle: str
    other_first_name: str
    other_last_name: str
    skill_id: Optional[uuid.UUID] = None
    skill_name: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None


class PeerMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=8000)


class PeerMessageOut(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}