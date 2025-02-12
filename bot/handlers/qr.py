import os
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot.templates import commands as tcommands
from bot.templates import helpers as thelpers
from bot.templates import qr as tqr
from core.bot import bot
from db.models.models import Check, User
from integrations.check_info import CheckApi
from utils.check import get_nds
from utils.report import create_report

router = Router()
check_api = CheckApi()


@router.callback_query(F.data == 'send_qr')
async def send_qr(call: CallbackQuery, state: FSMContext):
    """
        Запуск бота
    :param call: CallbackQuery
    :param state: FSMContext
    """
    state_data = await state.get_data()
    await state.clear()
    last_msg = await call.message.edit_text(
        text=tqr.send_qr_text,
        reply_markup=thelpers.comeback_ikb('start')
    )
    await state.set_state(tqr.QRState.qr)
    await state.update_data(
        last_msg=last_msg,
        expense_type=state_data['expense_type']
    )


@router.message(tqr.QRState.qr)
async def get_qr(message: Message, state: FSMContext):
    """
        Получени qr
    :param message: Message
    :param state: FSMContext
    """
    await message.delete()
    state_data = await state.get_data()

    if not message.photo:
        return state_data['last_msg'].edit_text(
            text=tqr.incorrect_type_text,
            reply_markup=thelpers.comeback_ikb('start')
        )

    await state_data['last_msg'].edit_text(tqr.wait_text)

    file = await bot.get_file(message.photo[-1].file_id)
    img_url = f'https://api.telegram.org/file/bot{bot.token}/{file.file_path}'
    check_data = await check_api.info_by_img(img_url)
    await state.update_data(check_data=check_data)

    if check_data.get('error'):
        return await state_data['last_msg'].edit_text(
            text=tqr.incorrect_qr_text,
            reply_markup=tqr.manual_filling_ikb()
        )

    await state_data['last_msg'].edit_text(
        text=tqr.check_added_text,
        reply_markup=tqr.check_added_ikb()
    )


@router.callback_query(F.data == 'check_manual_filling')
async def manual_filling(call: CallbackQuery, state: FSMContext):
    """
        Ручное заполнение
    :param call: CallbackQuery
    :param state: FSMContext
    """
    state_data = await state.get_data()
    await state.clear()
    last_msg = await call.message.edit_text(
        text=tqr.send_date_text,
        reply_markup=thelpers.comeback_ikb('send_qr')
    )
    await state.set_state(tqr.QRState.date)
    await state.update_data(
        last_msg=last_msg,
        expense_type=state_data['expense_type']
    )


@router.message(F.text, tqr.QRState.date)
async def get_date(msg: Message, state: FSMContext):
    """
        Получить дату
    :param msg: Message
    :param state: FSMContext
    """
    await msg.delete()
    state_data = await state.get_data()

    try:
        date = datetime.strptime(
            msg.text,
            '%d.%m.%y %H:%M'
        )
        await state.update_data(date=date)

    except:
        return await state_data['last_msg'].edit_text(
            text=thelpers.incorrect_value_text + tqr.send_date_text,
            reply_markup=thelpers.comeback_ikb('send_qr')
        )

    await state_data['last_msg'].edit_text(
        text=tqr.send_sum_text,
        reply_markup=thelpers.comeback_ikb('send_qr')
    )
    await state.set_state(tqr.QRState.sum)


@router.message(F.text, tqr.QRState.sum)
async def get_sum(msg: Message, state: FSMContext):
    """
        Получить сумму
    :param msg: Message
    :param state: FSMContext
    """
    await msg.delete()
    state_data = await state.get_data()

    try:
        await state.update_data(sum=int(float(msg.text) * 100))

    except:
        return await state_data['last_msg'].edit_text(
            text=thelpers.incorrect_value_text + tqr.send_sum_text,
            reply_markup=thelpers.comeback_ikb('send_qr')
        )

    await state_data['last_msg'].edit_text(
        text=tqr.send_fn_text,
        reply_markup=thelpers.comeback_ikb('send_qr')
    )
    await state.set_state(tqr.QRState.fn)


@router.message(F.text, tqr.QRState.fn)
async def get_fn(msg: Message, state: FSMContext):
    """
        Получить ФН
    :param msg: Message
    :param state: FSMContext
    """
    await msg.delete()
    state_data = await state.get_data()

    try:
        fn = int(msg.text)
        await state.update_data(fn=msg.text)

    except:
        return await state_data['last_msg'].edit_text(
            text=thelpers.incorrect_value_text + tqr.send_fn_text,
            reply_markup=thelpers.comeback_ikb('send_qr')
        )

    await state_data['last_msg'].edit_text(
        text=tqr.send_fd_text,
        reply_markup=thelpers.comeback_ikb('send_qr')
    )
    await state.set_state(tqr.QRState.fd)


