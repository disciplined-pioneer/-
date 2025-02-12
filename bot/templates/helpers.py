from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from settings import settings

incorrect_value_text = """
Не верный формат данных.
"""


def comeback_ikb(callback: str) -> InlineKeyboardMarkup:
    """
        Кнопка Назад
    :param callback: Колбэк в кнопке
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data=callback
        )
    )
    builder.adjust(1)
    return builder.as_markup()

