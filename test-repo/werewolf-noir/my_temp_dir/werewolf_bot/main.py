import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from database import init_db
from handlers import router
import os
from dotenv import load_dotenv

load_dotenv()

# To run this bot locally, replace 'YOUR_BOT_TOKEN_HERE' with your real bot token
# or set the BOT_TOKEN environment variable. 
API_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    dp.include_router(router)
    
    print("Бот успешно запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
