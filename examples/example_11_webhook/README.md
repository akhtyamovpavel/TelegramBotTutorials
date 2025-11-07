# Example 11: Bot Deployment with WebHook

**[Русская версия / Russian version](./README_RU.md)**

## 🎯 What's New in This Example

In previous examples (1-10), we used **polling** - the bot periodically queries the Telegram API for new messages.

**New concepts:**
- **WebHook** - Telegram pushes updates directly to your server
- **Production deployment** - proper bot deployment
- **SSL/HTTPS** - secure connection setup
- **Reverse proxy** - nginx in front of your application
- **Docker** - bot containerization

## 📚 Polling vs WebHook

### Polling (Examples 1-10)

```python
# Bot queries Telegram every N seconds
while True:
    updates = bot.get_updates()  # Request to Telegram API
    process(updates)
    time.sleep(1)
```

**Advantages:**
- ✅ Easy to set up - no public IP needed
- ✅ Works on local computer
- ✅ No SSL certificate required
- ✅ Easy to debug

**Disadvantages:**
- ❌ Constant API requests (load)
- ❌ Message delivery delay
- ❌ CPU resource consumption
- ❌ Not suitable for production

### WebHook (This Example)

```python
# Telegram sends updates to your server
@app.post("/webhook")
async def webhook(update: Update):
    await process(update)
    return {"ok": True}
```

**Advantages:**
- ✅ Instant update delivery
- ✅ Less load on API and server
- ✅ Production-ready
- ✅ Scalable

**Disadvantages:**
- ❌ Requires public domain with HTTPS
- ❌ SSL certificate needed
- ❌ More complex setup
- ❌ Doesn't work on localhost

## 📊 When to Use What?

| Scenario | Recommendation |
|----------|----------------|
| **Development and testing** | Polling |
| **Local computer** | Polling |
| **Production server** | WebHook |
| **High load (>1000 users)** | WebHook |
| **Multiple bots on one server** | WebHook |

## 🔧 Minimum Requirements for WebHook

1. **Public IP or domain**
   - ✅ example.com
   - ✅ bot.example.com
   - ❌ localhost
   - ❌ 192.168.x.x

