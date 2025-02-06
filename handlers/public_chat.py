import sqlite3
import logging
from aiogram import Router, F
from aiogram.types import Message

from config import settings


logging.basicConfig(level=logging.INFO)
PRIVATE_CHAT_ID = settings.PRIVATE_CHAT_ID
PUBLIC_CHAT_ID = settings.PUBLIC_CHAT_ID
PUBLIC_DB = settings.PUBLIC_DB
router = Router()


# Создаем таблицу для хранения маппинга
def init_db():
    conn = sqlite3.connect(PUBLIC_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_mapping (
                forwarded_message_id INTEGER PRIMARY KEY,
                original_message_id INTEGER
            )
        """)
        conn.commit()
        logging.info("Table 'message_mapping' created or already exists in database.")
    except Exception as e:
        logging.error(f"Failed to create table 'message_mapping': {e}")
    finally:
        conn.close()


# Сохраняем маппинг
def save_to_db(forwarded_message_id, original_message_id):
    conn = sqlite3.connect(PUBLIC_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO message_mapping (forwarded_message_id, original_message_id)
            VALUES (?, ?)
        """, (int(forwarded_message_id), int(original_message_id)))
        conn.commit()
        logging.info(f"Successfully saved to database: {forwarded_message_id} -> {original_message_id}")
    except Exception as e:
        logging.error(f"Failed to save to database: {e}")
    finally:
        conn.close()


# Получаем маппинг
def get_from_db(forwarded_message_id):
    conn = sqlite3.connect(PUBLIC_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT original_message_id FROM message_mapping WHERE forwarded_message_id = ?
        """, (int(forwarded_message_id),))
        result = cursor.fetchone()
        if result:
            logging.info(f"Found in database: {forwarded_message_id} -> {result[0]}")
            return result[0]
        else:
            logging.warning(f"No original message ID found in database for replied message ID: {forwarded_message_id}")
            return None
    except Exception as e:
        logging.error(f"Failed to fetch from database: {e}")
        return None
    finally:
        conn.close()


@router.message(F.chat.id == PUBLIC_CHAT_ID, F.text[-1] == '?')
async def forward_to_private_chat(message: Message):
    # Формируем ссылку на сообщение
    chat_username = message.chat.username
    if not chat_username:
        await message.bot.send_message(
            chat_id=PRIVATE_CHAT_ID,
            text="Новое сообщение не может быть преобразовано в ссылку."
        )
        return

    message_link = f"https://t.me/{chat_username}/{message.message_id}"
    notification_text = f"Новое сообщение: [ссылка]({message_link})"

    # Отправляем уведомление в приватный чат администраторов
    notification = await message.bot.send_message(
        chat_id=PRIVATE_CHAT_ID,
        text=notification_text,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

    # Пересылаем само сообщение
    forwarded_message = await message.forward(chat_id=PRIVATE_CHAT_ID)

    # Сохраняем связь между ID пересланного сообщения и ID оригинального сообщения
    save_to_db(forwarded_message.message_id, message.message_id)
    logging.info(f"Forwarded message: {forwarded_message.message_id}, Original message ID: {message.message_id}")


@router.message(F.chat.id == PRIVATE_CHAT_ID, F.reply_to_message)
async def reply_to_public_chat(message: Message):
    # Получаем ID сообщения, на которое ответил администратор
    replied_message_id = message.reply_to_message.message_id
    original_message_id = get_from_db(replied_message_id)

    if not original_message_id:
        logging.warning(f"No original message ID found in database for replied message ID: {replied_message_id}")
        return

    logging.info(f"Handling reply in private chat. Replied message ID: {replied_message_id}, Original message ID: {original_message_id}")
    # Отправляем ответ обратно в публичный чат
    if message.text:
        await message.bot.send_message(
            chat_id=PUBLIC_CHAT_ID,
            text=message.text,
            reply_to_message_id=original_message_id
        )
    elif message.photo:
        photo = message.photo[-1]
        await message.bot.send_photo(
            chat_id=PUBLIC_CHAT_ID,
            photo=photo.file_id,
            caption=message.caption,
            reply_to_message_id=original_message_id
        )
    elif message.video:
        await message.bot.send_video(
            chat_id=PUBLIC_CHAT_ID,
            video=message.video.file_id,
            caption=message.caption,
            reply_to_message_id=original_message_id
        )
