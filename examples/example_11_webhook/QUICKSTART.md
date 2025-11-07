# 🚀 Быстрый старт: WebHook бот за 5 минут

Этот гайд поможет запустить webhook бота локально с помощью ngrok.

## Шаг 1: Установите зависимости

```bash
cd aiogram  # или python_telegram_bot
pip install -r requirements.txt
```

## Шаг 2: Установите ngrok

### macOS
```bash
brew install ngrok
```

### Linux
```bash
# Ubuntu/Debian
sudo snap install ngrok

# Или скачайте:
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

### Windows
Скачайте с https://ngrok.com/download

## Шаг 3: Получите бот токен

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен (например: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Шаг 4: Запустите бота

### Терминал 1: Запустите бота

```bash
cd aiogram  # или python_telegram_bot

export BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # ← Ваш токен
export WEBHOOK_HOST="https://temp.ngrok-free.app"        # ← Заменим на шаге 6
export WEBHOOK_PATH="/webhook"
export WEBAPP_PORT="8000"

python bot_webhook.py
```

Вы увидите:
```
🚀 Запуск WebHook бота...
📍 Webhook URL: https://temp.ngrok-free.app/webhook
❌ Ошибка установки webhook!  # ← Это нормально, URL еще не работает
```

**Остановите бота (Ctrl+C) - мы вернемся к нему**

### Терминал 2: Запустите ngrok

```bash
ngrok http 8000
```

Вы увидите:
```
Session Status                online
Account                       user@example.com
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000
```

**Скопируйте HTTPS URL** (например: `https://abc123.ngrok-free.app`)

## Шаг 5: Обновите WEBHOOK_HOST

### Вернитесь в Терминал 1:

```bash
export WEBHOOK_HOST="https://abc123.ngrok-free.app"  # ← Ваш ngrok URL

python bot_webhook.py
```

Теперь вы должны увидеть:
```
🚀 Запуск WebHook бота...
📍 Webhook URL: https://abc123.ngrok-free.app/webhook
✅ Webhook успешно установлен!
📊 Webhook info:
   URL: https://abc123.ngrok-free.app/webhook
   Pending updates: 0
🌐 Веб-сервер слушает на 0.0.0.0:8000
🎯 Telegram будет отправлять обновления на: https://abc123.ngrok-free.app/webhook
```

## Шаг 6: Протестируйте бота

Откройте Telegram и найдите вашего бота:

1. Отправьте `/start`
   ```
   👋 Бот работает через WebHook!

   Это значит что Telegram отправляет обновления напрямую на наш сервер...
   ```

2. Отправьте `/status`
   ```
   📊 Статус бота

   URL: https://abc123.ngrok-free.app/webhook
   Pending updates: 0
   Last error: Нет ошибок
   ```

3. Отправьте любое сообщение
   ```
   📨 Получено сообщение:

   Привет!

   💡 Это демонстрирует что WebHook работает!
   ```

## ✅ Готово!

Ваш бот работает через webhook!

**Что происходит:**
1. Вы отправляете сообщение в Telegram
2. Telegram мгновенно отправляет HTTPS POST на `https://abc123.ngrok-free.app/webhook`
3. Ngrok проксирует запрос на `http://localhost:8000/webhook`
4. Ваш бот обрабатывает обновление
5. Бот отправляет ответ

## 🔍 Проверка webhook

### Проверьте webhook info через API:

```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

Должно показать:
```json
{
  "ok": true,
  "result": {
    "url": "https://abc123.ngrok-free.app/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40
  }
}
```

### Посмотрите логи ngrok:

В терминале с ngrok вы увидите входящие запросы от Telegram:
```
POST /webhook  200 OK
POST /webhook  200 OK
```

## 🐛 Проблемы?

### Бот не получает сообщения

```bash
# Проверьте что бот запущен
# Терминал 1 должен показывать: "Веб-сервер слушает на 0.0.0.0:8000"

# Проверьте что ngrok работает
# Терминал 2 должен показывать: "Session Status: online"

# Проверьте webhook info
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### SSL ошибки

Ngrok **автоматически** предоставляет валидный SSL сертификат. Если есть ошибки SSL - проверьте что используете **HTTPS** URL из ngrok (не HTTP).

### Ошибка "Wrong response from the webhook"

Убедитесь что бот отвечает `200 OK` в течение 60 секунд. Проверьте логи бота.

## 🎓 Следующие шаги

После того как webhook заработал локально:

1. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Разверните на production сервере
2. **[COMPARISON.md](./COMPARISON.md)** - Изучите различия между polling и webhook
3. **[README.md](./README.md)** - Подробная документация

## 💡 Совет

Для разработки используйте **polling** (проще), а webhook оставьте для **production**. Чтобы переключаться между ними:

```python
import os

if os.getenv("ENVIRONMENT") == "production":
    # WebHook
    await setup_webhook()
else:
    # Polling (development)
    await dp.start_polling(bot)
```

---

**Готово!** Теперь вы знаете как работать с webhook! 🎉
