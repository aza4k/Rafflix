import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from core.models import User, RaffleEntry, LedgerType
from core.wallet import credit_tickets

async def update_user_streaks(session: AsyncSession, raffle_id: uuid.UUID):
    """
    Updates user streak counts after a raffle completion.
    Participants get +1, everyone else resets to 0.
    """
    # 1. Get all participants for this raffle
    res = await session.execute(
        select(RaffleEntry.user_id).where(RaffleEntry.raffle_id == raffle_id)
    )
    participant_ids = res.scalars().all()

    # 2. Update participants
    if participant_ids:
        # Increment streak_count for participants
        await session.execute(
            update(User)
            .where(User.id.in_(participant_ids))
            .values(streak_count=User.streak_count + 1)
        )
        
        # 3. Check for bonuses for participants
        res = await session.execute(
            select(User).where(User.id.in_(participant_ids))
        )
        participants = res.scalars().all()
        
        for user in participants:
            if user.streak_count == 5:
                await credit_tickets(
                    session, user.id, 1, LedgerType.STREAK_BONUS, 
                    ref_raffle_id=raffle_id, note="5-raffle streak bonus!"
                )
            elif user.streak_count == 10:
                await credit_tickets(
                    session, user.id, 3, LedgerType.STREAK_BONUS, 
                    ref_raffle_id=raffle_id, note="10-raffle streak bonus!"
                )
    
    # 4. Reset everyone else who wasn't in this raffle but has a streak > 0
    # This might be tricky if we have millions of users. 
    # Usually we only reset those who were active recently.
    await session.execute(
        update(User)
        .where(User.id.notin_(participant_ids if participant_ids else [uuid.uuid4()]))
        .where(User.streak_count > 0)
        .values(streak_count=0)
    )
    
    await session.commit()
