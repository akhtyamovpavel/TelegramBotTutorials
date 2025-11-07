import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает главную клавиатуру с кнопками
    """
    keyboard = [
        [
            KeyboardButton("📊 Статистика"),
            KeyboardButton("⚙️ Настройки")
        ],
        [
            KeyboardButton("ℹ️ Помощь"),
            KeyboardButton("📞 Контакт")
        ],
        [
            KeyboardButton("🌍 Отправить локацию", request_location=True)
        ],
        [
            KeyboardButton("📱 Отправить контакт", request_contact=True)
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,  # Автоматически подгоняет размер кнопок
        one_time_keyboard=False,  # Клавиатура не скрывается после нажатия
        input_field_placeholder="Выберите действие..."  # Подсказка в поле ввода
    )


def get_settings_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру настроек
    """
    keyboard = [
        [
            KeyboardButton("🔔 Уведомления"),
            KeyboardButton("🌙 Темная тема")
        ],
        [
            KeyboardButton("🔙 Назад")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start - показывает главную клавиатуру
    """
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.full_name}!\n\n"
        "Это пример бота с Reply Keyboard (обычные кнопки).\n"
        "Выберите действие на клавиатуре ниже:",
        reply_markup=get_main_keyboard()
    )


async def hide_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Скрывает клавиатуру
    """
    await update.message.reply_text(
        "Клавиатура скрыта. Используйте /start для её отображения.",
        reply_markup=ReplyKeyboardRemove()
    )


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик кнопки "Статистика"
    """
    await update.message.reply_text(
        "📊 <b>Ваша статистика:</b>\n\n"
        "Сообщений отправлено: 42\n"
        "Дней в боте: 5\n"
        "Рейтинг: ⭐⭐⭐⭐⭐",
        parse_mode="HTML"
    )


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик кнопки "Настройки" - показывает другую клавиатуру
    """
    await update.message.reply_text(
        "⚙️ <b>Настройки</b>\n\n"
        "Выберите, что хотите изменить:",
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Возврат к главной клавиатуре
    """
    await update.message.reply_text(
        "Возвращаемся в главное меню:",
        reply_markup=get_main_keyboard()
    )


async def toggle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик кнопки "Уведомления"
    """
    await update.message.reply_text("🔔 Уведомления включены!")


async def toggle_dark_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик кнопки "Темная тема"
    """
    await update.message.reply_text("🌙 Темная тема активирована!")


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик кнопки "Помощь"
    """
    await update.message.reply_text(
        "ℹ️ <b>Помощь</b>\n\n"
        "Это демонстрационный бот с Reply Keyboard.\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Показать главное меню\n"
        "/hide - Скрыть клавиатуру\n\n"
        "<b>Кнопки:</b>\n"
        "• 📊 Статистика - ваша статистика\n"
        "• ⚙️ Настройки - настройки бота\n"
        "• 🌍 Локация - отправить геопозицию\n"
        "• 📱 Контакт - поделиться контактом",
        parse_mode="HTML"
    )


async def show_contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик кнопки "Контакт"
    """
    await update.message.reply_text(
        "📞 <b>Контактная информация:</b>\n\n"
        "Email: support@example.com\n"
        "Telegram: @example_bot",
        parse_mode="HTML"
    )


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик геолокации
    """
    location = update.message.location
    await update.message.reply_text(
        f"📍 Спасибо за локацию!\n\n"
        f"Широта: {location.latitude}\n"
        f"Долгота: {location.longitude}\n\n"
        f"Ссылка на карту: "
        f"https://www.google.com/maps?q={location.latitude},{location.longitude}"
    )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик контакта
    """
    contact = update.message.contact
    await update.message.reply_text(
        f"📱 Спасибо за контакт!\n\n"
        f"Имя: {contact.first_name} {contact.last_name or ''}\n"
        f"Телефон: {contact.phone_number}"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик любого другого текста
    """
    await update.message.reply_text(
        f"Вы написали: {update.message.text}\n\n"
        "Используйте кнопки на клавиатуре для навигации."
    )


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hide", hide_keyboard))

    # Регистрируем обработчики кнопок (важен порядок!)
    application.add_handler(MessageHandler(filters.Regex("^📊 Статистика$"), show_stats))
    application.add_handler(MessageHandler(filters.Regex("^⚙️ Настройки$"), show_settings))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Назад$"), back_to_main))
    application.add_handler(MessageHandler(filters.Regex("^🔔 Уведомления$"), toggle_notifications))
    application.add_handler(MessageHandler(filters.Regex("^🌙 Темная тема$"), toggle_dark_mode))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ Помощь$"), show_help))
    application.add_handler(MessageHandler(filters.Regex("^📞 Контакт$"), show_contact_info))

    # Регистрируем обработчики специальных типов сообщений
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Обработчик всех остальных текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling()


if __name__ == '__main__':
    main()
