import asyncio
import logging

from aiogram import Dispatcher
from handlers import user_handlers, callback_handlers
from data.database import Database
from notification.notification import scheduler
from bot_instance import bot

logger = logging.getLogger(__name__)
db_manager = Database()


async def on_startup():
    scheduler.start()


async def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(filename)s:%(lineno)d #%(levelname)-8s '
                               '[%(asctime)s] - %(name)s - %(message)s')
    logger.info('Starting bot')

    dp = Dispatcher()

    dp.include_router(user_handlers.router)
    dp.include_router(callback_handlers.router)

    await on_startup()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
