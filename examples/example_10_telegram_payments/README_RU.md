# Example 9: Telegram Payments (Покупки за звезды)

## 🎯 Что нового в этом примере

В предыдущих примерах мы научились:
- Работать с файлами, изображениями и альбомами
- Создавать интерактивные интерфейсы с кнопками

**Новые концепции:**
- **Telegram Stars** - внутренняя валюта Telegram для оплаты
- **Создание инвойсов** - отправка счетов на оплату пользователям
- **Pre-checkout query** - проверка перед оплатой
- **Successful payment** - обработка успешной оплаты
- **Refund** - возврат средств пользователю
- **Paid media** - платный контент (изображения, видео)

## 📚 Концепции

### Что такое Telegram Stars?

**Telegram Stars** (⭐) - это внутренняя валюта Telegram, которую пользователи могут покупать и использовать для оплаты товаров и услуг в ботах.

**Особенности:**
- Пользователи покупают звезды за реальные деньги
- Боты получают звезды от пользователей
- Возможность возврата средств (refund)
- Не требует подключения внешних платежных систем
- Работает во всех странах, где доступен Telegram

### Зачем это нужно для ИИ-ботов?

1. **Монетизация** - продажа доступа к ИИ-моделям
2. **Платный контент** - генерация изображений, текста за плату
3. **Подписки** - ежемесячный доступ к премиум-функциям
4. **Микротранзакции** - оплата за каждый запрос к модели
5. **Paid media** - продажа сгенерированных изображений

## 🔄 Различия между библиотеками

| Функция | aiogram 3.x | python-telegram-bot 20.x |
|---------|-------------|--------------------------|
| **Отправка инвойса** | `bot.send_invoice()` | `bot.send_invoice()` |
| **Pre-checkout** | `@router.pre_checkout_query()` | `PreCheckoutQueryHandler` |
| **Successful payment** | `F.successful_payment` | `filters.SUCCESSFUL_PAYMENT` |
| **Возврат средств** | `bot.refund_star_payment()` | `bot.refund_star_payment()` |
| **Валюта Stars** | `currency="XTR"` | `currency="XTR"` |

## 📖 Теория: Процесс оплаты

### Шаги оплаты через Telegram Stars:

1. **Создание инвойса** - бот отправляет счет пользователю
2. **Нажатие кнопки оплаты** - пользователь нажимает "Pay X ⭐"
3. **Pre-checkout query** - бот может проверить условия перед оплатой
4. **Оплата** - пользователь подтверждает списание звезд
5. **Successful payment** - бот получает уведомление об успешной оплате
6. **Предоставление услуги** - бот выдает доступ/контент

### aiogram: Создание инвойса

```python
from aiogram.types import LabeledPrice

@router.message(Command("buy"))
async def send_invoice(message: Message, bot: Bot):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Генерация изображения ИИ",
        description="Создание уникального изображения с помощью Stable Diffusion",
        payload="ai_image_generation",  # Внутренний ID
        currency="XTR",  # Telegram Stars
        prices=[
            LabeledPrice(label="Генерация изображения", amount=10)  # 10 звезд
        ]
    )
```

### python-telegram-bot: Создание инвойса

```python
from telegram import LabeledPrice

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Генерация изображения ИИ",
        description="Создание уникального изображения с помощью Stable Diffusion",
        payload="ai_image_generation",
        currency="XTR",
        prices=[
            LabeledPrice(label="Генерация изображения", amount=10)
        ]
    )
```

## 📖 Теория: Pre-checkout Query

**Pre-checkout query** - это callback, который вызывается **до** списания средств. Здесь можно проверить:
- Достаточно ли у пользователя прав
- Не превышен ли лимит покупок
- Доступна ли услуга в данный момент

### aiogram: Обработка pre-checkout

