import asyncio
import logging
import sys
from os import getenv, makedirs
from pathlib import Path

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

TOKEN = getenv("BOT_TOKEN")
router = Router()

# Создаем папки для хранения файлов
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Подпапки для разных типов файлов
(DOWNLOAD_DIR / "photos").mkdir(exist_ok=True)
(DOWNLOAD_DIR / "documents").mkdir(exist_ok=True)
(DOWNLOAD_DIR / "audio").mkdir(exist_ok=True)
(DOWNLOAD_DIR / "video").mkdir(exist_ok=True)


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    """
    Приветствие с инструкциями
    """
    await message.answer(
        "🤖 <b>Бот для загрузки файлов</b>\n\n"
        "Отправьте мне файл любого типа:\n"
        "• 📷 Фото\n"
        "• 📄 Документ (PDF, DOCX, TXT и т.д.)\n"
        "• 🎵 Аудио\n"
        "• 🎬 Видео\n\n"
        "Я сохраню его и покажу информацию о файле.\n\n"
        "<b>Команды:</b>\n"
        "/stats - Статистика загрузок\n"
        "/help - Справка"
    )


@router.message(Command("help"))
async def command_help(message: Message) -> None:
    """
    Справка
    """
    await message.answer(
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
        "• Извлечения данных из документов"
    )


@router.message(Command("stats"))
async def command_stats(message: Message) -> None:
    """
    Статистика загрузок
    """
    # Подсчитываем файлы
    photos_count = len(list((DOWNLOAD_DIR / "photos").glob("*")))
    docs_count = len(list((DOWNLOAD_DIR / "documents").glob("*")))
    audio_count = len(list((DOWNLOAD_DIR / "audio").glob("*")))
    video_count = len(list((DOWNLOAD_DIR / "video").glob("*")))
    total = photos_count + docs_count + audio_count + video_count

    await message.answer(
        f"📊 <b>Статистика загрузок:</b>\n\n"
        f"Всего файлов: {total}\n"
        f"📷 Фото: {photos_count}\n"
        f"📄 Документов: {docs_count}\n"
        f"🎵 Аудио: {audio_count}\n"
        f"🎬 Видео: {video_count}"
    )


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot) -> None:
    """
    Обработка фотографий
    """
    # Telegram отправляет фото в разных разрешениях, берем самое большое
    photo = message.photo[-1]

    # Формируем имя файла
    file_name = f"photo_{message.message_id}_{photo.file_id[:8]}.jpg"
    file_path = DOWNLOAD_DIR / "photos" / file_name

    # Скачиваем файл
    await bot.download(photo, destination=file_path)

    # Получаем информацию о файле
    file_info = await bot.get_file(photo.file_id)
    file_size_mb = file_info.file_size / (1024 * 1024)

    await message.answer(
        f"✅ <b>Фото сохранено!</b>\n\n"
        f"📁 Имя файла: <code>{file_name}</code>\n"
        f"📏 Размер: {file_size_mb:.2f} МБ\n"
        f"📐 Разрешение: {photo.width}x{photo.height}\n"
        f"💾 Путь: <code>{file_path}</code>\n\n"
        f"<i>Теперь вы можете обработать это изображение с помощью ИИ-модели:</i>\n"
        f"• Распознавание объектов\n"
        f"• OCR (извлечение текста)\n"
        f"• Классификация\n"
        f"• Генерация описания"
    )


@router.message(F.document)
async def handle_document(message: Message, bot: Bot) -> None:
    """
    Обработка документов
    """
    document = message.document

    # Формируем имя файла
    file_name = document.file_name or f"document_{message.message_id}.{document.mime_type.split('/')[-1]}"
    file_path = DOWNLOAD_DIR / "documents" / file_name

    # Скачиваем файл
    try:
        await bot.download(document, destination=file_path)

        # Получаем информацию о файле
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

        await message.answer(
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
            f"• CSV → анализ данных"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении файла: {str(e)}")


@router.message(F.audio)
async def handle_audio(message: Message, bot: Bot) -> None:
    """
    Обработка аудио файлов
    """
    audio = message.audio

    # Формируем имя файла
    file_name = audio.file_name or f"audio_{message.message_id}.mp3"
    file_path = DOWNLOAD_DIR / "audio" / file_name

    # Скачиваем файл
    await bot.download(audio, destination=file_path)

    # Информация о файле
    file_size_mb = audio.file_size / (1024 * 1024)
    duration_min = audio.duration / 60 if audio.duration else 0

    await message.answer(
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
        f"• Извлечение ключевых слов"
    )


@router.message(F.video)
async def handle_video(message: Message, bot: Bot) -> None:
    """
    Обработка видео файлов
    """
    video = message.video

    # Формируем имя файла
    file_name = video.file_name or f"video_{message.message_id}.mp4"
    file_path = DOWNLOAD_DIR / "video" / file_name

    # Скачиваем файл
    await bot.download(video, destination=file_path)

    # Информация о файле
    file_size_mb = video.file_size / (1024 * 1024)
    duration_min = video.duration / 60 if video.duration else 0

    await message.answer(
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
        f"• Анализ сцен"
    )


@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot) -> None:
    """
    Обработка голосовых сообщений
    """
    voice = message.voice

    # Формируем имя файла
    file_name = f"voice_{message.message_id}.ogg"
    file_path = DOWNLOAD_DIR / "audio" / file_name

    # Скачиваем файл
    await bot.download(voice, destination=file_path)

    # Информация о файле
    file_size_kb = voice.file_size / 1024
    duration_sec = voice.duration

    await message.answer(
        f"✅ <b>Голосовое сообщение сохранено!</b>\n\n"
        f"🎤 Имя: <code>{file_name}</code>\n"
        f"📏 Размер: {file_size_kb:.2f} КБ\n"
        f"⏱ Длительность: {duration_sec} сек\n"
        f"💾 Путь: <code>{file_path}</code>\n\n"
        f"<i>Идеально для:</i>\n"
        f"• Whisper (транскрипция)\n"
        f"• Анализ речи\n"
        f"• Распознавание говорящего"
    )


@router.message(F.video_note)
async def handle_video_note(message: Message, bot: Bot) -> None:
    """
    Обработка видео-кружочков
    """
    video_note = message.video_note

    # Формируем имя файла
    file_name = f"video_note_{message.message_id}.mp4"
    file_path = DOWNLOAD_DIR / "video" / file_name

    # Скачиваем файл
    await bot.download(video_note, destination=file_path)

    # Информация о файле
    file_size_mb = video_note.file_size / (1024 * 1024)
    duration_sec = video_note.duration

    await message.answer(
        f"✅ <b>Видео-кружочек сохранен!</b>\n\n"
        f"🎥 Имя: <code>{file_name}</code>\n"
        f"📏 Размер: {file_size_mb:.2f} МБ\n"
        f"⏱ Длительность: {duration_sec} сек\n"
        f"💾 Путь: <code>{file_path}</code>"
    )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
