# Example 6: Telegram Mini Apps (WebApp)

## ⚠️ Критически важные требования

### 1️⃣ Тип кнопки: ТОЛЬКО KeyboardButton!

**`sendData()` работает ТОЛЬКО с `KeyboardButton` (reply клавиатура), НЕ с `InlineKeyboardButton`!**

```python
# ✅ ПРАВИЛЬНО - KeyboardButton (кнопка в клавиатуре):
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Open", web_app=WebAppInfo(url=URL))]],
    resize_keyboard=True
)

# ❌ НЕПРАВИЛЬНО - InlineKeyboardButton (кнопка под сообщением):
# keyboard = InlineKeyboardMarkup(
#     inline_keyboard=[[InlineKeyboardButton(text="Open", web_app=WebAppInfo(url=URL))]]
# )
# WebApp откроется, но sendData() НЕ будет работать!
```

**Источник:** [StackOverflow - Web App Data not received](https://stackoverflow.com/questions/72988184/)

### 2️⃣ HTTPS обязателен

**Telegram НЕ поддерживает `data:` URLs и HTTP для WebApp!**

WebApp **обязательно** должен быть размещен на **реальном HTTPS сервере**.

📖 **[Подробная инструкция по размещению → DEPLOYMENT.md](./DEPLOYMENT.md)**

**Быстрые варианты:**
- ✅ GitHub Pages (бесплатно, рекомендуется)
- ✅ Vercel/Netlify (бесплатно)
- ✅ Ngrok (для тестирования)

---

## 🎯 Что нового в этом примере

В предыдущих примерах мы работали с:
- Обычными кнопками (Reply Keyboard, Example 3)
- Машиной состояний (FSM, Example 4)
- Базами данных (Example 5)

**Новые концепции:**
- **Telegram Mini Apps (WebApp)** - веб-приложения внутри Telegram
- **WebAppInfo** - кнопки, открывающие веб-интерфейс
- **web_app_data** - получение данных из WebApp
- **Telegram WebApp API** - JavaScript API для взаимодействия

## 📚 Концепции

### Что такое Telegram Mini Apps?

**Telegram Mini Apps** (ранее WebApp) - это веб-приложения (HTML/CSS/JavaScript), которые открываются **внутри** Telegram. Они позволяют создавать богатые интерактивные интерфейсы, которые невозможно реализовать с помощью обычных кнопок.

**Преимущества:**
- **Богатый UI** - полноценный веб-интерфейс (canvas, WebGL, формы)
- **Нативная интеграция** - доступ к данным пользователя Telegram
- **Без установки** - открывается прямо в чате
- **Кроссплатформенность** - работает на всех устройствах

### Зачем это для ИИ-ботов?

1. **Интерактивная визуализация** - показ графиков, диаграмм результатов
2. **Сложные формы** - настройка параметров ИИ-модели
3. **Canvas/WebGL** - рисование промптов для Image-to-Image
4. **Превью результатов** - интерактивный просмотр сгенерированного контента
5. **Настройки моделей** - UI для тонкой настройки параметров

## 🔄 Различия между библиотеками

| Функция | aiogram 3.x | python-telegram-bot 20.x |
|---------|-------------|--------------------------|
| **WebApp кнопка** | `WebAppInfo(url="...")` | `WebAppInfo(url="...")` |
| **Получение данных** | `F.web_app_data` | `filters.StatusUpdate.WEB_APP_DATA` |
| **Keyboard** | `InlineKeyboardButton` | `InlineKeyboardButton` |
| **Данные WebApp** | `message.web_app_data.data` | `message.web_app_data.data` |

## 📖 Теория: Как работает WebApp

### Архитектура:

```
┌─────────────────┐
│  Telegram Bot   │
│   (Python)      │
└────────┬────────┘
         │
         │ 1. Отправляет кнопку с WebApp
         ↓
┌─────────────────┐
│   Пользователь  │
│   в Telegram    │
└────────┬────────┘
         │
         │ 2. Нажимает кнопку
         ↓
┌─────────────────┐
│   WebApp        │
│ (HTML/CSS/JS)   │
│ на веб-сервере  │
└────────┬────────┘
         │
         │ 3. Отправляет данные через Telegram.WebApp.sendData()
         ↓
┌─────────────────┐
│  Telegram Bot   │
│  получает данные│
└─────────────────┘
```

### Процесс взаимодействия:

1. **Бот отправляет** кнопку с `web_app` параметром
2. **Пользователь** нажимает кнопку
3. **Telegram открывает** WebApp (ваш HTML/JS) внутри чата
4. **WebApp** взаимодействует с пользователем
5. **WebApp отправляет** данные обратно боту через `Telegram.WebApp.sendData()`
6. **Бот получает** данные и обрабатывает

## 📖 Теория: Создание WebApp

### 1. Создание HTML страницы

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ИИ Настройки</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            font-family: sans-serif;
            padding: 20px;
            background-color: var(--tg-theme-bg-color);
            color: var(--tg-theme-text-color);
        }
    </style>
