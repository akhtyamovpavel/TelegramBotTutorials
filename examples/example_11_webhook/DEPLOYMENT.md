# 🚀 Comprehensive Deployment Guide for WebHook Bots

**[🇷🇺 Русская версия / Russian version](./DEPLOYMENT_RU.md)**

This guide covers various ways to deploy a Telegram bot with webhook.

## 📋 Contents

1. [Local Testing with Ngrok](#1-local-testing-with-ngrok)
2. [VPS (DigitalOcean, Hetzner, Linode)](#2-vps-digitalocean-hetzner-linode)
3. [Docker Deployment](#3-docker-deployment)
4. [Heroku](#4-heroku)
5. [Railway](#5-railway)
6. [Render.com](#6-rendercom)

---

## 1. Local Testing with Ngrok

**Use for**: Development and quick testing

### Step 1: Install Ngrok

```bash
# macOS
brew install ngrok

# Linux
snap install ngrok

# Or download from https://ngrok.com/download
```

### Step 2: Run the Bot

```bash
cd aiogram  # or python_telegram_bot
pip install -r requirements.txt

export BOT_TOKEN="your_token_here"
export WEBHOOK_HOST="https://will-be-set-by-ngrok.ngrok-free.app"
export WEBHOOK_PATH="/webhook"
export WEBAPP_PORT="8000"

python bot_webhook.py
```

### Step 3: Run Ngrok (in another terminal)

```bash
ngrok http 8000
```

You'll see:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

### Step 4: Update WEBHOOK_HOST

```bash
# Stop the bot (Ctrl+C)

# Update variable:
export WEBHOOK_HOST="https://abc123.ngrok-free.app"

# Restart:
python bot_webhook.py
```

### ✅ Verification

```bash
# Check webhook info
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

**Pros:**
- ✅ Quick testing
- ✅ No VPS needed
- ✅ Automatic HTTPS

**Cons:**
- ❌ URL changes on each ngrok restart
- ❌ Not for production
- ❌ Free version has limitations

---

## 2. VPS (DigitalOcean, Hetzner, Linode)

**Use for**: Production deployment

### Requirements

- Ubuntu 20.04/22.04 LTS
- Public IP address
- Domain name (e.g., `bot.example.com`)

### Step 1: Connect to Server

```bash
ssh root@your-server-ip
```

### Step 2: Update System

```bash
apt update && apt upgrade -y
```

### Step 3: Install Python and Dependencies

```bash
apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx -y
```

### Step 4: Create Bot User

```bash
adduser botuser
usermod -aG sudo botuser
su - botuser
```

### Step 5: Clone Repository

```bash
cd ~
git clone <your-repo-url>
cd example_11_webhook/aiogram  # or python_telegram_bot
```

### Step 6: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 7: Set Environment Variables

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

### Step 8: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/bot
```

Insert:

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

    # SSL certificates (will be created by certbot)
    ssl_certificate /etc/letsencrypt/live/bot.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.example.com/privkey.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logs
    access_log /var/log/nginx/bot_access.log;
    error_log /var/log/nginx/bot_error.log;

    # Webhook endpoint
    location /webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Allow only Telegram IPs
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

    # Block all other requests
    location / {
        return 404;
    }
}
```

Activate configuration:

```bash
sudo ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/
sudo nginx -t
```

### Step 9: Get SSL Certificate

```bash
# Temporarily comment out SSL lines in nginx config
sudo nano /etc/nginx/sites-available/bot
# Comment out ssl_certificate* lines

sudo systemctl reload nginx

# Get certificate
sudo certbot --nginx -d bot.example.com

# Uncomment SSL lines back
sudo nano /etc/nginx/sites-available/bot

# Reload nginx
sudo systemctl reload nginx
```

### Step 10: Create systemd Service

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Insert:

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

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

[Install]
WantedBy=multi-user.target
```

### Step 11: Start Bot

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### ✅ Verification

```bash
# Check status
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f

# Check webhook
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo

# Check healthcheck
curl https://bot.example.com/health
```

### 🔧 Management

```bash
# Stop
sudo systemctl stop telegram-bot

# Restart
sudo systemctl restart telegram-bot

# View logs
sudo journalctl -u telegram-bot -f --lines 100
```

---

## 3. Docker Deployment

**Use for**: Isolated development and production deployment

### Step 1: Dockerfile

Already created in `docker/Dockerfile`

### Step 2: Docker Compose

Already created in `docker/docker-compose.yml`

### Step 3: Run

```bash
cd docker

# Create .env file
cat > .env <<EOF
BOT_TOKEN=your_token_here
WEBHOOK_HOST=https://bot.example.com
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=your_secret_here
EOF

# Run
docker-compose up -d

# View logs
docker-compose logs -f bot
```

### ✅ Verification

```bash
# Container status
docker-compose ps

# Logs
docker-compose logs bot

# Stop
docker-compose down
```

---

## 4. Heroku

**Use for**: Quick free deployment (with limitations)

### Step 1: Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Create Application

```bash
cd example_11_webhook/aiogram  # or python_telegram_bot
heroku create your-bot-name
```

### Step 4: Create Procfile

```bash
cat > Procfile <<EOF
web: python bot_webhook.py
EOF
```

### Step 5: Create runtime.txt

```bash
echo "python-3.11.0" > runtime.txt
```

### Step 6: Configure Variables

```bash
heroku config:set BOT_TOKEN=your_token_here
heroku config:set WEBHOOK_HOST=https://your-bot-name.herokuapp.com
heroku config:set WEBHOOK_PATH=/webhook
heroku config:set WEBAPP_HOST=0.0.0.0
heroku config:set WEBAPP_PORT=$PORT  # Heroku auto-sets $PORT
```

⚠️ **Important**: Heroku dynamically assigns port. Modify `bot_webhook.py`:

```python
# Was:
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8000))

# Should be:
WEBAPP_PORT = int(os.getenv("PORT", 8000))  # Heroku uses PORT
```

### Step 7: Deploy

```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### ✅ Verification

```bash
heroku logs --tail
heroku ps
```

**Pros:**
- ✅ Free tier
- ✅ Automatic HTTPS
- ✅ Easy deploy

**Cons:**
- ❌ Sleeps after 30 minutes of inactivity (free plan)
- ❌ Limited hours per month
- ❌ Can be slow

---

## 5. Railway

**Use for**: Modern production-ready deployment

### Step 1: Create Account on Railway.app

Go to https://railway.app

### Step 2: Install Railway CLI

```bash
npm install -g @railway/cli
# or
brew install railway
```

### Step 3: Login

```bash
railway login
```

### Step 4: Initialize Project

```bash
cd example_11_webhook/aiogram  # or python_telegram_bot
railway init
```

### Step 5: Configure Variables

```bash
railway variables set BOT_TOKEN=your_token_here
railway variables set WEBHOOK_HOST=https://your-project.up.railway.app
railway variables set WEBHOOK_PATH=/webhook
railway variables set WEBAPP_HOST=0.0.0.0
railway variables set WEBAPP_PORT=8000
```

### Step 6: Deploy

```bash
railway up
```

### ✅ Verification

```bash
railway logs
railway status
```

**Pros:**
- ✅ Doesn't sleep
- ✅ Automatic HTTPS
- ✅ Modern UI
- ✅ CI/CD out of box

**Cons:**
- ❌ Free plan limited
- ❌ Can be more expensive than alternatives

---

## 6. Render.com

**Use for**: Production deployment with free tier

### Step 1: Create Account on Render.com

Go to https://render.com

### Step 2: Create New Web Service

- Click "New +"
- Select "Web Service"
- Connect your GitHub repository

### Step 3: Configure

```
Name: telegram-bot
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python bot_webhook.py
```

### Step 4: Add Environment Variables

```
BOT_TOKEN=your_token_here
WEBHOOK_HOST=https://telegram-bot.onrender.com
WEBHOOK_PATH=/webhook
WEBAPP_HOST=0.0.0.0
WEBAPP_PORT=10000  # Render uses 10000 by default
```

### Step 5: Deploy

Click "Create Web Service"

### ✅ Verification

View logs in Dashboard

**Pros:**
- ✅ Free tier doesn't sleep (unlike Heroku)
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub

**Cons:**
- ❌ Cold start can be slow
- ❌ Free plan limitations

---

## 📊 Platform Comparison

| Platform | Free | HTTPS | Sleeps | Complexity | Production-ready |
|----------|------|-------|--------|------------|------------------|
| **Ngrok** | ✅ | ✅ | ❌ | ⭐ | ❌ |
| **VPS** | ❌ ($5/mo) | ✅* | ❌ | ⭐⭐⭐⭐ | ✅ |
| **Docker** | - | - | - | ⭐⭐⭐ | ✅ |
| **Heroku** | ✅ (limited) | ✅ | ✅ | ⭐⭐ | ⚠️ |
| **Railway** | ✅ (limited) | ✅ | ❌ | ⭐⭐ | ✅ |
| **Render** | ✅ | ✅ | ❌ | ⭐⭐ | ✅ |

*\* Requires Let's Encrypt setup*

---

## 🔍 Troubleshooting

### Webhook Not Setting

```bash
# Check URL is accessible
curl -I https://your-domain.com/webhook

# Check SSL
curl -vI https://your-domain.com/webhook 2>&1 | grep SSL

# Check webhook info
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### Bot Not Receiving Messages

```bash
# Check logs
sudo journalctl -u telegram-bot -f

# Check nginx
sudo tail -f /var/log/nginx/error.log

# Check port is open
netstat -tulpn | grep 8000
```

### SSL Errors

```bash
# Check certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Renew certificate
sudo certbot renew

# Reload nginx
sudo systemctl reload nginx
```

---

## 📚 Additional Resources

- [Telegram Bot API - Webhooks](https://core.telegram.org/bots/api#setwebhook)
- [Let's Encrypt](https://letsencrypt.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [systemd Guide](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

**[🇷🇺 Русская версия / Russian version](./DEPLOYMENT_RU.md)**
