from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from models.db_transaction import TransactionCategory, PaymentMethod, LLMMetadata

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    first_name: str = Field(..., min_length=1)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: str

class TransactionCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
    category: TransactionCategory
    payment_method: PaymentMethod
    merchant: Optional[str] = ""
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = ""
    source_type: str = "manual"  # "manual" | "llm"
    llm_metadata: Optional[LLMMetadata] = None

class TransactionUpdateRequest(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[TransactionCategory] = None
    payment_method: Optional[PaymentMethod] = None
    merchant: Optional[str] = None
    transaction_date: Optional[datetime] = None
    description: Optional[str] = None

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$", description="Role must be either 'user' or 'assistant'")
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
