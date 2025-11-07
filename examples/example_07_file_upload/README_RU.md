# Example 6: Загрузка файлов (для ИИ-моделей)

## Описание

Бот для приема и сохранения файлов различных типов - критически важная функциональность для работы с ИИ-моделями:
- 📷 Фотографии (для компьютерного зрения, OCR)
- 📄 Документы (PDF, DOCX, TXT для NLP)
- 🎵 Аудио (для транскрипции, анализа речи)
- 🎬 Видео (для анализа видео, детекции объектов)
- 🎤 Голосовые сообщения (для Speech-to-Text)

## Зачем это нужно для ИИ?

### Типичные сценарии:
1. **Компьютерное зрение** - загрузка изображений для классификации, детекции объектов
2. **NLP обработка** - загрузка текстовых документов для анализа
3. **Speech-to-Text** - транскрипция аудио файлов (Whisper, Vosk)
4. **OCR** - извлечение текста из изображений (Tesseract, EasyOCR)
5. **Видео-анализ** - обработка видео кадр за кадром
6. **Датасеты** - сбор данных для обучения моделей

## Что нового по сравнению с предыдущими примерами

### ➕ Добавлено:
1. **Обработка разных типов файлов** - фото, документы, аудио, видео
2. **Скачивание файлов** - `bot.download()` / `file.download_to_drive()`
3. **Получение метаданных** - размер, разрешение, длительность
4. **Файловая система** - создание структуры папок
5. **Фильтры по типам** - `F.photo`, `F.document`, `filters.PHOTO`

### Что изменилось:
- Работа с файловой системой (Path, makedirs)
- Асинхронное скачивание файлов
- Обработка метаданных файлов
- Организация хранилища

## Установка

```bash
# Стандартные зависимости
pip install aiogram
# или
pip install python-telegram-bot
```

## Запуск

```bash
export BOT_TOKEN="your_bot_token_here"

# aiogram
python examples/example_06_file_upload/aiogram/bot.py

# python-telegram-bot
python examples/example_06_file_upload/python_telegram_bot/bot.py
```

## Ключевые концепции

### 1. Типы файлов в Telegram

| Тип | Описание | Макс. размер | Использование |
|-----|----------|--------------|---------------|
| **photo** | Изображения | 10 МБ (сжатые) | CV, OCR |
| **document** | Файлы без сжатия | 20 МБ / 50 МБ* | Любые документы |
| **audio** | Аудио с метаданными | 20 МБ / 50 МБ* | Музыка |
| **voice** | Голосовое сообщение | - | Speech-to-Text |
| **video** | Видеофайлы | 20 МБ / 50 МБ* | Видео-анализ |
| **video_note** | Видео-кружочки | - | Короткие видео |

*50 МБ для Premium пользователей

### 2. Скачивание файлов

**aiogram:**
```python
# Получаем file_id из сообщения
photo = message.photo[-1]  # Самое большое разрешение

# Скачиваем файл
file_path = Path("downloads/photo.jpg")
await bot.download(photo, destination=file_path)

# Или получаем информацию о файле
file_info = await bot.get_file(photo.file_id)
file_size = file_info.file_size
```

**python-telegram-bot:**
```python
# Получаем file_id
photo = update.message.photo[-1]

# Получаем объект File
file = await context.bot.get_file(photo.file_id)

# Скачиваем
await file.download_to_drive("downloads/photo.jpg")
```

### 3. Фильтры по типам файлов

**aiogram:**
```python
@router.message(F.photo)
async def handle_photo(message: Message): ...

@router.message(F.document)
async def handle_document(message: Message): ...

@router.message(F.audio)
async def handle_audio(message: Message): ...

@router.message(F.video)
async def handle_video(message: Message): ...

@router.message(F.voice)
async def handle_voice(message: Message): ...
```

**python-telegram-bot:**
```python
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
application.add_handler(MessageHandler(filters.VIDEO, handle_video))
application.add_handler(MessageHandler(filters.VOICE, handle_voice))
```

### 4. Метаданные файлов

#### Фото:
```python
photo = message.photo[-1]
width = photo.width
height = photo.height
file_size = photo.file_size
file_id = photo.file_id
```

#### Документ:
```python
document = message.document
file_name = document.file_name
mime_type = document.mime_type  # 'application/pdf', 'text/plain', etc.
file_size = document.file_size
```

#### Аудио:
```python
audio = message.audio
duration = audio.duration  # в секундах
performer = audio.performer
title = audio.title
file_name = audio.file_name
```

#### Видео:
```python
video = message.video
duration = video.duration
width = video.width
height = video.height
file_size = video.file_size
```

## Интеграция с ИИ-моделями

### 1. Компьютерное зрение (PyTorch/TensorFlow)

```python
from PIL import Image
import torch
from torchvision import models, transforms

@router.message(F.photo)
async def classify_image(message: Message, bot: Bot):
    # Скачиваем фото
    photo = message.photo[-1]
    file_path = Path("temp.jpg")
    await bot.download(photo, destination=file_path)

    # Загружаем изображение
    image = Image.open(file_path)

    # Предобработка
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
    ])
    input_tensor = preprocess(image).unsqueeze(0)

    # Загружаем модель
    model = models.resnet50(pretrained=True)
    model.eval()

    # Предсказание
    with torch.no_grad():
        output = model(input_tensor)

    await message.answer(f"Распознано: {get_class_name(output)}")
```

### 2. OCR (Tesseract/EasyOCR)

```python
import easyocr

reader = easyocr.Reader(['ru', 'en'])

@router.message(F.photo)
async def extract_text(message: Message, bot: Bot):
    # Скачиваем фото
    photo = message.photo[-1]
    file_path = Path("temp.jpg")
    await bot.download(photo, destination=file_path)

    # Извлекаем текст
    result = reader.readtext(str(file_path))
    text = "\n".join([item[1] for item in result])

    await message.answer(f"📝 Распознанный текст:\n\n{text}")
```

