from config.config import load_config, Config
from aiogram import Bot

config: Config = load_config()
bot = Bot(token=config.tg_bot.token,
          parse_mode='HTML')