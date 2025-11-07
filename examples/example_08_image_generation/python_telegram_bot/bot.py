import logging
import os
from pathlib import Path
from io import BytesIO
import random

from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes

# Для примера генерации изображений
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

# Создаем папку для генерированных изображений
OUTPUT_DIR = Path("generated_images")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_placeholder_image(width: int = 800, height: int = 600, text: str = "Generated") -> Path:
    """
    Генерирует простое изображение с текстом (пример)
    """
    image = Image.new('RGB', (width, height), color=(
        random.randint(50, 150),
        random.randint(50, 150),
        random.randint(50, 150)
    ))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill=(255, 255, 255), font=font)

    file_path = OUTPUT_DIR / f"generated_{random.randint(1000, 9999)}.png"
    image.save(file_path)

    return file_path


def create_chart_image(data: list[int], title: str = "Chart") -> BytesIO:
    """
    Создает график (простой пример)
    """
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font_title = font_label = ImageFont.load_default()

    draw.text((20, 20), title, fill=(0, 0, 0), font=font_title)

    bar_width = (width - 100) // len(data)
    max_value = max(data) if data else 1

    for i, value in enumerate(data):
        bar_height = int((value / max_value) * (height - 150))
        x1 = 50 + i * bar_width
        y1 = height - 50 - bar_height
        x2 = x1 + bar_width - 10
        y2 = height - 50

        draw.rectangle([x1, y1, x2, y2], fill=(100, 150, 200))
        draw.text((x1 + 5, y2 + 10), str(value), fill=(0, 0, 0), font=font_label)

    bio = BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)

    return bio


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Приветствие
    """
    await update.message.reply_text(
        "🎨 <b>Бот для работы с изображениями</b>\n\n"
        "<b>Команды генерации:</b>\n"
        "/generate - Сгенерировать изображение\n"
        "/chart - Создать график\n"
        "/send_file - Отправить из файла\n"
        "/send_url - Отправить по URL\n"
        "/send_bytes - Отправить из памяти\n\n"
        "<b>Примеры с текстом:</b>\n"
        "/text <ваш текст> - Текст на изображении\n\n"
        "<i>Это демонстрация различных способов отправки изображений</i>",
        parse_mode="HTML"
    )


async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Генерирует и отправляет изображение
    """
    await update.message.reply_text("🎨 Генерирую изображение...")

    image_path = generate_placeholder_image(text="AI Generated!")

    with open(image_path, 'rb') as photo:
        await update.message.reply_photo(
            photo,
            caption="✅ <b>Изображение сгенерировано!</b>\n\n"
                    "<i>В реальном проекте здесь может быть:</i>\n"
                    "• Stable Diffusion\n"
                    "• DALL-E API\n"
                    "• MidJourney\n"
                    "• Кастомные GAN модели",
            parse_mode="HTML"
        )


async def generate_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Создает и отправляет график
    """
    await update.message.reply_text("📊 Создаю график...")

    data = [random.randint(10, 100) for _ in range(7)]
    chart_bytes = create_chart_image(data, title="Weekly Stats")

    await update.message.reply_photo(
        chart_bytes,
        caption=f"📊 <b>График готов!</b>\n\n"
                f"Данные: {', '.join(map(str, data))}\n\n"
                f"<i>Можно использовать matplotlib, plotly, seaborn</i>",
        parse_mode="HTML"
    )


async def send_from_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправка изображения из файла
    """
    image_path = generate_placeholder_image(text="From File")

    with open(image_path, 'rb') as photo:
        await update.message.reply_photo(
            photo,
            caption="📁 <b>Из файла</b>\n\n"
                    "Используется для отправки файлов с диска",
            parse_mode="HTML"
        )


async def send_from_bytes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправка изображения из памяти
    """
    image = Image.new('RGB', (400, 300), color=(255, 100, 100))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    draw.text((50, 125), "From Memory", fill=(255, 255, 255), font=font)

    bio = BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)

    await update.message.reply_photo(
        bio,
        caption="💾 <b>Из памяти</b>\n\n"
                "Используется для отправки из памяти\n"
                "Экономит место на диске",
        parse_mode="HTML"
    )


async def send_from_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправка изображения по URL
    """
    url = "https://picsum.photos/800/600"

    await update.message.reply_photo(
        url,
        caption="🌐 <b>По URL</b>\n\n"
                "Используется для отправки изображений по URL\n"
                "Полезно для интеграции с внешними API",
        parse_mode="HTML"
    )


async def text_on_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Создает изображение с пользовательским текстом
    """
    text = ' '.join(context.args) if context.args else ""

    if not text:
        await update.message.reply_text("Используйте: /text <ваш текст>")
        return

    await update.message.reply_text(f"🎨 Создаю изображение с текстом: '{text}'...")

    image_path = generate_placeholder_image(text=text)

    with open(image_path, 'rb') as photo:
        await update.message.reply_photo(
            photo,
            caption=f"✅ <b>Готово!</b>\n\nВаш текст: <i>{text}</i>",
            parse_mode="HTML"
        )


async def send_media_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправка группы изображений (альбом)
    """
    await update.message.reply_text("📸 Создаю альбом из 3 изображений...")

    media = []
    for i in range(3):
        image_path = generate_placeholder_image(text=f"Image {i+1}")
        with open(image_path, 'rb') as photo:
            media.append(InputMediaPhoto(
                media=photo.read(),
                caption=f"Изображение {i+1}" if i == 0 else None
            ))

    await update.message.reply_media_group(media=media)
    await update.message.reply_text("✅ Альбом из 3 изображений отправлен!")


async def send_as_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправка изображения как документ (без сжатия)
    """
    await update.message.reply_text("📄 Отправляю как документ...")

    image_path = generate_placeholder_image(width=3000, height=2000, text="High Quality")

    with open(image_path, 'rb') as document:
        await update.message.reply_document(
            document,
            caption="📄 <b>Отправлено как документ</b>\n\n"
                    "Изображение не сжато Telegram\n"
                    "Полезно для:\n"
                    "• Высокого разрешения\n"
                    "• PNG с прозрачностью\n"
                    "• Архивации",
            parse_mode="HTML"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Справка по командам
    """
    await update.message.reply_text(
        "📖 <b>Справка по командам</b>\n\n"
        "<b>Способы отправки изображений:</b>\n\n"
        "1️⃣ <b>Из файла</b> - с диска\n"
        "<code>/send_file</code>\n\n"
        "2️⃣ <b>Из памяти</b> - BytesIO\n"
        "<code>/send_bytes</code>\n\n"
        "3️⃣ <b>По URL</b>\n"
        "<code>/send_url</code>\n\n"
        "4️⃣ <b>Media Group</b> - альбом\n"
        "<code>/album</code>\n\n"
        "5️⃣ <b>Document</b> - без сжатия\n"
        "<code>/document</code>\n\n"
        "<b>Генерация:</b>\n"
        "/generate - Сгенерировать изображение\n"
        "/chart - Создать график\n"
        "/text <текст> - Текст на изображении",
        parse_mode="HTML"
    )


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("generate", generate_image))
    application.add_handler(CommandHandler("chart", generate_chart))
    application.add_handler(CommandHandler("send_file", send_from_file))
    application.add_handler(CommandHandler("send_bytes", send_from_bytes))
    application.add_handler(CommandHandler("send_url", send_from_url))
    application.add_handler(CommandHandler("text", text_on_image))
    application.add_handler(CommandHandler("album", send_media_group))
    application.add_handler(CommandHandler("document", send_as_document))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()


if __name__ == '__main__':
    main()
