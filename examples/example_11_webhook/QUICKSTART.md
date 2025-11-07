# 🚀 Quick Start: WebHook Bot in 5 Minutes

**[🇷🇺 Русская версия / Russian version](./QUICKSTART_RU.md)**

This guide will help you run a webhook bot locally using ngrok.

## Step 1: Install Dependencies

```bash
cd aiogram  # or python_telegram_bot
pip install -r requirements.txt
```

## Step 2: Install ngrok

### macOS
```bash
brew install ngrok
```

### Linux
```bash
# Ubuntu/Debian
sudo snap install ngrok

# Or download:
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

### Windows
Download from https://ngrok.com/download

## Step 3: Get Bot Token

1. Find [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot`
3. Follow instructions
4. Copy token (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 4: Run the Bot

### Terminal 1: Start the bot

```bash
cd aiogram  # or python_telegram_bot

export BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # ← Your token
export WEBHOOK_HOST="https://temp.ngrok-free.app"        # ← Will update in step 6
export WEBHOOK_PATH="/webhook"
export WEBAPP_PORT="8000"

python bot_webhook.py
```

You'll see:
```
🚀 Starting WebHook bot...
📍 Webhook URL: https://temp.ngrok-free.app/webhook
❌ Failed to set webhook!  # ← This is normal, URL doesn't work yet
```

**Stop the bot (Ctrl+C) - we'll return to it**

### Terminal 2: Start ngrok

```bash
ngrok http 8000
```

You'll see:
```
Session Status                online
Account                       user@example.com
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

## Step 5: Update WEBHOOK_HOST

### Return to Terminal 1:

```bash
export WEBHOOK_HOST="https://abc123.ngrok-free.app"  # ← Your ngrok URL

python bot_webhook.py
```

Now you should see:
```
🚀 Starting WebHook bot...
📍 Webhook URL: https://abc123.ngrok-free.app/webhook
✅ Webhook successfully set!
📊 Webhook info:
   URL: https://abc123.ngrok-free.app/webhook
   Pending updates: 0
🌐 Web server listening on 0.0.0.0:8000
🎯 Telegram will send updates to: https://abc123.ngrok-free.app/webhook
```

## Step 6: Test the Bot

Open Telegram and find your bot:

1. Send `/start`
   ```
   👋 Bot is running via WebHook!

   This means Telegram sends updates directly to our server...
   ```

2. Send `/status`
   ```
   📊 Bot Status

   URL: https://abc123.ngrok-free.app/webhook
   Pending updates: 0
   Last error: No errors
   ```

3. Send any message
   ```
   📨 Received message:

   Hello!

   💡 This demonstrates that WebHook is working!
   ```

## ✅ Done!

Your bot is working via webhook!

**What's happening:**
1. You send a message in Telegram
2. Telegram instantly sends HTTPS POST to `https://abc123.ngrok-free.app/webhook`
3. Ngrok proxies the request to `http://localhost:8000/webhook`
4. Your bot processes the update
5. Bot sends response

## 🔍 Verify Webhook

### Check webhook info via API:

```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

Should show:
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

### View ngrok logs:

In the terminal with ngrok you'll see incoming requests from Telegram:
```
POST /webhook  200 OK
POST /webhook  200 OK
```

## 🐛 Problems?

### Bot not receiving messages

```bash
# Check bot is running
# Terminal 1 should show: "Web server listening on 0.0.0.0:8000"

# Check ngrok is working
# Terminal 2 should show: "Session Status: online"

# Check webhook info
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### SSL errors

Ngrok **automatically** provides a valid SSL certificate. If there are SSL errors - check that you're using **HTTPS** URL from ngrok (not HTTP).

### Error "Wrong response from the webhook"

Make sure bot responds with `200 OK` within 60 seconds. Check bot logs.

## 🎓 Next Steps

After webhook works locally:

1. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deploy on production server
2. **[COMPARISON.md](./COMPARISON.md)** - Study differences between polling and webhook
3. **[README.md](./README.md)** - Detailed documentation

## 💡 Tip

For development use **polling** (easier), and save webhook for **production**. To switch between them:

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

**Done!** Now you know how to work with webhooks! 🎉

**[🇷🇺 Русская версия / Russian version](./QUICKSTART_RU.md)**
