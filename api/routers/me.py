from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from api.auth import get_current_user, get_db_session
from api.schemas.user import UserResponse, LedgerResponse
from core.models import User, TicketLedger

router = APIRouter(prefix="/me", tags=["me"])

@router.get("", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user

@router.get("/history", response_model=List[LedgerResponse])
async def get_my_history(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    limit: int = 50,
    offset: int = 0
):
    res = await session.execute(
        select(TicketLedger)
        .where(TicketLedger.user_id == user.id)
        .order_by(desc(TicketLedger.created_at))
        .limit(limit)
        .offset(offset)
    )
    return res.scalars().all()
