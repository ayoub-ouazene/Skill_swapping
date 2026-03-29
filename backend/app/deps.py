import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models import User

# HTTPBearer (not OAuth2 password flow) so Swagger "Authorize" accepts a pasted JWT.
# Our /auth/login uses JSON { email, password }; OAuth2's username/password form does not match that.
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception
    try:
        user_id = uuid.UUID(str(sub))
    except (ValueError, TypeError):
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
