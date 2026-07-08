from fastapi import APIRouter, Depends, Query
from typing import Optional
from api.dependencies import get_current_user
from models.db_user import User
from models.response import DashboardResponse
from services import analytics as analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    timeframe: Optional[str] = Query(
        None,
        description="Timeframe for the dashboard statistics: 'this-month' (default), 'last-30-days', or 'this-year'."
    ),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the dashboard statistics for the authenticated user.
    Includes total spent, daily average, category and payment method breakdowns,
    spending trends over time, and the 5 most recent transactions.
    """
    return await analytics_service.get_dashboard_data(current_user.id, timeframe)
