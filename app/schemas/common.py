from pydantic import BaseModel, Field


class Message(BaseModel):
    """Generic message response."""

    message: str
    detail: str | None = None


class PaginationParams(BaseModel):
    """Parameters for pagination."""

    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(
        default=50, ge=1, le=100, description="Maximum number of items to return"
    )