```python
@router.pre_checkout_query()
async def process_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
    bot: Bot
):
    # Можно добавить проверки
    # Например, проверить базу данных на лимиты

    # Если все OK, подтверждаем
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )

    # Если ошибка, отклоняем с сообщением
    # await bot.answer_pre_checkout_query(
    #     pre_checkout_query.id,
    #     ok=False,
    #     error_message="Превышен лимит покупок на сегодня"
    # )
```

### python-telegram-bot: Обработка pre-checkout

```python
async def precheckout_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.pre_checkout_query

    # Проверки перед оплатой
    # ...

    # Подтверждаем
    await query.answer(ok=True)

    # Или отклоняем
    # await query.answer(ok=False, error_message="Ошибка")
```

## 📖 Теория: Successful Payment

После успешной оплаты бот получает сообщение с `successful_payment`.

### aiogram: Обработка успешной оплаты

```python
@router.message(F.successful_payment)
async def process_successful_payment(message: Message, bot: Bot):
    payment = message.successful_payment

    logger.info(
        f"Успешная оплата от {message.from_user.id}: "
        f"{payment.total_amount} {payment.currency}"
    )

    # Сохраняем ID транзакции для возможного возврата
    telegram_payment_charge_id = payment.telegram_payment_charge_id

    # Предоставляем услугу
    if payment.invoice_payload == "ai_image_generation":
        await message.answer("🎨 Генерирую изображение...")
        # ... генерация ...
        await message.answer_photo(generated_image)
```

### python-telegram-bot: Обработка успешной оплаты

```python
async def successful_payment_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    payment = update.message.successful_payment

    logger.info(
        f"Успешная оплата: {payment.total_amount} {payment.currency}"
    )

    # Предоставляем услугу
    if payment.invoice_payload == "ai_image_generation":
        await update.message.reply_text("🎨 Генерирую изображение...")
        # ... генерация ...
```

## 📖 Теория: Возврат средств (Refund)

Бот может вернуть средства пользователю:

### aiogram: Возврат

```python
@router.message(Command("refund"))
async def refund_payment(message: Message, bot: Bot):
    # Получаем telegram_payment_charge_id из БД
    payment_id = get_last_payment_id(message.from_user.id)

    result = await bot.refund_star_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=payment_id
    )

    if result:
        await message.answer("💰 Средства возвращены!")
```

### python-telegram-bot: Возврат

```python
async def refund_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment_id = get_last_payment_id(update.effective_user.id)

    result = await context.bot.refund_star_payment(
        user_id=update.effective_user.id,
        telegram_payment_charge_id=payment_id
    )

    if result:
        await update.message.reply_text("💰 Средства возвращены!")
```

## 🎨 Практическое применение для ИИ

### 1. Платная генерация изображений

```python
# Цены на разные модели
PRICES = {
    "stable_diffusion": LabeledPrice(label="Stable Diffusion", amount=5),
    "dalle": LabeledPrice(label="DALL-E", amount=10),
    "midjourney_style": LabeledPrice(label="Midjourney Style", amount=15),
}

@router.message(Command("generate_paid"))
async def paid_generation(message: Message, bot: Bot):
    # Показываем варианты
    builder = InlineKeyboardBuilder()
    builder.button(text="SD (5⭐)", callback_data="pay_stable_diffusion")
    builder.button(text="DALL-E (10⭐)", callback_data="pay_dalle")
    builder.button(text="MJ Style (15⭐)", callback_data="pay_midjourney_style")

    await message.answer(
        "Выберите модель для генерации:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("pay_"))
async def send_payment_invoice(callback: CallbackQuery, bot: Bot):
    model = callback.data.replace("pay_", "")

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Генерация изображения - {model}",
        description="Создание уникального изображения",
        payload=f"generate_{model}",
        currency="XTR",
        prices=[PRICES[model]]
    )
```

### 2. Подписка на премиум-функции

