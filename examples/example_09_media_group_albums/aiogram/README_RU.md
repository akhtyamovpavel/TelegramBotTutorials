# Решение проблемы дублирования - aiogram

## Как использовать

```bash
export BOT_TOKEN="your_token"
python bot_with_middleware.py
```

## Визуальное сравнение

### ❌ БЕЗ middleware (bot.py):

```
Пользователь отправляет: 📷📷 (альбом из 2 фото)
   ↓
Telegram → Bot:
   ├─ Message 1 (media_group_id="12345")
   │     ↓
   │  Обработчик handle_album_photo()
   │     ↓
   │  asyncio.sleep(0.5)
   │     ↓
   │  Проверка: завершен ли альбом?
   │     ↓
   │  ✅ "Получен альбом!" (Ответ 1)
   │
   └─ Message 2 (media_group_id="12345")
         ↓
      Обработчик handle_album_photo()
         ↓
      asyncio.sleep(0.5)
         ↓
      Проверка: завершен ли альбом?
         ↓
      ✅ "Получен альбом!" (Ответ 2) ❌ ДУБЛИКАТ!
```

### ✅ С middleware (bot_with_middleware.py):

```
Пользователь отправляет: 📷📷 (альбом из 2 фото)
   ↓
Telegram → Bot:
   ├─ Message 1 (media_group_id="12345")
   │     ↓
   │  [AlbumMiddleware]
   │     ↓
   │  Добавляет в буфер: [Message 1]
   │     ↓
   │  Запускает таймер: 0.3 сек
   │
   └─ Message 2 (media_group_id="12345")
         ↓
      [AlbumMiddleware]
         ↓
      Добавляет в буфер: [Message 1, Message 2]
         ↓
      Перезапускает таймер: 0.3 сек
         ↓
      (таймер истекает)
         ↓
      Вызывает обработчик ОДИН РАЗ:
      handle_album(message, album=[Message 1, Message 2])
         ↓
      ✅ "Получен альбом!" (Только один ответ!) ✅
```

## Код middleware

```python
# album_middleware.py
class AlbumMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict):
        # Если не альбом - пропускаем
        if not event.media_group_id:
            return await handler(event, data)

        media_group_id = event.media_group_id

        # Добавляем в буфер
        if media_group_id not in self.album_data:
            self.album_data[media_group_id] = []
        self.album_data[media_group_id].append(event)

        # Отменяем старый таймер
        if media_group_id in self.tasks:
            self.tasks[media_group_id].cancel()

        # Создаем новый таймер
        self.tasks[media_group_id] = asyncio.create_task(
            self._process_album(media_group_id, handler, data)
        )

        # ⭐ ВАЖНО: Возвращаем None, чтобы остановить обработку
        return None

    async def _process_album(self, media_group_id, handler, data):
        await asyncio.sleep(self.latency)  # Ждем 0.3 сек

        # Получаем все сообщения альбома
        messages = self.album_data.pop(media_group_id, [])

        # Добавляем в data
        data['album'] = messages

        # ⭐ Вызываем обработчик ОДИН РАЗ
        await handler(messages[-1], data)
```

## Использование в боте

```python
from aiogram import Router
from album_middleware import AlbumMiddleware

router = Router()

# ⭐ Регистрируем middleware
router.message.middleware(AlbumMiddleware(latency=0.3))

@router.message(F.media_group_id, F.photo)
async def handle_album(message: Message, album: List[Message] = None):
    """
    ⭐ Этот обработчик вызывается ОДИН РАЗ для всего альбома
    """
    if album is None:
        album = [message]

    photos = [msg.photo[-1] for msg in album if msg.photo]

    await message.answer(
        f"📸 Получен альбом!\n\n"
        f"Количество фотографий: {len(photos)}\n"
        f"Media Group ID: {message.media_group_id}\n\n"
        f"Размеры фотографий:\n" +
        "\n".join([f"  • {p.width}x{p.height} px" for p in photos]) +
        f"\n\n✅ Обработано middleware - без дублирования!"
    )
```

## Параметры

- `latency` - время ожидания (сек) для сбора всех фото альбома
  - Слишком мало (0.1) - может не собрать все фото
  - Слишком много (1.0) - медленная реакция бота
  - **Оптимально: 0.3-0.5 сек**

## Файлы

- `album_middleware.py` - реализация middleware
- `bot_with_middleware.py` - бот с использованием middleware ✅
- `bot.py` - оригинальный бот (для сравнения) ❌
