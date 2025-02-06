from aiogram import BaseMiddleware
from aiogram.types import Message
from config import PUBLIC_CHAT_ID, PRIVATE_CHAT_ID
import logging

logging.basicConfig(level=logging.INFO)

class MessageMarkerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        # Логируем входящее сообщение
        logging.info(f"Processing message: {event.text}, forward_from_chat={event.forward_from_chat}")

        # Проверяем, является ли сообщение пересланным
        if event.forward_from or event.forward_from_chat:
            # Если сообщение из публичного чата
            if event.forward_from_chat and event.forward_from_chat.id == PUBLIC_CHAT_ID:
                event.text = f"[PUBLIC_CHAT_REPLY] {event.text}" if event.text else "[PUBLIC_CHAT_REPLY]"
                logging.info("Added [PUBLIC_CHAT_REPLY] marker")
            # Если сообщение из личных сообщений пользователя
            elif event.forward_from:
                event.text = f"[PRIVATE_USER_REPLY] {event.text}" if event.text else "[PRIVATE_USER_REPLY]"
                logging.info("Added [PRIVATE_USER_REPLY] marker")
        else:
            logging.warning("Message is not forwarded")

        # Передаем управление дальше
        return await handler(event, data)
