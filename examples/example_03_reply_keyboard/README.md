# Example 3: Reply Keyboard (Обычные кнопки)

## Описание

Бот с Reply Keyboard - обычными кнопками, которые заменяют клавиатуру пользователя:
- Главное меню с навигацией
- Подменю настроек
- Кнопки для отправки локации и контакта
- Возможность скрыть клавиатуру

## Что нового по сравнению с Example 2 (Inline Keyboard)

### ➕ Добавлено:
1. **ReplyKeyboardMarkup** - обычная клавиатура (не inline)
2. **KeyboardButton** - кнопки на клавиатуре
3. **request_location** - запрос геолокации
4. **request_contact** - запрос контакта
5. **ReplyKeyboardRemove** - скрытие клавиатуры
6. **Фильтры по тексту** - обработка конкретных кнопок

### Ключевые различия: Reply Keyboard vs Inline Keyboard

| Характеристика | Reply Keyboard | Inline Keyboard |
|----------------|----------------|-----------------|
| **Расположение** | Заменяет системную клавиатуру | Под сообщением |
| **Отправка** | Отправляет текст | Отправляет callback_data |
| **Постоянство** | Остается после нажатия | Остается с сообщением |
| **Редактирование** | Нельзя изменить | Можно изменить |
| **Использование** | Навигация, меню | Действия, выбор |

## Когда использовать Reply Keyboard?

✅ **Подходит для:**
- Главного меню бота
- Постоянной навигации
- Частых действий
- Запроса локации/контакта

❌ **Не подходит для:**
- Динамических списков
- Действий с данными
- Редактируемых опций

## Установка

```bash
# Зависимости те же
pip install aiogram
# или
pip install python-telegram-bot
```

## Запуск

```bash
export BOT_TOKEN="your_bot_token_here"

# aiogram
python examples/example_05_reply_keyboard/aiogram/bot.py

# python-telegram-bot
python examples/example_05_reply_keyboard/python_telegram_bot/bot.py
```

## Ключевые концепции

### 1. Создание ReplyKeyboard

**aiogram:**
```python
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Кнопка 1"), KeyboardButton(text="Кнопка 2")],
        [KeyboardButton(text="Кнопка 3")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)
```

**python-telegram-bot:**
```python
keyboard = [
    [KeyboardButton("Кнопка 1"), KeyboardButton("Кнопка 2")],
    [KeyboardButton("Кнопка 3")]
]
reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True,
    one_time_keyboard=False
)
```

### 2. Параметры ReplyKeyboardMarkup

- **resize_keyboard** - автоматически подгоняет размер кнопок
- **one_time_keyboard** - скрывает клавиатуру после нажатия
- **input_field_placeholder** - подсказка в поле ввода
- **selective** - показывать только определенным пользователям

### 3. Специальные кнопки

**Запрос локации:**
```python
KeyboardButton(text="📍 Локация", request_location=True)
```

**Запрос контакта:**
```python
KeyboardButton(text="📱 Контакт", request_contact=True)
```

### 4. Обработка нажатий

**aiogram** (через фильтры):
```python
@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    await message.answer("Ваша статистика")
```

**python-telegram-bot** (через Regex):
```python
application.add_handler(
    MessageHandler(filters.Regex("^📊 Статистика$"), show_stats)
)
```

### 5. Скрытие клавиатуры

Обе библиотеки:
```python
await message.reply_text(
    "Клавиатура скрыта",
    reply_markup=ReplyKeyboardRemove()
)
```

## Обработка специальных типов сообщений

### Геолокация

**aiogram:**
```python
@router.message(F.location)
async def handle_location(message: Message):
    lat = message.location.latitude
    lon = message.location.longitude
```

**python-telegram-bot:**
```python
application.add_handler(
    MessageHandler(filters.LOCATION, handle_location)
)
```

### Контакт

**aiogram:**
```python
@router.message(F.contact)
async def handle_contact(message: Message):
    phone = message.contact.phone_number
    name = message.contact.first_name
```

**python-telegram-bot:**
```python
application.add_handler(
    MessageHandler(filters.CONTACT, handle_contact)
)
```

## Паттерны использования

### 1. Многоуровневое меню

```python
# Главное меню
main_keyboard = ReplyKeyboardMarkup(...)

# Подменю
settings_keyboard = ReplyKeyboardMarkup(...)

# Переключение между меню
await message.answer("Настройки", reply_markup=settings_keyboard)
await message.answer("Главное меню", reply_markup=main_keyboard)
```

### 2. Условные кнопки

```python
def get_user_keyboard(is_premium: bool):
    buttons = [
        [KeyboardButton("📊 Статистика")],
        [KeyboardButton("⚙️ Настройки")]
    ]

    if is_premium:
        buttons.append([KeyboardButton("👑 Premium функции")])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
```

### 3. Динамическая генерация

```python
def get_category_keyboard(categories: list[str]):
    keyboard = []
    row = []

    for i, category in enumerate(categories):
        row.append(KeyboardButton(category))

        # По 2 кнопки в ряд
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []

    if row:  # Добавляем остаток
        keyboard.append(row)

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
```

## Важные моменты

### ⚠️ Безопасность

При использовании кнопок с локацией/контактом:
- Объясняйте пользователю, зачем нужны данные
- Храните данные безопасно
- Соблюдайте GDPR и другие законы

### ⚠️ UX рекомендации

1. **Не перегружайте** - максимум 3-4 кнопки в ряд
2. **Используйте эмодзи** - для визуального разделения
3. **Логичная группировка** - связанные действия рядом
4. **Кнопка "Назад"** - для навигации между меню
5. **Команда /hide** - дайте возможность скрыть клавиатуру

### ⚠️ Порядок обработчиков (PTB)

В python-telegram-bot важен порядок регистрации:
```python
# Сначала специфичные фильтры
application.add_handler(MessageHandler(filters.Regex("^📊$"), stats))

# Потом общие
application.add_handler(MessageHandler(filters.TEXT, handle_text))
```

## Сравнение подходов

| Аспект | aiogram | python-telegram-bot |
|--------|---------|---------------------|
| **Создание** | `keyboard=[[...]]` | Список списков |
| **Обработка** | `F.text == "..."` | `filters.Regex("^...$")` |
| **Фильтры** | Magic Filter `F` | Модуль `filters` |
| **Локация** | `F.location` | `filters.LOCATION` |
| **Контакт** | `F.contact` | `filters.CONTACT` |

## Комбинирование с Inline Keyboard

Можно использовать оба типа одновременно:

```python
# Reply Keyboard - для навигации
reply_kb = ReplyKeyboardMarkup(...)
await message.answer("Главное меню", reply_markup=reply_kb)

# Inline Keyboard - для действий
inline_kb = InlineKeyboardMarkup(...)
await message.answer("Выберите опцию", reply_markup=inline_kb)
```

## Best Practices

1. **Одна клавиатура** - не показывайте несколько reply keyboard одновременно
2. **Кнопка "Назад"** - всегда в подменю
3. **Тексты кнопок** - короткие и понятные
4. **Responsive** - используйте `resize_keyboard=True`
5. **Тестирование** - проверьте на разных устройствах
