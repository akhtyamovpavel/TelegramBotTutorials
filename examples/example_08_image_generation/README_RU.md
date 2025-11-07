# Example 7: Работа с изображениями (Генерация и отправка)

## Описание

Комплексный пример работы с изображениями - генерация, обработка и различные способы отправки. Критически важно для:
- 🎨 Генерации изображений (AI Art, Stable Diffusion, DALL-E)
- 📊 Создания графиков и визуализаций
- 🖼️ Обработки изображений с помощью ИИ
- 📈 Отчетов с визуальными данными

## Что нового

### ➕ Добавлено:
1. **FSInputFile** - отправка файла с диска
2. **BufferedInputFile** - отправка из памяти (BytesIO)
3. **URLInputFile** - отправка по URL
4. **InputMediaPhoto** - отправка альбомов (Media Group)
5. **answer_document** - отправка без сжатия Telegram
6. **PIL/Pillow** - генерация и обработка изображений

## Установка

```bash
# Базовые зависимости
pip install aiogram
# или
pip install python-telegram-bot

# Для работы с изображениями
pip install Pillow

# Опционально для продвинутой работы:
pip install matplotlib  # Графики
pip install opencv-python  # Обработка изображений
pip install numpy  # Массивы для изображений
```

## Запуск

```bash
export BOT_TOKEN="your_bot_token_here"

# aiogram
python examples/example_07_image_generation/aiogram/bot.py

# python-telegram-bot
python examples/example_07_image_generation/python_telegram_bot/bot.py
```

## Способы отправки изображений

### 1. FSInputFile - из файла на диске (aiogram)

**Когда использовать:** Файл уже сохранен на диске

```python
from aiogram.types import FSInputFile

photo = FSInputFile("path/to/image.jpg", filename="custom_name.jpg")
await message.answer_photo(photo, caption="Из файла")
```

**python-telegram-bot:**
```python
with open("path/to/image.jpg", 'rb') as photo:
    await update.message.reply_photo(photo, caption="Из файла")
```

### 2. BufferedInputFile - из памяти (aiogram)

**Когда использовать:** Изображение генерируется в памяти, не нужно сохранять

```python
from aiogram.types import BufferedInputFile
from io import BytesIO
from PIL import Image

# Создаем изображение в памяти
image = Image.new('RGB', (800, 600), color='blue')
bio = BytesIO()
image.save(bio, format='PNG')
bio.seek(0)

# Отправляем
photo = BufferedInputFile(bio.read(), filename="generated.png")
await message.answer_photo(photo)
```

**python-telegram-bot:**
```python
from io import BytesIO
from PIL import Image

image = Image.new('RGB', (800, 600), color='blue')
bio = BytesIO()
image.save(bio, format='PNG')
bio.seek(0)

await update.message.reply_photo(bio, caption="Из памяти")
```

### 3. URLInputFile - по URL (aiogram)

**Когда использовать:** Изображение находится в интернете

```python
from aiogram.types import URLInputFile

photo = URLInputFile("https://example.com/image.jpg")
await message.answer_photo(photo, caption="Из URL")
```

**python-telegram-bot:**
```python
url = "https://example.com/image.jpg"
await update.message.reply_photo(url, caption="Из URL")
```

### 4. Media Group - альбом изображений

**aiogram:**
```python
from aiogram.types import InputMediaPhoto, FSInputFile

media = [
    InputMediaPhoto(media=FSInputFile("img1.jpg"), caption="Фото 1"),
    InputMediaPhoto(media=FSInputFile("img2.jpg")),
    InputMediaPhoto(media=FSInputFile("img3.jpg")),
]

await message.answer_media_group(media=media)
```

**python-telegram-bot:**
```python
from telegram import InputMediaPhoto

media = []
for img_path in ["img1.jpg", "img2.jpg", "img3.jpg"]:
    with open(img_path, 'rb') as photo:
        media.append(InputMediaPhoto(media=photo.read()))

await update.message.reply_media_group(media=media)
```

### 5. Document - без сжатия Telegram

**Когда использовать:** Нужно полное качество, PNG с прозрачностью

```python
# aiogram
document = FSInputFile("high_quality.png")
await message.answer_document(document, caption="Без сжатия")

# python-telegram-bot
with open("high_quality.png", 'rb') as doc:
    await update.message.reply_document(doc, caption="Без сжатия")
```

## Интеграция с ИИ-моделями

### 1. Генерация изображений (Stable Diffusion)

