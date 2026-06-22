from aiogram import Bot
from core.models import Raffle, User
from core.config import settings

async def announce_new_raffle(bot: Bot, raffle: Raffle):
    """
    Posts a new raffle to the configured channel.
    """
    text = (
        f"🎬 <b>RAFFLIX — NEW RAFFLE</b>\n\n"
        f"🎁 Prize: <b>{raffle.gift_name}</b>\n"
        f"💰 Value: {raffle.gift_price} ⭐\n"
        f"🎟️ Ticket Price: {raffle.ticket_price} ticket\n"
        f"🎯 Target Pool: {raffle.target_stars} ⭐\n"
        f"👥 spots available!\n\n"
        f"Join now and win this gift! 🚀"
    )
    
    builder = [[{"text": "🎟️ Join on Rafflix", "web_app": {"url": settings.WEBAPP_URL}}]]
    
    try:
        await bot.send_message(
            chat_id=settings.CHANNEL_ID,
            text=text,
            reply_markup={"inline_keyboard": builder}
        )
    except Exception as e:
        print(f"Failed to announce raffle: {e}")

async def announce_winner(bot: Bot, raffle: Raffle, winner: User):
    """
    Announces the winner of a completed raffle.
    """
    text = (
        f"🎬 <b>RAFFLIX — RAFFLE COMPLETE</b>\n\n"
        f"🎁 Prize: <b>{raffle.gift_name}</b>\n"
        f"🎉 Winner: <b>{winner.full_name or winner.username or 'User'}</b>\n"
        f"⭐ Pool: {raffle.collected_stars} Stars collected\n\n"
        f"Congratulations! The gift has been sent to the winner! 🎁"
    )
    
    try:
        await bot.send_message(
            chat_id=settings.CHANNEL_ID,
            text=text
        )
    except Exception as e:
        print(f"Failed to announce winner: {e}")
