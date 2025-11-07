"""
Telegram Bot Example 9: Media Group Albums с Middleware (aiogram)
Демонстрирует правильную обработку альбомов с использованием middleware
"""

import logging
import os
from io import BytesIO
from pathlib import Path
from typing import List

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from PIL import Image, ImageDraw, ImageFont

from album_middleware import AlbumMiddleware

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не указан BOT_TOKEN! Установите переменную окружения.")

# Создаем директорию для сгенерированных изображений
IMAGES_DIR = Path("generated_albums")
IMAGES_DIR.mkdir(exist_ok=True)

# Роутер для обработчиков
router = Router()


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


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветственное сообщение"""
    await message.answer(
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


@router.message(Command("generate"))
async def cmd_generate(message: Message):
    """Генерирует и отправляет альбом из 3 изображений"""
    await message.answer("🎨 Генерирую альбом из 3 изображений...")

    # Создаем MediaGroupBuilder
    builder = MediaGroupBuilder(caption="🖼️ Альбом цветных изображений")

    # Генерируем 3 цветных изображения
    colors = [
        ((255, 100, 100), "Красный"),
        ((100, 255, 100), "Зеленый"),
        ((100, 100, 255), "Синий"),
    ]

    for color, name in colors:
        image_bio = generate_colored_image(color, name)
        builder.add_photo(
            media=BufferedInputFile(image_bio.read(), f"{name}.png")
        )

    await message.answer_media_group(media=builder.build())
    logger.info(f"Отправлен альбом пользователю {message.from_user.id}")


@router.message(Command("compare"))
async def cmd_compare(message: Message):
    """Генерирует сравнение 'До и После'"""
    await message.answer("🔄 Создаю сравнение 'До и После'...")

    builder = MediaGroupBuilder(caption="📊 Сравнение: До и После")

    # Изображение "До"
    before_img = generate_colored_image((150, 150, 150), "ДО", size=(600, 400))
    builder.add_photo(
        media=BufferedInputFile(before_img.read(), "before.png")
    )

    # Изображение "После"
    after_img = generate_colored_image((100, 200, 255), "ПОСЛЕ", size=(600, 400))
    builder.add_photo(
        media=BufferedInputFile(after_img.read(), "after.png")
    )

    await message.answer_media_group(media=builder.build())
    logger.info(f"Отправлено сравнение пользователю {message.from_user.id}")


@router.message(Command("variants"))
async def cmd_variants(message: Message):
    """Генерирует 4 варианта (имитация генерации ИИ)"""
    await message.answer("🎲 Генерирую 4 варианта...")

    builder = MediaGroupBuilder(
        caption="🎨 4 варианта генерации (имитация Stable Diffusion)"
    )

    # Создаем 4 варианта с разными цветами
    variants = [
        ((255, 100, 100), "Вариант 1"),
        ((100, 255, 100), "Вариант 2"),
        ((100, 100, 255), "Вариант 3"),
        ((255, 255, 100), "Вариант 4"),
    ]

    for color, name in variants:
        image_bio = generate_colored_image(color, name, size=(512, 512))
        builder.add_photo(
            media=BufferedInputFile(image_bio.read(), f"{name}.png")
        )

    await message.answer_media_group(media=builder.build())
    logger.info(f"Отправлено 4 варианта пользователю {message.from_user.id}")


@router.message(F.media_group_id, F.photo)
async def handle_album(message: Message, album: List[Message] = None):
    """
    Обработчик альбомов от пользователя

    Благодаря AlbumMiddleware этот обработчик вызывается ОДИН раз
    для всего альбома, а не для каждого фото отдельно!

    Args:
        message: Последнее сообщение альбома
        album: Список всех сообщений альбома (добавляется middleware)
    """
    if album is None:
        # Если middleware не сработал, обрабатываем как одиночное фото
        album = [message]

    media_group_id = message.media_group_id

    # Извлекаем все фото из альбома
    photos = [msg.photo[-1] for msg in album if msg.photo]

    await message.answer(
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


@router.message(F.photo)
async def handle_single_photo(message: Message):
    """Обработчик одиночных фото (не в альбоме)"""
    photo = message.photo[-1]
    await message.answer(
        f"📷 <b>Получено одиночное фото</b>\n\n"
        f"Размер: {photo.width}x{photo.height} px\n\n"
        f"💡 Отправьте несколько фото одновременно, чтобы создать альбом!",
        parse_mode="HTML"
    )


async def main():
    """Главная функция запуска бота"""
    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # ⭐ РЕГИСТРИРУЕМ MIDDLEWARE ДЛЯ РОУТЕРА
    router.message.middleware(AlbumMiddleware(latency=0.3))

    # Регистрируем роутер
    dp.include_router(router)

    logger.info("Бот запущен с AlbumMiddleware!")
    logger.info("Альбомы будут обрабатываться без дублирования")

    try:
        # Запускаем polling
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
