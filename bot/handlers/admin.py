from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.models import User, Raffle, RaffleStatus
from core.config import settings
from datetime import datetime

router = Router()

class RaffleCreation(StatesGroup):
    title = State()
    gift_name = State()
    gift_price = State()
    multiplier = State()
    ticket_price = State()
    confirm = State()

def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="🆕 New Raffle"), types.KeyboardButton(text="📊 Stats")],
        [types.KeyboardButton(text="🏠 Back to Menu")]
    ], resize_keyboard=True)
    
    await message.answer("🛠️ <b>Admin Panel</b>", reply_markup=keyboard)

@router.message(F.text == "🆕 New Raffle")
@router.message(Command("newraffle"))
async def start_new_raffle(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(RaffleCreation.title)
    await message.answer("Enter Raffle Title (e.g. '🧸 Teddy Bear Raffle'):")

@router.message(RaffleCreation.title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(RaffleCreation.gift_name)
    await message.answer("Enter Gift Internal Name/ID:")

@router.message(RaffleCreation.gift_name)
async def process_gift_name(message: types.Message, state: FSMContext):
    await state.update_data(gift_name=message.text)
    await state.set_state(RaffleCreation.gift_price)
    await message.answer("Enter Gift Price in Stars:")

@router.message(RaffleCreation.gift_price)
async def process_gift_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Please enter a number.")
    await state.update_data(gift_price=int(message.text))
    await state.set_state(RaffleCreation.multiplier)
    await message.answer("Enter Multiplier (default 3.0):")

@router.message(RaffleCreation.multiplier)
async def process_multiplier(message: types.Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        val = 3.0
    await state.update_data(multiplier=val)
    await state.set_state(RaffleCreation.ticket_price)
    await message.answer("Enter Ticket Price (default 1):")

@router.message(RaffleCreation.ticket_price)
async def process_ticket_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        val = 1
    else:
        val = int(message.text)
    
    data = await state.get_data()
    target_stars = int(data['gift_price'] * data['multiplier'])
    await state.update_data(ticket_price=val, target_stars=target_stars)
    
    text = (
        "✅ <b>Confirm Raffle Creation</b>\n\n"
        f"Title: {data['title']}\n"
        f"Gift: {data['gift_name']}\n"
        f"Price: {data['gift_price']} ⭐\n"
        f"Multiplier: {data.get('multiplier', 3.0)}x\n"
        f"Target Pool: {target_stars} ⭐\n"
        f"Ticket Price: {val} 🎟️\n\n"
        "Create this raffle?"
    )
    
    builder = types.InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🚀 Create", callback_data="confirm_raffle_creation"))
    builder.add(types.InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_raffle_creation"))
    
    await state.set_state(RaffleCreation.confirm)
    await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data == "confirm_raffle_creation", RaffleCreation.confirm)
async def confirm_creation(callback: types.CallbackQuery, state: FSMContext, db_session: AsyncSession):
    data = await state.get_data()
    
    # Get admin user ID from DB
    res = await db_session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    admin_user = res.scalar_one_or_none()
    
    raffle = Raffle(
        title=data['title'],
        gift_name=data['gift_name'],
        gift_price=data['gift_price'],
        multiplier=data['multiplier'],
        target_stars=data['target_stars'],
        ticket_price=data['ticket_price'],
        status=RaffleStatus.ACTIVE,
        created_by=admin_user.id
    )
    db_session.add(raffle)
    await db_session.commit()
    
    await state.clear()
    await callback.message.edit_text("🚀 Raffle created and is now active!")

@router.message(F.text == "📊 Stats")
@router.message(Command("stats"))
async def cmd_stats(message: types.Message, db_session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
        
    user_count = await db_session.execute(select(func.count(User.id)))
    raffle_count = await db_session.execute(select(func.count(Raffle.id)))
    active_raffles = await db_session.execute(select(func.count(Raffle.id)).where(Raffle.status == RaffleStatus.ACTIVE))
    total_stars = await db_session.execute(select(func.sum(Raffle.collected_stars)))
    
    text = (
        "📊 <b>Global Statistics</b>\n\n"
        f"Total Users: {user_count.scalar()}\n"
        f"Total Raffles: {raffle_count.scalar()}\n"
        f"Active Raffles: {active_raffles.scalar()}\n"
        f"Total Stars Collected: {total_stars.scalar() or 0} ⭐"
    )
    await message.answer(text)
