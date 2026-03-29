import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import Token, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, summary="Register a New User")
def register(body: UserRegister, db: Session = Depends(get_db)):
    """
    SIGN UP
    Creates a new user account in the system and returns a JWT access token.
    
    New users are automatically granted 2.0 Time Credits upon registration 
    so they can immediately participate in the SkillSwap economy.
    """
    # 1. Normalize the email to lowercase to prevent duplicate accounts 
    # (e.g., 'John@Doe.com' vs 'john@doe.com')
    normalized_email = body.email.lower()
    
    # 2. Check if a user with this email already exists
    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 3. Create the new user object
    user = User(
        id=uuid.uuid4(),
        email=normalized_email,
        first_name=body.first_name,
        last_name=body.last_name,
        # NEVER store plain text passwords. Hash it before saving to the database.
        hashed_password=hash_password(body.password),
        # Seed the user's wallet with 2 free hours to get them started
        credit=2.0, 
    )
    
    # 4. Save to the database
    db.add(user)
    db.commit()
    db.refresh(user)

    # 5. Generate a JWT token so the user is instantly logged in after registering
    token = create_access_token(str(user.id))
    return Token(access_token=token)


@router.post("/login", response_model=Token, summary="User Login")
def login(body: UserLogin, db: Session = Depends(get_db)):
    """
    LOGIN
    Authenticates a user using their email and password.
    
    If the credentials are correct, it returns a JWT access token that the 
    frontend must include in the Authorization header for future requests.
    """
    # 1. Normalize the email to match how it is stored in the database
    normalized_email = body.email.lower()
    
    # 2. Fetch the user from the database
    user = db.query(User).filter(User.email == normalized_email).first()
    
    # 3. Verify the user exists AND the password matches
    # Note: We use a generic error message ("Incorrect email or password") 
    # for both cases to prevent malicious actors from guessing valid emails.
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    # 4. Generate and return the JWT access token
    token = create_access_token(str(user.id))
    return Token(access_token=token)