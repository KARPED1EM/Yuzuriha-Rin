from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Session(BaseModel):
    id: str
    character_id: str
    is_active: bool = False
    created_at: Optional[datetime] = None
