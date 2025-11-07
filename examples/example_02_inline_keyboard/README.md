# Example 2: Inline Keyboard (Кнопки)

## Описание

Бот с интерактивными кнопками:
- Показывает inline-клавиатуру с опциями
- Обрабатывает нажатия на кнопки
- Редактирует сообщение после выбора

## Что нового по сравнению с Example 1

### ➕ Добавлено:
1. **InlineKeyboardButton** - создание кнопок
2. **InlineKeyboardMarkup** - компоновка клавиатуры
3. **CallbackQuery** - обработка нажатий на кнопки
4. **callback.answer()** - обязательный ответ на callback
5. **edit_message_text()** - редактирование сообщения

### Что изменилось:
- Добавлен обработчик `CallbackQueryHandler` / `@router.callback_query()`
- Используется `callback_data` для идентификации нажатий

## Установка

```bash
# Установка зависимостей (если еще не установлены)
pip install aiogram
# или
pip install python-telegram-bot
```

## Запуск

```bash
export BOT_TOKEN="your_bot_token_here"

# aiogram
python examples/example_02_inline_keyboard/aiogram/bot.py

# python-telegram-bot
python examples/example_02_inline_keyboard/python_telegram_bot/bot.py
```

## Ключевые концепции

### Inline клавиатура
- Кнопки появляются **под сообщением**
- Каждая кнопка имеет `callback_data` (идентификатор)
- При нажатии отправляется callback query

### CallbackQuery
- Специальный тип обновления
- Содержит `data` (то, что было в `callback_data`)
- Требует обязательного ответа через `answer()`

### Различия между библиотеками

**aiogram:**
```python
keyboard = InlineKeyboardMarkup(inline_keyboard=[[...]])
@router.callback_query(F.data.startswith("option_"))
```

**python-telegram-bot:**
```python
keyboard = InlineKeyboardMarkup([[...]])
CallbackQueryHandler(handle_option)
```