2. **HTTPS with valid SSL certificate**
   - ✅ Let's Encrypt (free)
   - ✅ Cloudflare (free)
   - ❌ Self-signed certificates (won't work)

3. **Supported port**
   - ✅ 443 (standard HTTPS)
   - ✅ 80, 88, 8443 (alternative)
   - ❌ Other ports not supported by Telegram

4. **Web server (optional but recommended)**
   - nginx or Apache as reverse proxy
   - Handles SSL
   - Load balancing

## 📁 Example Structure

```
example_11_webhook/
├── README.md                          # This documentation
├── DEPLOYMENT.md                      # Deployment instructions
├── COMPARISON.md                      # Detailed polling vs webhook comparison
├── QUICKSTART.md                      # 5-minute quick start
├── aiogram/
│   ├── bot_webhook.py                 # Bot with aiogram
│   └── requirements.txt
├── python_telegram_bot/
│   ├── bot_webhook.py                 # Bot with python-telegram-bot
│   └── requirements.txt
├── nginx_config/
│   ├── simple.conf                    # Simple nginx config
│   └── advanced.conf                  # Advanced configuration
└── docker/
    ├── Dockerfile                     # Bot containerization
    ├── docker-compose.yml             # Docker Compose setup
    └── nginx.conf                     # Nginx in Docker
```

## 🚀 Quick Start

### Local Testing (with ngrok)

```bash
# Terminal 1: Run the bot
cd aiogram
pip install -r requirements.txt
export BOT_TOKEN="your_token_here"
python bot_webhook.py

# Terminal 2: Create tunnel
ngrok http 8000

# Copy HTTPS URL from ngrok (e.g., https://abc123.ngrok-free.app)
# Bot will automatically set webhook
```

### Production (on server)

```bash
# 1. Clone repository on server
git clone <repo>
cd example_11_webhook

# 2. Install dependencies
pip install -r aiogram/requirements.txt

# 3. Set environment variables
export BOT_TOKEN="your_token_here"
export WEBHOOK_URL="https://your-domain.com/webhook"
export WEBHOOK_PATH="/webhook"
export WEBAPP_HOST="0.0.0.0"
export WEBAPP_PORT="8000"

# 4. Configure nginx (see nginx_config/)
sudo cp nginx_config/simple.conf /etc/nginx/sites-available/bot
sudo ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 5. Get SSL certificate
sudo certbot --nginx -d your-domain.com

# 6. Run the bot
python aiogram/bot_webhook.py
```

## 🐳 Docker Deployment

```bash
cd docker
docker-compose up -d
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

## 🔍 How WebHook Works

### 1. Register webhook

```python
# Bot tells Telegram where to send updates
await bot.set_webhook(
    url="https://your-domain.com/webhook",
    drop_pending_updates=True
)
```

### 2. Telegram sends updates

```
User → Telegram → HTTPS POST → Your Server → Bot
```

### 3. Process update

```python
@app.post("/webhook")
async def webhook_handler(update: Update):
    # Process update
    await dp.feed_update(bot, update)
    return Response(status_code=200)
```

### 4. Response to Telegram

Bot **must** respond within 60 seconds:
- `200 OK` - update processed
- `4xx/5xx` - error, Telegram will retry

## 📋 WebHook Checklist

- [ ] Have public domain with HTTPS
- [ ] Valid SSL certificate (not self-signed)
- [ ] Port 443 or other supported port
- [ ] Firewall allows incoming connections
- [ ] Webhook URL accessible from internet
- [ ] Bot responds to requests within 60 seconds
- [ ] Nginx configured (if using)
- [ ] Logging works
- [ ] Monitoring configured

## 🔐 Security

### 1. Secret token verification

```python
# Set secret token when registering webhook
await bot.set_webhook(
    url="https://your-domain.com/webhook",
    secret_token="your_secret_here"
)

# Verify token in handler
if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET_TOKEN:
    return Response(status_code=403)
```

### 2. IP restriction

```nginx
# nginx.conf - allow only Telegram IPs
location /webhook {
    allow 149.154.160.0/20;
    allow 91.108.4.0/22;
    deny all;

    proxy_pass http://localhost:8000;
}
```

## 📖 Additional Materials

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - detailed deployment instructions for various platforms
- **[COMPARISON.md](./COMPARISON.md)** - detailed polling vs webhook comparison
- **[QUICKSTART.md](./QUICKSTART.md)** - 5-minute quick start guide
- **[nginx_config/](./nginx_config/)** - nginx configuration examples
- **[docker/](./docker/)** - Docker and Docker Compose examples

## 🎓 For Students

**Assignment:**
1. Deploy bot with webhook on VPS (DigitalOcean, Linode, Hetzner)
2. Configure nginx as reverse proxy
3. Get SSL certificate via Let's Encrypt
4. Set up monitoring and logging
5. Add systemd service for auto-start

**Report should include:**
- Screenshots of working bot
- Configuration files (nginx, systemd)
- Webhook operation logs
- Results of `curl` requests to webhook URL

## 🔗 Useful Links

- [Telegram Bot API - Using Webhook](https://core.telegram.org/bots/api#setwebhook)
- [Telegram Bot API - IP Ranges](https://core.telegram.org/bots/webhooks#the-short-version)
- [Let's Encrypt](https://letsencrypt.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 💡 Tips

1. **Start with ngrok** - test locally before deploying
2. **Use Let's Encrypt** - free SSL certificates
3. **Configure nginx** - don't expose bot directly to internet
4. **Log everything** - makes debugging easier
5. **Monitor health** - use healthcheck endpoint

## ⚠️ Common Issues

### Webhook not working

```bash
# Check webhook info
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo

# Delete webhook
curl https://api.telegram.org/bot<TOKEN>/deleteWebhook

# Set again
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -d url=https://your-domain.com/webhook
```

### SSL errors

```bash
# Check certificate
openssl s_client -connect your-domain.com:443

# Check expiration
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Nginx not forwarding requests

```bash
# Check configuration
sudo nginx -t

# View logs
sudo tail -f /var/log/nginx/error.log
```

---

**[Русская версия / Russian version](./README_RU.md)**
