import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

from database import Database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

# Инициализируем БД
db = Database()

# Состояния
NAME, AGE, CITY = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Начало регистрации + добавление в БД
    """
    user = update.effective_user

    # Добавляем пользователя в БД
    db.add_user(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    await update.message.reply_text(
        "Привет! Давайте заполним ваш профиль.\n"
        "Как вас зовут?\n\n"
        "Команды:\n"
        "/cancel - отменить\n"
        "/profile - посмотреть профиль\n"
        "/stats - статистика бота"
    )

    return NAME


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показать профиль пользователя
    """
    user_data = db.get_user(update.effective_user.id)

    if not user_data or not user_data['name']:
        await update.message.reply_text(
            "У вас еще нет профиля. Используйте /start для регистрации."
        )
        return

    await update.message.reply_text(
        f"👤 Ваш профиль:\n\n"
        f"Имя: {user_data['name']}\n"
        f"Возраст: {user_data['age']}\n"
        f"Город: {user_data['city']}\n"
        f"Зарегистрирован: {user_data['created_at']}"
    )


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показать статистику бота
    """
    count = db.get_all_users_count()
    await update.message.reply_text(f"📊 Статистика:\n\nВсего пользователей: {count}")


async def process_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка имени
    """
    context.user_data['name'] = update.message.text

    await update.message.reply_text(
        f"Приятно познакомиться, {update.message.text}!\nСколько вам лет?"
    )

    return AGE


async def process_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка возраста
    """
    text = update.message.text

    if not text.isdigit():
        await update.message.reply_text("Пожалуйста, введите возраст числом.")
        return AGE

    age = int(text)
    if age < 0 or age > 120:
        await update.message.reply_text("Введите корректный возраст (от 0 до 120).")
        return AGE

    context.user_data['age'] = age
    await update.message.reply_text("В каком городе вы живете?")

    return CITY


async def process_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка города и сохранение в БД
    """
    context.user_data['city'] = update.message.text

    # Сохраняем профиль в БД
    db.update_user_profile(
        user_id=update.effective_user.id,
        name=context.user_data['name'],
        age=context.user_data['age'],
        city=context.user_data['city']
    )

    await update.message.reply_text(
        f"✅ Регистрация завершена!\n\n"
        f"📝 Ваши данные сохранены в базе данных:\n"
        f"Имя: {context.user_data['name']}\n"
        f"Возраст: {context.user_data['age']}\n"
        f"Город: {context.user_data['city']}\n\n"
        f"Используйте /profile для просмотра профиля"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отмена регистрации
    """
    await update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # ConversationHandler
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
    application.add_handler(CommandHandler("profile", show_profile))
    application.add_handler(CommandHandler("stats", show_stats))

    application.run_polling()


if __name__ == '__main__':
    main()
