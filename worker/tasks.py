import asyncio
import logging
from uuid import UUID
from .celery_app import celery_app
from core.database import AsyncSessionLocal
from core.models import Raffle, RaffleStatus
from core.draw import draw_winner
from core.streaks import update_user_streaks
from sqlalchemy import select

logger = logging.getLogger(__name__)

def run_async(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # In case we're somehow already in an event loop
        new_loop = asyncio.new_event_loop()
        return new_loop.run_until_complete(coro)
    return loop.run_until_complete(coro)

@celery_app.task
def check_raffles():
    """
    Check for raffles that reached their target stars and trigger drawing.
    """
    async def _logic():
        async with AsyncSessionLocal() as session:
            # Find active raffles where collected_stars >= target_stars
            res = await session.execute(
                select(Raffle).where(
                    Raffle.status == RaffleStatus.ACTIVE,
                    Raffle.collected_stars >= Raffle.target_stars
                )
            )
            raffles = res.scalars().all()
            
            for raffle in raffles:
                logger.info(f"Triggering draw for raffle {raffle.id}")
                process_draw.delay(str(raffle.id))
                
    run_async(_logic())

@celery_app.task
def process_draw(raffle_id_str: str):
    """
    Execute the draw and update streaks.
    """
    raffle_id = UUID(raffle_id_str)
    
    async def _logic():
        async with AsyncSessionLocal() as session:
            # 1. Draw winner
            winner_id = await draw_winner(session, raffle_id)
            if winner_id:
                logger.info(f"Winner for raffle {raffle_id}: {winner_id}")
                
                # 2. Update user streaks
                await update_user_streaks(session, raffle_id)
                
                # 3. Notify winner (logic to be added: calling bot API)
                
    run_async(_logic())
