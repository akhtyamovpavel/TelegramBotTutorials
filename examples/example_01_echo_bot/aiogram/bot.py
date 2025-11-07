import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Получаем токен из переменных окружения
TOKEN = getenv("BOT_TOKEN")

# Создаем роутер для обработчиков
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start
    """
    await message.answer(f"Привет, {message.from_user.full_name}! Я эхо-бот. Отправь мне любое сообщение!")


@router.message(F.text)
async def echo_handler(message: Message) -> None:
    """
    Обработчик текстовых сообщений - повторяет сообщение пользователя
    """
    await message.answer(f"Вы написали: {message.text}")


async def main() -> None:
    # Инициализируем бота с настройками по умолчанию (HTML парсинг)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Создаем диспетчер
    dp = Dispatcher()

    # Регистрируем роутер
    dp.include_router(router)

    # Запускаем polling (бот начинает получать обновления)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
