import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserMe(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    bio: Optional[str]
    credit: float
    rating: float

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=2000)


class SkillSummary(BaseModel):
    id: uuid.UUID
    skill_name: str

    model_config = {"from_attributes": True}


class PublicUserProfile(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    bio: Optional[str]
    rating: float
    skills: list[SkillSummary]


class SkillListItem(BaseModel):
    id: uuid.UUID
    skill_name: str
    teacher_id: uuid.UUID
    teacher_first_name: str
    teacher_last_name: str
    teacher_rating: float


class SkillDetail(BaseModel):
    id: uuid.UUID
    skill_name: str
    teacher_id: uuid.UUID
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