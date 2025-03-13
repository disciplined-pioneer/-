from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

event_back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="report_back_two")]
    ]
)

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="question_present_back")]
    ]
)


gift_action_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔘 Добавить инф о получателе подарков", callback_data="add_gift_info")],
        [InlineKeyboardButton(text="✅ Сформировать документы по встрече", callback_data="gen_documents")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="question_present_back")]
    ]
)

conf_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_document")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_document")]
    ]
)

new_expense_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, добавить новый расход", callback_data="next_point")],
        [InlineKeyboardButton(text="❌ Нет, завершить отчет", callback_data="skip")]
    ]
)

gift_info_keyboard  = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔘 Добавить инф о получателе подарков", callback_data="add_gift_info")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="question_present_back")]
    ]
)