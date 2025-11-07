# 🚀 Быстрый старт: Размещение на GitHub Pages

## За 5 минут

### 1️⃣ Создайте репозиторий

```bash
# В папке example_06_mini_apps выполните:
git init
git add webapp/
git commit -m "Add Telegram WebApp"
```

### 2️⃣ Загрузите на GitHub

1. Зайдите на [github.com](https://github.com)
2. Создайте новый **публичный** репозиторий:
   - Name: `telegram-ai-webapp`
   - Public ✅
   - Без README (уже есть)

3. Загрузите код:
```bash
git remote add origin https://github.com/YOUR_USERNAME/telegram-ai-webapp.git
git branch -M main
git push -u origin main
```

### 3️⃣ Включите GitHub Pages

1. Зайдите в Settings репозитория
2. Слева выберите **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main** / root
5. Нажмите **Save**

⏳ Подождите 1-2 минуты пока GitHub развернет ваш сайт.

### 4️⃣ Получите URL

Ваш WebApp будет доступен по адресу:
```
https://YOUR_USERNAME.github.io/telegram-ai-webapp/webapp/index.html
```

Замените `YOUR_USERNAME` на ваш username на GitHub.

### 5️⃣ Запустите бота

```bash
# В папке examples/example_06_mini_apps
export BOT_TOKEN="your_bot_token_here"
export WEBAPP_URL="https://YOUR_USERNAME.github.io/telegram-ai-webapp/webapp/index.html"

# Для aiogram:
python aiogram/bot.py

# Для python-telegram-bot:
python python_telegram_bot/bot.py
```

### 6️⃣ Тестируйте!

1. Откройте бота в Telegram
2. Отправьте `/start`
3. Нажмите `/webapp`
4. Нажмите кнопку "⚙️ Открыть настройки генерации"
5. WebApp откроется внутри Telegram! ✅

---

## 🔧 Альтернатива: Быстрое тестирование с Ngrok

Если не хотите создавать репозиторий:

```bash
# 1. Установите ngrok
brew install ngrok  # macOS
# или скачайте с ngrok.com

# 2. Запустите локальный сервер
cd webapp
python -m http.server 8000

# 3. В другом терминале создайте туннель
ngrok http 8000

# 4. Скопируйте HTTPS URL (например: https://abc123.ngrok.io)

# 5. Запустите бота
export BOT_TOKEN="your_token"
export WEBAPP_URL="https://abc123.ngrok.io/index.html"
python ../aiogram/bot.py
```

⚠️ **Внимание:** URL от Ngrok меняется при каждом перезапуске!

---

## ❌ Что НЕ работает

```python
# ❌ НЕ РАБОТАЕТ: data: URL
simple_webapp_url = "data:text/html,<!DOCTYPE html>..."

# ❌ НЕ РАБОТАЕТ: HTTP без S
WEBAPP_URL = "http://example.com/webapp.html"

# ❌ НЕ РАБОТАЕТ: localhost
WEBAPP_URL = "http://localhost:8000/index.html"
```

## ✅ Что работает

```python
# ✅ РАБОТАЕТ: GitHub Pages
WEBAPP_URL = "https://username.github.io/repo/webapp/index.html"

# ✅ РАБОТАЕТ: Vercel
WEBAPP_URL = "https://project.vercel.app/index.html"

# ✅ РАБОТАЕТ: Netlify
WEBAPP_URL = "https://random-name.netlify.app/index.html"

# ✅ РАБОТАЕТ: Ngrok (для тестирования)
WEBAPP_URL = "https://abc123.ngrok.io/index.html"

# ✅ РАБОТАЕТ: Свой домен с SSL
WEBAPP_URL = "https://your-domain.com/webapp/index.html"
```

---

## 📖 Дополнительные материалы

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - полная инструкция по всем вариантам размещения
- **[README.md](./README.md)** - основная документация по Mini Apps
- [GitHub Pages документация](https://pages.github.com/)
- [Telegram WebApp API](https://core.telegram.org/bots/webapps)

---

## 💡 Совет

Для учебных проектов и курсовых работ рекомендуем **GitHub Pages**:
- ✅ Бесплатно
- ✅ Постоянный URL
- ✅ Можно показать преподавателю
- ✅ Автоматический HTTPS
- ✅ Портфолио на GitHub
