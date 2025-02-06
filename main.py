import logging
import asyncio
from aiogram import Bot, Dispatcher

from handlers.public_chat import router as public_router
from handlers.private_chat import router as private_router
from handlers.welcome_in_bot import router as welcome_router

from handlers.public_chat import init_db as public_db
from handlers.private_chat import init_db as private_db

from config import settings


async def main():
    public_db()
    private_db()

    # Создаем бота и диспетчер
    bot = Bot(token=settings.TOKEN.get_secret_value())
    dp = Dispatcher()

    # # Регистрируем middleware
    # dp.message.middleware(MessageMarkerMiddleware())

    # Регистрируем роутеры
    dp.include_router(welcome_router)
    dp.include_router(private_router)
    dp.include_router(public_router)

    await dp.start_polling(bot)


# Запускаем бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
