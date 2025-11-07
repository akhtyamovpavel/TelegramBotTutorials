# 🐛 Отладка: Бот не показывает ответы

## Частые причины

### 1️⃣ WEBAPP_URL не установлен или неправильный

**Проверьте:**
```bash
echo $WEBAPP_URL
```

**Должно быть:**
```
https://ваш-домен.com/webapp/index.html
```

**НЕ должно быть:**
```
https://example.com/webapp.html  # ❌ По умолчанию, не работает
http://localhost:8000/index.html  # ❌ HTTP не работает
data:text/html,...                # ❌ data: URLs не работают
```

### 2️⃣ WebApp не размещен

**Проверьте в браузере:**
Откройте URL из `$WEBAPP_URL` в браузере - должна открыться форма.

**Если не открывается:**
- WebApp не размещен на сервере
- URL неправильный
- Сервер недоступен

### 3️⃣ WebApp не отправляет данные

**Откройте консоль браузера (F12) в WebApp:**

Добавьте временно в `webapp/index.html`:
```javascript
function sendData() {
    console.log("sendData called!");  // ← Добавьте это

    const data = {
        prompt: document.getElementById('prompt').value,
        model: document.getElementById('model').value,
        // ...
    };

    console.log("Data to send:", data);  // ← И это

    tg.sendData(JSON.stringify(data));

    console.log("Data sent!");  // ← И это
}
```

**Проверьте в консоли:**
- Видите "sendData called!" → функция вызывается
- Видите "Data to send:" → данные собираются
- Видите "Data sent!" → данные отправляются
- Нет сообщений → кнопка не работает

### 4️⃣ Бот не получает данные

**Проверьте логи бота:**

Должны видеть:
```
INFO:__main__:Получены данные из WebApp от 123456: {"prompt":"..."}
```

**Если не видите:**
Добавьте отладочное логирование в `bot.py`:

```python
@router.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    logger.info("⭐ handle_webapp_data ВЫЗВАН!")  # ← Добавьте
    logger.info(f"⭐ web_app_data: {message.web_app_data}")  # ← Добавьте

    try:
        webapp_data = message.web_app_data.data
        logger.info(f"⭐ Получены данные: {webapp_data}")  # ← Добавьте
        # ...
```

Перезапустите бота и проверьте логи.

### 5️⃣ Обработчик не зарегистрирован

**Проверьте, что в `bot.py` есть:**

```python
@router.message(F.web_app_data)  # ← Этот декоратор
async def handle_webapp_data(message: Message):
    # ...
```

**И что роутер зарегистрирован:**

```python
async def main():
    # ...
    dp.include_router(router)  # ← Эта строка
    # ...
```

## 🔍 Пошаговая диагностика

### Шаг 1: Проверьте переменные окружения

```bash
echo "BOT_TOKEN: $BOT_TOKEN"
echo "WEBAPP_URL: $WEBAPP_URL"
```

**Должно быть:**
```
BOT_TOKEN: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
WEBAPP_URL: https://your-domain.com/webapp/index.html
```

### Шаг 2: Проверьте WebApp в браузере

1. Откройте `$WEBAPP_URL` в браузере
2. Должна появиться форма
3. Откройте консоль браузера (F12)
4. Проверьте ошибки (красные сообщения)

**Типичные ошибки:**
```
Failed to load resource: net::ERR_NAME_NOT_RESOLVED
→ Домен не существует

Mixed Content: The page was loaded over HTTPS, but...
→ Используется HTTP вместо HTTPS

Uncaught ReferenceError: Telegram is not defined
→ Не подключен telegram-web-app.js
```

### Шаг 3: Проверьте WebApp API

В консоли браузера (на странице WebApp):
```javascript
console.log(window.Telegram);
// Должен показать объект WebApp

console.log(window.Telegram.WebApp);
// Должен показать методы (ready, expand, sendData, etc.)

console.log(window.Telegram.WebApp.initDataUnsafe.user);
// Должен показать данные пользователя
```

**Если undefined:**
- Не подключен `telegram-web-app.js`
- WebApp открыт не через Telegram (открыт напрямую в браузере)

### Шаг 4: Протестируйте отправку данных

В консоли браузера (в WebApp):
```javascript
// Тест 1: Отправить простую строку
window.Telegram.WebApp.sendData("test");

// Тест 2: Отправить JSON
window.Telegram.WebApp.sendData(JSON.stringify({test: "hello"}));
```

После каждого теста проверьте **логи бота**.

### Шаг 5: Проверьте логи бота

Запустите бота с подробным логированием:

```bash
# Добавьте в начало bot.py:
logging.basicConfig(
    level=logging.DEBUG,  # ← Измените на DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Должны видеть при получении данных:**
```
INFO:__main__:⭐ handle_webapp_data ВЫЗВАН!
INFO:__main__:⭐ web_app_data: <WebAppData object>
INFO:__main__:⭐ Получены данные: {"prompt":"..."}
INFO:__main__:Получены данные из WebApp от 123456: {"prompt":"..."}
```

## 🚀 Быстрый тест с Ngrok

Самый быстрый способ проверить что все работает:

```bash
# Терминал 1: Локальный сервер
cd examples/example_06_mini_apps/webapp
python -m http.server 8000

