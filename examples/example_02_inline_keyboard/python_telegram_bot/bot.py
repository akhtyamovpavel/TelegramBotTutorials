import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет приветствие с inline-клавиатурой
    """
    # Создаем inline-клавиатуру
    keyboard = [
        [
            InlineKeyboardButton("Опция 1 ✅", callback_data="option_1"),
            InlineKeyboardButton("Опция 2 ⭐", callback_data="option_2")
        ],
        [
            InlineKeyboardButton("Опция 3 🎯", callback_data="option_3")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите опцию:",
        reply_markup=reply_markup
    )


async def handle_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатий на inline-кнопки
    """
    query = update.callback_query

    # Отвечаем на callback
    await query.answer()

    # Редактируем сообщение
    option_texts = {
        "option_1": "Вы выбрали Опцию 1 ✅",
        "option_2": "Вы выбрали Опцию 2 ⭐",
        "option_3": "Вы выбрали Опцию 3 🎯"
    }

    await query.edit_message_text(option_texts.get(query.data, "Неизвестная опция"))


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_option))

    application.run_polling()


if __name__ == '__main__':
    main()
