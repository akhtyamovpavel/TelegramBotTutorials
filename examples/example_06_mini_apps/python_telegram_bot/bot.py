"""
Telegram Bot Example 6: Telegram Mini Apps / WebApp (python-telegram-bot)
Демонстрирует работу с веб-приложениями внутри Telegram
"""

import asyncio
import json
import logging
import os
from io import BytesIO

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from PIL import Image, ImageDraw, ImageFont

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен и URL WebApp из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
# URL вашего WebApp (должен быть HTTPS!)
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://example.com/webapp.html")

if not BOT_TOKEN:
    raise ValueError("Не указан BOT_TOKEN! Установите переменную окружения.")


def generate_image_placeholder(settings: dict) -> BytesIO:
    """
    Генерация placeholder изображения с настройками
    В реальности здесь был бы вызов Stable Diffusion

    Args:
        settings: Настройки генерации из WebApp

    Returns:
        BytesIO объект с изображением
    """
    # Парсим размер
    size_str = settings.get('size', '768x768')
    width, height = map(int, size_str.split('x'))

    # Создаем изображение
    image = Image.new('RGB', (width, height), color=(100, 150, 255))
    draw = ImageDraw.Draw(image)

    # Пытаемся загрузить шрифт
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Рисуем информацию о настройках
    y_offset = height // 4

    # Модель
    model_text = f"Model: {settings.get('model', 'unknown')}"
    bbox = draw.textbbox((0, 0), model_text, font=font_large)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, y_offset), model_text, fill='white', font=font_large)

    y_offset += 60

    # Промпт (сокращенный)
    prompt = settings.get('prompt', 'No prompt')[:50]
    bbox = draw.textbbox((0, 0), prompt, font=font_small)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, y_offset), prompt, fill='white', font=font_small)

    y_offset += 40

    # Параметры
    params_text = f"Steps: {settings.get('steps', 30)} | CFG: {settings.get('cfg_scale', 7.0)}"
    bbox = draw.textbbox((0, 0), params_text, font=font_small)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, y_offset), params_text, fill='white', font=font_small)

    # Водяной знак
    draw.text((10, height - 30), "AI Generated (Demo)", fill=(200, 200, 200), font=font_small)

    # Сохраняем в BytesIO
    bio = BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)

    return bio


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветственное сообщение"""
    await update.message.reply_text(
        "👋 <b>Telegram Mini Apps Demo</b>\n\n"
        "Этот бот демонстрирует работу с Telegram WebApp -\n"
        "веб-приложениями, которые открываются внутри Telegram.\n\n"
        "<b>Команды:</b>\n"
        "/webapp - Открыть настройки генерации\n"
        "/simple - Информация о WebApp и размещении\n"
        "/help - Справка по WebApp\n\n"
        "⚠️ <b>Важно:</b> Для работы /webapp необходимо разместить\n"
        "HTML файл на HTTPS сервере и указать URL в переменной WEBAPP_URL.\n\n"
        "💡 <i>WebApp позволяет создавать богатые интерактивные\n"
        "интерфейсы для сложных настроек ИИ-моделей.</i>",
        parse_mode="HTML"
    )


async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка кнопки для открытия WebApp"""
    # ВАЖНО: sendData() работает ТОЛЬКО с KeyboardButton (reply клавиатура),
    # НЕ с InlineKeyboardButton!
    keyboard = ReplyKeyboardMarkup(
        [[
            KeyboardButton(
                text="⚙️ Открыть настройки генерации",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🎨 <b>Настройка параметров генерации</b>\n\n"
        "Нажмите кнопку ниже (в клавиатуре), чтобы открыть интерактивный\n"
        "интерфейс настройки параметров ИИ-модели.\n\n"
        "Там вы сможете:\n"
        "• Написать промпт с подсказками\n"
        "• Выбрать модель (SD, DALL-E, etc.)\n"
        "• Настроить количество вариантов\n"
        "• Установить steps, CFG scale\n"
        "• Выбрать размер изображения\n\n"
        "⚠️ <i>Кнопка WebApp должна быть в reply-клавиатуре для работы sendData()</i>",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def simple_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация о простом WebApp"""
    await update.message.reply_text(
        "ℹ️ <b>О простых WebApp</b>\n\n"
        "⚠️ <b>Важно:</b> Telegram <u>не поддерживает</u> data: URLs для WebApp!\n\n"
        "WebApp должен быть размещен на <b>реальном HTTPS сервере</b>.\n\n"
        "<b>Варианты размещения:</b>\n"
        "• GitHub Pages (бесплатно)\n"
        "• Vercel/Netlify (бесплатно)\n"
        "• Свой сервер с SSL\n"
        "• Ngrok для тестирования\n\n"
        "📁 Готовый HTML файл находится в папке <code>webapp/index.html</code>\n\n"
        "📖 См. README для инструкций по размещению.",
        parse_mode="HTML"
    )


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка данных, полученных из WebApp
    Вызывается когда пользователь отправляет данные через WebApp
    """
    try:
        # Получаем данные из WebApp
        webapp_data = update.message.web_app_data.data

        logger.info(f"Получены данные из WebApp от {update.effective_user.id}: {webapp_data}")

        # Пытаемся распарсить как JSON
        try:
            settings = json.loads(webapp_data)

            # Проверяем, что это наши настройки генерации
            if 'prompt' in settings and 'model' in settings:
                await handle_generation_settings(update, context, settings)
            else:
                # Простые данные (текст)
                await update.message.reply_text(
                    f"✅ Получены данные:\n\n{webapp_data}"
                )

        except json.JSONDecodeError:
            # Если не JSON, значит простой текст
            await update.message.reply_text(
                f"✅ Получено сообщение:\n\n{webapp_data}"
            )

    except Exception as e:
        logger.error(f"Ошибка обработки WebApp данных: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке данных.\n"
            f"Детали: {str(e)}"
        )


async def handle_generation_settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    settings: dict
) -> None:
    """
    Обработка настроек генерации из WebApp

    Args:
        update: Update объект
        context: Context объект
        settings: Настройки генерации
    """
    prompt = settings.get('prompt', 'No prompt')
    model = settings.get('model', 'unknown')
    num_images = settings.get('num_images', 1)
    steps = settings.get('steps', 30)
    cfg_scale = settings.get('cfg_scale', 7.0)
    size = settings.get('size', '768x768')

    # Формируем красивое отображение всех параметров
    response_text = (
        "✅ <b>Данные успешно получены из WebApp!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 <b>ПАРАМЕТРЫ ГЕНЕРАЦИИ:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Промпт:</b>\n"
        f"   <code>{prompt}</code>\n\n"
        f"🤖 <b>Модель:</b> {model}\n"
        f"🖼️ <b>Количество изображений:</b> {num_images}\n"
        f"🔄 <b>Steps (качество):</b> {steps}\n"
        f"⚖️ <b>CFG Scale (точность):</b> {cfg_scale}\n"
        f"📐 <b>Размер:</b> {size}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏳ Генерирую {num_images} изображени{'е' if num_images == 1 else 'я'}...\n"
        "Пожалуйста, подождите..."
    )

    # Отправляем подтверждение с параметрами
    await update.message.reply_text(response_text, parse_mode="HTML")

    # Генерируем изображения (в реальности здесь был бы вызов SD/DALL-E)
    for i in range(num_images):
        # Имитация генерации
        await asyncio.sleep(0.5)

        # Генерируем placeholder
        image = generate_image_placeholder(settings)

        # Отправляем
        await update.message.reply_photo(
            photo=image,
            caption=f"✨ Вариант {i + 1}/{num_images}\n"
                    f"Промпт: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
        )

    await update.message.reply_text(
        "✅ <b>Генерация завершена!</b>\n\n"
        "💡 Используйте /webapp для новой генерации с другими параметрами.",
        parse_mode="HTML"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Помощь"""
    await update.message.reply_text(
        "📖 <b>Справка по WebApp</b>\n\n"
        "<b>Что такое WebApp?</b>\n"
        "Это веб-приложения (HTML/CSS/JS), которые открываются\n"
        "внутри Telegram и могут взаимодействовать с ботом.\n\n"
        "<b>Как это работает?</b>\n"
        "1. Бот отправляет кнопку с WebApp\n"
        "2. Вы нажимаете кнопку\n"
        "3. Открывается веб-интерфейс\n"
        "4. Вы настраиваете параметры\n"
        "5. WebApp отправляет данные боту\n"
        "6. Бот обрабатывает и генерирует\n\n"
        "<b>Преимущества:</b>\n"
        "• Богатый UI (слайдеры, формы, canvas)\n"
        "• Интерактивность\n"
        "• Нативная интеграция с Telegram\n\n"
        "Попробуйте: /webapp",
        parse_mode="HTML"
    )


def main() -> None:
    """Главная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("webapp", webapp_command))
    application.add_handler(CommandHandler("simple", simple_command))
    application.add_handler(CommandHandler("help", help_command))

    # Обработчик данных из WebApp
    application.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data)
    )

    logger.info("Бот запущен и готов к работе с WebApp!")
    logger.info(f"WebApp URL: {WEBAPP_URL}")

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