# Терминал 2: Ngrok туннель
ngrok http 8000
# Скопируйте HTTPS URL: https://abc123.ngrok-free.app

# Терминал 3: Бот
cd examples/example_06_mini_apps
export BOT_TOKEN="your_token_here"
export WEBAPP_URL="https://abc123.ngrok-free.app/index.html"
python aiogram/bot.py
```

**Проверьте логи:**
```
INFO:__main__:Бот запущен и готов к работе с WebApp!
INFO:__main__:WebApp URL: https://abc123.ngrok-free.app/index.html
```

**В Telegram:**
1. `/webapp`
2. Нажать кнопку
3. Заполнить форму
4. Нажать "Сгенерировать"

**Ожидаемый результат:**
```
✅ Данные успешно получены из WebApp!
...
```

## 🐛 Если всё равно не работает

### Добавьте максимальное логирование

**В `bot.py`:**

```python
@router.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    print("=" * 50)
    print("🔴 ПОЛУЧЕНО СООБЩЕНИЕ С web_app_data!")
    print(f"🔴 От пользователя: {message.from_user.id}")
    print(f"🔴 web_app_data: {message.web_app_data}")
    print(f"🔴 data: {message.web_app_data.data}")
    print("=" * 50)

    try:
        webapp_data = message.web_app_data.data
        logger.info(f"Получены данные: {webapp_data}")

        # Пробуем распарсить
        try:
            settings = json.loads(webapp_data)
            print(f"🔴 Распарсенные данные: {settings}")

            if 'prompt' in settings and 'model' in settings:
                print("🔴 Вызываем handle_generation_settings")
                await handle_generation_settings(message, settings)
            else:
                print("🔴 Простой текст, не настройки генерации")
                await message.answer(f"✅ Получены данные:\n\n{webapp_data}")

        except json.JSONDecodeError as e:
            print(f"🔴 Ошибка JSON: {e}")
            await message.answer(f"✅ Получено сообщение:\n\n{webapp_data}")

    except Exception as e:
        print(f"🔴 ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        await message.answer(f"❌ Ошибка: {str(e)}")
```

**В `webapp/index.html`:**

```javascript
function sendData() {
    console.log("=" + "=".repeat(50));
    console.log("🔵 sendData() вызвана!");

    const data = {
        prompt: document.getElementById('prompt').value,
        model: document.getElementById('model').value,
        num_images: parseInt(document.getElementById('num_images').value),
        steps: parseInt(document.getElementById('steps').value),
        cfg_scale: parseFloat(document.getElementById('cfg_scale').value),
        size: document.getElementById('size').value
    };

    console.log("🔵 Данные:", data);
    console.log("🔵 JSON:", JSON.stringify(data));

    if (!data.prompt.trim()) {
        console.log("🔵 Ошибка: промпт пустой!");
        tg.showAlert('Пожалуйста, введите промпт!');
        return;
    }

    console.log("🔵 Отправляем данные...");
    tg.sendData(JSON.stringify(data));
    console.log("🔵 Данные отправлены!");
    console.log("=" + "=".repeat(50));
}
```

### Проверьте update types

Возможно бот не получает web_app_data updates.

**В `main()`:**

```python
async def main():
    # ...

    # Убедитесь, что получаем ВСЕ типы обновлений
    await dp.start_polling(bot, allowed_updates=["message", "web_app_data"])

    # Или просто все:
    # await dp.start_polling(bot)
```

## 📋 Чеклист

- [ ] `BOT_TOKEN` установлен
- [ ] `WEBAPP_URL` установлен на правильный HTTPS URL
- [ ] WebApp открывается в браузере по `$WEBAPP_URL`
- [ ] В WebApp подключен `telegram-web-app.js`
- [ ] В консоли браузера нет ошибок
- [ ] `window.Telegram.WebApp` доступен в консоли
- [ ] Кнопка "Сгенерировать" вызывает `sendData()`
- [ ] В логах бота видно "Бот запущен и готов к работе"
- [ ] В логах бота видно правильный WEBAPP_URL
- [ ] Декоратор `@router.message(F.web_app_data)` присутствует
- [ ] Роутер зарегистрирован через `dp.include_router(router)`
- [ ] После нажатия "Сгенерировать" в логах появляется "Получены данные..."

## 💡 Совет

Если ничего не помогает:

1. **Используйте готовый пример:**
   ```bash
   # Используйте ngrok для быстрого теста
   ngrok http 8000
   ```

2. **Попробуйте python-telegram-bot версию:**
   Может быть проблема специфична для aiogram.

3. **Проверьте версии библиотек:**
   ```bash
   pip show aiogram
   # Должна быть aiogram 3.x
   ```

4. **Создайте минимальный тестовый бот:**
   Только `/start` и обработчик `web_app_data` для изоляции проблемы.
