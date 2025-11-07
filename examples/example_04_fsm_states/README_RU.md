# Example 4: FSM (Машина состояний)

## Описание

Бот с многошаговым диалогом (регистрация пользователя):
1. Запрашивает имя
2. Запрашивает возраст (с валидацией)
3. Запрашивает город
4. Выводит итоговую информацию

## Что нового по сравнению с Example 2

### ➕ Добавлено:
1. **States (Состояния)** - определение шагов диалога
2. **FSMContext / context.user_data** - хранение данных между сообщениями
3. **Переходы между состояниями** - управление flow диалога
4. **Валидация данных** - проверка корректности ввода
5. **Команда /cancel** - прерывание диалога

### Что изменилось:
- Появилась концепция "состояния" бота для каждого пользователя
- Данные сохраняются между сообщениями
- Обработчики теперь зависят от текущего состояния
- Добавлена логика валидации и обработки ошибок

## Ключевые концепции

### FSM (Finite State Machine)
Машина состояний позволяет боту "помнить", на каком этапе диалога находится пользователь.

**Пример flow:**
```
/start → NAME → AGE → CITY → END
```

### Состояния (aiogram)
```python
class RegistrationForm(StatesGroup):
    name = State()   # Ожидаем имя
    age = State()    # Ожидаем возраст
    city = State()   # Ожидаем город
```

### Состояния (python-telegram-bot)
```python
NAME, AGE, CITY = range(3)  # Константы для состояний
```

### Хранение данных

**aiogram:**
```python
# Сохранить
await state.update_data(name="Иван")

# Получить все данные
data = await state.get_data()

# Очистить состояние
await state.clear()
```

**python-telegram-bot:**
```python
# Сохранить
context.user_data['name'] = "Иван"

# Получить
name = context.user_data['name']

# Завершить диалог
return ConversationHandler.END
```

## Установка

```bash
# Установка зависимостей
pip install aiogram
# или
pip install python-telegram-bot
```

## Запуск

```bash
export BOT_TOKEN="your_bot_token_here"

# aiogram
python examples/example_03_fsm_states/aiogram/bot.py

# python-telegram-bot
python examples/example_03_fsm_states/python_telegram_bot/bot.py
```

## Сравнение подходов

| Аспект | aiogram | python-telegram-bot |
|--------|---------|---------------------|
| **Определение** | `StatesGroup` класс | Константы `NAME, AGE = range(2)` |
| **Хранилище** | `MemoryStorage` (или Redis/MongoDB) | `context.user_data` |
| **Переход** | `await state.set_state(NextState)` | `return NEXT_STATE` |
| **Данные** | `state.update_data()` / `get_data()` | `context.user_data[key]` |
| **Завершение** | `await state.clear()` | `return ConversationHandler.END` |
| **Структура** | Декларативная (роутеры) | Императивная (ConversationHandler) |

## Важные моменты

### Валидация данных
Всегда проверяйте пользовательский ввод:
```python
if not text.isdigit():
    await message.answer("Введите число!")
    return AGE  # Остаемся в том же состоянии
```

### Отмена диалога
Предоставьте пользователям возможность выйти из диалога:
```python
@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.")
```

### Хранилище состояний (aiogram)
- **MemoryStorage** - в памяти (для разработки)
- **RedisStorage** - в Redis (для production)
- **MongoStorage** - в MongoDB (для production)

При перезапуске бота с MemoryStorage все состояния теряются!
