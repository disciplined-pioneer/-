from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.templates import qr as tqr
from bot.templates import helpers as thelpers

router = Router()


@router.callback_query(F.data == "stationery")
async def stationery_menu(call: CallbackQuery, state: FSMContext):
    """
        Возврат к начальной позиции
    :param call:
    :param state:
    """
    last_msg = await call.message.edit_text(
        text=tqr.send_qr_text,
        reply_markup=thelpers.comeback_ikb('start')
    )
    await state.set_state(tqr.QRState.qr)
    await state.update_data(
        last_msg=last_msg,
        expense_type='Канцтовары'
    )
