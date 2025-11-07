# Решение проблемы дублирования при обработке Media Group

## 🔴 Проблема

Когда пользователь отправляет альбом (несколько фото одновременно), Telegram отправляет **каждое фото как отдельное сообщение**, но все они имеют одинаковый `media_group_id`.

**Результат:** Если обработчик реагирует на каждое фото, бот отправит ответ несколько раз!

### Пример проблемы:

```
Пользователь отправляет: 📷📷 (2 фото в альбоме)
   ↓
Telegram отправляет боту:
   1. Message с photo[0] и media_group_id="12345"
   2. Message с photo[1] и media_group_id="12345"
   ↓
Бот без middleware:
   ✅ "Получен альбом!" (после 1-го фото)
   ✅ "Получен альбом!" (после 2-го фото) ❌ ДУБЛИКАТ!
```

### Текущее решение с `asyncio.sleep()` (ненадежное):

```python
@router.message(F.media_group_id, F.photo)
async def handle_album_photo(message: Message):
    media_group_id = message.media_group_id

    if media_group_id not in user_albums:
        user_albums[media_group_id] = []

    user_albums[media_group_id].append(message.photo[-1])

    # ❌ Ждем 0.5 сек и надеемся, что все фото пришли
    await asyncio.sleep(0.5)

    current_count = len(user_albums[media_group_id])
    await asyncio.sleep(0.3)

    # ❌ Если количество не изменилось, считаем альбом завершенным
    if current_count == len(user_albums[media_group_id]):
        await message.answer("Получен альбом!")  # Может сработать 2+ раза!
        del user_albums[media_group_id]
```

**Проблемы:**
- Каждое фото проходит через обработчик
- Проверка через `sleep()` ненадежна
- При медленном интернете может быть дублирование
- При быстром интернете может обработать не все фото

---

## ✅ Решение: Middleware

Middleware **перехватывает** сообщения **до** обработчика и группирует их.

### Принцип работы:

```
Telegram отправляет:
   Message 1 (media_group_id="12345")
         ↓
   [Middleware] → Добавляет в буфер, запускает таймер
         ↓
   Message 2 (media_group_id="12345")
         ↓
   [Middleware] → Добавляет в буфер, перезапускает таймер
         ↓
   (таймер истекает через 0.3 сек)
         ↓
   [Middleware] → Вызывает обработчик ОДИН РАЗ со всеми сообщениями
         ↓
   Обработчик получает: [Message 1, Message 2]
         ↓
   Бот отправляет: "Получен альбом!" ✅ ОДИН РАЗ!
```

---

## 📝 Реализация для aiogram

### 1. Создаем `album_middleware.py`:

```python
import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)


class AlbumMiddleware(BaseMiddleware):
    """Middleware для группировки Media Group сообщений"""

    def __init__(self, latency: float = 0.3):
        """
        Args:
            latency: Время ожидания (сек) для сбора всех сообщений альбома
        """
        self.latency = latency
        self.album_data: Dict[str, List[Message]] = {}
        self.tasks: Dict[str, asyncio.Task] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Если сообщение не содержит media_group_id, обрабатываем как обычно
        if not event.media_group_id:
            return await handler(event, data)

        media_group_id = event.media_group_id

        # Добавляем сообщение в буфер
        if media_group_id not in self.album_data:
            self.album_data[media_group_id] = []
        self.album_data[media_group_id].append(event)

        # Отменяем предыдущую задачу ожидания
        if media_group_id in self.tasks:
            self.tasks[media_group_id].cancel()

        # Создаем новую задачу ожидания
        self.tasks[media_group_id] = asyncio.create_task(
            self._process_album(media_group_id, handler, data)
        )

        # ⭐ Возвращаем None, чтобы предотвратить дальнейшую обработку
        return None

    async def _process_album(
        self,
        media_group_id: str,
        handler: Callable,
        data: Dict[str, Any]
    ):
        try:
            # Ждем, пока все сообщения альбома будут получены
            await asyncio.sleep(self.latency)

            # Получаем все сообщения альбома
            messages = self.album_data.pop(media_group_id, [])

            if not messages:
                return

            logger.info(f"Обработка альбома {media_group_id} из {len(messages)} сообщений")

            # Добавляем список сообщений в data
            data['album'] = messages

            # ⭐ Вызываем обработчик ТОЛЬКО ОДИН РАЗ
            await handler(messages[-1], data)

        except asyncio.CancelledError:
            pass
        finally:
            self.tasks.pop(media_group_id, None)
```

### 2. Используем в боте:

```python
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from album_middleware import AlbumMiddleware

router = Router()

@router.message(F.media_group_id, F.photo)
async def handle_album(message: Message, album: List[Message] = None):
    """
    ⭐ Вызывается ОДИН РАЗ для всего альбома!
    """
    if album is None:
        album = [message]

    photos = [msg.photo[-1] for msg in album if msg.photo]

    await message.answer(
        f"📸 Получен альбом!\n"
        f"Количество фотографий: {len(photos)}\n"
        f"✅ Обработано middleware - без дублирования!"
    )

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # ⭐ РЕГИСТРИРУЕМ MIDDLEWARE
    router.message.middleware(AlbumMiddleware(latency=0.3))

    dp.include_router(router)

    await dp.start_polling(bot)
```

---

## 📝 Реализация для python-telegram-bot

