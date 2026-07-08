from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class WalletWizException(Exception):
    """Base exception class for WalletWiz application errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserAlreadyExistsException(WalletWizException):
    """Raised when a registration attempt is made with an existing email."""
    def __init__(self, message: str = "A user with this email already exists"):
        super().__init__(message, status_code=400)

class InvalidCredentialsException(WalletWizException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, status_code=401)

class TransactionNotFoundException(WalletWizException):
    """Raised when a requested transaction ID does not exist."""
    def __init__(self, message: str = "Transaction not found"):
        super().__init__(message, status_code=404)

class UnauthorizedException(WalletWizException):
    """Raised when user permissions are invalid or missing."""
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message, status_code=401)

def register_exception_handlers(app: FastAPI):
    """Registers global exception handlers for FastAPI integration."""
    @app.exception_handler(WalletWizException)
    async def walletwiz_exception_handler(request: Request, exc: WalletWizException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
