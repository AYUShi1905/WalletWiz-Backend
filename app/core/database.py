from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.db_user import User
from app.models.db_transaction import Transaction

async def init_db():
    """
    Initializes the MongoDB connection using Motor and registers
    Beanie ODM document models (User and Transaction).
    """
    # Create the async Motor client
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    
    # Try to extract the database name from the connection string
    # If not specified, default to "expense_tracker"
    try:
        db = client.get_default_database()
        if db is None:
            db = client["expense_tracker"]
    except Exception:
        db = client["expense_tracker"]
        
    # Initialize Beanie ODM with the database and models
    await init_beanie(
        database=db,
        document_models=[
            User,
            Transaction
        ]
    )
