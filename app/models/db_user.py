from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field

class User(Document):
    email: Indexed(str, unique=True)
    password_hash: Optional[str] = None
    first_name: str
    auth_provider: str = "email"  # "email" | "google"
    google_id: Optional[Indexed(str, unique=True)] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
