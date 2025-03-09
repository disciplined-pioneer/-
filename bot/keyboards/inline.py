import datetime
from aiogram import types
from typing import Optional, Set
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


start_options = InlineKeyboardBuilder()
start_options.add(
    InlineKeyboardButton(text="Суточные", callback_data="var1"),
    InlineKeyboardButton(text="Бензин и прочие расходы по автомобилю", callback_data="var2"),
    InlineKeyboardButton(text="Канцтовары", callback_data="stationery"),
    InlineKeyboardButton(text="Представительские расходы", callback_data="entertainment"),
    InlineKeyboardButton(text="Бизнес-завтрак/Фармкружок", callback_data="biznes_zavtrak_farmkruzhok")
)
start_options.adjust(1, 1)

choose_country = InlineKeyboardBuilder()
choose_country.add(
    InlineKeyboardButton(text="РФ", callback_data="russian"),
    InlineKeyboardButton(text="Не РФ", callback_data="not_russian"),
    InlineKeyboardButton(text="Цикловое совещание", callback_data="cycle_meeting"),
    InlineKeyboardButton(text="⬅️ Назад ", callback_data="daily_back1"),
)
choose_country.adjust(1, 1, 1)

expenses = InlineKeyboardBuilder()
expenses.add(
    InlineKeyboardButton(text="Бензин", callback_data="ex1"),
    InlineKeyboardButton(text="Стеклоомыватель", callback_data="ex2"),
    InlineKeyboardButton(text="Парковка", callback_data="ex3"),
    InlineKeyboardButton(text="Мойка", callback_data="ex4"),
    InlineKeyboardButton(text="Прочее", callback_data="ex5"),
    InlineKeyboardButton(text="⬅️ Назад ", callback_data="start"),
)
expenses.adjust(1, 1, 1, 1, 1, 1)

to_start = InlineKeyboardBuilder()
to_start.add(types.InlineKeyboardButton(text="◀️ В начало", callback_data="start"))

fill_check = InlineKeyboardBuilder()
fill_check.add(types.InlineKeyboardButton(text="Заполнить данные", callback_data="fill_check"))


check_failed = InlineKeyboardBuilder()
check_failed.add(
    InlineKeyboardButton(text="Заполнить данные", callback_data="fill_check"),
    InlineKeyboardButton(text="Сформировать отчет", callback_data="make_report"),
    InlineKeyboardButton(text="◀️ В начало", callback_data="start")
)
check_failed.adjust(1, 1, 1)


daily_back1 = InlineKeyboardBuilder()
daily_back1.add(types.InlineKeyboardButton(text="⬅️ Назад ", callback_data="start"))

input_check_back1 = InlineKeyboardBuilder()
input_check_back1.add(types.InlineKeyboardButton(text="⬅️ Назад ", callback_data="input_check_back1"))

input_check_back2 = InlineKeyboardBuilder()
input_check_back2.add(types.InlineKeyboardButton(text="⬅️ Назад ", callback_data="input_check_back2"))

input_check_back3 = InlineKeyboardBuilder()
input_check_back3.add(types.InlineKeyboardButton(text="⬅️ Назад ", callback_data="input_check_back3"))

input_check_back4 = InlineKeyboardBuilder()
input_check_back4.add(types.InlineKeyboardButton(text="⬅️ Назад ", callback_data="input_check_back4"))

input_check_back5 = InlineKeyboardBuilder()
input_check_back5.add(types.InlineKeyboardButton(text="⬅️ Назад ", callback_data="input_check_back5"))

input_check_back6 = InlineKeyboardBuilder()
input_check_back6.add(types.InlineKeyboardButton(text="⬅️ Назад ", callback_data="input_check_back6"))