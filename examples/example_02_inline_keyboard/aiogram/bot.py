import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

TOKEN = getenv("BOT_TOKEN")
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Отправляет приветствие с inline-клавиатурой
    """
    # Создаем inline-клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Опция 1 ✅", callback_data="option_1"),
            InlineKeyboardButton(text="Опция 2 ⭐", callback_data="option_2")
        ],
        [
            InlineKeyboardButton(text="Опция 3 🎯", callback_data="option_3")
        ]
    ])

    await message.answer(
        "Выберите опцию:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("option_"))
async def handle_option(callback: CallbackQuery) -> None:
    """
    Обработчик нажатий на inline-кнопки
    """
    # Получаем данные из callback_data
    option = callback.data

    # Отвечаем на callback (убирает "часики" загрузки)
    await callback.answer()

    # Редактируем сообщение
    option_texts = {
        "option_1": "Вы выбрали Опцию 1 ✅",
        "option_2": "Вы выбрали Опцию 2 ⭐",
        "option_3": "Вы выбрали Опцию 3 🎯"
    }

    await callback.message.edit_text(option_texts.get(option, "Неизвестная опция"))


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
