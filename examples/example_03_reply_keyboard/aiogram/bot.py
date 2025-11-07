import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

TOKEN = getenv("BOT_TOKEN")
router = Router()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает главную клавиатуру с кнопками
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Статистика"),
                KeyboardButton(text="⚙️ Настройки")
            ],
            [
                KeyboardButton(text="ℹ️ Помощь"),
                KeyboardButton(text="📞 Контакт")
            ],
            [
                KeyboardButton(text="🌍 Отправить локацию", request_location=True)
            ],
            [
                KeyboardButton(text="📱 Отправить контакт", request_contact=True)
            ]
        ],
        resize_keyboard=True,  # Автоматически подгоняет размер кнопок
        one_time_keyboard=False,  # Клавиатура не скрывается после нажатия
        input_field_placeholder="Выберите действие..."  # Подсказка в поле ввода
    )
    return keyboard


def get_settings_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру настроек
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔔 Уведомления"),
                KeyboardButton(text="🌙 Темная тема")
            ],
            [
                KeyboardButton(text="🔙 Назад")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    """
    Обработчик команды /start - показывает главную клавиатуру
    """
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n\n"
        "Это пример бота с Reply Keyboard (обычные кнопки).\n"
        "Выберите действие на клавиатуре ниже:",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("hide"))
async def command_hide(message: Message) -> None:
    """
    Скрывает клавиатуру
    """
    await message.answer(
        "Клавиатура скрыта. Используйте /start для её отображения.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message) -> None:
    """
    Обработчик кнопки "Статистика"
    """
    await message.answer(
        "📊 <b>Ваша статистика:</b>\n\n"
        "Сообщений отправлено: 42\n"
        "Дней в боте: 5\n"
        "Рейтинг: ⭐⭐⭐⭐⭐"
    )


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message) -> None:
    """
    Обработчик кнопки "Настройки" - показывает другую клавиатуру
    """
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Выберите, что хотите изменить:",
        reply_markup=get_settings_keyboard()
    )


@router.message(F.text == "🔙 Назад")
async def back_to_main(message: Message) -> None:
    """
    Возврат к главной клавиатуре
    """
    await message.answer(
        "Возвращаемся в главное меню:",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "🔔 Уведомления")
async def toggle_notifications(message: Message) -> None:
    """
    Обработчик кнопки "Уведомления"
    """
    await message.answer("🔔 Уведомления включены!")


@router.message(F.text == "🌙 Темная тема")
async def toggle_dark_mode(message: Message) -> None:
    """
    Обработчик кнопки "Темная тема"
    """
    await message.answer("🌙 Темная тема активирована!")


@router.message(F.text == "ℹ️ Помощь")
async def show_help(message: Message) -> None:
    """
    Обработчик кнопки "Помощь"
    """
    await message.answer(
        "ℹ️ <b>Помощь</b>\n\n"
        "Это демонстрационный бот с Reply Keyboard.\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Показать главное меню\n"
        "/hide - Скрыть клавиатуру\n\n"
        "<b>Кнопки:</b>\n"
        "• 📊 Статистика - ваша статистика\n"
        "• ⚙️ Настройки - настройки бота\n"
        "• 🌍 Локация - отправить геопозицию\n"
        "• 📱 Контакт - поделиться контактом"
    )


@router.message(F.text == "📞 Контакт")
async def show_contact_info(message: Message) -> None:
    """
    Обработчик кнопки "Контакт"
    """
    await message.answer(
        "📞 <b>Контактная информация:</b>\n\n"
        "Email: support@example.com\n"
        "Telegram: @example_bot"
    )


@router.message(F.location)
async def handle_location(message: Message) -> None:
    """
    Обработчик геолокации
    """
    location = message.location
    await message.answer(
        f"📍 Спасибо за локацию!\n\n"
        f"Широта: {location.latitude}\n"
        f"Долгота: {location.longitude}\n\n"
        f"Ссылка на карту: "
        f"https://www.google.com/maps?q={location.latitude},{location.longitude}"
    )


@router.message(F.contact)
async def handle_contact(message: Message) -> None:
    """
    Обработчик контакта
    """
    contact = message.contact
    await message.answer(
        f"📱 Спасибо за контакт!\n\n"
        f"Имя: {contact.first_name} {contact.last_name or ''}\n"
        f"Телефон: {contact.phone_number}"
    )


@router.message(F.text)
async def handle_text(message: Message) -> None:
    """
    Обработчик любого другого текста
    """
    await message.answer(
        f"Вы написали: {message.text}\n\n"
        "Используйте кнопки на клавиатуре для навигации."
    )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
