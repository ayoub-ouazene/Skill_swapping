"""Build a text block of SkillSwap + user facts for the personal chat system prompt."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Session as LearningSession, Skill, User


def build_user_context(db: Session, user: User) -> str:
    skills = db.query(Skill.skill_name).filter(Skill.user_id == user.id).all()
    skill_names = [s[0] for s in skills]

    taught = (
        db.query(LearningSession)
        .filter(LearningSession.teacher_id == user.id)
        .count()
    )
    attended = (
        db.query(LearningSession)
        .filter(LearningSession.student_id == user.id)
        .count()
    )
    completed = (
        db.query(LearningSession)
        .filter(
            LearningSession.status == "COMPLETED",
            or_(
                LearningSession.student_id == user.id,
                LearningSession.teacher_id == user.id,
            ),
        )
        .count()
    )

    lines = [
        "=== Current user (SkillSwap) — use this to personalize answers ===",
        f"Name: {user.first_name} {user.last_name}",
        f"Email: {user.email}",
        f"Bio: {user.bio or '(not set)'}",
        f"Time credits (wallet): {user.credit}",
        f"Rating (aggregate): {user.rating}",
        f"Skills they teach / offer: {', '.join(skill_names) if skill_names else '(none listed yet)'}",
        f"Sessions as teacher (all statuses): {taught}",
        f"Sessions as student (all statuses): {attended}",
        f"Completed sessions (as teacher or student): {completed}",
        "=== End user context ===",
    ]
    return "\n".join(lines)
