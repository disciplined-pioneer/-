from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_text = """
Выберите тип расхода
"""


def start_ikb() -> InlineKeyboardMarkup:
    """
        Добавление чека в отчет
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Суточные", callback_data="var1"),
        InlineKeyboardButton(text="Бензин и прочие расходы по автомобилю", callback_data="var2"),
        InlineKeyboardButton(text="Канцтовары", callback_data="stationery"),
        InlineKeyboardButton(text="Представительские расходы", callback_data="entertainment"),
        InlineKeyboardButton(text="Бизнес-завтрак/Фармкружок", callback_data="biznes_zavtrak_farmkruzhok"),
        InlineKeyboardButton(text="Командировочные", callback_data="business_trips"),
        InlineKeyboardButton(text="Расходы в иностранной валюте", callback_data="expense_foreign_currency")
    )
    builder.adjust(1)
    return builder.as_markup()
