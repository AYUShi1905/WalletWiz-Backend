from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from core.config import settings
from core.exceptions import UserAlreadyExistsException, InvalidCredentialsException
from core.security import hash_password, verify_password, create_access_token
from models.db_user import User
from models.request import UserRegisterRequest, UserLoginRequest, GoogleAuthRequest

async def register_user(request: UserRegisterRequest) -> User:
    """
    Registers a new user in the database.
    Raises UserAlreadyExistsException if the email is already in use.
    """
    # Check if user already exists
    existing_user = await User.find_one(User.email == request.email)
    if existing_user:
        raise UserAlreadyExistsException()

    # Hash the password
    hashed_pwd = hash_password(request.password)

    # Create and insert the user
    new_user = User(
        email=request.email,
        password_hash=hashed_pwd,
        first_name=request.first_name,
        auth_provider="email",
        created_at=datetime.utcnow()
    )
    await new_user.insert()
    return new_user

async def login_user(request: UserLoginRequest) -> str:
    """
    Authenticates a user via email/password and returns a JWT access token.
    Raises InvalidCredentialsException if authentication fails.
    """
    # Fetch the user by email
    user = await User.find_one(User.email == request.email)
    if not user:
        raise InvalidCredentialsException()

    # Verify password if user registered with email
    if user.auth_provider != "email" or not user.password_hash:
        raise InvalidCredentialsException("Account created via Google. Please log in using Google.")

    if not verify_password(request.password, user.password_hash):
        raise InvalidCredentialsException()

    # Create and return JWT access token
    access_token = create_access_token(data={"sub": str(user.id)})
    return access_token

async def authenticate_google_user(request: GoogleAuthRequest) -> tuple[str, bool]:
    """
    Verifies a Google ID token. If the user does not exist, registers them.
    If the user exists, links their Google account.
    Returns a tuple of (access_token, is_new_user).
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise InvalidCredentialsException("Google OAuth is not configured on the backend.")

    try:
        # Verify the Google ID token
        id_info = id_token.verify_oauth2_token(
            request.id_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise InvalidCredentialsException("Invalid Google ID token")
    except Exception as e:
        raise InvalidCredentialsException(f"Google token verification failed: {str(e)}")

    # Extract user information from Google verified token claims
    email = id_info.get("email")
    google_id = id_info.get("sub")
    first_name = id_info.get("given_name") or id_info.get("name") or "Google User"

    if not email or not google_id:
        raise InvalidCredentialsException("Invalid token payload: Email or User ID missing.")

    # Search for an existing user with this email
    user = await User.find_one(User.email == email)
    is_new_user = False

    if user:
        # If user exists but google_id is not set, link it
        updated = False
        if not user.google_id:
            user.google_id = google_id
            updated = True
        
        # If they registered via email, we allow dual-provider login by linking
        if user.auth_provider == "email":
            # Keep email as main, or update provider if desired.
            # We keep it but ensure google_id is saved
            pass
            
        if updated:
            await user.save()
    else:
        # Create a new user with Google as the auth provider
        is_new_user = True
        user = User(
            email=email,
            first_name=first_name,
            auth_provider="google",
            google_id=google_id,
            created_at=datetime.utcnow()
        )
        await user.insert()

    # Create and return JWT access token
    access_token = create_access_token(data={"sub": str(user.id)})
    return access_token, is_new_user