### 1. Создаем `album_middleware.py`:

```python
import asyncio
import logging
from typing import Dict, List, Optional

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class AlbumCollector:
    """Класс для сбора и группировки альбомов"""

    def __init__(self, latency: float = 0.3):
        self.latency = latency
        self.album_data: Dict[str, List[Update]] = {}
        self.tasks: Dict[str, asyncio.Task] = {}

    def wrap_handler(self, handler):
        """Оборачивает обработчик для группировки альбомов"""
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
            message = update.effective_message

            # Если не альбом, обрабатываем как обычно
            if not message or not message.media_group_id:
                return await handler(update, context)

            media_group_id = message.media_group_id

            # Добавляем в буфер
            if media_group_id not in self.album_data:
                self.album_data[media_group_id] = []
            self.album_data[media_group_id].append(update)

            # Отменяем предыдущую задачу
            if media_group_id in self.tasks:
                self.tasks[media_group_id].cancel()

            # Создаем новую задачу ожидания
            self.tasks[media_group_id] = asyncio.create_task(
                self._process_album(media_group_id, handler, context)
            )

        return wrapped

    async def _process_album(self, media_group_id: str, handler, context):
        try:
            await asyncio.sleep(self.latency)

            updates = self.album_data.pop(media_group_id, [])
            if not updates:
                return

            # ⭐ Сохраняем в контекст
            context.user_data['album_updates'] = updates

            # ⭐ Вызываем обработчик ОДИН РАЗ
            await handler(updates[-1], context)

            context.user_data.pop('album_updates', None)

        except asyncio.CancelledError:
            pass
        finally:
            self.tasks.pop(media_group_id, None)


def get_album_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[List[Update]]:
    """Вспомогательная функция для получения всех сообщений альбома"""
    return context.user_data.get('album_updates', None)
```

### 2. Используем в боте:

```python
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from album_middleware import AlbumCollector, get_album_messages

# ⭐ Создаем экземпляр коллектора
album_collector = AlbumCollector(latency=0.3)

async def handle_album(update: Update, context):
    """⭐ Вызывается ОДИН РАЗ для всего альбома!"""

    # Получаем все updates альбома
    album_updates = get_album_messages(update, context)

    if album_updates is None:
        album_updates = [update]

    photos = [upd.effective_message.photo[-1] for upd in album_updates
              if upd.effective_message.photo]

    await update.effective_message.reply_text(
        f"📸 Получен альбом!\n"
        f"Количество фотографий: {len(photos)}\n"
        f"✅ Обработано middleware - без дублирования!"
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # ⭐ ОБОРАЧИВАЕМ обработчик в AlbumCollector
    wrapped_handler = album_collector.wrap_handler(handle_album)

    application.add_handler(
        MessageHandler(filters.PHOTO & ~filters.FORWARDED, wrapped_handler)
    )

    application.run_polling()
```

---

## 🔑 Ключевые моменты

### 1. **Таймер с отменой**
```python
# Отменяем предыдущую задачу
if media_group_id in self.tasks:
    self.tasks[media_group_id].cancel()

# Создаем новую
self.tasks[media_group_id] = asyncio.create_task(...)
```

Каждое новое фото **перезапускает** таймер. Обработка начнется только когда перестанут приходить новые фото.

### 2. **Время ожидания (latency)**
```python
AlbumMiddleware(latency=0.3)  # 300 мс
```

- Слишком маленькое (0.1 сек) → может обработать не все фото
- Слишком большое (1.0 сек) → медленная реакция бота
- **Оптимально: 0.3-0.5 сек**

### 3. **Предотвращение дальнейшей обработки**

**aiogram:**
```python
return None  # Останавливает цепочку обработчиков
```

**python-telegram-bot:**
```python
# Обертка не вызывает оригинальный handler сразу
# Вызов происходит в _process_album через заданное время
```

---

## 🚀 Запуск

### aiogram:
```bash
cd examples/example_09_media_group_albums/aiogram
export BOT_TOKEN="your_token"
python bot_with_middleware.py
```

### python-telegram-bot:
```bash
cd examples/example_09_media_group_albums/python_telegram_bot
export BOT_TOKEN="your_token"
python bot_with_middleware.py
```

---

## 📊 Сравнение подходов

| Подход | Надежность | Сложность | Производительность |
|--------|------------|-----------|-------------------|
| **asyncio.sleep() проверка** | ⚠️ Низкая | 🟢 Простая | 🟡 Средняя |
| **Middleware** | ✅ Высокая | 🟡 Средняя | ✅ Отличная |
| **Очередь событий** | ✅ Высокая | 🔴 Сложная | ✅ Отличная |

---

## 💡 Когда использовать Middleware?

✅ **Используйте middleware когда:**
- Нужно группировать альбомы без дублирования
- Важна надежность обработки
- Работаете с production ботом

❌ **Можно обойтись без middleware когда:**
- Учебный проект / прототип
- Альбомы встречаются редко
- Дублирование не критично

---

## 🎓 Дополнительные материалы

- [aiogram Middleware документация](https://docs.aiogram.dev/en/dev-3.x/dispatcher/middlewares.html)
- [python-telegram-bot Context](https://docs.python-telegram-bot.org/en/stable/telegram.ext.contextypes.html)
- [Telegram Bot API: Media Groups](https://core.telegram.org/bots/api#sendmediagroup)
