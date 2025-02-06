from aiogram import F
from aiogram.filters import BaseFilter
from aiogram.types import Message


class ReplyToMessageContains(BaseFilter):
    def __init__(self, start: str):
        self.start = start

    async def __call__(self, message: Message) -> bool:
        # Проверяем, является ли сообщение ответом
        if not message.reply_to_message or not message.reply_to_message.text:
            return False

        # Проверяем, содержит ли текст исходного сообщения ключевое слово
        return message.reply_to_message.text.startswith(self.start)
