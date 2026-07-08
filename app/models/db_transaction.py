from datetime import datetime
from enum import Enum
from typing import Optional
from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field

class TransactionCategory(str, Enum):
    FOOD_DINING = "Food & Dining"
    SHOPPING = "Shopping"
    TRAVEL_TRANSPORT = "Travel & Transport"
    BILLS_UTILITIES = "Bills & Utilities"
    ENTERTAINMENT = "Entertainment"
    HEALTH_MEDICAL = "Health & Medical"
    OTHERS = "Others"

class PaymentMethod(str, Enum):
    CASH = "Cash"
    CARD = "Card"
    UPI = "UPI"

class LLMMetadata(BaseModel):
    confidence_score: float
    raw_input_text: str

class Transaction(Document):
    user_id: Indexed(PydanticObjectId)
    amount: float
    category: TransactionCategory
    payment_method: PaymentMethod
    merchant: Optional[str] = ""
    description: Optional[str] = ""
    transaction_date: Indexed(datetime)
    source_type: str = "manual"  # "manual" | "llm"
    llm_metadata: Optional[LLMMetadata] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "transactions"
        indexes = [
            "category",
            "payment_method"
        ]
