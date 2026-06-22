import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.config import settings
from core.database import AsyncSessionLocal
from bot.handlers import start, menu, payments, admin

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def db_session_middleware(handler, event, data):
    async with AsyncSessionLocal() as session:
        data["db_session"] = session
        try:
            return await handler(event, data)
        finally:
            await session.close()

async def main():
    # Initialize Bot and Dispatcher
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    # Register Middlewares
    dp.update.outer_middleware(db_session_middleware)

    # Register Routers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(payments.router)
    dp.include_router(admin.router)

    # Set Bot Commands
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Start the bot"),
        types.BotCommand(command="wallet", description="View ticket balance"),
        types.BotCommand(command="raffles", description="List active raffles"),
        types.BotCommand(command="history", description="Transaction history"),
        types.BotCommand(command="referral", description="Referral program"),
        types.BotCommand(command="help", description="How it works"),
    ])

    # Start Polling
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
