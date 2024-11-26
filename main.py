import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from handlers import register_handlers
from config import load_config

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def main():
    config = load_config()
    if not config:
        logger.error("Ошибка загрузки конфигурации.")
        return
    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    register_handlers(dp, config)

    try:
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
