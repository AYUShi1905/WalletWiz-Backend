from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from beanie import PydanticObjectId
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.models.db_user import User

# Define the OAuth2 security scheme pointing to our login route
# auto_error=False allows us to manually raise custom exceptions
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    FastAPI dependency that extracts the JWT token from the Authorization header,
    validates it, and retrieves the authenticated User from the database.
    Raises UnauthorizedException (HTTP 401) if validation fails.
    """
    if not token:
        raise UnauthorizedException("Authentication token is missing. Please log in.")

    # Decode and validate JWT claims
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired session token. Please log in again.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload. Subject claim (sub) missing.")

    try:
        # Parse standard string ID into Beanie's PydanticObjectId
        user_id = PydanticObjectId(user_id_str)
    except Exception:
        raise UnauthorizedException("Invalid user identifier in token.")

    # Fetch the user document from MongoDB Atlas
    user = await User.get(user_id)
    if not user:
        raise UnauthorizedException("User account associated with this token was not found.")

    return user
