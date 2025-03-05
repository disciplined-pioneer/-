import asyncio
import locale
import logging

from aiogram import Dispatcher
from aiogram.types import BotCommandScopeDefault

from bot.handlers import routers
from core.bot import bot
from db.crud.base import init_postgres
from settings import settings

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
dp.include_routers(*routers)


async def main():
    """
        Запуск бота
    :return:
    """
    # file = await bot.get_file('AgACAgIAAxkBAAM-Z6sfUzSD-9eJPIeYt6W5v_6j2UMAAgjtMRtpj1hJPWx7lSgtcSEBAAMCAAN5AAM2BA')
    # url = f'https://api.telegram.org/file/bot{bot.token}/{file.file_path}'
    # data = await CheckApi().info_by_img(url)
    # print(data)

    await init_postgres()
    await bot.set_my_commands(
        commands=settings.bot.COMMANDS,
        scope=BotCommandScopeDefault()
    )
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен 🛑\n")
