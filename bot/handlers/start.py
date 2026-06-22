import uuid
from typing import Optional
from aiogram import Router, types, filters
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import User, Referral, ReferralStatus
from core.config import settings

router = Router()

async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> Optional[User]:
    res = await session.execute(select(User).where(User.telegram_id == tg_id))
    return res.scalar_one_or_none()

@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject, db_session: AsyncSession):
    tg_user = message.from_user
    if not tg_user:
        return

    # 1. Check if user exists
    user = await get_user_by_tg_id(db_session, tg_user.id)
    is_new = False

    if not user:
        is_new = True
        # Create new user
        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            full_name=tg_user.full_name
        )
        db_session.add(user)
        await db_session.flush() # Get user.id

        # 2. Handle Referral
        if command.args and command.args.startswith("ref_"):
            try:
                referrer_id_str = command.args.replace("ref_", "")
                referrer_id = uuid.UUID(referrer_id_str)
                
                # Check if referrer exists and is not the same user
                res = await db_session.execute(select(User).where(User.id == referrer_id))
                referrer = res.scalar_one_or_none()
                
                if referrer and referrer.id != user.id:
                    user.referred_by = referrer.id
                    
                    # Record referral
                    referral = Referral(
                        referrer_id=referrer.id,
                        referred_id=user.id,
                        status=ReferralStatus.PENDING
                    )
                    db_session.add(referral)
            except (ValueError, Exception):
                pass # Invalid UUID or other error

        await db_session.commit()

    # 3. Welcome Message
    welcome_text = (
        f"🎬 <b>Welcome to Rafflix, {tg_user.first_name}!</b>\n\n"
        "The ultimate Telegram Gift raffle platform. "
        "Buy tickets with Stars, enter raffles, and win exclusive gifts! 🎁\n\n"
        "🔗 <b>Your Referral Link:</b>\n"
        f"<code>t.me/{settings.BOT_USERNAME}?start=ref_{user.id}</code>\n\n"
        "Use /help to learn how it works or tap the button below to open the Web App!"
    )

    builder = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🚀 Open Rafflix", web_app=types.WebAppInfo(url=settings.WEBAPP_URL))],
        [types.InlineKeyboardButton(text="💳 Wallet", callback_data="wallet_main"),
         types.InlineKeyboardButton(text="🏆 Raffles", callback_data="raffles_list")]
    ])

    await message.answer(welcome_text, reply_markup=builder)
