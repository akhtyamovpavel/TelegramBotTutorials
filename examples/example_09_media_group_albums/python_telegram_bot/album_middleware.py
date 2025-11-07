"""
Middleware для группировки Media Group сообщений (python-telegram-bot)
Решает проблему дублирования ответов при получении альбомов
"""

import asyncio
import logging
from typing import Dict, List, Optional

from telegram import Update
from telegram.ext import BaseHandler, ContextTypes

logger = logging.getLogger(__name__)


class AlbumCollector:
    """
    Класс для сбора и группировки альбомов

    Использование в python-telegram-bot:
    1. Создать экземпляр: collector = AlbumCollector()
    2. Обернуть обработчик: collector.wrap_handler(your_handler)
    """

    def __init__(self, latency: float = 0.3):
        """
        Args:
            latency: Время ожидания (сек) для сбора всех сообщений альбома
        """
        self.latency = latency
        self.album_data: Dict[str, List[Update]] = {}
        self.tasks: Dict[str, asyncio.Task] = {}

    def wrap_handler(self, handler):
        """
        Оборачивает обработчик для группировки альбомов

        Args:
            handler: Асинхронная функция-обработчик

        Returns:
            Обернутая функция-обработчик
        """
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
            message = update.effective_message

            # Если сообщение не содержит media_group_id, обрабатываем как обычно
            if not message or not message.media_group_id:
                return await handler(update, context)

            media_group_id = message.media_group_id

            # Если это первое сообщение альбома
            if media_group_id not in self.album_data:
                self.album_data[media_group_id] = []

            # Добавляем update в группу
            self.album_data[media_group_id].append(update)

            logger.debug(
                f"Получено сообщение {len(self.album_data[media_group_id])} "
                f"для альбома {media_group_id}"
            )

            # Отменяем предыдущую задачу ожидания (если была)
            if media_group_id in self.tasks:
                self.tasks[media_group_id].cancel()

            # Создаем новую задачу ожидания
            self.tasks[media_group_id] = asyncio.create_task(
                self._process_album(media_group_id, handler, context)
            )

        return wrapped

    async def _process_album(
        self,
        media_group_id: str,
        handler,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Обработка альбома после сбора всех сообщений

        Args:
            media_group_id: ID медиа-группы
            handler: Обработчик
            context: Контекст
        """
        try:
            # Ждем, пока все сообщения альбома будут получены
            await asyncio.sleep(self.latency)

            # Получаем все updates альбома
            updates = self.album_data.pop(media_group_id, [])

            if not updates:
                return

            logger.info(
                f"Обработка альбома {media_group_id} "
                f"из {len(updates)} сообщений"
            )

            # Добавляем список всех updates в контекст
            context.user_data['album_updates'] = updates

            # Вызываем обработчик только один раз
            # Передаем последний update как основной
            await handler(updates[-1], context)

            # Очищаем данные
            context.user_data.pop('album_updates', None)

        except asyncio.CancelledError:
            # Задача была отменена, игнорируем
            pass
        finally:
            # Удаляем задачу из словаря
            self.tasks.pop(media_group_id, None)


def get_album_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[List[Update]]:
    """
    Вспомогательная функция для получения всех сообщений альбома в обработчике

    Args:
        update: Update объект
        context: Context объект

    Returns:
        Список всех Update объектов альбома или None для одиночных сообщений
    """
    return context.user_data.get('album_updates', None)
