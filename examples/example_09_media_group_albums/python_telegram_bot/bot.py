"""
Telegram Bot Example 8: Media Group Albums (python-telegram-bot)
Демонстрирует работу с альбомами (несколькими изображениями)
"""

import asyncio
import logging
import os
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from typing import Dict, List

from telegram import Update, InputMediaPhoto
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

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не указан BOT_TOKEN! Установите переменную окружения.")

# Создаем директорию для сгенерированных изображений
IMAGES_DIR = Path("generated_albums")
IMAGES_DIR.mkdir(exist_ok=True)

# Словарь для хранения альбомов от пользователей
# Структура: {media_group_id: [Photo, Photo, ...]}
user_albums: Dict[str, List] = defaultdict(list)


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
        "Команды:\n"
        "/generate - Сгенерировать альбом из 3 цветных изображений\n"
        "/compare - Показать сравнение 'До и После'\n"
        "/variants - Создать 4 варианта изображения\n\n"
        "📤 Отправьте мне несколько фото одновременно (альбом),\n"
        "и я распознаю их как единую группу!",
        parse_mode="HTML"
    )


async def generate_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерирует и отправляет альбом из 3 изображений"""
    await update.message.reply_text("🎨 Генерирую альбом из 3 изображений...")

    # Создаем список InputMediaPhoto
    media = []

    # Генерируем 3 цветных изображения
    colors = [
        ((255, 0, 0), "Красный"),
        ((0, 255, 0), "Зеленый"),
        ((0, 0, 255), "Синий")
    ]

    for i, (color, name) in enumerate(colors):
        image_bio = generate_colored_image(color, name)

        # Первое изображение с caption
        if i == 0:
            media.append(
                InputMediaPhoto(
                    media=image_bio,
                    caption="🖼️ Альбом цветных изображений"
                )
            )
        else:
            media.append(InputMediaPhoto(media=image_bio))

    # Отправляем альбом
    await context.bot.send_media_group(
        chat_id=update.effective_chat.id,
        media=media
    )

    logger.info(f"Отправлен альбом из 3 изображений пользователю {update.effective_user.id}")


async def compare_images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Демонстрирует сравнение 'До и После'"""
    await update.message.reply_text("🔄 Создаю сравнение 'До и После'...")

    # Создаем два изображения: "до" и "после"
    before_bio = generate_colored_image((100, 100, 100), "ДО обработки")
    after_bio = generate_colored_image((255, 215, 0), "ПОСЛЕ обработки")

    # Создаем список InputMediaPhoto
    media = [
        InputMediaPhoto(
            media=before_bio,
            caption="📷 Сравнение обработки изображения"
        ),
        InputMediaPhoto(media=after_bio),
    ]

    # Отправляем альбом
    await context.bot.send_media_group(
        chat_id=update.effective_chat.id,
        media=media
    )

    logger.info(f"Отправлено сравнение 'До и После' пользователю {update.effective_user.id}")


async def generate_variants(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Создает 4 варианта изображения (имитация генерации ИИ)"""
    await update.message.reply_text("🎲 Генерирую 4 варианта изображения...")

    media = []

    # Создаем 4 варианта с разными цветами
    variants = [
        ((255, 100, 100), "Вариант 1"),
        ((100, 255, 100), "Вариант 2"),
        ((100, 100, 255), "Вариант 3"),
        ((255, 255, 100), "Вариант 4"),
    ]

    for i, (color, name) in enumerate(variants):
        image_bio = generate_colored_image(color, name, size=(512, 512))

        if i == 0:
            media.append(
                InputMediaPhoto(
                    media=image_bio,
                    caption="🎨 4 варианта генерации (имитация Stable Diffusion)"
                )
            )
        else:
            media.append(InputMediaPhoto(media=image_bio))

    await context.bot.send_media_group(
        chat_id=update.effective_chat.id,
        media=media
    )

    logger.info(f"Отправлено 4 варианта пользователю {update.effective_user.id}")


async def handle_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик альбомов от пользователя
    Группирует фото по media_group_id
    """
    message = update.message

    # Проверяем, что это часть альбома
    if message.media_group_id:
        media_group_id = message.media_group_id

        # Добавляем фото в словарь альбомов
        # Сохраняем самое большое фото (последнее в списке)
        photo = message.photo[-1]
        user_albums[media_group_id].append(photo)

        logger.info(
            f"Получено фото {len(user_albums[media_group_id])} "
            f"для альбома {media_group_id}"
        )

        # Ждем 0.5 секунды, чтобы собрать все фото альбома
        await asyncio.sleep(0.5)

        # Проверяем, что это последнее фото в альбоме
        current_count = len(user_albums[media_group_id])

        # Ждем еще немного для уверенности
        await asyncio.sleep(0.3)

        # Если количество не изменилось, альбом завершен
        if current_count == len(user_albums[media_group_id]):
            photos = user_albums[media_group_id]

            await message.reply_text(
                f"📸 <b>Получен альбом!</b>\n\n"
                f"Количество фотографий: {len(photos)}\n"
                f"Media Group ID: <code>{media_group_id}</code>\n\n"
                f"Размеры фотографий:\n" +
                "\n".join([f"  • {p.width}x{p.height} px" for p in photos]),
                parse_mode="HTML"
            )

            logger.info(
                f"Обработан альбом {media_group_id} "
                f"из {len(photos)} фотографий"
            )

            # Удаляем обработанный альбом
            del user_albums[media_group_id]

    else:
        # Одиночное фото (не в альбоме)
        photo = message.photo[-1]
        await message.reply_text(
            f"📷 Получено одиночное фото\n"
            f"Размер: {photo.width}x{photo.height} px\n\n"
            f"💡 Отправьте несколько фото одновременно, чтобы создать альбом!"
        )


def main() -> None:
    """Главная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("generate", generate_album))
    application.add_handler(CommandHandler("compare", compare_images))
    application.add_handler(CommandHandler("variants", generate_variants))

    # Обработчик фотографий (включая альбомы)
    application.add_handler(
        MessageHandler(filters.PHOTO, handle_album)
    )

    logger.info("Бот запущен и готов к работе!")

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
