import random
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from core.models import Raffle, RaffleStatus, RaffleEntry, User

async def draw_winner(session: AsyncSession, raffle_id: uuid.UUID) -> Optional[uuid.UUID]:
    """
    Executes the weighted drawing algorithm for a raffle.
    Returns the winner_id or None if no entries.
    """
    # 1. Fetch raffle and lock for update
    res = await session.execute(
        select(Raffle).where(Raffle.id == raffle_id).with_for_update()
    )
    raffle = res.scalar_one_or_none()
    
    if not raffle or raffle.status != RaffleStatus.ACTIVE:
        return None

    # 2. Set status to DRAWING to prevent new entries
    raffle.status = RaffleStatus.DRAWING
    await session.flush()

    # 3. Fetch all entries
    res = await session.execute(
        select(RaffleEntry).where(RaffleEntry.raffle_id == raffle_id)
    )
    entries = res.scalars().all()
    
    if not entries:
        # No participants, maybe cancel or extend?
        # For now, just mark as cancelled if no entries and it was reached
        raffle.status = RaffleStatus.CANCELLED
        await session.commit()
        return None

    # 4. Build weighted pool
    # Optimization: Instead of expanding a huge list, use prefix sums
    total_tickets = sum(e.tickets_used for e in entries)
    pick = random.randint(1, total_tickets)
    
    current = 0
    winner_id = None
    for entry in entries:
        current += entry.tickets_used
        if pick <= current:
            winner_id = entry.user_id
            break
            
    # 5. Record winner
    raffle.winner_id = winner_id
    raffle.status = RaffleStatus.COMPLETED
    from datetime import datetime
    raffle.completed_at = datetime.utcnow()
    
    # Placeholder: Notify winner/Admin about prize delivery
    # This should be handled by a task after commit
    
    await session.commit()
    return winner_id
