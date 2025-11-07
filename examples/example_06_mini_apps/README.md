# Example 6: Telegram Mini Apps (WebApp)

**[Русская версия / Russian version](./README_RU.md)**

## ⚠️ Critical Requirements

### 1️⃣ Button Type: ONLY KeyboardButton!

**`sendData()` works ONLY with `KeyboardButton` (reply keyboard), NOT with `InlineKeyboardButton`!**

```python
# ✅ CORRECT - KeyboardButton (button in keyboard):
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Open", web_app=WebAppInfo(url=URL))]],
    resize_keyboard=True
)

# ❌ WRONG - InlineKeyboardButton (button under message):
# keyboard = InlineKeyboardMarkup(
#     inline_keyboard=[[InlineKeyboardButton(text="Open", web_app=WebAppInfo(url=URL))]]
# )
# WebApp will open, but sendData() WON'T work!
```

**Source:** [StackOverflow - Web App Data not received](https://stackoverflow.com/questions/72988184/)

### 2️⃣ HTTPS Required

**Telegram does NOT support `data:` URLs and HTTP for WebApp!**

WebApp **must** be hosted on a **real HTTPS server**.

📖 **[Detailed deployment instructions → DEPLOYMENT.md](./DEPLOYMENT.md)**

**Quick options:**
- ✅ GitHub Pages (free, recommended)
- ✅ Vercel/Netlify (free)
- ✅ Ngrok (for testing)

---

## 🎯 What's New in This Example

In previous examples we worked with:
- Regular buttons (Reply Keyboard, Example 3)
- State machines (FSM, Example 4)
- Databases (Example 5)

**New concepts:**
- **Telegram Mini Apps (WebApp)** - web applications inside Telegram
- **WebAppInfo** - buttons that open web interfaces
- **web_app_data** - receiving data from WebApp
- **Telegram WebApp API** - JavaScript API for interaction

## 📚 Concepts

### What are Telegram Mini Apps?

**Telegram Mini Apps** (formerly WebApp) are web applications (HTML/CSS/JavaScript) that open **inside** Telegram. They allow creating rich interactive interfaces impossible with regular buttons.

**Advantages:**
- **Rich UI** - full web interface (canvas, WebGL, forms)
- **Native integration** - access to Telegram user data
- **No installation** - opens directly in chat
- **Cross-platform** - works on all devices

### Why for AI Bots?

1. **Interactive visualization** - displaying graphs, result diagrams
2. **Complex forms** - configuring AI model parameters
3. **Canvas/WebGL** - drawing prompts for Image-to-Image
4. **Result preview** - interactive view of generated content
5. **Model settings** - UI for fine-tuning parameters

## 🔄 Differences Between Libraries

| Feature | aiogram 3.x | python-telegram-bot 20.x |
|---------|-------------|--------------------------|
| **WebApp button** | `WebAppInfo(url="...")` | `WebAppInfo(url="...")` |
| **Receiving data** | `F.web_app_data` | `filters.StatusUpdate.WEB_APP_DATA` |
| **Keyboard** | `ReplyKeyboardMarkup` | `ReplyKeyboardMarkup` |
| **WebApp data** | `message.web_app_data.data` | `message.web_app_data.data` |

## 📁 Example Structure

```
example_06_mini_apps/
├── README.md                          # This file
├── DEPLOYMENT.md                      # Deployment instructions
├── IMPORTANT_BUTTON_TYPE.md           # Critical: Button type guide
├── DEBUG.md                           # Debugging guide
├── FIX_NO_RESPONSE.md                 # Fix "bot doesn't respond"
├── TESTING.md                         # Testing guide
├── webapp/
│   ├── index.html                     # Main WebApp
│   └── index_debug.html               # Debug version with console
├── aiogram/
│   ├── bot.py                         # Bot with aiogram
│   ├── test_bot_minimal.py            # Minimal test bot
│   └── requirements.txt
└── python_telegram_bot/
    ├── bot.py                         # Bot with python-telegram-bot
    └── requirements.txt
```

## 🚀 Quick Start

### Step 1: Deploy WebApp

WebApp MUST be on HTTPS server:

```bash
# Option 1: GitHub Pages (recommended)
# 1. Create repo on GitHub
# 2. Enable GitHub Pages
# 3. Upload webapp/ folder
# URL: https://username.github.io/repo/webapp/index.html

# Option 2: Ngrok (for testing)
cd webapp
python -m http.server 8000
# In another terminal:
ngrok http 8000
# Copy HTTPS URL
```

### Step 2: Configure Bot

```bash
export BOT_TOKEN="your_token"
export WEBAPP_URL="https://your-domain.com/webapp/index.html"
```

### Step 3: Run Bot

```bash
# aiogram
cd aiogram
pip install -r requirements.txt
python bot.py

# python-telegram-bot
cd python_telegram_bot
pip install -r requirements.txt
python bot.py
```

### Step 4: Test in Telegram

1. Send `/webapp` to your bot
2. Click button **in keyboard** (bottom of screen)
3. Fill form in WebApp
4. Click "🎨 Generate"
5. Bot will respond with parameters

## 🔧 Code Examples

### aiogram

```python
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

router = Router()

@router.message(Command("webapp"))
async def cmd_webapp(message: Message):
    """Open WebApp"""
    # IMPORTANT: KeyboardButton, NOT InlineKeyboardButton!
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="⚙️ Open Settings",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]],
        resize_keyboard=True
    )

    await message.answer("Click button below:", reply_markup=keyboard)

@router.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    """Handle data from WebApp"""
    data = json.loads(message.web_app_data.data)

    await message.answer(
        f"✅ Received data!\n\n"
        f"Prompt: {data['prompt']}\n"
        f"Model: {data['model']}"
    )
```

### python-telegram-bot

```python
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open WebApp"""
    # IMPORTANT: KeyboardButton, NOT InlineKeyboardButton!
    keyboard = ReplyKeyboardMarkup(
        [[
            KeyboardButton(
                text="⚙️ Open Settings",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]],
        resize_keyboard=True
    )

    await update.message.reply_text("Click button below:", reply_markup=keyboard)

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle data from WebApp"""
    data = json.loads(update.message.web_app_data.data)

    await update.message.reply_text(
        f"✅ Received data!\n\n"
        f"Prompt: {data['prompt']}\n"
        f"Model: {data['model']}"
    )

# Register handlers
app.add_handler(CommandHandler("webapp", webapp_command))
app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
```

### WebApp (index.html)

```javascript
// Initialize Telegram WebApp
let tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Send data to bot
function sendData() {
    const data = {
        prompt: document.getElementById('prompt').value,
        model: document.getElementById('model').value,
        steps: parseInt(document.getElementById('steps').value),
        // ... other parameters
    };

    // Send as JSON string
    tg.sendData(JSON.stringify(data));
}

// Setup main button
tg.MainButton.setText('🎨 Generate');
tg.MainButton.show();
tg.MainButton.onClick(sendData);
```

## 📖 Additional Documentation

- **[IMPORTANT_BUTTON_TYPE.md](./IMPORTANT_BUTTON_TYPE.md)** - Critical info about button types
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - How to deploy WebApp
- **[DEBUG.md](./DEBUG.md)** - Debugging guide
- **[FIX_NO_RESPONSE.md](./FIX_NO_RESPONSE.md)** - Fix "bot doesn't respond"
- **[TESTING.md](./TESTING.md)** - Testing guide

## ⚠️ Common Issues

### Bot doesn't receive data

**Cause**: Using `InlineKeyboardButton` instead of `KeyboardButton`

**Solution**: Use `ReplyKeyboardMarkup` + `KeyboardButton`. See [IMPORTANT_BUTTON_TYPE.md](./IMPORTANT_BUTTON_TYPE.md)

### WebApp doesn't open

**Cause 1**: Not HTTPS
**Solution**: Use GitHub Pages, Vercel, or Ngrok

**Cause 2**: data: URL
**Solution**: Host on real server

### Browser console errors

**Cause**: `telegram-web-app.js` not loaded

**Solution**: Add to `<head>`:
```html
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```

## 🎓 For Students

**Assignment:**
1. Create WebApp with AI model parameters
2. Deploy to GitHub Pages
3. Implement bot that receives and displays parameters
4. Test with different configurations

**Report should include:**
- Screenshots of working WebApp
- Bot code with handlers
- WebApp HTML/CSS/JS code
- Test results with different parameters

## 🔗 Useful Links

- [Telegram Mini Apps Documentation](https://core.telegram.org/bots/webapps)
- [WebApp JavaScript API](https://core.telegram.org/bots/webapps#initializing-mini-apps)
- [Bot API - WebAppInfo](https://core.telegram.org/bots/api#webappinfo)
- [GitHub Pages](https://pages.github.com/)

---

**[Русская версия / Russian version](./README_RU.md)**
