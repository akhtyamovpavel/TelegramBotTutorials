"""
Telegram Bot Example 9: Telegram Payments (aiogram)
Демонстрирует работу с платежами через Telegram Stars
"""

import asyncio
import logging
import os
from datetime import datetime
from io import BytesIO
from typing import Dict

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    LabeledPrice,
    PreCheckoutQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from PIL import Image, ImageDraw, ImageFont

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не указан BOT_TOKEN! Установите переменную окружения.")

# Роутер для обработчиков
router = Router()

# Хранилище платежей (в production используйте БД!)
# Структура: {user_id: {"payment_id": str, "timestamp": datetime}}
user_payments: Dict[int, dict] = {}


def generate_ai_image(text: str, color: tuple = (100, 150, 255)) -> BytesIO:
    """
    Имитация генерации изображения ИИ
    В реальности здесь был бы вызов Stable Diffusion или DALL-E

    Args:
        text: Текст для изображения
        color: Цвет фона

    Returns:
        BytesIO объект с изображением
    """
    # Создаем изображение
    image = Image.new('RGB', (512, 512), color=color)
    draw = ImageDraw.Draw(image)

    # Пытаемся загрузить шрифт
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Рисуем текст
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((512 - text_width) // 2, (512 - text_height) // 2)
    draw.text(position, text, fill='white', font=font)

    # Добавляем водяной знак
    draw.text((10, 480), "AI Generated", fill=(200, 200, 200))

    # Сохраняем в BytesIO
    bio = BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)

    return bio


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветственное сообщение"""
    await message.answer(
        "⭐ <b>Бот с оплатой через Telegram Stars</b>\n\n"
        "Это демонстрационный бот для изучения работы с платежами.\n\n"
        "<b>Доступные команды:</b>\n"
        "/buy_basic - Базовая генерация (5⭐)\n"
        "/buy_premium - Премиум генерация (10⭐)\n"
        "/buy_pack - Пакет из 10 генераций (40⭐)\n"
        "/refund - Вернуть последнюю покупку\n\n"
        "💡 <i>Для тестирования вам понадобятся Telegram Stars.\n"
        "Их можно купить в настройках Telegram.</i>",
        parse_mode="HTML"
    )


@router.message(Command("buy_basic"))
async def buy_basic(message: Message, bot: Bot):
    """Отправка инвойса для базовой генерации"""
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Базовая генерация изображения",
        description="Создание одного изображения с помощью ИИ (базовое качество)",
        payload="basic_generation",  # Внутренний ID для идентификации
        currency="XTR",  # Telegram Stars
        prices=[
            LabeledPrice(label="Генерация изображения", amount=5)  # 5 звезд
        ]
    )
    logger.info(f"Отправлен инвойс 'basic' пользователю {message.from_user.id}")


@router.message(Command("buy_premium"))
async def buy_premium(message: Message, bot: Bot):
    """Отправка инвойса для премиум генерации"""
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Премиум генерация изображения",
        description="Создание высококачественного изображения с помощью продвинутой ИИ-модели",
        payload="premium_generation",
        currency="XTR",
        prices=[
            LabeledPrice(label="Премиум генерация", amount=10)  # 10 звезд
        ]
    )
    logger.info(f"Отправлен инвойс 'premium' пользователю {message.from_user.id}")


@router.message(Command("buy_pack"))
async def buy_pack(message: Message, bot: Bot):
    """Отправка инвойса для пакета генераций"""
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Пакет из 10 генераций",
        description="Выгодный пакет: 10 генераций изображений со скидкой 20%",
        payload="pack_10_generations",
        currency="XTR",
        prices=[
            LabeledPrice(label="10 генераций", amount=40)  # 40 вместо 50
        ]
    )
    logger.info(f"Отправлен инвойс 'pack' пользователю {message.from_user.id}")


@router.pre_checkout_query()
async def process_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
    bot: Bot
):
    """
    Обработка pre-checkout query
    Здесь можно проверить условия перед оплатой
    """
    logger.info(
        f"Pre-checkout от {pre_checkout_query.from_user.id}: "
        f"{pre_checkout_query.invoice_payload}"
    )

    # В реальном боте здесь можно добавить проверки:
    # - Проверить лимит покупок пользователя
    # - Проверить доступность услуги
    # - Проверить баланс сервера и т.д.

    # Можно отклонить платеж с сообщением об ошибке:
    # await bot.answer_pre_checkout_query(
    #     pre_checkout_query.id,
    #     ok=False,
    #     error_message="Превышен лимит покупок на сегодня"
    # )

    # Подтверждаем платеж
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, bot: Bot):
    """
    Обработка успешной оплаты
    Здесь предоставляем услугу пользователю
    """
    payment = message.successful_payment

    logger.info(
        f"Успешная оплата от {message.from_user.id}: "
        f"{payment.total_amount} {payment.currency}, "
        f"payload: {payment.invoice_payload}"
    )

    # Сохраняем информацию о платеже для возможного возврата
    user_payments[message.from_user.id] = {
        "payment_id": payment.telegram_payment_charge_id,
        "timestamp": datetime.now(),
        "amount": payment.total_amount,
        "payload": payment.invoice_payload
    }

    # Благодарим за покупку
    await message.answer(
        f"✅ <b>Оплата успешна!</b>\n\n"
        f"Получено: {payment.total_amount} ⭐\n"
        f"ID транзакции: <code>{payment.telegram_payment_charge_id}</code>\n\n"
        f"🎨 Генерирую ваше изображение...",
        parse_mode="HTML"
    )

    # Предоставляем услугу в зависимости от типа покупки
    if payment.invoice_payload == "basic_generation":
        # Базовая генерация
        image = generate_ai_image("Basic AI Art", color=(100, 100, 200))
        await message.answer_photo(
            BufferedInputFile(image.read(), "basic_art.png"),
            caption="🎨 Ваше базовое изображение готово!"
        )

    elif payment.invoice_payload == "premium_generation":
        # Премиум генерация
        image = generate_ai_image("Premium AI Art", color=(200, 100, 200))
        await message.answer_photo(
            BufferedInputFile(image.read(), "premium_art.png"),
            caption="✨ Ваше премиум изображение готово!"
        )

    elif payment.invoice_payload == "pack_10_generations":
        # Пакет генераций
        await message.answer(
            "📦 <b>Пакет активирован!</b>\n\n"
            "У вас теперь 10 доступных генераций.\n"
            "Используйте команду /generate для создания изображений.",
            parse_mode="HTML"
        )

        # В реальном боте здесь бы обновили базу данных
        # add_user_credits(message.from_user.id, credits=10)


@router.message(Command("refund"))
async def refund_last_payment(message: Message, bot: Bot):
    """Возврат средств за последнюю покупку"""
    user_id = message.from_user.id

    # Проверяем, есть ли платежи
    if user_id not in user_payments:
        await message.answer(
            "❌ У вас нет платежей для возврата.\n"
            "Сначала совершите покупку!"
        )
        return

    payment_info = user_payments[user_id]

    # Проверяем, не прошло ли слишком много времени (для демонстрации - 5 минут)
    time_diff = datetime.now() - payment_info["timestamp"]
    if time_diff.total_seconds() > 300:  # 5 минут
        await message.answer(
            "⏰ К сожалению, время для возврата истекло.\n"
            "Возврат доступен в течение 5 минут после покупки."
        )
        return

    try:
        # Пытаемся вернуть средства
        result = await bot.refund_star_payment(
            user_id=user_id,
            telegram_payment_charge_id=payment_info["payment_id"]
        )

        if result:
            await message.answer(
                f"✅ <b>Возврат успешно выполнен!</b>\n\n"
                f"Возвращено: {payment_info['amount']} ⭐\n"
                f"ID транзакции: <code>{payment_info['payment_id']}</code>",
                parse_mode="HTML"
            )

            # Удаляем информацию о платеже
            del user_payments[user_id]

            logger.info(f"Возврат выполнен для пользователя {user_id}")
        else:
            await message.answer(
                "❌ Не удалось выполнить возврат.\n"
                "Попробуйте позже или обратитесь в поддержку."
            )

    except Exception as e:
        logger.error(f"Ошибка при возврате средств: {e}")
        await message.answer(
            "❌ Произошла ошибка при возврате средств.\n"
            f"Детали: {str(e)}"
        )


@router.message(Command("my_payments"))
async def show_payments_info(message: Message):
    """Показать информацию о платежах пользователя"""
    user_id = message.from_user.id

    if user_id not in user_payments:
        await message.answer(
            "📊 У вас пока нет платежей.\n\n"
            "Попробуйте:\n"
            "/buy_basic - Базовая генерация (5⭐)\n"
            "/buy_premium - Премиум генерация (10⭐)"
        )
        return

    payment_info = user_payments[user_id]
    time_diff = datetime.now() - payment_info["timestamp"]

    await message.answer(
        f"📊 <b>Ваш последний платеж:</b>\n\n"
        f"Сумма: {payment_info['amount']} ⭐\n"
        f"Тип: {payment_info['payload']}\n"
        f"Время: {payment_info['timestamp'].strftime('%H:%M:%S')}\n"
        f"ID: <code>{payment_info['payment_id']}</code>\n\n"
        f"⏰ Прошло: {int(time_diff.total_seconds())} секунд\n\n"
        f"💡 Возврат доступен в течение 5 минут после покупки.",
        parse_mode="HTML"
    )


async def main():
    """Главная функция запуска бота"""
    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем роутер
    dp.include_router(router)

    logger.info("Бот запущен и готов принимать платежи!")

    try:
        # Запускаем polling
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
