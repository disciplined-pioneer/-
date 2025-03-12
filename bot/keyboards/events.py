from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

report_category_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1️⃣ Мероприятие", callback_data="report_event")],
        [InlineKeyboardButton(text="2️⃣ Подарки", callback_data="report_gifts")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="report_back")]
    ]
)

event_back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="question_event_back")]
    ]
)

confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_action")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_action")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="question_event_back")]
    ]
)

meeting_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔘 Добавить участника", callback_data="add_participant")],
        [InlineKeyboardButton(text="✅ Сформировать документы по встрече", callback_data="generate_documents_two")]
    ]
)


confirmation_keyboard_two = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Сформировать документы по встрече", callback_data="generate_documents_tree")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="report_back")]
    ]
)

# Кнопки для выбора компании сотрудника
def get_company_keyboard(another_company):
    company_selection_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ООО «Альфасигма Рус»", callback_data="company_alphasigma")],
            [InlineKeyboardButton(text=f"{another_company}", callback_data="company_meeting_choice")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="question_event_back")]
        ]
    )
    return company_selection_keyboard
