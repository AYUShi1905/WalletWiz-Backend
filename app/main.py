from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from core.config import settings
from core.database import init_db
from core.exceptions import register_exception_handlers
from api.v1.auth import router as auth_router
from api.v1.transactions import router as transactions_router
from api.v1.analytics import router as analytics_router
from api.v1.query import router as chat_router, limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    print("--- Starting WalletWiz Backend ---")
    try:
        print("Connecting and initializing MongoDB Atlas Beanie models...")
        await init_db()
        print("✅ Database initialization successful.")
    except Exception as e:
        print(f"❌ Critical Error during database startup: {e}")
        raise e
    
    yield
    
    # Shutdown sequence
    print("--- Shutting down WalletWiz Backend ---")

# Instantiate FastAPI application
app = FastAPI(
    title="WalletWiz Backend API",
    description="Intelligent, backend-only expense tracking system powered by Gemini 2.5 Flash.",
    version="1.0.0",
    lifespan=lifespan
)

# Connect slowapi rate-limiting state and handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS Middleware
# Allows the frontend client (e.g. React/Vite running on localhost) to query the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom global exception handlers
register_exception_handlers(app)

# Include API Routers under /api/v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
async def health_check():
    """
    Base health-check endpoint to verify if the server is running.
    """
    return {
        "status": "online",
        "message": "Welcome to WalletWiz API!",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
