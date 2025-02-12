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
        InlineKeyboardButton(
            text='Суточные',
            callback_data='var1'
        ),
        InlineKeyboardButton(
            text='Бензин и прочие расходы по автомобилю',
            callback_data='var2'
        ),
        InlineKeyboardButton(
            text='Канцтовары',
            callback_data='stationery'
        )
    )
    builder.adjust(1)
    return builder.as_markup()
