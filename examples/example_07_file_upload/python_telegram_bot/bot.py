import logging
import os
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

# Создаем папки для хранения файлов
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Подпапки для разных типов файлов
(DOWNLOAD_DIR / "photos").mkdir(exist_ok=True)
(DOWNLOAD_DIR / "documents").mkdir(exist_ok=True)
(DOWNLOAD_DIR / "audio").mkdir(exist_ok=True)
(DOWNLOAD_DIR / "video").mkdir(exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Приветствие с инструкциями
    """
    await update.message.reply_text(
        "🤖 <b>Бот для загрузки файлов</b>\n\n"
        "Отправьте мне файл любого типа:\n"
        "• 📷 Фото\n"
        "• 📄 Документ (PDF, DOCX, TXT и т.д.)\n"
        "• 🎵 Аудио\n"
        "• 🎬 Видео\n\n"
        "Я сохраню его и покажу информацию о файле.\n\n"
        "<b>Команды:</b>\n"
        "/stats - Статистика загрузок\n"
        "/help - Справка",
        parse_mode="HTML"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Справка
    """
    await update.message.reply_text(
        "ℹ️ <b>Справка</b>\n\n"
        "Этот бот принимает файлы различных типов и сохраняет их локально.\n\n"
        "<b>Поддерживаемые типы:</b>\n"
        "• Фото (до 10 МБ как фото, больше - как документ)\n"
        "• Документы (до 20 МБ для бесплатных ботов)\n"
        "• Аудио (MP3, WAV и другие)\n"
        "• Видео (MP4, AVI и другие)\n\n"
        "<b>Для ИИ-моделей:</b>\n"
        "После загрузки файла вы можете обработать его с помощью:\n"
        "• Распознавания текста (OCR)\n"
        "• Анализа изображений\n"
        "• Транскрипции аудио\n"
        "• Извлечения данных из документов",
        parse_mode="HTML"
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Статистика загрузок
    """
    # Подсчитываем файлы
    photos_count = len(list((DOWNLOAD_DIR / "photos").glob("*")))
    docs_count = len(list((DOWNLOAD_DIR / "documents").glob("*")))
    audio_count = len(list((DOWNLOAD_DIR / "audio").glob("*")))
    video_count = len(list((DOWNLOAD_DIR / "video").glob("*")))
    total = photos_count + docs_count + audio_count + video_count

    await update.message.reply_text(
        f"📊 <b>Статистика загрузок:</b>\n\n"
        f"Всего файлов: {total}\n"
        f"📷 Фото: {photos_count}\n"
        f"📄 Документов: {docs_count}\n"
        f"🎵 Аудио: {audio_count}\n"
        f"🎬 Видео: {video_count}",
        parse_mode="HTML"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка фотографий
    """
    # Telegram отправляет фото в разных разрешениях, берем самое большое
    photo = update.message.photo[-1]

    # Формируем имя файла
    file_name = f"photo_{update.message.message_id}_{photo.file_id[:8]}.jpg"
    file_path = DOWNLOAD_DIR / "photos" / file_name

    # Скачиваем файл
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive(file_path)

    # Информация о файле
    file_size_mb = photo.file_size / (1024 * 1024)

    await update.message.reply_text(
        f"✅ <b>Фото сохранено!</b>\n\n"
        f"📁 Имя файла: <code>{file_name}</code>\n"
        f"📏 Размер: {file_size_mb:.2f} МБ\n"
        f"📐 Разрешение: {photo.width}x{photo.height}\n"
        f"💾 Путь: <code>{file_path}</code>\n\n"
        f"<i>Теперь вы можете обработать это изображение с помощью ИИ-модели:</i>\n"
        f"• Распознавание объектов\n"
        f"• OCR (извлечение текста)\n"
        f"• Классификация\n"
        f"• Генерация описания",
        parse_mode="HTML"
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка документов
    """
    document = update.message.document

    # Формируем имя файла
    file_name = document.file_name or f"document_{update.message.message_id}.{document.mime_type.split('/')[-1]}"
    file_path = DOWNLOAD_DIR / "documents" / file_name

    # Скачиваем файл
    try:
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(file_path)

        # Информация о файле
        file_size_mb = document.file_size / (1024 * 1024)

        # Определяем тип документа
        mime_type = document.mime_type or "неизвестно"
        doc_type_emoji = {
            "application/pdf": "📕",
            "application/msword": "📘",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "📘",
            "text/plain": "📄",
            "application/json": "📋",
            "text/csv": "📊"
        }.get(mime_type, "📄")

        await update.message.reply_text(
            f"✅ <b>Документ сохранен!</b>\n\n"
            f"{doc_type_emoji} Имя: <code>{file_name}</code>\n"
            f"📏 Размер: {file_size_mb:.2f} МБ\n"
            f"📝 MIME-тип: <code>{mime_type}</code>\n"
            f"💾 Путь: <code>{file_path}</code>\n\n"
            f"<i>Примеры обработки для ИИ:</i>\n"
            f"• PDF → извлечение текста\n"
            f"• DOCX → анализ содержимого\n"
            f"• TXT → обработка NLP\n"
            f"• JSON → парсинг данных\n"
            f"• CSV → анализ данных",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при сохранении файла: {str(e)}")


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка аудио файлов
    """
    audio = update.message.audio

    # Формируем имя файла
    file_name = audio.file_name or f"audio_{update.message.message_id}.mp3"
    file_path = DOWNLOAD_DIR / "audio" / file_name

    # Скачиваем файл
    file = await context.bot.get_file(audio.file_id)
    await file.download_to_drive(file_path)

    # Информация о файле
    file_size_mb = audio.file_size / (1024 * 1024)
    duration_min = audio.duration / 60 if audio.duration else 0

    await update.message.reply_text(
        f"✅ <b>Аудио сохранено!</b>\n\n"
        f"🎵 Имя: <code>{file_name}</code>\n"
        f"📏 Размер: {file_size_mb:.2f} МБ\n"
        f"⏱ Длительность: {duration_min:.1f} мин\n"
        f"🎤 Исполнитель: {audio.performer or 'неизвестно'}\n"
        f"🎼 Название: {audio.title or 'неизвестно'}\n"
        f"💾 Путь: <code>{file_path}</code>\n\n"
        f"<i>Обработка для ИИ:</i>\n"
        f"• Speech-to-Text (транскрипция)\n"
        f"• Распознавание эмоций\n"
        f"• Определение языка\n"
        f"• Извлечение ключевых слов",
        parse_mode="HTML"
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка видео файлов
    """
    video = update.message.video

    # Формируем имя файла
    file_name = video.file_name or f"video_{update.message.message_id}.mp4"
    file_path = DOWNLOAD_DIR / "video" / file_name

    # Скачиваем файл
    file = await context.bot.get_file(video.file_id)
    await file.download_to_drive(file_path)

    # Информация о файле
    file_size_mb = video.file_size / (1024 * 1024)
    duration_min = video.duration / 60 if video.duration else 0

    await update.message.reply_text(
        f"✅ <b>Видео сохранено!</b>\n\n"
        f"🎬 Имя: <code>{file_name}</code>\n"
        f"📏 Размер: {file_size_mb:.2f} МБ\n"
        f"⏱ Длительность: {duration_min:.1f} мин\n"
        f"📐 Разрешение: {video.width}x{video.height}\n"
        f"💾 Путь: <code>{file_path}</code>\n\n"
        f"<i>Обработка для ИИ:</i>\n"
        f"• Извлечение кадров\n"
        f"• Распознавание объектов\n"
        f"• Детекция действий\n"
        f"• Генерация субтитров\n"
        f"• Анализ сцен",
        parse_mode="HTML"
    )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка голосовых сообщений
    """
    voice = update.message.voice

    # Формируем имя файла
    file_name = f"voice_{update.message.message_id}.ogg"
    file_path = DOWNLOAD_DIR / "audio" / file_name

    # Скачиваем файл
    file = await context.bot.get_file(voice.file_id)
    await file.download_to_drive(file_path)

    # Информация о файле
    file_size_kb = voice.file_size / 1024
    duration_sec = voice.duration

    await update.message.reply_text(
        f"✅ <b>Голосовое сообщение сохранено!</b>\n\n"
        f"🎤 Имя: <code>{file_name}</code>\n"
        f"📏 Размер: {file_size_kb:.2f} КБ\n"
        f"⏱ Длительность: {duration_sec} сек\n"
        f"💾 Путь: <code>{file_path}</code>\n\n"
        f"<i>Идеально для:</i>\n"
        f"• Whisper (транскрипция)\n"
        f"• Анализ речи\n"
        f"• Распознавание говорящего",
        parse_mode="HTML"
    )


async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка видео-кружочков
    """
    video_note = update.message.video_note

    # Формируем имя файла
    file_name = f"video_note_{update.message.message_id}.mp4"
    file_path = DOWNLOAD_DIR / "video" / file_name

    # Скачиваем файл
    file = await context.bot.get_file(video_note.file_id)
    await file.download_to_drive(file_path)

    # Информация о файле
    file_size_mb = video_note.file_size / (1024 * 1024)
    duration_sec = video_note.duration

    await update.message.reply_text(
        f"✅ <b>Видео-кружочек сохранен!</b>\n\n"
        f"🎥 Имя: <code>{file_name}</code>\n"
        f"📏 Размер: {file_size_mb:.2f} МБ\n"
        f"⏱ Длительность: {duration_sec} сек\n"
        f"💾 Путь: <code>{file_path}</code>",
        parse_mode="HTML"
    )


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Регистрируем обработчики файлов
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))

    application.run_polling()


if __name__ == '__main__':
    main()
