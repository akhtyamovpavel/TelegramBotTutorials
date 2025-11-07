# Example 10: Telegram Payments - Telegram Stars

**[Русская версия / Russian version](./README_RU.md)**

## 🎯 What You'll Learn

- Creating invoices for payment
- Handling pre-checkout queries
- Processing successful payments
- Issuing refunds
- Monetizing AI features

## 🚀 Quick Start

```bash
cd aiogram  # or python_telegram_bot
pip install -r requirements.txt
export BOT_TOKEN="your_token_here"
python bot.py
```

## 💻 Key Code

```python
# aiogram - Create invoice
from aiogram.types import LabeledPrice

await message.answer_invoice(
    title="AI Image Generation",
    description="Generate 5 AI images with Stable Diffusion",
    payload="ai_generation_5_images",
    provider_token="",  # Empty for Telegram Stars
    currency="XTR",  # Telegram Stars
    prices=[LabeledPrice(label="5 Images", amount=100)]  # 100 stars
)

# Handle successful payment
@router.message(F.successful_payment)
async def handle_payment(message: Message):
    payment = message.successful_payment
    await message.answer(
        f"✅ Payment received!\n"
        f"Amount: {payment.total_amount} {payment.currency}"
    )
```

## 📖 Full Documentation

See [Russian version (README_RU.md)](./README_RU.md) for complete payments guide with refunds.

---

**[Full documentation in Russian](./README_RU.md)**