```python
@router.message(Command("premium"))
async def premium_subscription(message: Message, bot: Bot):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Премиум подписка",
        description="30 дней безлимитной генерации изображений",
        payload="premium_30days",
        currency="XTR",
        prices=[
            LabeledPrice(label="Подписка на 30 дней", amount=100)
        ]
    )

@router.message(F.successful_payment)
async def activate_premium(message: Message):
    payment = message.successful_payment

    if payment.invoice_payload == "premium_30days":
        # Активируем подписку в БД
        activate_user_premium(
            user_id=message.from_user.id,
            days=30
        )

        await message.answer(
            "🎉 Премиум активирован на 30 дней!\n\n"
            "Теперь доступны:\n"
            "• Безлимитная генерация\n"
            "• Приоритетная обработка\n"
            "• Эксклюзивные модели"
        )
```

### 3. Платные медиа (Paid Media)

```python
from aiogram.types import InputPaidMediaPhoto, FSInputFile

@router.message(Command("buy_art"))
async def send_paid_media(message: Message, bot: Bot):
    # Отправляем платное изображение
    await bot.send_paid_media(
        chat_id=message.chat.id,
        star_count=20,  # Стоимость в звездах
        media=[
            InputPaidMediaPhoto(
                media=FSInputFile("exclusive_art_1.jpg")
            ),
            InputPaidMediaPhoto(
                media=FSInputFile("exclusive_art_2.jpg")
            ),
        ],
        caption="🎨 Эксклюзивные работы ИИ-художника",
        show_caption_above_media=True
    )
```

## 🚀 Запуск примеров

### aiogram версия
```bash
export BOT_TOKEN="your_bot_token"
python examples/example_09_telegram_payments/aiogram/bot.py
```

### python-telegram-bot версия
```bash
export BOT_TOKEN="your_bot_token"
python examples/example_09_telegram_payments/python_telegram_bot/bot.py
```

## 📝 Команды бота

- `/start` - Приветствие и инструкции
- `/buy_basic` - Купить базовую генерацию (5⭐)
- `/buy_premium` - Купить премиум генерацию (10⭐)
- `/buy_pack` - Купить пакет из 10 генераций (40⭐)
- `/refund` - Вернуть последнюю покупку

## 🎓 Что изучили

1. ✅ Создание инвойсов для оплаты Telegram Stars
2. ✅ Обработка pre-checkout query
3. ✅ Обработка успешных платежей
4. ✅ Возврат средств пользователям
5. ✅ Интеграция платежей с ИИ-функциями

## 📚 Дополнительные материалы

### Важные замечания:

1. **Валюта**: Для Telegram Stars всегда используйте `currency="XTR"`
2. **provider_token**: Для Stars передавайте пустую строку `""`
3. **Цены**: Указываются в звездах (1 звезда = amount=1)
4. **Возврат**: Можно вернуть в течение 30 дней

### Лимиты:

- Минимальная цена: 1 звезда
- Максимальная цена: 10000 звезд
- Возврат доступен в течение 30 дней

### Лучшие практики:

1. **Сохраняйте payment_charge_id** для возможности возврата
2. **Используйте payload** для идентификации типа платежа
3. **Проверяйте в pre-checkout** доступность услуги
4. **Логируйте все транзакции** для отчетности
5. **Предоставляйте услугу сразу** после successful_payment

## 💰 Примеры цен для ИИ-услуг

| Услуга | Рекомендуемая цена |
|--------|-------------------|
| Генерация текста (GPT) | 1-3 ⭐ |
| Генерация изображения (SD) | 5-10 ⭐ |
| Генерация изображения (DALL-E) | 10-15 ⭐ |
| OCR текста | 2-5 ⭐ |
| Улучшение изображения | 5-8 ⭐ |
| Видео генерация | 20-50 ⭐ |
| Месячная подписка | 50-200 ⭐ |

## 🔗 Связанные примеры

- **Example 7** - Генерация изображений (можно монетизировать)
- **Example 8** - Альбомы (можно продавать как paid media)
- **Example 6** - Загрузка файлов (платная обработка)

---

**Совет для ИИ-разработчиков:** Telegram Stars - отличный способ монетизации ботов без сложной интеграции платежных систем. Начните с небольших цен и тестируйте спрос на ваши ИИ-услуги!
