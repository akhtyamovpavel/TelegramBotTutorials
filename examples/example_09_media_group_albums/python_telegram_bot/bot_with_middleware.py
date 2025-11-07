"""
Telegram Bot Example 9: Media Group Albums с Middleware (python-telegram-bot)
Демонстрирует правильную обработку альбомов с использованием middleware
"""

import logging
import os
from io import BytesIO
from pathlib import Path
from typing import List

from telegram import Update, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from PIL import Image, ImageDraw, ImageFont

from album_middleware import AlbumCollector, get_album_messages

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не указан BOT_TOKEN! Установите переменную окружения.")

# Создаем директорию для сгенерированных изображений
IMAGES_DIR = Path("generated_albums")
IMAGES_DIR.mkdir(exist_ok=True)

# ⭐ Создаем экземпляр AlbumCollector
album_collector = AlbumCollector(latency=0.3)


def generate_colored_image(color: tuple, text: str, size=(800, 600)) -> BytesIO:
    """
    Генерирует простое цветное изображение с текстом

    Args:
        color: RGB цвет фона
        text: Текст для отображения
        size: Размер изображения

    Returns:
        BytesIO объект с изображением
    """
    # Создаем изображение
    image = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(image)

    # Пытаемся загрузить шрифт
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = ImageFont.load_default()

    # Рисуем текст в центре
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, fill='white', font=font)

    # Сохраняем в BytesIO
    bio = BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)

    return bio


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветственное сообщение"""
    await update.message.reply_text(
        "🖼️ <b>Бот для работы с альбомами (Media Groups)</b>\n\n"
        "✨ <b>С Middleware - без дублирования!</b>\n\n"
        "Команды:\n"
        "/generate - Сгенерировать альбом из 3 цветных изображений\n"
        "/compare - Показать сравнение 'До и После'\n"
        "/variants - Создать 4 варианта изображения\n\n"
        "📤 Отправьте мне несколько фото одновременно (альбом),\n"
        "и я распознаю их как единую группу!\n\n"
        "💡 Middleware гарантирует, что ответ будет один!",
        parse_mode="HTML"
    )


async def cmd_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерирует и отправляет альбом из 3 изображений"""
    await update.message.reply_text("🎨 Генерирую альбом из 3 изображений...")

    # Генерируем 3 цветных изображения
    colors = [
        ((255, 100, 100), "Красный"),
        ((100, 255, 100), "Зеленый"),
        ((100, 100, 255), "Синий"),
    ]

    media = []
    for i, (color, name) in enumerate(colors):
        image_bio = generate_colored_image(color, name)
        media.append(
            InputMediaPhoto(
                media=image_bio,
                caption="🖼️ Альбом цветных изображений" if i == 0 else None
            )
        )

    await update.message.reply_media_group(media=media)
    logger.info(f"Отправлен альбом пользователю {update.effective_user.id}")


async def cmd_compare(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерирует сравнение 'До и После'"""
    await update.message.reply_text("🔄 Создаю сравнение 'До и После'...")

    # Изображение "До"
    before_img = generate_colored_image((150, 150, 150), "ДО", size=(600, 400))

    # Изображение "После"
    after_img = generate_colored_image((100, 200, 255), "ПОСЛЕ", size=(600, 400))

    media = [
        InputMediaPhoto(media=before_img, caption="📊 Сравнение: До и После"),
        InputMediaPhoto(media=after_img)
    ]

    await update.message.reply_media_group(media=media)
    logger.info(f"Отправлено сравнение пользователю {update.effective_user.id}")


async def cmd_variants(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерирует 4 варианта (имитация генерации ИИ)"""
    await update.message.reply_text("🎲 Генерирую 4 варианта...")

    # Создаем 4 варианта с разными цветами
    variants = [
        ((255, 100, 100), "Вариант 1"),
        ((100, 255, 100), "Вариант 2"),
        ((100, 100, 255), "Вариант 3"),
        ((255, 255, 100), "Вариант 4"),
    ]

    media = []
    for i, (color, name) in enumerate(variants):
        image_bio = generate_colored_image(color, name, size=(512, 512))
        media.append(
            InputMediaPhoto(
                media=image_bio,
                caption="🎨 4 варианта генерации (имитация Stable Diffusion)" if i == 0 else None
            )
        )

    await update.message.reply_media_group(media=media)
    logger.info(f"Отправлено 4 варианта пользователю {update.effective_user.id}")


async def handle_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик альбомов от пользователя

    Благодаря AlbumCollector этот обработчик вызывается ОДИН раз
    для всего альбома, а не для каждого фото отдельно!
    """
    # Получаем все updates альбома через вспомогательную функцию
    album_updates = get_album_messages(update, context)

    if album_updates is None:
        # Если это не альбом, обрабатываем как одиночное фото
        album_updates = [update]

    message = update.effective_message
    media_group_id = message.media_group_id

    # Извлекаем все фото из альбома
    photos = []
    for upd in album_updates:
        if upd.effective_message.photo:
            photos.append(upd.effective_message.photo[-1])

    await message.reply_text(
        f"📸 <b>Получен альбом!</b>\n\n"
        f"Количество фотографий: {len(photos)}\n"
        f"Media Group ID: <code>{media_group_id}</code>\n\n"
        f"Размеры фотографий:\n" +
        "\n".join([f"  • {p.width}x{p.height} px" for p in photos]) +
        f"\n\n✅ Обработано middleware - без дублирования!",
        parse_mode="HTML"
    )

    logger.info(
        f"Обработан альбом {media_group_id} "
        f"из {len(photos)} фотографий (один раз)"
    )


async def handle_single_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик одиночных фото (не в альбоме)"""
    photo = update.message.photo[-1]
    await update.message.reply_text(
        f"📷 <b>Получено одиночное фото</b>\n\n"
        f"Размер: {photo.width}x{photo.height} px\n\n"
        f"💡 Отправьте несколько фото одновременно, чтобы создать альбом!",
        parse_mode="HTML"
    )


def main() -> None:
    """Главная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("generate", cmd_generate))
    application.add_handler(CommandHandler("compare", cmd_compare))
    application.add_handler(CommandHandler("variants", cmd_variants))

    # ⭐ ОБОРАЧИВАЕМ обработчик альбомов в AlbumCollector
    wrapped_album_handler = album_collector.wrap_handler(handle_album)

    # Обработчик альбомов (фото с media_group_id)
    application.add_handler(
        MessageHandler(
            filters.PHOTO & ~filters.FORWARDED,  # Только оригинальные фото
            wrapped_album_handler
        )
    )

    # Обработчик одиночных фото (без media_group_id)
    # Примечание: этот обработчик не сработает для альбомов,
    # так как предыдущий обработчик уже обработает их
    # application.add_handler(
    #     MessageHandler(filters.PHOTO, handle_single_photo)
    # )

    logger.info("Бот запущен с AlbumCollector!")
    logger.info("Альбомы будут обрабатываться без дублирования")

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
