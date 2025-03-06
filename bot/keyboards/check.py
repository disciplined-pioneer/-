from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

fill_check_butt = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить данные", callback_data="fill_check")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="check_back")]
    ]
)

check_back_butt = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="check_back")]
    ]
)

start_back_butt = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ В начало", callback_data="start")]
    ]
)

confirm_receipt_butt = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_receipt")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="check_back")],
        [InlineKeyboardButton(text="↩️ Главное меню", callback_data="start")]
    ]
)

confirm_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📝 Сформировать в боте подтверждающие документы", callback_data="generate_documents")],
        [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip")]
    ]
)
