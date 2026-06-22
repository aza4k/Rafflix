from aiogram import Router, types, F
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.models import User, TicketLedger, Raffle, RaffleStatus
from core.config import settings

router = Router()

@router.message(Command("wallet"))
async def cmd_wallet(message: types.Message, db_session: AsyncSession):
    res = await db_session.execute(select(User).where(User.telegram_id == message.from_user.id))
    user = res.scalar_one_or_none()
    
    if not user:
        return await message.answer("Please /start the bot first.")

    text = (
        "💳 <b>Your Rafflix Wallet</b>\n\n"
        f"🎟️ Tickets: <b>{user.ticket_balance}</b>\n"
        f"✨ Total Earned: {user.total_earned}\n"
        f"🔥 Total Spent: {user.total_spent}\n\n"
        "You can buy more tickets with Telegram Stars in the Web App."
    )
    
    builder = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ Buy Tickets", web_app=types.WebAppInfo(url=f"{settings.WEBAPP_URL}/wallet"))]
    ])
    
    await message.answer(text, reply_markup=builder)

@router.message(Command("raffles"))
async def cmd_raffles(message: types.Message, db_session: AsyncSession):
    res = await db_session.execute(
        select(Raffle).where(Raffle.status == RaffleStatus.ACTIVE).limit(5)
    )
    active_raffles = res.scalars().all()
    
    if not active_raffles:
        return await message.answer("No active raffles at the moment. Check back soon!")

    text = "🏆 <b>Active Raffles</b>\n\n"
    for r in active_raffles:
        text += f"• {r.gift_name} ({r.gift_price} ⭐)\n"
    
    builder = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎟️ View All in Web App", web_app=types.WebAppInfo(url=settings.WEBAPP_URL))]
    ])
    
    await message.answer(text, reply_markup=builder)

@router.message(Command("history"))
async def cmd_history(message: types.Message, db_session: AsyncSession):
    res = await db_session.execute(select(User).where(User.telegram_id == message.from_user.id))
    user = res.scalar_one_or_none()
    
    if not user:
        return await message.answer("Please /start the bot first.")

    res = await db_session.execute(
        select(TicketLedger)
        .where(TicketLedger.user_id == user.id)
        .order_by(desc(TicketLedger.created_at))
        .limit(10)
    )
    ledger = res.scalars().all()
    
    if not ledger:
        return await message.answer("No transaction history yet.")

    text = "📜 <b>Last 10 Transactions</b>\n\n"
    for entry in ledger:
        sign = "+" if entry.amount > 0 else ""
        date_str = entry.created_at.strftime("%d.%m %H:%M")
        text += f"<code>{date_str}</code> | <b>{sign}{entry.amount}</b> 🎟️ | {entry.type.value}\n"
    
    await message.answer(text)

@router.message(Command("referral"))
async def cmd_referral(message: types.Message, db_session: AsyncSession):
    res = await db_session.execute(select(User).where(User.telegram_id == message.from_user.id))
    user = res.scalar_one_or_none()
    
    if not user:
        return await message.answer("Please /start the bot first.")

    text = (
        "👥 <b>Referral Program</b>\n\n"
        "Invite your friends and earn bonus tickets! When a friend joins via your link and makes their <b>first purchase</b>, you both get a bonus.\n\n"
        "🎁 <b>Reward:</b> +1 ticket for you\n\n"
        "🔗 <b>Your Link:</b>\n"
        f"<code>t.me/{settings.BOT_USERNAME}?start=ref_{user.id}</code>"
    )
    
    await message.answer(text)

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "🎬 <b>How Rafflix Works</b>\n\n"
        "1. <b>Buy Tickets:</b> Use Telegram Stars to purchase tickets (1 ticket = 1 Star).\n"
        "2. <b>Enter Raffles:</b> Pick a raffle you like and use your tickets to enter. More tickets = higher win chance!\n"
        "3. <b>The Draw:</b> Once enough Stars are collected, a winner is picked randomly.\n"
        "4. <b>Get Prizes:</b> Winners receive Telegram Gifts directly from the bot!\n\n"
        "<b>Commands:</b>\n"
        "/start - Main menu\n"
        "/wallet - Your balance\n"
        "/raffles - List prizes\n"
        "/referral - Earn free tickets"
    )
    await message.answer(text)