@router.message(F.text, tqr.QRState.fd)
async def get_fd(msg: Message, state: FSMContext):
    """
        Получить ФД
    :param msg: Message
    :param state: FSMContext
    """
    await msg.delete()
    state_data = await state.get_data()

    try:
        fd = int(msg.text)
        await state.update_data(fd=msg.text)

    except:
        return await state_data['last_msg'].edit_text(
            text=thelpers.incorrect_value_text + tqr.send_fd_text,
            reply_markup=thelpers.comeback_ikb('send_qr')
        )

    await state_data['last_msg'].edit_text(
        text=tqr.send_fp_text,
        reply_markup=thelpers.comeback_ikb('send_qr')
    )
    await state.set_state(tqr.QRState.fp)


@router.message(F.text, tqr.QRState.fp)
async def get_fp(msg: Message, state: FSMContext):
    """
        Получить ФД
    :param msg: Message
    :param state: FSMContext
    """
    await msg.delete()
    state_data = await state.get_data()

    try:
        fp = int(msg.text)
        await state.update_data(fp=msg.text)

    except:
        return await state_data['last_msg'].edit_text(
            text=thelpers.incorrect_value_text + tqr.send_fp_text,
            reply_markup=thelpers.comeback_ikb('send_qr')
        )

    check_data = await check_api.info_by_raw(
        date=state_data['date'],
        sum=state_data['sum'],
        fn=state_data['fn'],
        fd=state_data['fd'],
        fp=fp
    )

    if check_data.get('error'):
        await state.set_state(tqr.QRState.date)
        return await state_data['last_msg'].edit_text(
            text=tqr.incorrect_data_text,
            reply_markup=tqr.incorrect_data_ikb()
        )

    nds_sum = get_nds(check_data)
    await state_data['last_msg'].edit_text(
        text=tqr.success_text.format(
            date=state_data['date'].strftime("%d.%m.%y %H:%M"),
            fd=state_data['fd'],
            sum=state_data['sum'],
            nds=(nds_sum / state_data['sum'] * 100) * 100,
            sum_without_nds=state_data['sum'] - nds_sum,
        ),
        reply_markup=tqr.success_ikb()
    )
    await state.set_state(None)
    await state.update_data(check_data=check_data)


@router.callback_query(F.data == 'add_check')
async def confirm_check(call: CallbackQuery, state: FSMContext):
    """
        Подтвердить чек
    :param call: CallbackQuery
    :param state: FSMContext
    """
    state_data = await state.get_data()
    user = await User.get(tg_id=call.from_user.id)

    if state_data.get('check_data'):
        await Check.create(
            user_id=user.id,
            date=datetime.strptime(
                state_data['check_data']['data']['json']['dateTime'],
                '%Y-%m-%dT%H:%M:%S'
            ),
            fd=state_data['check_data']['request']['manual']['fd'],
            fn=state_data['check_data']['request']['manual']['fn'],
            fp=state_data['check_data']['request']['manual']['fp'],
            kkt_reg_id=state_data['check_data']['data']['json'].get('kktRegId'),
            inn=state_data['check_data']['data']['json'].get('userInn'),
            salesman=state_data['check_data']['data']['json'].get('user'),
            operator=state_data['check_data']['data']['json'].get('operator'),
            address=state_data['check_data']['data']['json']['metadata'].get('address'),
            sum=state_data['check_data']['data']['json'].get('totalSum'),
            nds=get_nds(state_data['check_data']),
            type=state_data['expense_type']
        )

    else:
        await Check.create(
            user_id=user.id,
            date=state_data['date'],
            sum=state_data['sum'],
            fn=state_data['fn'],
            fd=state_data['fd'],
            fp=state_data['fp'],
            type=state_data['expense_type']
        )

    try:
        await call.message.edit_text(
            text=tcommands.start_text,
            reply_markup=tcommands.start_ikb()
        )
    except:
        pass
    await state.clear()


@router.callback_query(F.data == 'create_report')
async def create_report_call(call: CallbackQuery, state: FSMContext):
    """
        Подтвердить чек
    :param call: CallbackQuery
    :param state: FSMContext
    """
    await confirm_check(call, state)
    path = await create_report(call.from_user.id)

    await call.message.delete()
    await call.message.answer_document(
        caption=tqr.create_report_text,
        document=FSInputFile(path)
    )
    await call.message.answer(
        text=tcommands.start_text,
        reply_markup=tcommands.start_ikb()
    )

    os.remove(path)
    await state.clear()


@router.callback_query(F.data == 'confirm_incorrect_data')
async def confirm_incorrect_data(call: CallbackQuery, state: FSMContext):
    """
        Подтвердить чек
    :param call: CallbackQuery
    :param state: FSMContext
    """
    state_data = await state.get_data()
    await call.message.edit_text(
        text=tqr.not_success_text.format(
            date=state_data['date'].strftime("%d.%m.%y %H:%M"),
            fd=state_data['fd'],
            sum=state_data['sum']
        ),
        reply_markup=tqr.not_success_ikb()
    )
