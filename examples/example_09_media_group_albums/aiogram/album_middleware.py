"""
Middleware для группировки Media Group сообщений (aiogram)
Решает проблему дублирования ответов при получении альбомов
"""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)


class AlbumMiddleware(BaseMiddleware):
    """
    Middleware для группировки сообщений Media Group

    Когда пользователь отправляет альбом (несколько фото), Telegram отправляет
    каждое фото как отдельное сообщение с одинаковым media_group_id.

    Этот middleware:
    - Группирует сообщения с одинаковым media_group_id
    - Передает в обработчик список всех сообщений альбома
    - Для одиночных сообщений работает как обычно
    """

    def __init__(self, latency: float = 0.3):
        """
        Args:
            latency: Время ожидания (сек) для сбора всех сообщений альбома
        """
        self.latency = latency
        self.album_data: Dict[str, List[Message]] = {}
        # Словарь для отслеживания задач ожидания
        self.tasks: Dict[str, asyncio.Task] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Основная логика middleware

        Args:
            handler: Следующий обработчик в цепочке
            event: Сообщение от пользователя
            data: Дополнительные данные
        """
        # Если сообщение не содержит media_group_id, обрабатываем как обычно
        if not event.media_group_id:
            return await handler(event, data)

        media_group_id = event.media_group_id

        # Если это первое сообщение альбома
        if media_group_id not in self.album_data:
            self.album_data[media_group_id] = []

        # Добавляем сообщение в группу
        self.album_data[media_group_id].append(event)

        logger.debug(
            f"Получено сообщение {len(self.album_data[media_group_id])} "
            f"для альбома {media_group_id}"
        )

        # Отменяем предыдущую задачу ожидания (если была)
        if media_group_id in self.tasks:
            self.tasks[media_group_id].cancel()

        # Создаем новую задачу ожидания
        self.tasks[media_group_id] = asyncio.create_task(
            self._process_album(media_group_id, handler, data)
        )

        # Возвращаем None, чтобы предотвратить дальнейшую обработку этого сообщения
        return None

    async def _process_album(
        self,
        media_group_id: str,
        handler: Callable,
        data: Dict[str, Any]
    ):
        """
        Обработка альбома после сбора всех сообщений

        Args:
            media_group_id: ID медиа-группы
            handler: Обработчик
            data: Дополнительные данные
        """
        try:
            # Ждем, пока все сообщения альбома будут получены
            await asyncio.sleep(self.latency)

            # Получаем все сообщения альбома
            messages = self.album_data.pop(media_group_id, [])

            if not messages:
                return

            logger.info(
                f"Обработка альбома {media_group_id} "
                f"из {len(messages)} сообщений"
            )

            # Добавляем список сообщений в data
            data['album'] = messages

            # Вызываем обработчик только один раз
            # Передаем последнее сообщение как основное
            await handler(messages[-1], data)

        except asyncio.CancelledError:
            # Задача была отменена, игнорируем
            pass
        finally:
            # Удаляем задачу из словаря
            self.tasks.pop(media_group_id, None)
