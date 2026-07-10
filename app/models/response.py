from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class UserRegisterResponse(BaseModel):
    message: str
    user_id: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class GoogleAuthResponse(TokenResponse):
    is_new_user: bool = False

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    amount: float
    category: str
    payment_method: str
    merchant: str
    transaction_date: datetime
    description: str
    source_type: str
    created_at: datetime

class PaginationMetadata(BaseModel):
    total_items: int
    page: int
    limit: int
    total_pages: int

class TransactionListResponse(BaseModel):
    data: List[TransactionResponse]
    pagination: PaginationMetadata

class ChatResponse(BaseModel):
    response: str
    tool_triggered: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CategorySpending(BaseModel):
    category: str
    amount: float
    percentage: float

class PaymentMethodSpending(BaseModel):
    payment_method: str
    amount: float
    percentage: float

class DailySpending(BaseModel):
    date: str
    amount: float

class DashboardResponse(BaseModel):
    total_spent: float
    daily_average: float
    by_category: List[CategorySpending]
    by_payment_method: List[PaymentMethodSpending]
    daily_trend: List[DailySpending]
    recent_transactions: List[TransactionResponse]

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    first_name: str
