from datetime import datetime, time
from typing import List, Optional, Tuple
from beanie import PydanticObjectId
from core.exceptions import TransactionNotFoundException, WalletWizException
from models.db_transaction import Transaction
from models.request import TransactionCreateRequest, TransactionUpdateRequest

async def create_transaction(user_id: PydanticObjectId, request: TransactionCreateRequest) -> Transaction:
    """
    Creates a new transaction document associated with the user.
    """
    new_transaction = Transaction(
        user_id=user_id,
        amount=request.amount,
        category=request.category,
        payment_method=request.payment_method,
        merchant=request.merchant,
        description=request.description,
        transaction_date=request.transaction_date,
        source_type=request.source_type,
        llm_metadata=request.llm_metadata
    )
    await new_transaction.insert()
    return new_transaction

async def list_transactions(
    user_id: PydanticObjectId,
    page: int = 1,
    limit: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    payment_method: Optional[str] = None
) -> Tuple[List[Transaction], int]:
    """
    Lists paginated transactions for a user, with optional filters for
    date range, category, and payment method.
    Returns a tuple of (transactions_list, total_matching_count).
    """
    # Start query scope restricted to the user's transactions
    query = Transaction.find(Transaction.user_id == user_id)

    # Apply date filters
    if start_date:
        try:
            start_dt = datetime.combine(datetime.strptime(start_date, "%Y-%m-%d"), time.min)
            query = query.find(Transaction.transaction_date >= start_dt)
        except ValueError:
            raise WalletWizException("Invalid start_date format. Use YYYY-MM-DD.", status_code=400)

    if end_date:
        try:
            end_dt = datetime.combine(datetime.strptime(end_date, "%Y-%m-%d"), time.max)
            query = query.find(Transaction.transaction_date <= end_dt)
        except ValueError:
            raise WalletWizException("Invalid end_date format. Use YYYY-MM-DD.", status_code=400)

    # Apply category & payment method filters
    if category:
        query = query.find(Transaction.category == category)
    if payment_method:
        query = query.find(Transaction.payment_method == payment_method)

    # Fetch total count before pagination
    total_count = await query.count()

    # Apply sorting (most recent first) and pagination (skip & limit)
    transactions = await query.sort(-Transaction.transaction_date).skip((page - 1) * limit).limit(limit).to_list()

    return transactions, total_count

async def update_transaction(
    user_id: PydanticObjectId,
    transaction_id: str,
    request: TransactionUpdateRequest
) -> Transaction:
    """
    Updates specific fields of an existing transaction if it belongs to the user.
    Raises TransactionNotFoundException if the transaction does not exist or belongs to another user.
    """
    try:
        tx_id = PydanticObjectId(transaction_id)
    except Exception:
        raise TransactionNotFoundException()

    # Find the transaction and verify ownership
    transaction = await Transaction.find_one(Transaction.id == tx_id, Transaction.user_id == user_id)
    if not transaction:
        raise TransactionNotFoundException()

    # Update only fields provided in the request
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transaction, key, value)

    await transaction.save()
    return transaction

async def delete_transaction(user_id: PydanticObjectId, transaction_id: str) -> None:
    """
    Deletes a transaction if it belongs to the user.
    Raises TransactionNotFoundException if the transaction does not exist or belongs to another user.
    """
    try:
        tx_id = PydanticObjectId(transaction_id)
    except Exception:
        raise TransactionNotFoundException()

    # Find the transaction and verify ownership
    transaction = await Transaction.find_one(Transaction.id == tx_id, Transaction.user_id == user_id)
    if not transaction:
        raise TransactionNotFoundException()

    await transaction.delete()
