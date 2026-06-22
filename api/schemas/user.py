import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: uuid.UUID
    telegram_id: int
    username: Optional[str]
    full_name: Optional[str]
    ticket_balance: int
    total_earned: int
    total_spent: int
    streak_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LedgerResponse(BaseModel):
    id: uuid.UUID
    amount: int
    type: str # Enum value
    note: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
