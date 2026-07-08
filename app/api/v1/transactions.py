from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from api.dependencies import get_current_user
from models.db_user import User
from models.request import TransactionCreateRequest, TransactionUpdateRequest
from models.response import TransactionResponse, TransactionListResponse, PaginationMetadata
from services import transaction as transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def map_to_response(tx) -> TransactionResponse:
    """Helper to cleanly convert a Beanie Transaction document to TransactionResponse."""
    return TransactionResponse(
        id=str(tx.id),
        amount=tx.amount,
        category=tx.category,
        payment_method=tx.payment_method,
        merchant=tx.merchant or "",
        description=tx.description or "",
        transaction_date=tx.transaction_date,
        source_type=tx.source_type,
        created_at=tx.created_at
    )

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    request: TransactionCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new transaction for the authenticated user.
    """
    tx = await transaction_service.create_transaction(current_user.id, request)
    return map_to_response(tx)

@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    Lists paginated transactions for the authenticated user, supporting optional filters.
    """
    transactions, total_items = await transaction_service.list_transactions(
        user_id=current_user.id,
        page=page,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        category=category,
        payment_method=payment_method
    )

    total_pages = (total_items + limit - 1) // limit

    return TransactionListResponse(
        data=[map_to_response(tx) for tx in transactions],
        pagination=PaginationMetadata(
            total_items=total_items,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    )

@router.put("/{id}", response_model=TransactionResponse)
async def update_transaction(
    id: str,
    request: TransactionUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Updates specific fields of a transaction by ID.
    """
    tx = await transaction_service.update_transaction(current_user.id, id, request)
    return map_to_response(tx)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a transaction by ID.
    """
    await transaction_service.delete_transaction(current_user.id, id)
