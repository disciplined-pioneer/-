from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from core.bot import bot
from bot.keyboards.check import *

from bot.handlers.events import generate_documents_callback
from bot.keyboards.biznes_zavtrak import *
from utils.biznes_zavtrak import *
from bot.templates.biznes_zavtrak import *

router = Router()


# Обработка кнопки для выбора препарата
@router.callback_query(F.data.startswith("preparation_"))
async def process_drug_selection(callback: CallbackQuery, state: FSMContext):

    # Сохраняем выбранный препарат в состоянии
    selected_drug = VALID_DRUGS.get(callback.data, "Неизвестный препарат")
    await state.update_data(selected_drug=selected_drug)

    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=f"{confirm_selected_drug} {selected_drug}",
        reply_markup=confirm_biznes_keyboard
    )


# Обработка кнопки "❌ Отменить выбор"
@router.callback_query(F.data == "change")
async def change_selection(callback: CallbackQuery, state: FSMContext):
    await generate_documents_callback(callback, state)
