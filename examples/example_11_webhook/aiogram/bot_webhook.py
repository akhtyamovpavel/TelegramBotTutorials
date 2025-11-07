"""
Telegram Bot Example 11: WebHook Deployment (aiogram)
Демонстрирует использование webhook вместо polling для production
"""

import logging
import os
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем настройки из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен!")

# WebHook настройки
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://example.com")  # Ваш домен
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Веб-сервер настройки
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8000))

# Secret token для безопасности (опционально, но рекомендуется)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "my-secret-token-12345")

# Роутер для обработчиков
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветствие"""
    await message.answer(
        "👋 <b>Бот работает через WebHook!</b>\n\n"
        "Это значит что Telegram отправляет обновления напрямую на наш сервер,\n"
        "вместо того чтобы бот постоянно опрашивал API.\n\n"
        "<b>Команды:</b>\n"
        "/start - Это сообщение\n"
        "/help - Справка\n"
        "/info - Информация о webhook\n"
        "/status - Статус бота",
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Справка"""
    await message.answer(
        "📚 <b>Справка по WebHook боту</b>\n\n"
        "<b>Что такое WebHook?</b>\n"
        "WebHook - это способ получения обновлений, при котором Telegram\n"
        "сам отправляет обновления на ваш сервер через HTTPS запросы.\n\n"
        "<b>Преимущества:</b>\n"
        "• Мгновенное получение сообщений\n"
        "• Меньше нагрузки на API\n"
        "• Production-ready\n"
        "• Масштабируемость\n\n"
        "<b>Требования:</b>\n"
        "• Публичный домен с HTTPS\n"
        "• Валидный SSL сертификат\n"
        "• Порт 443, 80, 88 или 8443",
        parse_mode="HTML"
    )


@router.message(Command("info"))
async def cmd_info(message: Message):
    """Информация о webhook"""
    await message.answer(
        f"ℹ️ <b>Информация о WebHook</b>\n\n"
        f"<b>Webhook URL:</b>\n<code>{WEBHOOK_URL}</code>\n\n"
        f"<b>Path:</b> <code>{WEBHOOK_PATH}</code>\n"
        f"<b>Host:</b> <code>{WEBHOOK_HOST}</code>\n"
        f"<b>Port:</b> <code>{WEBAPP_PORT}</code>\n\n"
        f"<b>Secret Token:</b> {'✅ Установлен' if WEBHOOK_SECRET else '❌ Не установлен'}\n\n"
        f"💡 <i>Для проверки статуса используйте /status</i>",
        parse_mode="HTML"
    )


@router.message(Command("status"))
async def cmd_status(message: Message, bot: Bot):
    """Статус бота и webhook"""
    try:
        # Получаем информацию о webhook
        webhook_info = await bot.get_webhook_info()

        status_text = (
            "📊 <b>Статус бота</b>\n\n"
            f"<b>URL:</b> <code>{webhook_info.url}</code>\n"
            f"<b>Pending updates:</b> {webhook_info.pending_update_count}\n"
            f"<b>Last error:</b> {webhook_info.last_error_message or 'Нет ошибок'}\n"
        )

        if webhook_info.last_error_date:
            from datetime import datetime
            error_time = datetime.fromtimestamp(webhook_info.last_error_date)
            status_text += f"<b>Last error date:</b> {error_time}\n"

        status_text += f"\n<b>Max connections:</b> {webhook_info.max_connections or 40}"

        if webhook_info.allowed_updates:
            status_text += f"\n<b>Allowed updates:</b> {', '.join(webhook_info.allowed_updates)}"

        await message.answer(status_text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Ошибка получения webhook info: {e}")
        await message.answer(
            f"❌ Ошибка получения статуса:\n<code>{str(e)}</code>",
            parse_mode="HTML"
        )


@router.message(F.text)
async def echo_message(message: Message):
    """Эхо - повторяет полученное сообщение"""
    await message.answer(
        f"📨 Получено сообщение:\n\n"
        f"<code>{message.text}</code>\n\n"
        f"💡 Это демонстрирует что WebHook работает!",
        parse_mode="HTML"
    )


async def on_startup(bot: Bot):
    """
    Вызывается при запуске бота
    Устанавливает webhook
    """
    logger.info("=" * 60)
    logger.info("🚀 Запуск WebHook бота...")
    logger.info(f"📍 Webhook URL: {WEBHOOK_URL}")
    logger.info(f"🔐 Secret Token: {'✅ Установлен' if WEBHOOK_SECRET else '❌ Не установлен'}")

    # Удаляем существующий webhook
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("🗑️ Старый webhook удален")

    # Устанавливаем новый webhook
    webhook_set = await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )

    if webhook_set:
        logger.info("✅ Webhook успешно установлен!")
    else:
        logger.error("❌ Ошибка установки webhook!")

    # Проверяем webhook
    webhook_info = await bot.get_webhook_info()
    logger.info(f"📊 Webhook info:")
    logger.info(f"   URL: {webhook_info.url}")
    logger.info(f"   Pending updates: {webhook_info.pending_update_count}")
    if webhook_info.last_error_message:
        logger.warning(f"   Last error: {webhook_info.last_error_message}")

    logger.info("=" * 60)
    logger.info(f"🌐 Веб-сервер слушает на {WEBAPP_HOST}:{WEBAPP_PORT}")
    logger.info(f"🎯 Telegram будет отправлять обновления на: {WEBHOOK_URL}")
    logger.info("=" * 60)


async def on_shutdown(bot: Bot):
    """
    Вызывается при остановке бота
    Удаляет webhook
    """
    logger.info("=" * 60)
    logger.info("🛑 Остановка бота...")
    await bot.delete_webhook()
    logger.info("🗑️ Webhook удален")
    logger.info("✅ Бот остановлен")
    logger.info("=" * 60)


@asynccontextmanager
async def lifespan_wrapper(bot: Bot, dp: Dispatcher):
    """Обертка для управления жизненным циклом"""
    await on_startup(bot)
    yield
    await on_shutdown(bot)


def main():
    """Главная функция"""
    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем роутер
    dp.include_router(router)

    # Создаем aiohttp приложение
    app = web.Application()

    # Создаем обработчик webhook
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET
    )

    # Регистрируем webhook endpoint
    webhook_handler.register(app, path=WEBHOOK_PATH)

    # Добавляем healthcheck endpoint (для мониторинга)
    async def healthcheck(request):
        return web.json_response({"status": "ok", "bot": "running"})

    app.router.add_get("/health", healthcheck)

    # Настраиваем приложение
    setup_application(app, dp, bot=bot)

    # Добавляем lifespan events
    app.on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))

    # Запускаем веб-сервер
    logger.info("Starting web server...")
    web.run_app(
        app,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
