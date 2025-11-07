# ⚠️ КРИТИЧЕСКИ ВАЖНО: Тип кнопки для WebApp

## Проблема: WebApp отправляет данные, но бот их не получает

Если вы видите в консоли браузера (DevTools):
```
[Telegram.WebView] > postEvent "web_app_data_send" {data: "..."}
```

Но бот **НЕ получает данные** - проблема в **типе кнопки**!

## ❌ Частая ошибка: InlineKeyboardButton

```python
# ❌ ЭТО НЕ РАБОТАЕТ для sendData()!
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(
            text="Открыть WebApp",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
)
```

**Что происходит:**
- ✅ WebApp откроется
- ✅ JavaScript выполнится
- ✅ `tg.sendData()` вызовется
- ❌ Данные **НЕ дойдут до бота**!

## ✅ Правильное решение: KeyboardButton

```python
# ✅ ЭТО РАБОТАЕТ!
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

keyboard = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(
            text="Открыть WebApp",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]],
    resize_keyboard=True  # Кнопка занимает меньше места
)
```

**Что происходит:**
- ✅ WebApp откроется
- ✅ JavaScript выполнится
- ✅ `tg.sendData()` вызовется
- ✅ Данные **дойдут до бота**!

## Разница между типами кнопок

| Характеристика | InlineKeyboardButton | KeyboardButton |
|----------------|----------------------|----------------|
| **Расположение** | Под сообщением | В клавиатуре (внизу экрана) |
| **Тип клавиатуры** | InlineKeyboardMarkup | ReplyKeyboardMarkup |
| **WebApp открывается?** | ✅ Да | ✅ Да |
| **`sendData()` работает?** | ❌ **НЕТ** | ✅ **ДА** |
| **Callback queries?** | ✅ Да | ❌ Нет |
| **Остается после клика?** | ✅ Да | Скрывается после отправки |

## Визуальная разница

### InlineKeyboardButton (под сообщением):
```
┌─────────────────────────┐
│ Сообщение от бота       │
└─────────────────────────┘
┌─────────────────────────┐
│    [Открыть WebApp]     │ ← Кнопка ПОД сообщением
└─────────────────────────┘
```

### KeyboardButton (в клавиатуре):
```
┌─────────────────────────┐
│ Сообщение от бота       │
└─────────────────────────┘

         ...

╔═════════════════════════╗
║   [Открыть WebApp]      ║ ← Кнопка В КЛАВИАТУРЕ
╚═════════════════════════╝
```

## Почему так?

Это **ограничение Telegram Bot API**:

- **InlineKeyboardButton** предназначен для callback queries
- **KeyboardButton** предназначен для отправки данных (текст, контакт, локация, **WebApp data**)

**Официальная документация:**
- [Telegram Bot API - KeyboardButton](https://core.telegram.org/bots/api#keyboardbutton)
- [Telegram Bot API - WebAppInfo](https://core.telegram.org/bots/webapps#launching-mini-apps)

**StackOverflow:**
- [Why Web App Data is not received by bot?](https://stackoverflow.com/questions/72988184/)

## Примеры кода

### aiogram 3.x

```python
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

router = Router()

@router.message(Command("webapp"))
async def cmd_webapp(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="⚙️ Открыть настройки",
                web_app=WebAppInfo(url="https://your-domain.com/webapp.html")
            )
        ]],
        resize_keyboard=True
    )

    await message.answer(
        "Нажмите кнопку в клавиатуре:",
        reply_markup=keyboard
    )
```

### python-telegram-bot

```python
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import ContextTypes

async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [[
            KeyboardButton(
                text="⚙️ Открыть настройки",
                web_app=WebAppInfo(url="https://your-domain.com/webapp.html")
            )
        ]],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Нажмите кнопку в клавиатуре:",
        reply_markup=keyboard
    )
```

## Как это исправить в существующем коде

### Шаг 1: Измените импорты

```python
# ❌ Удалите:
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ Добавьте:
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
```

### Шаг 2: Измените создание клавиатуры

```python
# ❌ Было:
# keyboard = InlineKeyboardMarkup(
#     inline_keyboard=[[
#         InlineKeyboardButton(text="...", web_app=WebAppInfo(url=URL))
#     ]]
# )

# ✅ Стало:
keyboard = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="...", web_app=WebAppInfo(url=URL))
    ]],
    resize_keyboard=True
)
```

### Шаг 3: Перезапустите бота

```bash
# Остановите бота (Ctrl+C)
# Перезапустите:
python bot.py
```

## Проверка

После исправления:

1. Отправьте команду `/webapp`
2. Вы увидите кнопку **В КЛАВИАТУРЕ** (внизу экрана)
3. Нажмите кнопку
4. Заполните WebApp
5. Нажмите "Отправить"
6. **Бот получит данные!**

## Чеклист

- [ ] Используется `KeyboardButton`, НЕ `InlineKeyboardButton`
- [ ] Используется `ReplyKeyboardMarkup`, НЕ `InlineKeyboardMarkup`
- [ ] Добавлен параметр `resize_keyboard=True` (опционально, для UX)
- [ ] Бот перезапущен после изменений
- [ ] WebApp размещен на HTTPS сервере
- [ ] Обработчик `F.web_app_data` / `filters.StatusUpdate.WEB_APP_DATA` зарегистрирован
- [ ] `allowed_updates` включает `UpdateType.MESSAGE`

## FAQ

### Q: Можно ли использовать оба типа кнопок?

**A:** Да, но для **разных целей**:

```python
# InlineKeyboardButton - для callback queries:
inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="ℹ️ Инфо", callback_data="info")
]])

# KeyboardButton - для WebApp с sendData():
reply_keyboard = ReplyKeyboardMarkup(keyboard=[[
    KeyboardButton(text="⚙️ Настройки", web_app=WebAppInfo(url=URL))
]])
```

### Q: Как скрыть reply клавиатуру после использования?

**A:** Используйте `ReplyKeyboardRemove`:

```python
from aiogram.types import ReplyKeyboardRemove

await message.answer(
    "Данные получены!",
    reply_markup=ReplyKeyboardRemove()
)
```

### Q: Можно ли сделать кнопку одноразовой?

**A:** Да, используйте `one_time_keyboard=True`:

```python
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="...", web_app=WebAppInfo(url=URL))]],
    resize_keyboard=True,
    one_time_keyboard=True  # Скроется после нажатия
)
```

## Дополнительные материалы

- 📖 [README.md](./README.md) - основная документация
- 🐛 [DEBUG.md](./DEBUG.md) - отладка проблем
- 🔧 [FIX_NO_RESPONSE.md](./FIX_NO_RESPONSE.md) - исправление "бот не отвечает"
- 🚀 [DEPLOYMENT.md](./DEPLOYMENT.md) - размещение WebApp

## Итог

**Запомните:**
- 🔴 **InlineKeyboardButton** → sendData() **НЕ РАБОТАЕТ**
- 🟢 **KeyboardButton** → sendData() **РАБОТАЕТ**

Это не баг, это **особенность Telegram Bot API**!
