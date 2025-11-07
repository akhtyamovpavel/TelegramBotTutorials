"""
Telegram Bot Example 11: WebHook Deployment (python-telegram-bot)
Демонстрирует использование webhook вместо polling для production
"""

import logging
import os
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие"""
    await update.message.reply_text(
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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Справка"""
    await update.message.reply_text(
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


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация о webhook"""
    await update.message.reply_text(
        f"ℹ️ <b>Информация о WebHook</b>\n\n"
        f"<b>Webhook URL:</b>\n<code>{WEBHOOK_URL}</code>\n\n"
        f"<b>Path:</b> <code>{WEBHOOK_PATH}</code>\n"
        f"<b>Host:</b> <code>{WEBHOOK_HOST}</code>\n"
        f"<b>Port:</b> <code>{WEBAPP_PORT}</code>\n\n"
        f"<b>Secret Token:</b> {'✅ Установлен' if WEBHOOK_SECRET else '❌ Не установлен'}\n\n"
        f"💡 <i>Для проверки статуса используйте /status</i>",
        parse_mode="HTML"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Статус бота и webhook"""
    try:
        # Получаем информацию о webhook
        webhook_info = await context.bot.get_webhook_info()

        status_text = (
            "📊 <b>Статус бота</b>\n\n"
            f"<b>URL:</b> <code>{webhook_info.url}</code>\n"
            f"<b>Pending updates:</b> {webhook_info.pending_update_count}\n"
            f"<b>Last error:</b> {webhook_info.last_error_message or 'Нет ошибок'}\n"
        )

        if webhook_info.last_error_date:
            error_time = webhook_info.last_error_date
            status_text += f"<b>Last error date:</b> {error_time}\n"

        status_text += f"\n<b>Max connections:</b> {webhook_info.max_connections or 40}"

        if webhook_info.allowed_updates:
            status_text += f"\n<b>Allowed updates:</b> {', '.join(webhook_info.allowed_updates)}"

        await update.message.reply_text(status_text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Ошибка получения webhook info: {e}")
        await update.message.reply_text(
            f"❌ Ошибка получения статуса:\n<code>{str(e)}</code>",
            parse_mode="HTML"
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Эхо - повторяет полученное сообщение"""
    await update.message.reply_text(
        f"📨 Получено сообщение:\n\n"
        f"<code>{update.message.text}</code>\n\n"
        f"💡 Это демонстрирует что WebHook работает!",
        parse_mode="HTML"
    )


async def post_init(application: Application) -> None:
    """
    Вызывается после инициализации
    Устанавливает webhook
    """
    logger.info("=" * 60)
    logger.info("🚀 Запуск WebHook бота...")
    logger.info(f"📍 Webhook URL: {WEBHOOK_URL}")
    logger.info(f"🔐 Secret Token: {'✅ Установлен' if WEBHOOK_SECRET else '❌ Не установлен'}")

    # Устанавливаем webhook
    await application.bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )

    logger.info("✅ Webhook успешно установлен!")

    # Проверяем webhook
    webhook_info = await application.bot.get_webhook_info()
    logger.info(f"📊 Webhook info:")
    logger.info(f"   URL: {webhook_info.url}")
    logger.info(f"   Pending updates: {webhook_info.pending_update_count}")
    if webhook_info.last_error_message:
        logger.warning(f"   Last error: {webhook_info.last_error_message}")

    logger.info("=" * 60)
    logger.info(f"🌐 Веб-сервер слушает на {WEBAPP_HOST}:{WEBAPP_PORT}")
    logger.info(f"🎯 Telegram будет отправлять обновления на: {WEBHOOK_URL}")
    logger.info("=" * 60)


async def post_shutdown(application: Application) -> None:
    """
    Вызывается при остановке
    Удаляет webhook
    """
    logger.info("=" * 60)
    logger.info("🛑 Остановка бота...")
    await application.bot.delete_webhook()
    logger.info("🗑️ Webhook удален")
    logger.info("✅ Бот остановлен")
    logger.info("=" * 60)


def main() -> None:
    """Главная функция"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("status", status_command))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Регистрируем callbacks для startup/shutdown
    application.post_init = post_init
    application.post_shutdown = post_shutdown

    # Запускаем webhook
    logger.info("Starting webhook server...")
    application.run_webhook(
        listen=WEBAPP_HOST,
        port=WEBAPP_PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
