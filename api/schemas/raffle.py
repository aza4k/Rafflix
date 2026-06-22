import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from core.models import RaffleStatus

class RaffleResponse(BaseModel):
    id: uuid.UUID
    title: str
    gift_name: str
    gift_price: int
    ticket_price: int
    target_stars: int
    collected_stars: int
    status: RaffleStatus
    ends_at: Optional[datetime]
    completed_at: Optional[datetime]
    winner_id: Optional[uuid.UUID]
    
    model_config = ConfigDict(from_attributes=True)

class RaffleEntryRequest(BaseModel):
    tickets: int

class RaffleEntryResponse(BaseModel):
    raffle_id: uuid.UUID
    user_id: uuid.UUID
    tickets_used: int
    
    model_config = ConfigDict(from_attributes=True)
