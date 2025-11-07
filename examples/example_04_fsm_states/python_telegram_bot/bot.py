import logging
import os
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

# Определяем состояния
NAME, AGE, CITY = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Начало регистрации
    """
    await update.message.reply_text(
        "Привет! Давайте познакомимся.\n"
        "Как вас зовут?\n\n"
        "Для отмены используйте /cancel"
    )
    return NAME


async def process_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка имени и переход к возрасту
    """
    # Сохраняем имя в контексте пользователя
    context.user_data['name'] = update.message.text

    await update.message.reply_text(
        f"Приятно познакомиться, {update.message.text}!\nСколько вам лет?"
    )

    return AGE


async def process_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка возраста и переход к городу
    """
    text = update.message.text

    # Проверяем, что введено число
    if not text.isdigit():
        await update.message.reply_text("Пожалуйста, введите возраст числом.")
        return AGE

    age = int(text)

    if age < 0 or age > 120:
        await update.message.reply_text("Введите корректный возраст (от 0 до 120).")
        return AGE

    # Сохраняем возраст
    context.user_data['age'] = age

    await update.message.reply_text("В каком городе вы живете?")

    return CITY


async def process_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка города и завершение регистрации
    """
    # Сохраняем город
    context.user_data['city'] = update.message.text

    # Получаем все данные
    name = context.user_data['name']
    age = context.user_data['age']
    city = context.user_data['city']

    # Выводим результат
    await update.message.reply_text(
        f"Регистрация завершена!\n\n"
        f"📝 Ваши данные:\n"
        f"Имя: {name}\n"
        f"Возраст: {age}\n"
        f"Город: {city}",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отмена регистрации
    """
    await update.message.reply_text(
        "Регистрация отменена.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_age)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_city)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