```python
# Установка: pip install diffusers torch transformers
from diffusers import StableDiffusionPipeline
import torch
from io import BytesIO

# Загружаем модель (один раз при старте)
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")  # Или "cpu" если нет GPU

@router.message(Command("generate"))
async def generate_sd(message: Message):
    # Получаем промпт от пользователя
    prompt = message.text.replace("/generate", "").strip()

    if not prompt:
        await message.answer("Используйте: /generate <описание изображения>")
        return

    await message.answer("🎨 Генерирую изображение... (это может занять минуту)")

    # Генерируем
    image = pipe(prompt).images[0]

    # Конвертируем в BytesIO
    bio = BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)

    # Отправляем
    photo = BufferedInputFile(bio.read(), filename="generated.png")
    await message.answer_photo(
        photo,
        caption=f"🎨 Промпт: {prompt}"
    )
```

### 2. DALL-E API (OpenAI)

```python
# Установка: pip install openai
import openai
from io import BytesIO
import requests

openai.api_key = "your-api-key"

@router.message(Command("dalle"))
async def generate_dalle(message: Message):
    prompt = message.text.replace("/dalle", "").strip()

    await message.answer("🎨 Генерирую через DALL-E...")

    # Генерируем
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )

    # Скачиваем изображение
    image_url = response['data'][0]['url']
    image_data = requests.get(image_url).content

    # Отправляем
    photo = BufferedInputFile(image_data, filename="dalle.png")
    await message.answer_photo(
        photo,
        caption=f"🎨 DALL-E: {prompt}"
    )
```

### 3. Графики с Matplotlib

```python
# Установка: pip install matplotlib
import matplotlib.pyplot as plt
from io import BytesIO

@router.message(Command("plot"))
async def create_plot(message: Message):
    # Создаем данные
    x = list(range(10))
    y = [i**2 for i in x]

    # Создаем график
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o')
    plt.title('Квадратичная функция')
    plt.xlabel('X')
    plt.ylabel('Y = X²')
    plt.grid(True)

    # Сохраняем в BytesIO
    bio = BytesIO()
    plt.savefig(bio, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    bio.seek(0)

    # Отправляем
    photo = BufferedInputFile(bio.read(), filename="plot.png")
    await message.answer_photo(photo, caption="📊 График функции Y = X²")
```

### 4. Обработка с OpenCV

```python
# Установка: pip install opencv-python
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

@router.message(F.photo)
async def apply_filter(message: Message, bot: Bot):
    # Скачиваем фото
    photo = message.photo[-1]
    file_path = Path("temp.jpg")
    await bot.download(photo, destination=file_path)

    # Загружаем с OpenCV
    img = cv2.imread(str(file_path))

    # Применяем фильтр (например, Canny edge detection)
    edges = cv2.Canny(img, 100, 200)

    # Конвертируем обратно в RGB для PIL
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    # Сохраняем в BytesIO
    pil_img = Image.fromarray(edges_rgb)
    bio = BytesIO()
    pil_img.save(bio, format='PNG')
    bio.seek(0)

    # Отправляем
    photo_result = BufferedInputFile(bio.read(), filename="edges.png")
    await message.answer_photo(
        photo_result,
        caption="🎨 Применен фильтр обнаружения границ"
    )
```

### 5. Модели классификации изображений

```python
# Установка: pip install transformers pillow torch
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image

# Загружаем модель
processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

@router.message(F.photo)
async def classify_image(message: Message, bot: Bot):
    # Скачиваем фото
    photo = message.photo[-1]
    file_path = Path("temp.jpg")
    await bot.download(photo, destination=file_path)

    # Загружаем изображение
    image = Image.open(file_path)

    # Обрабатываем
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits

    # Получаем предсказание
    predicted_class_idx = logits.argmax(-1).item()
    predicted_class = model.config.id2label[predicted_class_idx]

    await message.answer(
        f"🤖 <b>Классификация изображения:</b>\n\n"
        f"Класс: {predicted_class}\n"
        f"Уверенность: {logits.softmax(dim=1).max().item():.2%}"
    )
```

## Работа с PIL (Pillow)

### Основные операции

```python
from PIL import Image, ImageDraw, ImageFont

# Создание изображения
img = Image.new('RGB', (800, 600), color=(73, 109, 137))

# Открытие существующего
img = Image.open('photo.jpg')

# Изменение размера
img = img.resize((400, 300))

# Поворот
img = img.rotate(45)

# Отражение
img = img.transpose(Image.FLIP_LEFT_RIGHT)

# Конвертация в grayscale
img = img.convert('L')
```

