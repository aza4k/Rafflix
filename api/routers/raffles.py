from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update
from typing import List
import uuid
from api.auth import get_current_user, get_db_session
from api.schemas.raffle import RaffleResponse, RaffleEntryRequest, RaffleEntryResponse
from core.models import User, Raffle, RaffleStatus, RaffleEntry, LedgerType
from core.wallet import debit_tickets, InsufficientTicketsError

router = APIRouter(prefix="/raffles", tags=["raffles"])

@router.get("", response_model=List[RaffleResponse])
async def list_active_raffles(
    session: AsyncSession = Depends(get_db_session)
):
    res = await session.execute(
        select(Raffle)
        .where(Raffle.status == RaffleStatus.ACTIVE)
        .order_by(desc(Raffle.created_at))
    )
    return res.scalars().all()

@router.get("/{raffle_id}", response_model=RaffleResponse)
async def get_raffle(
    raffle_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    res = await session.execute(select(Raffle).where(Raffle.id == raffle_id))
    raffle = res.scalar_one_or_none()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    return raffle

@router.post("/{raffle_id}/enter", response_model=RaffleEntryResponse)
async def enter_raffle(
    raffle_id: uuid.UUID,
    request: RaffleEntryRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    # 1. Get Raffle
    res = await session.execute(select(Raffle).where(Raffle.id == raffle_id).with_for_update())
    raffle = res.scalar_one_or_none()
    
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    if raffle.status != RaffleStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Raffle is not active")

    # 2. Debit Tickets
    try:
        await debit_tickets(
            session, 
            user.id, 
            request.tickets, 
            LedgerType.RAFFLE_ENTRY, 
            ref_raffle_id=raffle_id,
            note=f"Entered {raffle.title}"
        )
    except InsufficientTicketsError:
        raise HTTPException(status_code=400, detail="Not enough tickets in wallet")

    # 3. Create or update entry
    res = await session.execute(
        select(RaffleEntry)
        .where(RaffleEntry.raffle_id == raffle_id, RaffleEntry.user_id == user.id)
    )
    entry = res.scalar_one_or_none()
    
    if entry:
        entry.tickets_used += request.tickets
    else:
        entry = RaffleEntry(
            raffle_id=raffle_id,
            user_id=user.id,
            tickets_used=request.tickets
        )
        session.add(entry)

    # 4. We don't update collected_stars here because that tracks real Stars, not entries.
    # Entry with bonus tickets is allowed.
    
    await session.commit()
    return entry
