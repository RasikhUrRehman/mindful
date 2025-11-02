from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.auth_schema import (
    LoginRequest, 
    TokenResponse, 
    LogoutResponse,
    GoogleAuthRequest,
    GoogleAuthResponse
)
from app.utils.email_validator import is_valid_email
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.
    
    - **name**: User's full name
    - **email**: Valid email address
    - **password**: Password (minimum 8 characters) - required for email/password signup
    """
    # Validate email format
    if not is_valid_email(user_data.email):
        raise HTTPException(
            
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # For traditional signup, password is required
    if not user_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required for email/password signup",
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        gender=user_data.gender,
        motivations=user_data.motivations,
        language=user_data.language,
        picture=user_data.picture,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token.
    
    - **email**: User's email
    - **password**: User's password
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,  # in seconds
    }


@router.post("/google", response_model=GoogleAuthResponse)
def google_auth(auth_data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with Google OAuth.
    
    - **id_token**: Google ID token received from Google Sign-In on Android
    
    This endpoint verifies the Google ID token and either:
    - Creates a new user if they don't exist
    - Returns existing user if they already have an account
    
    Returns an access token that can be used for subsequent API calls.
    """
    try:
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(
            auth_data.id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # Get user information from the token
        google_user_id = idinfo.get('sub')
        email = idinfo.get('email')
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')
        
        if not email or not google_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token - missing required fields"
            )
        
        # Check if user exists by OAuth ID
        user = db.query(User).filter(User.oauth_id == google_user_id).first()
        is_new_user = False
        
        if not user:
            # Check if user exists by email (linking existing account)
            user = db.query(User).filter(User.email == email).first()
            
            if user:
                # Link Google account to existing user
                user.oauth_provider = "google"
                user.oauth_id = google_user_id
                if picture and not user.picture:
                    user.picture = picture
                db.commit()
                db.refresh(user)
            else:
                # Create new user
                is_new_user = True
                user = User(
                    name=name,
                    email=email,
                    oauth_provider="google",
                    oauth_id=google_user_id,
                    picture=picture,
                    password_hash=None,  # No password for OAuth users
                )
                db.add(user)
                db.commit()
                db.refresh(user)
        
        # Create JWT access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )
        
        # Return response with user info
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "picture": user.picture,
                "oauth_provider": user.oauth_provider
            },
            "is_new_user": is_new_user
        }
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/logout", response_model=LogoutResponse)
def logout():
    """
    Logout user (token invalidation handled client-side).
    """
    return {"message": "Logged out successfully"}


@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(token: str):
    """
    Refresh access token using existing token.
    """
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id = payload.get("sub")
    access_token = create_access_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,
    }
