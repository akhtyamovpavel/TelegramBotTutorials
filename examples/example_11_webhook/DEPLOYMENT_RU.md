# 🚀 Подробное руководство по развертыванию WebHook бота

Это руководство покрывает различные способы развертывания Telegram бота с webhook.

## 📋 Содержание

1. [Локальное тестирование с Ngrok](#1-локальное-тестирование-с-ngrok)
2. [VPS (DigitalOcean, Hetzner, Linode)](#2-vps-digitalocean-hetzner-linode)
3. [Docker Deployment](#3-docker-deployment)
4. [Heroku](#4-heroku)
5. [Railway](#5-railway)
6. [Render.com](#6-rendercom)

---

## 1. Локальное тестирование с Ngrok

**Используйте для**: Разработки и быстрого тестирования

### Шаг 1: Установите Ngrok

```bash
# macOS
brew install ngrok

# Linux
snap install ngrok

# Или скачайте с https://ngrok.com/download
```

### Шаг 2: Запустите бота

```bash
cd aiogram  # или python_telegram_bot
pip install -r requirements.txt

export BOT_TOKEN="your_token_here"
export WEBHOOK_HOST="https://will-be-set-by-ngrok.ngrok-free.app"
export WEBHOOK_PATH="/webhook"
export WEBAPP_PORT="8000"

python bot_webhook.py
```

### Шаг 3: Запустите Ngrok (в другом терминале)

```bash
ngrok http 8000
```

Вы увидите:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

### Шаг 4: Обновите WEBHOOK_HOST

```bash
# Остановите бота (Ctrl+C)

# Обновите переменную:
export WEBHOOK_HOST="https://abc123.ngrok-free.app"

# Перезапустите:
python bot_webhook.py
```

### ✅ Проверка

```bash
# Проверьте webhook info
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

**Плюсы:**
- ✅ Быстрое тестирование
- ✅ Не нужен VPS
- ✅ Автоматический HTTPS

**Минусы:**
- ❌ URL меняется при каждом запуске ngrok
- ❌ Не для production
- ❌ Бесплатная версия имеет ограничения

---

## 2. VPS (DigitalOcean, Hetzner, Linode)

**Используйте для**: Production deployment

### Требования

- Ubuntu 20.04/22.04 LTS
- Публичный IP адрес
- Доменное имя (например, `bot.example.com`)

### Шаг 1: Подключитесь к серверу

```bash
ssh root@your-server-ip
```

### Шаг 2: Обновите систему

```bash
apt update && apt upgrade -y
```

### Шаг 3: Установите Python и зависимости

```bash
apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx -y
```

### Шаг 4: Создайте пользователя для бота

```bash
adduser botuser
usermod -aG sudo botuser
su - botuser
```

### Шаг 5: Клонируйте репозиторий

```bash
cd ~
git clone <your-repo-url>
cd example_11_webhook/aiogram  # или python_telegram_bot
```

### Шаг 6: Создайте виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 7: Настройте переменные окружения

```bash
cat > ~/bot.env <<EOF
BOT_TOKEN=your_token_here
WEBHOOK_HOST=https://bot.example.com
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=your_random_secret_string_here
WEBAPP_HOST=127.0.0.1
WEBAPP_PORT=8000
EOF
```

### Шаг 8: Настройте Nginx

```bash
sudo nano /etc/nginx/sites-available/bot
```

Вставьте:

```nginx
server {
    listen 80;
    server_name bot.example.com;

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name bot.example.com;

    # SSL сертификаты (будут созданы certbot)
    ssl_certificate /etc/letsencrypt/live/bot.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.example.com/privkey.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Логи
    access_log /var/log/nginx/bot_access.log;
    error_log /var/log/nginx/bot_error.log;

    # Webhook endpoint
    location /webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Ограничить доступ только с IP Telegram
        allow 149.154.160.0/20;
        allow 91.108.4.0/22;
        deny all;
    }

    # Healthcheck endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        access_log off;
    }

    # Блокировать все остальные запросы
    location / {
        return 404;
    }
}
```

Активируйте конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/
sudo nginx -t
```

### Шаг 9: Получите SSL сертификат

```bash
# Временно закомментируйте SSL строки в nginx конфиге
sudo nano /etc/nginx/sites-available/bot
# Закомментируйте строки ssl_certificate*

sudo systemctl reload nginx

# Получите сертификат
sudo certbot --nginx -d bot.example.com

# Раскомментируйте SSL строки обратно
sudo nano /etc/nginx/sites-available/bot

# Перезагрузите nginx
sudo systemctl reload nginx
```

### Шаг 10: Создайте systemd service

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Вставьте:

```ini
[Unit]
Description=Telegram Bot WebHook
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/example_11_webhook/aiogram
EnvironmentFile=/home/botuser/bot.env
ExecStart=/home/botuser/example_11_webhook/aiogram/venv/bin/python bot_webhook.py
Restart=on-failure
RestartSec=10

# Логирование
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

[Install]
WantedBy=multi-user.target
```

### Шаг 11: Запустите бота

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### ✅ Проверка

```bash
# Проверьте статус
sudo systemctl status telegram-bot

# Посмотрите логи
sudo journalctl -u telegram-bot -f

# Проверьте webhook
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo

# Проверьте healthcheck
curl https://bot.example.com/health
```

### 🔧 Управление

```bash
# Остановить
sudo systemctl stop telegram-bot

# Перезапустить
sudo systemctl restart telegram-bot

# Посмотреть логи
sudo journalctl -u telegram-bot -f --lines 100
```

---

## 3. Docker Deployment

**Используйте для**: Изолированного development и production deployment

### Шаг 1: Dockerfile

Уже создан в `docker/Dockerfile`

### Шаг 2: Docker Compose

Уже создан в `docker/docker-compose.yml`

### Шаг 3: Запустите

```bash
cd docker

# Создайте .env файл
cat > .env <<EOF
BOT_TOKEN=your_token_here
WEBHOOK_HOST=https://bot.example.com
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=your_secret_here
EOF

# Запустите
docker-compose up -d

# Посмотрите логи
docker-compose logs -f bot
```

### ✅ Проверка

```bash
# Статус контейнеров
docker-compose ps

# Логи
docker-compose logs bot

# Остановить
docker-compose down
```

---

## 4. Heroku

**Используйте для**: Быстрого бесплатного деплоя (с ограничениями)

### Шаг 1: Установите Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### Шаг 2: Войдите в Heroku

```bash
heroku login
```

### Шаг 3: Создайте приложение

```bash
cd example_11_webhook/aiogram  # или python_telegram_bot
heroku create your-bot-name
```

### Шаг 4: Создайте Procfile

```bash
cat > Procfile <<EOF
web: python bot_webhook.py
EOF
```

### Шаг 5: Создайте runtime.txt

```bash
echo "python-3.11.0" > runtime.txt
```

### Шаг 6: Настройте переменные

```bash
heroku config:set BOT_TOKEN=your_token_here
heroku config:set WEBHOOK_HOST=https://your-bot-name.herokuapp.com
heroku config:set WEBHOOK_PATH=/webhook
heroku config:set WEBAPP_HOST=0.0.0.0
heroku config:set WEBAPP_PORT=$PORT  # Heroku автоматически устанавливает $PORT
```

⚠️ **Важно**: Heroku динамически назначает порт. Измените `bot_webhook.py`:

```python
# Было:
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8000))

# Должно быть:
WEBAPP_PORT = int(os.getenv("PORT", 8000))  # Heroku использует PORT
```

### Шаг 7: Deploy

```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### ✅ Проверка

```bash
heroku logs --tail
heroku ps
```

**Плюсы:**
- ✅ Бесплатный tier
- ✅ Автоматический HTTPS
- ✅ Простой deploy

**Минусы:**
- ❌ Спит после 30 минут неактивности (бесплатный план)
- ❌ Ограниченные часы в месяц
- ❌ Может быть медленным

---

## 5. Railway

**Используйте для**: Современного production-ready деплоя

### Шаг 1: Создайте аккаунт на Railway.app

Перейдите на https://railway.app

### Шаг 2: Установите Railway CLI

```bash
npm install -g @railway/cli
# или
brew install railway
```

### Шаг 3: Войдите

```bash
railway login
```

### Шаг 4: Инициализируйте проект

```bash
cd example_11_webhook/aiogram  # или python_telegram_bot
railway init
```

### Шаг 5: Настройте переменные

```bash
railway variables set BOT_TOKEN=your_token_here
railway variables set WEBHOOK_HOST=https://your-project.up.railway.app
railway variables set WEBHOOK_PATH=/webhook
railway variables set WEBAPP_HOST=0.0.0.0
railway variables set WEBAPP_PORT=8000
```

### Шаг 6: Deploy

```bash
railway up
```

### ✅ Проверка

```bash
railway logs
railway status
```

**Плюсы:**
- ✅ Не засыпает
- ✅ Автоматический HTTPS
- ✅ Современный UI
- ✅ CI/CD из коробки

**Минусы:**
- ❌ Бесплатный план ограничен
- ❌ Может быть дороже других решений

---

## 6. Render.com

**Используйте для**: Production deployment с бесплатным tier

### Шаг 1: Создайте аккаунт на Render.com

Перейдите на https://render.com

### Шаг 2: Создайте новый Web Service

- Click "New +"
- Select "Web Service"
- Connect your GitHub repository

### Шаг 3: Настройте

```
Name: telegram-bot
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python bot_webhook.py
```

### Шаг 4: Добавьте переменные окружения

```
BOT_TOKEN=your_token_here
WEBHOOK_HOST=https://telegram-bot.onrender.com
WEBHOOK_PATH=/webhook
WEBAPP_HOST=0.0.0.0
WEBAPP_PORT=10000  # Render использует 10000 по умолчанию
```

### Шаг 5: Deploy

Click "Create Web Service"

### ✅ Проверка

Посмотрите логи в Dashboard

**Плюсы:**
- ✅ Бесплатный tier не спит (в отличие от Heroku)
- ✅ Автоматический HTTPS
- ✅ Auto-deploy из GitHub

**Минусы:**
- ❌ Холодный старт может быть медленным
- ❌ Ограничения бесплатного плана

---

## 📊 Сравнение платформ

| Платформа | Бесплатно | HTTPS | Спит | Сложность | Production-ready |
|-----------|-----------|-------|------|-----------|------------------|
| **Ngrok** | ✅ | ✅ | ❌ | ⭐ | ❌ |
| **VPS** | ❌ ($5/мес) | ✅* | ❌ | ⭐⭐⭐⭐ | ✅ |
| **Docker** | - | - | - | ⭐⭐⭐ | ✅ |
| **Heroku** | ✅ (ограничен) | ✅ | ✅ | ⭐⭐ | ⚠️ |
| **Railway** | ✅ (ограничен) | ✅ | ❌ | ⭐⭐ | ✅ |
| **Render** | ✅ | ✅ | ❌ | ⭐⭐ | ✅ |

*\* Требуется настройка Let's Encrypt*

---

## 🔍 Отладка проблем

### Webhook не устанавливается

```bash
# Проверьте что URL доступен
curl -I https://your-domain.com/webhook

# Проверьте SSL
curl -vI https://your-domain.com/webhook 2>&1 | grep SSL

# Проверьте webhook info
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### Бот не получает сообщения

```bash
# Проверьте логи
sudo journalctl -u telegram-bot -f

# Проверьте nginx
sudo tail -f /var/log/nginx/error.log

# Проверьте что порт открыт
netstat -tulpn | grep 8000
```

### SSL ошибки

```bash
# Проверьте сертификат
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Обновите сертификат
sudo certbot renew

# Перезагрузите nginx
sudo systemctl reload nginx
```

---

## 📚 Дополнительные ресурсы

- [Telegram Bot API - Webhooks](https://core.telegram.org/bots/api#setwebhook)
- [Let's Encrypt](https://letsencrypt.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [systemd Guide](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