### Рисование на изображении

```python
from PIL import Image, ImageDraw, ImageFont

# Создаем изображение
img = Image.new('RGB', (800, 600), color='white')
draw = ImageDraw.Draw(img)

# Текст
try:
    font = ImageFont.truetype("arial.ttf", 60)
except:
    font = ImageFont.load_default()

draw.text((50, 50), "Hello, World!", fill='black', font=font)

# Линия
draw.line([(0, 0), (800, 600)], fill='red', width=5)

# Прямоугольник
draw.rectangle([100, 100, 300, 200], outline='blue', width=3)

# Круг
draw.ellipse([400, 200, 600, 400], fill='green')

# Сохранение
img.save('result.png')
```

### Наложение изображений

```python
from PIL import Image

# Открываем два изображения
background = Image.open('background.jpg')
overlay = Image.open('overlay.png')

# Изменяем размер оверлея
overlay = overlay.resize((200, 200))

# Накладываем
background.paste(overlay, (100, 100), overlay)  # Третий параметр - маска прозрачности

background.save('combined.png')
```

## Сравнение способов отправки

| Способ | Преимущества | Недостатки | Использование |
|--------|-------------|------------|---------------|
| **FSInputFile** | Простота, работа с существующими файлами | Требует место на диске | Готовые изображения |
| **BufferedInputFile** | Экономия места, быстрота | Больше кода | Генерация на лету |
| **URLInputFile** | Не нужно скачивать | Зависит от интернета | Внешние API |
| **Media Group** | Красивое отображение | До 10 файлов | Альбомы, серии |
| **Document** | Без сжатия | Больший размер | Высокое качество |

## Важные моменты

### ⚠️ Ограничения размеров

```python
# Проверка размера перед отправкой
from PIL import Image

img = Image.open('large_image.jpg')

# Ограничиваем размер (для фото - 10 МБ)
MAX_SIZE = (2048, 2048)
img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)

bio = BytesIO()
img.save(bio, format='JPEG', quality=85, optimize=True)
bio.seek(0)
```

### ⚠️ Форматы изображений

```python
# Telegram поддерживает: JPEG, PNG, GIF, WebP

# PNG с прозрачностью - отправляйте как document
if img.mode == 'RGBA':
    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    await message.answer_document(
        BufferedInputFile(bio.read(), "image.png"),
        caption="PNG с прозрачностью"
    )
else:
    # JPEG для фото
    bio = BytesIO()
    img.convert('RGB').save(bio, format='JPEG', quality=90)
    bio.seek(0)
    await message.answer_photo(BufferedInputFile(bio.read(), "image.jpg"))
```

### ⚠️ Производительность

```python
# Генерация изображений в отдельном процессе
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(max_workers=4)

@router.message(Command("heavy"))
async def generate_heavy(message: Message):
    await message.answer("⏳ Генерирую...")

    # Запускаем в отдельном процессе
    loop = asyncio.get_event_loop()
    image_data = await loop.run_in_executor(
        executor,
        generate_complex_image,  # Тяжелая функция
        "parameters"
    )

    photo = BufferedInputFile(image_data, "result.png")
    await message.answer_photo(photo, caption="✅ Готово!")
```

## Best Practices

1. **Используйте BytesIO** для генерируемых изображений
2. **Сжимайте изображения** перед отправкой
3. **Обрабатывайте ошибки** (файл не найден, невалидный формат)
4. **Удаляйте временные файлы** после отправки
5. **Используйте async** для долгих операций
6. **Кэшируйте результаты** если возможно
7. **Оптимизируйте качество** vs размер файла

## Требования для production

```txt
# requirements.txt
aiogram==3.15.0  # или python-telegram-bot==21.9
Pillow==10.4.0
numpy==1.26.4

# Опционально:
matplotlib==3.9.0  # Графики
opencv-python==4.10.0  # Обработка изображений
torch==2.3.0  # Для deep learning
diffusers==0.28.0  # Stable Diffusion
transformers==4.41.0  # Hugging Face модели
openai==1.30.0  # DALL-E API
```

## Примеры реальных проектов

1. **AI Art бот** - генерация по текстовому описанию
2. **Мем-генератор** - добавление текста на изображения
3. **Фоторедактор бот** - применение фильтров
4. **Аналитический бот** - графики и визуализация данных
5. **QR-код генератор** - создание QR-кодов
6. **Бот-дизайнер** - создание превью, баннеров
7. **OCR бот** - извлечение текста из изображений
