from aiogram import F, Router
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
    await state.update_data(expense_type=callback.data)  # Сохраняем тип расхода
    await handle_entertainment(callback, state)


# Обработка кнопки "Прочее" (запрос ввода названия расхода)
@router.callback_query(F.data == "expense_other")
async def other_expense_selected(callback: CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Пожалуйста, введите название расхода:"
    )
    await state.set_state(BusinessTripState.waiting_for_expense_name)

    # Обработка чека
    await handle_entertainment(callback, state)
