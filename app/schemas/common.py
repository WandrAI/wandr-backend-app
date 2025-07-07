from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None