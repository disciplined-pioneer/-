from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

preparations_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Альфа Нормикс", callback_data="preparation_alpha_normix")],
        [InlineKeyboardButton(text="Альфазокс", callback_data="preparation_alfazox")],
        [InlineKeyboardButton(text="Цистифлюкс", callback_data="preparation_cystiflux")],
        [InlineKeyboardButton(text="Энтеролактис", callback_data="preparation_enterolactis")],
        [InlineKeyboardButton(text="Фибраксин", callback_data="preparation_fibraksin")],
        [InlineKeyboardButton(text="Флюксум", callback_data="preparation_fluxum")],
        [InlineKeyboardButton(text="Неотон", callback_data="preparation_neoton")],
        [InlineKeyboardButton(text="Вессел", callback_data="preparation_vessel")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="report_back")]
])

confirm_biznes_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✔️ Да, это правильный препарат", callback_data="confirm")],
        [InlineKeyboardButton(text="❌ Нет, изменить выбор", callback_data="change")]
    ])