# Решение проблемы дублирования - python-telegram-bot

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
   ├─ Update 1 (media_group_id="12345")
   │     ↓
   │  Обработчик handle_album_photo()
   │     ↓
   │  asyncio.sleep(0.5)
   │     ↓
   │  Проверка: завершен ли альбом?
   │     ↓
   │  ✅ "Получен альбом!" (Ответ 1)
   │
   └─ Update 2 (media_group_id="12345")
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
   ├─ Update 1 (media_group_id="12345")
   │     ↓
   │  [AlbumCollector]
   │     ↓
   │  Добавляет в буфер: [Update 1]
   │     ↓
   │  Запускает таймер: 0.3 сек
   │
   └─ Update 2 (media_group_id="12345")
         ↓
      [AlbumCollector]
         ↓
      Добавляет в буфер: [Update 1, Update 2]
         ↓
      Перезапускает таймер: 0.3 сек
         ↓
      (таймер истекает)
         ↓
      Вызывает обработчик ОДИН РАЗ:
      handle_album(Update 2, context)
      (context содержит: album_updates=[Update 1, Update 2])
         ↓
      ✅ "Получен альбом!" (Только один ответ!) ✅
```

## Код middleware

```python
# album_middleware.py
class AlbumCollector:
    def wrap_handler(self, handler):
        """Оборачивает обработчик для группировки альбомов"""
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
            message = update.effective_message

            # Если не альбом - пропускаем
            if not message or not message.media_group_id:
                return await handler(update, context)

            media_group_id = message.media_group_id

            # Добавляем в буфер
            if media_group_id not in self.album_data:
                self.album_data[media_group_id] = []
            self.album_data[media_group_id].append(update)

            # Отменяем старый таймер
            if media_group_id in self.tasks:
                self.tasks[media_group_id].cancel()

            # Создаем новый таймер
            self.tasks[media_group_id] = asyncio.create_task(
                self._process_album(media_group_id, handler, context)
            )

        return wrapped

    async def _process_album(self, media_group_id, handler, context):
        await asyncio.sleep(self.latency)  # Ждем 0.3 сек

        # Получаем все updates альбома
        updates = self.album_data.pop(media_group_id, [])

        # ⭐ Сохраняем в контекст
        context.user_data['album_updates'] = updates

        # ⭐ Вызываем обработчик ОДИН РАЗ
        await handler(updates[-1], context)

        context.user_data.pop('album_updates', None)


def get_album_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить все updates альбома в обработчике"""
    return context.user_data.get('album_updates', None)
```

## Использование в боте

```python
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from album_middleware import AlbumCollector, get_album_messages

# ⭐ Создаем экземпляр коллектора
album_collector = AlbumCollector(latency=0.3)

async def handle_album(update: Update, context):
    """
    ⭐ Этот обработчик вызывается ОДИН РАЗ для всего альбома
    """
    # Получаем все updates альбома
    album_updates = get_album_messages(update, context)

    if album_updates is None:
        album_updates = [update]

    photos = [upd.effective_message.photo[-1] for upd in album_updates
              if upd.effective_message.photo]

    await update.effective_message.reply_text(
        f"📸 Получен альбом!\n\n"
        f"Количество фотографий: {len(photos)}\n"
        f"Media Group ID: {update.effective_message.media_group_id}\n\n"
        f"Размеры фотографий:\n" +
        "\n".join([f"  • {p.width}x{p.height} px" for p in photos]) +
        f"\n\n✅ Обработано middleware - без дублирования!"
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

## Разница с aiogram

В python-telegram-bot middleware реализован через **обертку (wrapper)** обработчика:

```python
# aiogram - встроенный механизм middleware
router.message.middleware(AlbumMiddleware())

# python-telegram-bot - обертка обработчика
wrapped = album_collector.wrap_handler(handle_album)
```

Данные передаются через **контекст**:

```python
# Middleware сохраняет в контекст
context.user_data['album_updates'] = updates

# Обработчик извлекает из контекста
album_updates = get_album_messages(update, context)
```

## Параметры

- `latency` - время ожидания (сек) для сбора всех фото альбома
  - Слишком мало (0.1) - может не собрать все фото
  - Слишком много (1.0) - медленная реакция бота
  - **Оптимально: 0.3-0.5 сек**

## Файлы

- `album_middleware.py` - реализация AlbumCollector
- `bot_with_middleware.py` - бот с использованием middleware ✅
- `bot.py` - оригинальный бот (для сравнения) ❌
