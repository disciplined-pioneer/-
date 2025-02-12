from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State

from bot.handlers.expenses import edit_prev_msg
from bot.keyboards.inline import choose_country, to_start, daily_back1

router = Router()


class DailExpensesState(StatesGroup):
    """ Состояния """
    set_days = State()
    set_geo = State()
    calculate = State()


@router.callback_query(F.data == 'daily_back1')
async def go_to_prev_daily(call: CallbackQuery, state: FSMContext):
    await state.set_state(DailExpensesState.set_days)
    try:
        await call.message.edit_text('Укажите кол-во дней', reply_markup=daily_back1.as_markup())
    except Exception:
        await call.message.answer('Укажите кол-во дней', reply_markup=daily_back1.as_markup())


@router.callback_query(F.data == 'var1')
async def set_days(call: CallbackQuery, state: FSMContext):
    await state.set_state(DailExpensesState.set_days)
    msg = await call.message.edit_text('Укажите кол-во дней', reply_markup=daily_back1.as_markup())
    await state.update_data(
        delkeyboard=msg.message_id,
        expense_type='Суточные'
    )


@router.message(DailExpensesState.set_days)
async def set_geo(message: Message, state: FSMContext, bot: Bot):

    data = await state.get_data()
    await edit_prev_msg(data, bot, message, state)
    await state.update_data(delkeyboard=None)

    try:
        days = int(message.text)
    except ValueError:
        msg = await message.answer('Пожалуйста, укажите число', reply_markup=daily_back1.as_markup())
        await state.update_data(delkeyboard=msg.message_id)
        return
    await state.set_state(DailExpensesState.set_geo)
    await state.update_data(days=days)
    await message.answer('Укажите страну', reply_markup=choose_country.as_markup())


@router.message(DailExpensesState.set_geo)
async def set_country(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    await edit_prev_msg(data, bot, message, state)
    await state.update_data(delkeyboard=None)
    await message.answer('Укажите страну', reply_markup=choose_country.as_markup())


@router.callback_query(DailExpensesState.set_geo)
async def calculate_bill(call: CallbackQuery, state: FSMContext):
    await state.set_state(DailExpensesState.calculate)
    data = await state.get_data()
    days = data['days']

    k = 0
    if call.data == 'russian':
        k = 1445
    elif call.data == 'not_russian':
        k = 2750
    elif call.data == 'cycle_meeting':
        k = 100

    await call.message.edit_text(f'<u>Cумма к добавлению в расчет:</u><b> {k * days}</b> ₽', parse_mode="HTML", reply_markup=to_start.as_markup())