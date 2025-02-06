import logging
from aiogram import Router, F
from aiogram.types import Message


router = Router()


@router.message(F.chat.type == "private", F.text == "/start")
async def welcome_message(message: Message):
    logging.info(f"User {message.from_user.id} started the bot.")
    user_name = message.from_user.full_name or message.from_user.username
    # Приветственное сообщение для пользователя
    await message.answer(
        f"Здравствуйте, {user_name}! 👋\n"
        "Я бот, который помогает администраторам отвечать на ваши вопросы.\n\n"
        "Напишите мне ваш вопрос, и я передам его администраторам!"
    )



# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
#
# @router.message(F.chat.type == "private", F.text == "/start")
# async def welcome_message(message: Message):
#     keyboard = ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="Задать вопрос")],
#             [KeyboardButton(text="Помощь")]
#         ],
#         resize_keyboard=True
#     )
#     await message.answer(
#         "Привет! 👋\n"
#         "Я бот, который помогает администраторам отвечать на ваши вопросы.\n"
#         "Нажмите 'Задать вопрос', чтобы отправить свой вопрос администраторам.",
#         reply_markup=keyboard
#     )
