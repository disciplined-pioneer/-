from datetime import datetime
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram import F, Router, types
from bot.keyboards.foreign_expenses import *
from bot.templates.foreign_expenses import *
from core.bot import bot
from db.models.models import Check, User


router = Router()


# Обработка начала ввода расхода в иностранной валюте
@router.callback_query(F.data == "expense_foreign_currency")
async def start_expense(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseState.choosing_type)
    
    # Отправляем новое сообщение и сохраняем его ID
    sent_message = await callback.message.edit_text(
        expense_type_massege,
        reply_markup=start
    )
    
    # Сохраняем message_id последнего сообщения бота
    await state.update_data(last_bot_message_id=sent_message.message_id)


# Обработка ввода типа расхода
@router.message(ExpenseState.choosing_type)
async def process_expense_type(message: types.Message, state: FSMContext):
    await state.update_data(expense_type=message.text)
    await state.set_state(ExpenseState.entering_foreign_amount)

    keyboard = await get_back_keyboard()
    await message.delete()  # Удаляем сообщение пользователя

    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message_id")

    # Редактируем предыдущее сообщение бота
    sent_message = await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=last_bot_message_id,
        text=expense_amount_message,
        reply_markup=keyboard
    )

    # Обновляем ID последнего сообщения бота
    await state.update_data(last_bot_message_id=sent_message.message_id)


# Обработка ввода суммы в иностранной валюте
@router.message(ExpenseState.entering_foreign_amount)
async def process_foreign_amount(message: types.Message, state: FSMContext):
    await state.update_data(foreign_amount=message.text)
    await state.set_state(ExpenseState.entering_rub_amount)

    keyboard = await get_back_keyboard()
    await message.delete()  # Удаляем сообщение пользователя

    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message_id")

    sent_message = await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=last_bot_message_id,
        text=rubles_amount_message,
        reply_markup=keyboard
    )

    await state.update_data(last_bot_message_id=sent_message.message_id)


@router.callback_query(F.data == "confirm_foreign")
async def confirm_expense(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = await get_finish_keyboard()

    # Добавляем в БД
    user = await User.get(tg_id=callback.from_user.id)
    await Check.create(
        user_id=user.id,
        date=datetime.utcnow(),
        sum=int(data['rub_amount'])*100,
        fn="default_fn",
        fd="default_fd",
        fp="default_fp",
        type="Расходы в иностранной валюте" + data['expense_type']
    )
    
    # Редактируем предыдущее сообщение вместо удаления
    await callback.message.edit_text(
        expense_added_message,
        reply_markup=keyboard
    )
    
    await state.clear()


# Обработка ввода суммы в рублях
@router.message(ExpenseState.entering_rub_amount)
async def process_rub_amount(message: types.Message, state: FSMContext):
    await state.update_data(rub_amount=message.text)
    await state.set_state(ExpenseState.confirming)

    keyboard = await get_confirm_keyboard()
    await message.delete()  # Удаляем сообщение пользователя

    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message_id")

    sent_message = await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=last_bot_message_id,
        text=generate_expense_report(data),
        reply_markup=keyboard
    )

    await state.update_data(last_bot_message_id=sent_message.message_id)


# Обработка нажатия кнопки "Назад"
@router.callback_query(F.data == "back_foreign")
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == ExpenseState.entering_foreign_amount:
        await state.set_state(ExpenseState.choosing_type)
        await callback.message.edit_text(expense_type_massege)

    elif current_state == ExpenseState.entering_rub_amount:
        keyboard = await get_back_keyboard()
        await state.set_state(ExpenseState.entering_foreign_amount)
        await callback.message.edit_text(
            expense_amount_message,
            reply_markup=keyboard
        )
