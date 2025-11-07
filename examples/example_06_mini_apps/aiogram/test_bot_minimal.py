"""
Минимальный тестовый бот для отладки WebApp
Используйте этот бот для проверки базовой функциональности
"""

import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.enums import UpdateType

# Настройка логирования с подробным выводом
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Токен и URL
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

if not BOT_TOKEN:
    raise ValueError("❌ Не указан BOT_TOKEN!")

if not WEBAPP_URL:
    raise ValueError("❌ Не указан WEBAPP_URL!")

logger.info(f"✅ BOT_TOKEN установлен: {BOT_TOKEN[:10]}...")
logger.info(f"✅ WEBAPP_URL установлен: {WEBAPP_URL}")

# Роутер
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветствие"""
    logger.info(f"📨 Получена команда /start от {message.from_user.id}")

    await message.answer(
        "🧪 <b>Тестовый бот для отладки WebApp</b>\n\n"
        "Команды:\n"
        "/test - Тестовая кнопка с WebApp\n"
        "/info - Показать настройки\n\n"
        "Этот бот создан для отладки. "
        "Он покажет подробные логи.",
        parse_mode="HTML"
    )


@router.message(Command("info"))
async def cmd_info(message: Message):
    """Информация о настройках"""
    logger.info(f"📨 Получена команда /info от {message.from_user.id}")

    await message.answer(
        f"ℹ️ <b>Информация о настройках:</b>\n\n"
        f"<b>WEBAPP_URL:</b>\n<code>{WEBAPP_URL}</code>\n\n"
        f"<b>Ваш User ID:</b> <code>{message.from_user.id}</code>\n"
        f"<b>Ваше имя:</b> {message.from_user.first_name}",
        parse_mode="HTML"
    )


@router.message(Command("test"))
async def cmd_test(message: Message):
    """Тестовая кнопка с WebApp"""
    logger.info(f"📨 Получена команда /test от {message.from_user.id}")
    logger.info(f"🔗 Создаем кнопку с URL: {WEBAPP_URL}")

    # ВАЖНО: sendData() работает ТОЛЬКО с KeyboardButton, НЕ с InlineKeyboardButton!
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="🧪 Открыть тестовый WebApp",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]],
        resize_keyboard=True
    )

    await message.answer(
        "🧪 <b>Тестовая кнопка</b>\n\n"
        "Нажмите кнопку ниже (в клавиатуре), чтобы открыть WebApp.\n"
        "После отправки данных бот должен ответить.\n\n"
        "⚠️ <i>Кнопка WebApp должна быть в reply-клавиатуре, не inline!</i>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    logger.info("✅ Кнопка отправлена")


@router.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    """
    Обработчик данных из WebApp
    С МАКСИМАЛЬНО ПОДРОБНЫМ ЛОГИРОВАНИЕМ
    """
    print("\n" + "=" * 70)
    print("🔴 ОБРАБОТЧИК handle_webapp_data ВЫЗВАН!")
    print("=" * 70)

    logger.info(f"🔴 От пользователя: {message.from_user.id} ({message.from_user.first_name})")
    logger.info(f"🔴 Message ID: {message.message_id}")
    logger.info(f"🔴 Chat ID: {message.chat.id}")

    try:
        # Проверяем наличие web_app_data
        if not message.web_app_data:
            logger.error("❌ message.web_app_data is None!")
            await message.answer("❌ Ошибка: web_app_data пустой")
            return

        logger.info(f"🔴 web_app_data объект: {message.web_app_data}")
        logger.info(f"🔴 web_app_data.data: {message.web_app_data.data}")
        logger.info(f"🔴 web_app_data.button_text: {message.web_app_data.button_text}")

        # Получаем данные
        webapp_data = message.web_app_data.data
        logger.info(f"✅ Получены данные из WebApp: {webapp_data}")

        print("\n📦 ПОЛУЧЕННЫЕ ДАННЫЕ:")
        print(f"   Тип: {type(webapp_data)}")
        print(f"   Длина: {len(webapp_data)}")
        print(f"   Содержимое: {webapp_data}")
        print()

        # Пытаемся распарсить JSON
        try:
            settings = json.loads(webapp_data)
            logger.info(f"✅ JSON успешно распарсен: {settings}")

            print("📋 РАСПАРСЕННЫЕ ПАРАМЕТРЫ:")
            for key, value in settings.items():
                print(f"   {key}: {value} (type: {type(value).__name__})")
            print()

            # Формируем ответ
            response_lines = ["✅ <b>Данные получены!</b>\n"]
            response_lines.append("📋 <b>Параметры:</b>\n")

            for key, value in settings.items():
                response_lines.append(f"• <b>{key}:</b> <code>{value}</code>")

            response_text = "\n".join(response_lines)

            logger.info(f"📤 Отправляем ответ пользователю...")
            await message.answer(response_text, parse_mode="HTML")
            logger.info("✅ Ответ отправлен!")

        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            logger.error(f"   Данные: {webapp_data}")

            # Отправляем как есть
            await message.answer(
                f"✅ <b>Получены данные (не JSON):</b>\n\n"
                f"<code>{webapp_data}</code>",
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"❌ ОШИБКА в обработчике: {e}")
        import traceback
        traceback.print_exc()

        await message.answer(
            f"❌ <b>Произошла ошибка:</b>\n\n"
            f"<code>{str(e)}</code>",
            parse_mode="HTML"
        )

    print("=" * 70)
    print("🔴 ОБРАБОТЧИК ЗАВЕРШЕН")
    print("=" * 70 + "\n")


@router.message()
async def handle_any_message(message: Message):
    """Ловим любые другие сообщения"""
    logger.info(f"📨 Получено сообщение от {message.from_user.id}: {message.text}")

    await message.answer(
        "ℹ️ Доступные команды:\n"
        "/start - Приветствие\n"
        "/test - Тестовая кнопка\n"
        "/info - Информация"
    )


async def main():
    """Главная функция"""
    logger.info("🚀 Запуск тестового бота...")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем роутер
    dp.include_router(router)

    logger.info("=" * 70)
    logger.info("✅ ТЕСТОВЫЙ БОТ ЗАПУЩЕН")
    logger.info("=" * 70)
    logger.info(f"📍 WEBAPP_URL: {WEBAPP_URL}")
    logger.info(f"👤 Bot запущен, ожидаем сообщения...")
    logger.info("=" * 70)

    try:
        # Запускаем polling, явно указывая что хотим получать все типы обновлений
        # Это критично важно для web_app_data!
        # UpdateType.MESSAGE включает в себя web_app_data
        await dp.start_polling(
            bot,
            allowed_updates=[UpdateType.MESSAGE]
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