</head>
<body>
    <h2>Настройки генерации</h2>
    <label>Промпт:</label>
    <textarea id="prompt" rows="4"></textarea>

    <label>Количество вариантов:</label>
    <input type="number" id="num_images" value="4" min="1" max="10">

    <button onclick="sendData()">Сгенерировать</button>

    <script>
        // Инициализация Telegram WebApp
        let tg = window.Telegram.WebApp;
        tg.expand(); // Развернуть на весь экран

        function sendData() {
            const data = {
                prompt: document.getElementById('prompt').value,
                num_images: document.getElementById('num_images').value
            };

            // Отправляем данные боту
            tg.sendData(JSON.stringify(data));
        }
    </script>
</body>
</html>
```

### 2. Размещение WebApp

⚠️ **Важно:** WebApp должен быть доступен по **HTTPS URL**! Telegram не поддерживает `data:` URLs.

**📖 [Подробная инструкция → DEPLOYMENT.md](./DEPLOYMENT.md)**

**Быстрые опции:**
- **GitHub Pages** - бесплатно, просто, рекомендуется
- **Vercel/Netlify** - бесплатно для статики
- **Ngrok** - для локальной разработки и тестирования
- **Свой сервер** - с SSL сертификатом

### 3. aiogram: Отправка кнопки с WebApp

```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

@router.message(Command("settings"))
async def show_webapp(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚙️ Открыть настройки",
                    web_app=WebAppInfo(url="https://your-domain.com/webapp.html")
                )
            ]
        ]
    )

    await message.answer(
        "Настройте параметры генерации:",
        reply_markup=keyboard
    )
```

### 4. aiogram: Получение данных из WebApp

```python
@router.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    # Получаем данные из WebApp
    import json
    data = json.loads(message.web_app_data.data)

    prompt = data['prompt']
    num_images = int(data['num_images'])

    await message.answer(
        f"Получены настройки:\n"
        f"Промпт: {prompt}\n"
        f"Количество: {num_images}\n\n"
        f"Генерирую..."
    )

    # Генерация изображений
    images = generate_images(prompt, count=num_images)

    # Отправка результата
    builder = MediaGroupBuilder(caption=f"Результаты для: {prompt}")
    for img in images:
        builder.add_photo(media=img)

    await message.answer_media_group(media=builder.build())
```

### 5. python-telegram-bot: Аналогично

```python
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import MessageHandler, filters

async def show_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="⚙️ Открыть настройки",
                web_app=WebAppInfo(url="https://your-domain.com/webapp.html")
            )
        ]
    ])

    await update.message.reply_text(
        "Настройте параметры генерации:",
        reply_markup=keyboard
    )

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import json
    data = json.loads(update.message.web_app_data.data)

    prompt = data['prompt']
    num_images = int(data['num_images'])

    await update.message.reply_text(f"Генерирую {num_images} изображений...")

    # Генерация и отправка...

# Регистрация
application.add_handler(CommandHandler("settings", show_webapp))
application.add_handler(
    MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data)
)
```

## 🎨 Практическое применение для ИИ

### 1. Интерактивный редактор промптов

```html
<!-- Редактор с превью -->
<div id="prompt-editor">
    <textarea id="prompt">beautiful landscape</textarea>
    <div id="suggestions">
        <button onclick="addToPrompt('sunset')">🌅 Sunset</button>
        <button onclick="addToPrompt('mountains')">⛰️ Mountains</button>
        <button onclick="addToPrompt('4k, detailed')">✨ HD</button>
    </div>
</div>

<script>
function addToPrompt(text) {
    let prompt = document.getElementById('prompt');
    prompt.value += ', ' + text;
}
</script>
```

### 2. Настройка параметров модели

```html
<div class="settings">
    <label>Модель:</label>
    <select id="model">
        <option value="sd1.5">Stable Diffusion 1.5</option>
        <option value="sdxl">Stable Diffusion XL</option>
        <option value="dalle">DALL-E 3</option>
    </select>

    <label>Steps: <span id="steps-value">30</span></label>
    <input type="range" id="steps" min="10" max="100" value="30"
           oninput="document.getElementById('steps-value').innerText = this.value">

    <label>CFG Scale: <span id="cfg-value">7</span></label>
    <input type="range" id="cfg" min="1" max="20" value="7"
           oninput="document.getElementById('cfg-value').innerText = this.value">

    <label>Размер:</label>
    <select id="size">
        <option value="512x512">512x512</option>
        <option value="768x768">768x768</option>
        <option value="1024x1024">1024x1024</option>
    </select>
</div>

<button onclick="generateWithSettings()">Генерировать</button>

<script>
function generateWithSettings() {
    const settings = {
        model: document.getElementById('model').value,
        steps: parseInt(document.getElementById('steps').value),
        cfg_scale: parseFloat(document.getElementById('cfg').value),
        size: document.getElementById('size').value,
        prompt: document.getElementById('prompt').value
    };

    window.Telegram.WebApp.sendData(JSON.stringify(settings));
}
</script>
```

### 3. Canvas для рисования маски (Inpainting)

```html
<canvas id="mask-canvas" width="512" height="512"></canvas>
<div class="tools">
    <button onclick="setBrushSize(10)">Маленькая кисть</button>
    <button onclick="setBrushSize(30)">Большая кисть</button>
    <button onclick="clearCanvas()">Очистить</button>
