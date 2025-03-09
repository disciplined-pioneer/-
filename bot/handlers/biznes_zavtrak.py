
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from core.bot import bot
from bot.keyboards.check import *
from integrations.check_info import CheckApi
from datetime import datetime

from bot.handlers.events import generate_documents_callback
from bot.keyboards.biznes_zavtrak import confirm_biznes_keyboard

router = Router()

# Список препаратов с префиксом "preparation_"
VALID_DRUGS = {
    "preparation_alpha_normix": "Альфа Нормикс",
    "preparation_alfazox": "Альфазокс",
    "preparation_cystiflux": "Цистифлюкс",
    "preparation_enterolactis": "Энтеролактис",
    "preparation_fibraksin": "Фибраксин",
    "preparation_fluxum": "Флюксум",
    "preparation_neoton": "Неотон",
    "preparation_vessel": "Вессел"
}

# Обработка кнопки для выбора препарата
@router.callback_query(F.data.startswith("preparation_"))
async def process_drug_selection(callback: CallbackQuery, state: FSMContext):

    # Сохраняем выбранный препарат в состоянии
    selected_drug = VALID_DRUGS.get(callback.data, "Неизвестный препарат")
    await state.update_data(selected_drug=selected_drug)

    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=f"🔍 Пожалуйста, подтвердите ваш выбор препарата: {selected_drug}",
        reply_markup=confirm_biznes_keyboard
    )


# Обработка кнопки "❌ Отменить выбор"
@router.callback_query(F.data == "change")
async def change_selection(callback: CallbackQuery, state: FSMContext):
    await generate_documents_callback(callback, state)
