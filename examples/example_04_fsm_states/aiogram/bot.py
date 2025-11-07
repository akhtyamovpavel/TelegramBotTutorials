import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardRemove

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

TOKEN = getenv("BOT_TOKEN")
router = Router()


# Определяем состояния
class RegistrationForm(StatesGroup):
    name = State()      # Ожидание имени
    age = State()       # Ожидание возраста
    city = State()      # Ожидание города


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    """
    Начало регистрации
    """
    await state.set_state(RegistrationForm.name)
    await message.answer(
        "Привет! Давайте познакомимся.\n"
        "Как вас зовут?\n\n"
        "Для отмены используйте /cancel"
    )


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Отмена текущего действия
    """
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.")
        return

    await state.clear()
    await message.answer(
        "Регистрация отменена.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(RegistrationForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    """
    Обработка имени и переход к возрасту
    """
    # Сохраняем имя в контексте
    await state.update_data(name=message.text)

    # Переходим к следующему состоянию
    await state.set_state(RegistrationForm.age)

    await message.answer(f"Приятно познакомиться, {message.text}!\nСколько вам лет?")


@router.message(RegistrationForm.age)
async def process_age(message: Message, state: FSMContext) -> None:
    """
    Обработка возраста и переход к городу
    """
    # Проверяем, что введено число
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите возраст числом.")
        return

    age = int(message.text)

    if age < 0 or age > 120:
        await message.answer("Введите корректный возраст (от 0 до 120).")
        return

    # Сохраняем возраст
    await state.update_data(age=age)

    # Переходим к следующему состоянию
    await state.set_state(RegistrationForm.city)

    await message.answer("В каком городе вы живете?")


@router.message(RegistrationForm.city)
async def process_city(message: Message, state: FSMContext) -> None:
    """
    Обработка города и завершение регистрации
    """
    # Сохраняем город
    await state.update_data(city=message.text)

    # Получаем все данные
    data = await state.get_data()

    # Очищаем состояние
    await state.clear()

    # Выводим результат
    await message.answer(
        f"Регистрация завершена!\n\n"
        f"📝 Ваши данные:\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}\n"
        f"Город: {data['city']}"
    )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Используем MemoryStorage для хранения состояний
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
