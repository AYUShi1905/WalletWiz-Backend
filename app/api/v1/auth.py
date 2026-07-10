from fastapi import APIRouter, Depends, status
from models.request import UserRegisterRequest, UserLoginRequest, GoogleAuthRequest
from models.response import UserRegisterResponse, TokenResponse, GoogleAuthResponse, UserProfileResponse
from services import auth as auth_service
from api.dependencies import get_current_user
from models.db_user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest):
    """
    Registers a new user account using email, password, and first name.
    """
    user = await auth_service.register_user(request)
    return UserRegisterResponse(
        message="User registered successfully",
        user_id=str(user.id)
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    """
    Authenticates a user via email and password, returning a JWT access token.
    """
    token = await auth_service.login_user(request)
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )

@router.post("/google", response_model=GoogleAuthResponse)
async def google_auth(request: GoogleAuthRequest):
    """
    Authenticates a user via Google OAuth Identity token.
    Automatically links accounts or registers new users.
    """
    token, is_new_user = await auth_service.authenticate_google_user(request)
    return GoogleAuthResponse(
        access_token=token,
        token_type="bearer",
        is_new_user=is_new_user
    )

@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the authenticated user's profile details.
    """
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name
    )
