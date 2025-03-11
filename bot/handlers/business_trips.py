from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from core.bot import bot

from bot.templates.business_trips import *
from bot.keyboards.business_trips import *

router = Router()


# Обработка кнопки для "Командировочных""
@router.callback_query(F.data == 'business_trips')
async def business_trips_start(callback: CallbackQuery, state: FSMContext):

    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=expense_type_message,
        reply_markup=consumption_type_keyboard
    )