from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from beanie import init_beanie
from core.config import settings
from models.db_user import User
from models.db_transaction import Transaction

# Monkeypatch AsyncIOMotorClient to support append_metadata (no-op)
# This is a compatibility workaround for Beanie v2.1.0 running on Motor v3.x / PyMongo v4.x,
# where append_metadata was removed from the MongoDB client.
if not hasattr(AsyncIOMotorClient, "append_metadata"):
    AsyncIOMotorClient.append_metadata = lambda *args, **kwargs: None

# Monkeypatch AsyncIOMotorCollection.aggregate to be awaitable
# In Motor v3.x, collection.aggregate(...) is synchronous, but Beanie v2.1.0
# expects it to be asynchronous and awaits it, causing a TypeError.
# Wrapping it in an async function resolves this incompatibility.
original_aggregate = AsyncIOMotorCollection.aggregate

async def async_aggregate(self, *args, **kwargs):
    return original_aggregate(self, *args, **kwargs)

AsyncIOMotorCollection.aggregate = async_aggregate

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