### 3. Speech-to-Text (Whisper)

```python
import whisper

model = whisper.load_model("base")

@router.message(F.voice)
async def transcribe_voice(message: Message, bot: Bot):
    # Скачиваем голосовое сообщение
    voice = message.voice
    file_path = Path("temp.ogg")
    await bot.download(voice, destination=file_path)

    # Транскрибируем
    result = model.transcribe(str(file_path), language='ru')
    text = result["text"]

    await message.answer(f"🎤 Транскрипция:\n\n{text}")
```

### 4. PDF обработка (PyPDF2)

```python
import PyPDF2

@router.message(F.document)
async def extract_pdf_text(message: Message, bot: Bot):
    document = message.document

    if document.mime_type == "application/pdf":
        # Скачиваем PDF
        file_path = Path("temp.pdf")
        await bot.download(document, destination=file_path)

        # Извлекаем текст
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

        await message.answer(f"📄 Извлечено {len(text)} символов")
```

### 5. Видео обработка (OpenCV)

```python
import cv2

@router.message(F.video)
async def analyze_video(message: Message, bot: Bot):
    # Скачиваем видео
    video = message.video
    file_path = Path("temp.mp4")
    await bot.download(video, destination=file_path)

    # Открываем видео
    cap = cv2.VideoCapture(str(file_path))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Извлекаем кадры для анализа
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()

    await message.answer(
        f"🎬 Видео проанализировано:\n"
        f"Кадров: {frame_count}\n"
        f"FPS: {fps}\n"
        f"Длительность: {frame_count/fps:.1f} сек"
    )
```

## Структура хранилища

```
downloads/
├── photos/           # Изображения
│   ├── photo_123_abcd1234.jpg
│   └── photo_124_efgh5678.jpg
├── documents/        # Документы
│   ├── report.pdf
│   └── data.csv
├── audio/           # Аудиофайлы и голосовые
│   ├── song.mp3
│   └── voice_125.ogg
└── video/           # Видеофайлы
    ├── clip.mp4
    └── video_note_126.mp4
```

## Важные моменты

### ⚠️ Ограничения Telegram Bot API

1. **Размер файлов:**
   - Обычные пользователи: 20 МБ
   - Premium пользователи: 50 МБ
   - Фото (сжатые): 10 МБ

2. **Скорость:**
   - Лимит на скачивание: зависит от сервера
   - Используйте прогресс-бары для больших файлов

3. **Хранение:**
   - Файлы хранятся на серверах Telegram ограниченное время
   - Скачивайте важные файлы сразу

### ⚠️ Безопасность

```python
# Проверяйте MIME-типы
ALLOWED_MIMES = ['image/jpeg', 'image/png', 'application/pdf']

if document.mime_type not in ALLOWED_MIMES:
    await message.answer("❌ Недопустимый тип файла")
    return

# Проверяйте размер
MAX_SIZE = 10 * 1024 * 1024  # 10 МБ

if document.file_size > MAX_SIZE:
    await message.answer("❌ Файл слишком большой")
    return

# Санитизируйте имена файлов
import re
safe_name = re.sub(r'[^\w\s.-]', '', document.file_name)
```

### ⚠️ Производительность

```python
# Обработка в фоне для больших файлов
import asyncio

@router.message(F.video)
async def process_video_async(message: Message, bot: Bot):
    await message.answer("⏳ Обработка началась...")

    # Запускаем в фоне
    asyncio.create_task(process_video_task(message, bot))

async def process_video_task(message: Message, bot: Bot):
    # Долгая обработка
    ...
    await bot.send_message(
        message.chat.id,
        "✅ Обработка завершена!"
    )
```

## Примеры использования

### Датасет для обучения модели

```python
# Сохраняем все загруженные изображения с метками
@router.message(F.photo)
async def save_to_dataset(message: Message, bot: Bot):
    photo = message.photo[-1]
    caption = message.caption or "unlabeled"

    # Создаем папку для класса
    class_dir = DOWNLOAD_DIR / "dataset" / caption
    class_dir.mkdir(parents=True, exist_ok=True)

    # Сохраняем
    file_path = class_dir / f"{message.message_id}.jpg"
    await bot.download(photo, destination=file_path)

    await message.answer(f"✅ Добавлено в класс '{caption}'")
```

### Batch обработка

```python
# Обрабатываем несколько файлов одновременно
pending_files = []

@router.message(F.photo)
async def collect_photos(message: Message, bot: Bot):
    pending_files.append(message.photo[-1])
    await message.answer(f"📸 Файл {len(pending_files)} добавлен")

@router.message(Command("process"))
async def process_batch(message: Message, bot: Bot):
    await message.answer(f"⏳ Обработка {len(pending_files)} файлов...")

    for photo in pending_files:
        # Обработка...
        pass

    pending_files.clear()
    await message.answer("✅ Обработка завершена!")
```

## Best Practices

1. **Проверяйте типы и размеры** перед обработкой
2. **Удаляйте временные файлы** после обработки
3. **Используйте async** для долгих операций
4. **Логируйте ошибки** при работе с файлами
5. **Сжимайте результаты** перед отправкой
6. **Используйте прогресс-индикаторы** для UX
7. **Ограничивайте concurrent загрузки**

## Дальнейшее развитие

- Интеграция с облачными хранилищами (S3, Google Drive)
- Очередь задач (Celery, RQ)
- Кэширование результатов (Redis)
- Масштабирование (микросервисы)
- Мониторинг использования (Prometheus)
