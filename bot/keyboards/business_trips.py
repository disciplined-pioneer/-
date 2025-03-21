from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

consumption_type_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Такси", callback_data="expense_taxi")],
        [InlineKeyboardButton(text="Услуги в отеле", callback_data="expense_hotel_services")],
        [InlineKeyboardButton(text="Прочее", callback_data="expense_other")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="start")]
    ]
)

back_trips_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_business_trips")]
    ]
)