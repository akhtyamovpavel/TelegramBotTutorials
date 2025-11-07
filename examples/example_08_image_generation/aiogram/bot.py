import asyncio
import logging
import sys
from os import getenv
from pathlib import Path
from io import BytesIO

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, BufferedInputFile, URLInputFile

# Для примера генерации изображений
from PIL import Image, ImageDraw, ImageFont
import random

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

TOKEN = getenv("BOT_TOKEN")
router = Router()

# Создаем папку для генерированных изображений
OUTPUT_DIR = Path("generated_images")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_placeholder_image(width: int = 800, height: int = 600, text: str = "Generated") -> Path:
    """
    Генерирует простое изображение с текстом (пример)
    В реальных проектах здесь может быть:
    - Stable Diffusion
    - DALL-E
    - MidJourney API
    - Кастомные GAN модели
    """
    # Создаем изображение
    image = Image.new('RGB', (width, height), color=(
        random.randint(50, 150),
        random.randint(50, 150),
        random.randint(50, 150)
    ))
    draw = ImageDraw.Draw(image)

    # Добавляем текст
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = ImageFont.load_default()

    # Центрируем текст
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill=(255, 255, 255), font=font)

    # Сохраняем
    file_path = OUTPUT_DIR / f"generated_{random.randint(1000, 9999)}.png"
    image.save(file_path)

    return file_path


def create_chart_image(data: list[int], title: str = "Chart") -> BytesIO:
    """
    Создает график (простой пример)
    В реальности используйте matplotlib, plotly, seaborn
    """
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Заголовок
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font_title = font_label = ImageFont.load_default()

    draw.text((20, 20), title, fill=(0, 0, 0), font=font_title)

    # Простой столбчатый график
    bar_width = (width - 100) // len(data)
    max_value = max(data) if data else 1

    for i, value in enumerate(data):
        bar_height = int((value / max_value) * (height - 150))
        x1 = 50 + i * bar_width
        y1 = height - 50 - bar_height
        x2 = x1 + bar_width - 10
        y2 = height - 50

        # Рисуем столбец
        draw.rectangle([x1, y1, x2, y2], fill=(100, 150, 200))

        # Подпись значения
        draw.text((x1 + 5, y2 + 10), str(value), fill=(0, 0, 0), font=font_label)

    # Сохраняем в BytesIO
    bio = BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)

    return bio


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    """
    Приветствие
    """
    await message.answer(
        "🎨 <b>Бот для работы с изображениями</b>\n\n"
        "<b>Команды генерации:</b>\n"
        "/generate - Сгенерировать изображение\n"
        "/chart - Создать график\n"
        "/send_file - Отправить из файла\n"
        "/send_url - Отправить по URL\n"
        "/send_bytes - Отправить из памяти\n\n"
        "<b>Примеры с текстом:</b>\n"
        "/text &lt;ваш текст&gt; - Текст на изображении\n\n"
        "<i>Это демонстрация различных способов отправки изображений</i>"
    )


@router.message(Command("generate"))
async def generate_image(message: Message) -> None:
    """
    Генерирует и отправляет изображение
    """
    await message.answer("🎨 Генерирую изображение...")

    # Генерируем изображение
    image_path = generate_placeholder_image(text="AI Generated!")

    # Отправляем как фото
    photo = FSInputFile(image_path)
    await message.answer_photo(
        photo,
        caption="✅ <b>Изображение сгенерировано!</b>\n\n"
                "<i>В реальном проекте здесь может быть:</i>\n"
                "• Stable Diffusion\n"
                "• DALL-E API\n"
                "• MidJourney\n"
                "• Кастомные GAN модели"
    )


@router.message(Command("chart"))
async def generate_chart(message: Message) -> None:
    """
    Создает и отправляет график
    """
    await message.answer("📊 Создаю график...")

    # Генерируем случайные данные
    data = [random.randint(10, 100) for _ in range(7)]

    # Создаем график
    chart_bytes = create_chart_image(data, title="Weekly Stats")

    # Отправляем из памяти (без сохранения на диск)
    photo = BufferedInputFile(chart_bytes.read(), filename="chart.png")
    await message.answer_photo(
        photo,
        caption=f"📊 <b>График готов!</b>\n\n"
                f"Данные: {', '.join(map(str, data))}\n\n"
                f"<i>Можно использовать matplotlib, plotly, seaborn</i>"
    )


