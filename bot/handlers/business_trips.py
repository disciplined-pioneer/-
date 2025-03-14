from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.handlers.check import handle_entertainment
from core.bot import bot

from bot.templates.business_trips import *
from bot.keyboards.business_trips import *


router = Router()


# Обработка кнопки для "Командировочных"
@router.callback_query(F.data == "business_trips")
async def business_trips_start(callback: CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=expense_type_message,
        reply_markup=consumption_type_keyboard
    )


# Обработка выбора категории расхода (Такси / Услуги в отеле)
@router.callback_query(F.data.in_(["expense_taxi", "expense_hotel_services"]))
async def predefined_expense_selected(callback: CallbackQuery, state: FSMContext):

    if callback.data == 'expense_taxi':
        type = 'Такси'
    else:
        type = 'Услуги в отеле'

    data = await state.get_data()
    answers_check = data.get("answers_check", {})
    answers_check['type'] = type
    await state.update_data(answers_check=answers_check,
                            type=type)
    await handle_entertainment(callback, state)


# Обработка кнопки "Прочее"
@router.callback_query(F.data == "expense_other")
async def other_expense_selected(callback: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Пожалуйста, введите название расхода:"
    )
    await state.set_state(BusinessTripState.waiting_for_expense_name)

    # Сохраняем callback, чтобы использовать его позже
    await state.update_data(callback=callback)


# Обрабатываем ввод пользователя
@router.message(BusinessTripState.waiting_for_expense_name)
async def process_expense_name(message: types.Message, state: FSMContext):

    await message.delete()
    
    # Получаем сохранённый callback
    expense_name = message.text
    await state.set_state(None)

    data = await state.get_data()
    callback = data.get("callback")

    if callback:
        data = await state.get_data()
        answers_check = data.get("answers_check", {})
        answers_check['type'] = expense_name
        await state.update_data(answers_check=answers_check,
                                type=expense_name)
        await handle_entertainment(callback, state)