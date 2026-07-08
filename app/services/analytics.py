from datetime import datetime, timedelta, time
from typing import Optional, Tuple
from beanie import PydanticObjectId
from app.models.db_transaction import Transaction
from app.models.response import (
    DashboardResponse,
    CategorySpending,
    PaymentMethodSpending,
    DailySpending
)

def get_timeframe_range(timeframe: Optional[str]) -> Tuple[datetime, datetime]:
    """
    Helper function to determine the start and end datetime
    for a given timeframe query.
    """
    now = datetime.utcnow()
    end_date = now

    if timeframe == "last-30-days":
        start_date = datetime.combine(now.date() - timedelta(days=30), time.min)
    elif timeframe == "this-year":
        start_date = datetime(now.year, 1, 1, 0, 0, 0)
    else:  # "this-month" (default)
        start_date = datetime(now.year, now.month, 1, 0, 0, 0)

    return start_date, end_date

async def get_dashboard_data(user_id: PydanticObjectId, timeframe: Optional[str] = None) -> DashboardResponse:
    """
    Aggregates transaction data for the authenticated user during the
    specified timeframe, calculating total spent, daily average, category
    breakdowns, payment method breakdowns, daily trends, and fetching the 5
    most recent transactions.
    """
    start_date, end_date = get_timeframe_range(timeframe)

    # 1. Pipeline for Total Spent
    pipeline_total = [
        {
            "$match": {
                "user_id": user_id,
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_spent": {"$sum": "$amount"}
            }
        }
    ]
    result_total = await Transaction.aggregate(pipeline_total).to_list()
    total_spent = result_total[0]["total_spent"] if result_total else 0.0

    # Calculate daily average
    num_days = (end_date - start_date).days
    if num_days <= 0:
        num_days = 1
    daily_average = total_spent / num_days

    # 2. Pipeline for Category Breakdown
    pipeline_category = [
        {
            "$match": {
                "user_id": user_id,
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": "$category",
                "amount": {"$sum": "$amount"}
            }
        },
        {"$sort": {"amount": -1}}
    ]
    result_category = await Transaction.aggregate(pipeline_category).to_list()
    by_category = [
        CategorySpending(
            category=str(item["_id"]),
            amount=round(item["amount"], 2),
            percentage=round((item["amount"] / total_spent * 100), 1) if total_spent > 0 else 0.0
        )
        for item in result_category
    ]

    # 3. Pipeline for Payment Method Breakdown
    pipeline_payment = [
        {
            "$match": {
                "user_id": user_id,
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": "$payment_method",
                "amount": {"$sum": "$amount"}
            }
        },
        {"$sort": {"amount": -1}}
    ]
    result_payment = await Transaction.aggregate(pipeline_payment).to_list()
    by_payment_method = [
        PaymentMethodSpending(
            payment_method=str(item["_id"]),
            amount=round(item["amount"], 2),
            percentage=round((item["amount"] / total_spent * 100), 1) if total_spent > 0 else 0.0
        )
        for item in result_payment
    ]

    # 4. Pipeline for Daily Spending Trend
    pipeline_trend = [
        {
            "$match": {
                "user_id": user_id,
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$transaction_date"
                    }
                },
                "amount": {"$sum": "$amount"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    result_trend = await Transaction.aggregate(pipeline_trend).to_list()
    daily_trend = [
        DailySpending(
            date=str(item["_id"]),
            amount=round(item["amount"], 2)
        )
        for item in result_trend
    ]

    # 5. Fetch Recent Transactions (Limit 5)
    recent_transactions = await Transaction.find(
        Transaction.user_id == user_id
    ).sort(-Transaction.transaction_date).limit(5).to_list()

    # Import and map recent transactions to Response schemas
    from app.api.v1.transactions import map_to_response
    mapped_recent = [map_to_response(tx) for tx in recent_transactions]

    return DashboardResponse(
        total_spent=round(total_spent, 2),
        daily_average=round(daily_average, 2),
        by_category=by_category,
        by_payment_method=by_payment_method,
        daily_trend=daily_trend,
        recent_transactions=mapped_recent
    )
