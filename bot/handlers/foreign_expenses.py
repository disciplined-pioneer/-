import re
from datetime import datetime
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram import F, Router, types
from bot.keyboards.foreign_expenses import *
from bot.templates.foreign_expenses import *
from core.bot import bot
from db.models.models import Check, User


router = Router()

VALID_CURRENCIES = {"USD", "EUR", "GBP", "CNY", "JPY"}


# Обработка начала ввода расхода в иностранной валюте
@router.callback_query(F.data == "expense_foreign_currency")
async def start_expense(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseState.choosing_type)
    
    # Отправляем новое сообщение и сохраняем его ID
    sent_message = await callback.message.edit_text(
        "📝Пожалуйста, укажи тип расхода. Например: \"покупка\", \"услуга\", \"командировка\" и т.д. 💼",
        reply_markup=start
    )
    
    # Сохраняем message_id последнего сообщения бота
    await state.update_data(last_bot_message_id=sent_message.message_id)


# Обработка ввода типа расхода
@router.message(ExpenseState.choosing_type)
async def process_expense_type(message: types.Message, state: FSMContext):

    await message.delete() 
    await state.update_data(expense_type=message.text)
    await state.set_state(ExpenseState.entering_foreign_amount)

    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message_id")

    # Редактируем предыдущее сообщение бота
    sent_message = await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=last_bot_message_id,
        text="💵Введите сумму в валюте, в которой был произведен расход. Например: 100 USD, 50 EUR и т.д. 💱",
        reply_markup=await get_back_keyboard()
    )

    # Обновляем ID последнего сообщения бота
    await state.update_data(last_bot_message_id=sent_message.message_id)


# Обработка ввода суммы в иностранной валюте
@router.message(ExpenseState.entering_foreign_amount)
async def process_foreign_amount(message: types.Message, state: FSMContext):

    await message.delete()
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message_id")

    # Обработка на корректный ввод
    match = re.match(r"^(\d+(\.\d+)?)\s([A-Z]{3})$", message.text.upper())
    if not match or match.group(3) not in VALID_CURRENCIES:
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                text='❌ Некорректный формат. Используйте: "100 USD" или "50 EUR"',
                reply_markup=await get_back_keyboard()
            )
        except:
            pass

        return

    await state.update_data(foreign_amount=message.text.upper())
    await state.set_state(ExpenseState.entering_rub_amount)

    sent_message = await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=last_bot_message_id,
        text = (
            "💲 Сумма в рублях для включения в отчет:\n"
            "Пожалуйста, укажите сумму в рублях, которая будет включена в отчет ( Например: 7500.50 )\n"
            "Пересчитайте ее по курсу ЦБ на дату расхода 📊"
        ),
        reply_markup=await get_back_keyboard()
    )

    await state.update_data(last_bot_message_id=sent_message.message_id)


# Обработка ввода суммы в рублях
@router.message(ExpenseState.entering_rub_amount)
async def process_rub_amount(message: types.Message, state: FSMContext):

    await message.delete()
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message_id")

    # Проверка данных на корректность
    if not message.text.replace(".", "", 1).isdigit():
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                text="❌ Некорректная сумма. Введите число, например: 7500.50",
                reply_markup=await get_back_keyboard()
            )
        except:
            pass
        return

    await state.update_data(rub_amount=message.text)
    await state.set_state(ExpenseState.confirming)

    data = await state.get_data()
    sent_message = await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=last_bot_message_id,
        text=(
            f"📝Данные по расходу\n"
            f"Тип расхода: {data['expense_type']}\n"
            f"Сумма в валюте документа: {data['foreign_amount']}\n"
            f"Сумма в рублях для включения в отчет: {data['rub_amount']}\n\n"
            "Пожалуйста, проверьте информацию выше"
        ),
        reply_markup=await get_confirm_keyboard()
    )

    await state.update_data(last_bot_message_id=sent_message.message_id)


# Обработка кнопки "✅ Подтвердить"
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
        "🎉 Ваш расход успешно добавлен в отчет! 🎉\n\n"
        "Вы можете продолжить заполнение авансового отчета, добавив другие виды расходов.\n"
        "Хотите добавить новый тип расхода в существующий отчет?",
        reply_markup=keyboard
    )
    
    await state.clear()


# Обработка нажатия кнопки "Назад"
@router.callback_query(F.data == "back_foreign")
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == ExpenseState.entering_foreign_amount:
        await state.set_state(ExpenseState.choosing_type)
        await callback.message.edit_text(
            "📝Пожалуйста, укажи тип расхода. Например: \"покупка\", \"услуга\", \"командировка\" и т.д. 💼"
        )
    elif current_state == ExpenseState.entering_rub_amount:
        keyboard = await get_back_keyboard()
        await state.set_state(ExpenseState.entering_foreign_amount)
        await callback.message.edit_text(
            "💵Введите сумму в валюте, в которой был произведен расход. Например: 100 USD, 50 EUR и т.д. 💱",
            reply_markup=keyboard
        )