</div>

<button onclick="sendMask()">Отправить маску</button>

<script>
const canvas = document.getElementById('mask-canvas');
const ctx = canvas.getContext('2d');
let painting = false;
let brushSize = 20;

// Рисование маски
canvas.addEventListener('mousedown', startPaint);
canvas.addEventListener('mouseup', stopPaint);
canvas.addEventListener('mousemove', paint);

function startPaint(e) {
    painting = true;
    paint(e);
}

function stopPaint() {
    painting = false;
    ctx.beginPath();
}

function paint(e) {
    if (!painting) return;

    ctx.lineWidth = brushSize;
    ctx.lineCap = 'round';
    ctx.strokeStyle = 'white';

    ctx.lineTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
}

function sendMask() {
    // Конвертируем canvas в base64
    const maskData = canvas.toDataURL('image/png');

    window.Telegram.WebApp.sendData(JSON.stringify({
        type: 'inpainting',
        mask: maskData,
        prompt: document.getElementById('prompt').value
    }));
}
</script>
```

## 🚀 Запуск примеров

### Шаг 1: Разместите WebApp

⚠️ **Обязательно:** Разместите файл `webapp/index.html` на HTTPS сервере.

📖 **[Подробные инструкции в DEPLOYMENT.md](./DEPLOYMENT.md)**

**Быстрый вариант (GitHub Pages):**
1. Создайте публичный репозиторий на GitHub
2. Загрузите папку `webapp`
3. Включите GitHub Pages в Settings
4. Получите URL: `https://username.github.io/repo-name/webapp/index.html`

### Шаг 2: Запустите бота

```bash
# aiogram версия
export BOT_TOKEN="your_bot_token"
export WEBAPP_URL="https://your-domain.com/webapp.html"
python examples/example_06_mini_apps/aiogram/bot.py

# python-telegram-bot версия
export BOT_TOKEN="your_bot_token"
export WEBAPP_URL="https://your-domain.com/webapp.html"
python examples/example_06_mini_apps/python_telegram_bot/bot.py
```

### Шаг 3: Используйте

1. Отправьте `/start` боту
2. Нажмите кнопку "Открыть WebApp"
3. Настройте параметры в веб-интерфейсе
4. Нажмите "Отправить"
5. Бот получит данные и обработает их

## 📝 Команды бота

- `/start` - Приветствие
- `/webapp` - Открыть WebApp с настройками
- `/simple` - Пример простого WebApp
- `/advanced` - Продвинутый WebApp с canvas

## 🎓 Что изучили

1. ✅ Создание Telegram Mini Apps (WebApp)
2. ✅ Интеграция веб-интерфейса с ботом
3. ✅ Telegram WebApp API (JavaScript)
4. ✅ Отправка данных из WebApp в бота
5. ✅ Практическое применение для настройки ИИ-моделей

## 📚 Дополнительные материалы

### Telegram WebApp API методы:

```javascript
// Основные методы
Telegram.WebApp.ready();              // Готовность WebApp
Telegram.WebApp.expand();             // Развернуть на весь экран
Telegram.WebApp.close();              // Закрыть WebApp
Telegram.WebApp.sendData(data);       // Отправить данные боту

// Получение данных пользователя
Telegram.WebApp.initDataUnsafe.user;  // Данные пользователя
Telegram.WebApp.initDataUnsafe.query_id; // ID запроса

// Кнопки
Telegram.WebApp.MainButton.setText("Отправить");
Telegram.WebApp.MainButton.show();
Telegram.WebApp.MainButton.onClick(callback);

// Тема
Telegram.WebApp.themeParams.bg_color;        // Цвет фона
Telegram.WebApp.themeParams.text_color;      // Цвет текста
Telegram.WebApp.themeParams.button_color;    // Цвет кнопки
```

### CSS переменные Telegram:

```css
body {
    background-color: var(--tg-theme-bg-color);
    color: var(--tg-theme-text-color);
}

button {
    background-color: var(--tg-theme-button-color);
    color: var(--tg-theme-button-text-color);
}

a {
    color: var(--tg-theme-link-color);
}
```

### Лучшие практики:

1. **HTTPS обязательно** - WebApp работает только по HTTPS
2. **Адаптивность** - делайте responsive design
3. **Тема Telegram** - используйте CSS переменные для цветов
4. **Валидация данных** - проверяйте данные на боте
5. **Feedback** - показывайте прогресс генерации

## 🔗 Связанные примеры

- **Example 3** - Reply Keyboard (более простой UI)
- **Example 4** - FSM States (альтернатива WebApp для простых форм)
- **Example 8** - Image Generation (куда отправлять результаты из WebApp)

---

**Совет для ИИ-разработчиков:** WebApp идеально подходит для сложных настроек ИИ-моделей, где нужны слайдеры, превью, canvas. Для простых форм используйте FSM + обычные кнопки.
