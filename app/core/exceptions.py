from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


async def database_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Database constraint violation", 
            "type": "integrity_error",
            "message": "The requested operation violates a database constraint"
        }
    )


async def validation_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": str(exc), 
            "type": "validation_error",
            "message": "The provided data failed validation"
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_error",
            "status_code": exc.status_code
        },
        headers=getattr(exc, "headers", None),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup custom exception handlers."""
    app.add_exception_handler(IntegrityError, database_exception_handler)
    app.add_exception_handler(ValueError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)