import asyncio
import logging
import sys
from os import getenv
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, TelegramObject

from database import Database

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

TOKEN = getenv("BOT_TOKEN")
router = Router()


# Middleware для передачи БД в обработчики
class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, database: Database):
        self.database = database

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Добавляем объект БД в данные
        data["db"] = self.database
        return await handler(event, data)


# Состояния для регистрации
class RegistrationForm(StatesGroup):
    name = State()
    age = State()
    city = State()


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext, db: Database) -> None:
    """
    Начало регистрации + добавление в БД
    """
    # Добавляем пользователя в БД
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    await state.set_state(RegistrationForm.name)
    await message.answer(
        "Привет! Давайте заполним ваш профиль.\n"
        "Как вас зовут?\n\n"
        "Команды:\n"
        "/cancel - отменить\n"
        "/profile - посмотреть профиль\n"
        "/stats - статистика бота"
    )


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Отмена регистрации
    """
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.")
        return

    await state.clear()
    await message.answer("Регистрация отменена.")


@router.message(Command("profile"))
async def show_profile(message: Message, db: Database) -> None:
    """
    Показать профиль пользователя
    """
    user = await db.get_user(message.from_user.id)

    if not user or not user['name']:
        await message.answer("У вас еще нет профиля. Используйте /start для регистрации.")
        return

    await message.answer(
        f"👤 Ваш профиль:\n\n"
        f"Имя: {user['name']}\n"
        f"Возраст: {user['age']}\n"
        f"Город: {user['city']}\n"
        f"Зарегистрирован: {user['created_at']}"
    )


@router.message(Command("stats"))
async def show_stats(message: Message, db: Database) -> None:
    """
    Показать статистику бота
    """
    count = await db.get_all_users_count()
    await message.answer(f"📊 Статистика:\n\nВсего пользователей: {count}")


@router.message(RegistrationForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    """
    Обработка имени
    """
    await state.update_data(name=message.text)
    await state.set_state(RegistrationForm.age)
    await message.answer(f"Приятно познакомиться, {message.text}!\nСколько вам лет?")


@router.message(RegistrationForm.age)
async def process_age(message: Message, state: FSMContext) -> None:
    """
    Обработка возраста
    """
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите возраст числом.")
        return

    age = int(message.text)
    if age < 0 or age > 120:
        await message.answer("Введите корректный возраст (от 0 до 120).")
        return

    await state.update_data(age=age)
    await state.set_state(RegistrationForm.city)
    await message.answer("В каком городе вы живете?")


@router.message(RegistrationForm.city)
async def process_city(message: Message, state: FSMContext, db: Database) -> None:
    """
    Обработка города и сохранение в БД
    """
    await state.update_data(city=message.text)
    data = await state.get_data()

    # Сохраняем профиль в БД
    await db.update_user_profile(
        user_id=message.from_user.id,
        name=data['name'],
        age=data['age'],
        city=data['city']
    )

    await state.clear()

    await message.answer(
        f"✅ Регистрация завершена!\n\n"
        f"📝 Ваши данные сохранены в базе данных:\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}\n"
        f"Город: {data['city']}\n\n"
        f"Используйте /profile для просмотра профиля"
    )


async def main() -> None:
    # Инициализируем БД
    db = Database()
    await db.create_tables()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем middleware
    dp.message.middleware(DatabaseMiddleware(db))

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
