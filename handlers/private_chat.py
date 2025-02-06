import sqlite3
import logging
from aiogram import Router, F
from aiogram.types import Message

from config import settings
from filters.contain_word import ReplyToMessageContains


logging.basicConfig(level=logging.INFO)
PRIVATE_CHAT_ID = settings.PRIVATE_CHAT_ID
PRIVATE_DB = settings.PRIVATE_DB
router = Router()


# Создаем таблицу для хранения маппинга
def init_db():
    conn = sqlite3.connect(PRIVATE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_mapping (
            forwarded_message_id INTEGER PRIMARY KEY,
            user_id INTEGER
        )
    """)
    conn.commit()
    conn.close()


# Сохраняем маппинг
def save_to_db(forwarded_message_id, user_id):
    conn = sqlite3.connect(PRIVATE_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO message_mapping (forwarded_message_id, user_id)
            VALUES (?, ?)
        """, (int(forwarded_message_id), int(user_id)))
        conn.commit()
        logging.info(f"Successfully saved to database: {forwarded_message_id} -> {user_id}")
    except Exception as e:
        logging.error(f"Failed to save to database: {e}")
    finally:
        conn.close()


# Получаем маппинг
def get_from_db(forwarded_message_id):
    conn = sqlite3.connect(PRIVATE_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT user_id FROM message_mapping WHERE forwarded_message_id = ?
        """, (int(forwarded_message_id),))
        result = cursor.fetchone()
        if result:
            logging.info(f"Found in database: {forwarded_message_id} -> {result[0]}")
            return result[0]
        else:
            logging.warning(f"No user ID found in database for replied message ID: {forwarded_message_id}")
            return None
    except Exception as e:
        logging.error(f"Failed to fetch from database: {e}")
        return None
    finally:
        conn.close()


@router.message(F.chat.type == "private")
async def forward_user_message_to_private_chat(message: Message):
    # Формируем текст сообщения для администраторов
    user_name = message.from_user.full_name or message.from_user.username
    quoted_message = f"<blockquote>{message.text}</blockquote>"  # Цитата сообщения пользователя
    formatted_message = f"Сообщение от {user_name}:\n{quoted_message}"

    # Отправляем сообщение в приватный чат администраторов
    sent_message = await message.bot.send_message(
        chat_id=PRIVATE_CHAT_ID,
        text=formatted_message,
        parse_mode="HTML"
    )

    # Сохраняем связь между ID отправленного сообщения и ID пользователя
    save_to_db(sent_message.message_id, message.from_user.id)
    logging.info(f"Sent to private chat: {sent_message.message_id}, User ID: {message.from_user.id}")


@router.message(F.chat.id == PRIVATE_CHAT_ID, F.reply_to_message, ReplyToMessageContains(start="Сообщение от"))
async def reply_to_user_from_private_chat(message: Message):
    # Получаем ID сообщения, на которое ответил администратор
    replied_message_id = message.reply_to_message.message_id
    user_id = get_from_db(replied_message_id)

    if not user_id:
        logging.warning(f"No user ID found in database for replied message ID: {replied_message_id}")
        return

    logging.info(f"Handling reply in private chat. Replied message ID: {replied_message_id}, User ID: {user_id}")
    # Отправляем ответ пользователю в личные сообщения
    if message.text:
        await message.bot.send_message(chat_id=user_id, text=message.text)
    elif message.photo:
        photo = message.photo[-1]
        await message.bot.send_photo(
            chat_id=user_id,
            photo=photo.file_id,
            caption=message.caption
        )
    elif message.video:
        await message.bot.send_video(
            chat_id=user_id,
            video=message.video.file_id,
            caption=message.caption
        )