@router.message(Command("send_file"))
async def send_from_file(message: Message) -> None:
    """
    Отправка изображения из файла (FSInputFile)
    Используется когда файл уже сохранен на диске
    """
    # Генерируем файл
    image_path = generate_placeholder_image(text="From File")

    # Отправляем через FSInputFile
    photo = FSInputFile(image_path, filename="from_file.png")
    await message.answer_photo(
        photo,
        caption="📁 <b>FSInputFile</b>\n\n"
                "Используется для отправки файлов с диска"
    )


@router.message(Command("send_bytes"))
async def send_from_bytes(message: Message) -> None:
    """
    Отправка изображения из памяти (BufferedInputFile)
    Используется когда изображение генерируется в памяти
    """
    # Создаем изображение в памяти
    image = Image.new('RGB', (400, 300), color=(255, 100, 100))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    draw.text((50, 125), "From Memory", fill=(255, 255, 255), font=font)

    # Конвертируем в байты
    bio = BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)

    # Отправляем через BufferedInputFile
    photo = BufferedInputFile(bio.read(), filename="from_memory.png")
    await message.answer_photo(
        photo,
        caption="💾 <b>BufferedInputFile</b>\n\n"
                "Используется для отправки из памяти\n"
                "Экономит место на диске"
    )


@router.message(Command("send_url"))
async def send_from_url(message: Message) -> None:
    """
    Отправка изображения по URL (URLInputFile)
    Бот скачивает изображение и отправляет пользователю
    """
    # Используем публичное изображение
    url = "https://picsum.photos/800/600"

    # Отправляем через URLInputFile
    photo = URLInputFile(url, filename="from_url.jpg")
    await message.answer_photo(
        photo,
        caption="🌐 <b>URLInputFile</b>\n\n"
                "Используется для отправки изображений по URL\n"
                "Полезно для интеграции с внешними API"
    )


@router.message(Command("text"))
async def text_on_image(message: Message) -> None:
    """
    Создает изображение с пользовательским текстом
    """
    # Извлекаем текст из команды
    text = message.text.replace("/text", "").strip()

    if not text:
        await message.answer("Используйте: /text <ваш текст>")
        return

    await message.answer(f"🎨 Создаю изображение с текстом: '{text}'...")

    # Генерируем изображение с текстом
    image_path = generate_placeholder_image(text=text)

    # Отправляем
    photo = FSInputFile(image_path)
    await message.answer_photo(
        photo,
        caption=f"✅ <b>Готово!</b>\n\nВаш текст: <i>{text}</i>"
    )


@router.message(Command("album"))
async def send_media_group(message: Message) -> None:
    """
    Отправка группы изображений (альбом)
    """
    await message.answer("📸 Создаю альбом из 3 изображений...")

    from aiogram.types import InputMediaPhoto

    # Генерируем несколько изображений
    images = []
    for i in range(3):
        image_path = generate_placeholder_image(text=f"Image {i+1}")
        images.append(InputMediaPhoto(
            media=FSInputFile(image_path),
            caption=f"Изображение {i+1}" if i == 0 else None  # Подпись только к первому
        ))

    # Отправляем группу
    await message.answer_media_group(media=images)
    await message.answer("✅ Альбом из 3 изображений отправлен!")


@router.message(Command("document"))
async def send_as_document(message: Message) -> None:
    """
    Отправка изображения как документ (без сжатия)
    """
    await message.answer("📄 Отправляю как документ...")

    # Генерируем изображение
    image_path = generate_placeholder_image(width=3000, height=2000, text="High Quality")

    # Отправляем как документ (без сжатия Telegram)
    document = FSInputFile(image_path)
    await message.answer_document(
        document,
        caption="📄 <b>Отправлено как документ</b>\n\n"
                "Изображение не сжато Telegram\n"
                "Полезно для:\n"
                "• Высокого разрешения\n"
                "• PNG с прозрачностью\n"
                "• Архивации"
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    """
    Справка по командам
    """
    await message.answer(
        "📖 <b>Справка по командам</b>\n\n"
        "<b>Способы отправки изображений:</b>\n\n"
        "1️⃣ <b>FSInputFile</b> - из файла на диске\n"
        "<code>/send_file</code>\n\n"
        "2️⃣ <b>BufferedInputFile</b> - из памяти (байты)\n"
        "<code>/send_bytes</code>\n\n"
        "3️⃣ <b>URLInputFile</b> - по URL\n"
        "<code>/send_url</code>\n\n"
        "4️⃣ <b>Media Group</b> - альбом изображений\n"
        "<code>/album</code>\n\n"
        "5️⃣ <b>Document</b> - без сжатия\n"
        "<code>/document</code>\n\n"
        "<b>Генерация:</b>\n"
        "/generate - Сгенерировать изображение\n"
        "/chart - Создать график\n"
        "/text <текст> - Текст на изображении"
    )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
