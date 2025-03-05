import re
# import cv2
# import io
# import numpy as np

from aiogram import F, Router, Bot
from decimal import Decimal
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
# from qreader import QReader

from integrations.check_info import NalogRuPython
from bot.keyboards.inline import expenses, to_start, fill_check, check_failed, input_check_back1, input_check_back2, \
    input_check_back3, input_check_back4, input_check_back5, input_check_back6

router = Router()
# qreader = QReader()


go_back = [
    'input_check_back1',
    'input_check_back2',
    'input_check_back3',
    'input_check_back4',
    'input_check_back5',
    'input_check_back6'
]


class ExpensesState(StatesGroup):
    """ Состояния """
    choose_expense = State()
    choose_other = State()
    load_check = State()


class InputCheckState(StatesGroup):
    """ Состояния """
    input_date = State()
    input_time = State()
    input_sum = State()
    input_fn = State()
    input_fd = State()
    input_fp = State()


def check_info(ticket):
    date = ticket["operation"]["date"]
    parsed_date = datetime.fromisoformat(date)
    formatted_date = parsed_date.strftime("%d.%m.%Y %H:%M")
    total = Decimal(ticket["operation"]["sum"]) / Decimal(100)
    nds = Decimal(ticket["ticket"]["document"]["receipt"]["nds18"]) / Decimal(100)
    dif = total - nds
    data = {
        "date": formatted_date,
        "fd": ticket["query"]["documentId"],
        "total": f"{total:.2f}",
        "nds": f"{nds:.2f}",
        "sum": f"{dif:.2f}"
    }
    print(data)

    formatted_text = (
        f"<b>Статус отчёта:</b> подтверждён ✅\n"
        f"<b>Дата чека:</b> {data['date']}\n"
        f"<b>ФД:</b> {data['fd']}\n"
        f"<b>Итого:</b> {data['total']}\n"
        f"<b>НДС:</b> {data['nds']}\n"
        f"<b>Сумма без НДС:</b> {data['sum']}\n"
    )

    return formatted_text


def check_fake_info(data):
    formatted_text = (
        f"<b>Статус отчёта:</b> не подтвержден ❌\n"
        f"<b>Дата чека:</b> {data['date']} {data['time']}\n"
        f"<b>ФД:</b> {data['fd']}\n"
        f"<b>Итого:</b> {data['sum']}\n"
    )

    return formatted_text


async def edit_prev_msg(data, bot: Bot, message, state: FSMContext):
    if data["delkeyboard"]:
        prev_msg = data["delkeyboard"]
        try:
            await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=prev_msg, reply_markup=None)
        except Exception as e:
            print(e)


async def cmd_clear(message: Message, bot: Bot, report_id) -> None:
    await bot.delete_messages(message.chat.id, list(range(max(1, message.message_id - 90, report_id + 1), message.message_id + 1)))


@router.callback_query(F.data == 'var2')
async def choose_expense(call: CallbackQuery, state: FSMContext):
    await state.set_state(ExpensesState.choose_expense)
    try:
        await call.message.edit_text('Выберите тип расхода', reply_markup=expenses.as_markup())
    except Exception:
        await call.message.answer('Выберите тип расхода', reply_markup=expenses.as_markup())

    await state.update_data(expense_type='Бензин и прочие расходы по автомобилю')


@router.callback_query(ExpensesState.choose_expense, F.data == 'ex5')
async def add_category(call: CallbackQuery, state: FSMContext):
    await state.update_data(ex_type=call.data)
    await state.set_state(ExpensesState.choose_other)
    try:
        await call.message.edit_text('Введите тип расхода')
    except Exception:
        await call.message.answer('Введите тип расхода')


@router.message(ExpensesState.choose_other)
async def handle_post(message: Message, state: FSMContext):
    await state.update_data(ex_type=message.text)
    await state.set_state(ExpensesState.load_check)
    await message.answer('Отправьте фото чека, чтобы на нем было видно QR-код')


@router.message(ExpensesState.choose_expense)
async def handle_post(message: Message, state: FSMContext):
    await state.set_state(ExpensesState.choose_expense)
    try:
        await message.edit_text('Выберите тип расхода', reply_markup=expenses.as_markup())
    except Exception:
        await message.answer('Выберите тип расхода', reply_markup=expenses.as_markup())


@router.callback_query(ExpensesState.choose_expense)
async def load_check(call: CallbackQuery, state: FSMContext):
    await state.update_data(ex_type=call.data)
    await state.set_state(ExpensesState.load_check)
    try:
        await call.message.edit_text('Отправьте фото чека, чтобы на нем было видно QR-код')
    except Exception:
        await call.message.answer('Отправьте фото чека, чтобы на нем было видно QR-код')


@router.callback_query(lambda call: call.data in go_back)
async def go_to_prev_check_input(call: CallbackQuery, state: FSMContext):
    msg = None
    if call.data == 'input_check_back1':
        await state.set_state(ExpensesState.load_check)
        try:
            msg = await call.message.edit_text('Отправьте фото чека, чтобы на нем было видно QR-код')
        except Exception:
            msg = await call.message.answer('Отправьте фото чека, чтобы на нем было видно QR-код')
    elif call.data == 'input_check_back2':
        await state.set_state(InputCheckState.input_date)
        try:
            msg = await call.message.edit_text('Введите дату с чека в формате: ДД.ММ.ГГГГ (например: 02.02.2020)',
                                  reply_markup=input_check_back1.as_markup())
        except Exception:
            msg = await call.message.answer('Введите дату с чека в формате: ДД.ММ.ГГГГ (например: 02.02.2020)',
                                         reply_markup=input_check_back1.as_markup())
    elif call.data == 'input_check_back3':
        await state.set_state(InputCheckState.input_time)
        try:
            msg = await call.message.edit_text('Введите время с чека в формате: ЧЧ:ММ (например: 15:30)',
                             reply_markup=input_check_back2.as_markup())
        except Exception:
            msg = await call.message.answer('Введите время с чека в формате: ЧЧ:ММ (например: 15:30)',
                                         reply_markup=input_check_back2.as_markup())
    elif call.data == 'input_check_back4':
        await state.set_state(InputCheckState.input_sum)
        try:
            msg = await call.message.edit_text('Введите сумму с чека например 157.00 (157 рублей 00 копеек)',
                             reply_markup=input_check_back3.as_markup())
        except Exception:
            msg = await call.message.answer('Введите сумму с чека например 157.00 (157 рублей 00 копеек)',
                                         reply_markup=input_check_back3.as_markup())
    elif call.data == 'input_check_back5':
        await state.set_state(InputCheckState.input_fn)
        try:
            msg = await call.message.edit_text('Введите ФН', reply_markup=input_check_back4.as_markup())
        except Exception:
            msg = await call.message.answer('Введите ФН', reply_markup=input_check_back4.as_markup())
    elif call.data == 'input_check_back6':
        await state.set_state(InputCheckState.input_fd)
        try:
            msg = await call.message.edit_text('Введите ФД', reply_markup=input_check_back5.as_markup())
        except Exception:
            msg = await call.message.answer('Введите ФД', reply_markup=input_check_back5.as_markup())
    if msg:
        await state.update_data(delkeyboard=msg.message_id)


@router.callback_query(ExpensesState.load_check, F.data == 'fill_check')
async def input_check_data(call: CallbackQuery, state: FSMContext):
    await state.set_state(InputCheckState.input_date)
    try:
        msg = await call.message.edit_text('Введите дату с чека в формате: ДД.ММ.ГГГГ (например: 02.02.2020)',
                                  reply_markup=input_check_back1.as_markup())
    except Exception:
        msg = await call.message.answer('Введите дату с чека в формате: ДД.ММ.ГГГГ (например: 02.02.2020)', reply_markup=input_check_back1.as_markup())
    await state.update_data(delkeyboard=msg.message_id)


@router.message(InputCheckState.input_date)
async def input_check_time(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await edit_prev_msg(data, bot, message, state)
    await state.update_data(delkeyboard=None)

    date_text = message.text.strip()

    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_text):
        msg = await message.reply("Неверный формат даты. Введите дату в формате: ДД.ММ.ГГГГ (например: 02.02.2020)", reply_markup=input_check_back1.as_markup())
        await state.update_data(delkeyboard=msg.message_id)
        return

    try:
        datetime.strptime(date_text, "%d.%m.%Y")
    except ValueError:
        msg = await message.reply("Некорректная дата. Проверьте правильность ввода и попробуйте снова.", reply_markup=input_check_back1.as_markup())
        await state.update_data(delkeyboard=msg.message_id)
        return

    await state.set_state(InputCheckState.input_time)
    await state.update_data(date=message.text)
    msg = await message.answer('Введите время с чека в формате: ЧЧ:ММ (например: 15:30)', reply_markup=input_check_back2.as_markup())
    await state.update_data(delkeyboard=msg.message_id)


@router.message(InputCheckState.input_time)
async def input_check_sum(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await edit_prev_msg(data, bot, message, state)
    await state.update_data(delkeyboard=None)

    time_text = message.text.strip()

    if not re.match(r"^\d{2}:\d{2}$", time_text):
        msg = await message.reply("Неверный формат времени. Введите время в формате: ЧЧ:ММ (например: 15:30)", reply_markup=input_check_back2.as_markup())
        await state.update_data(delkeyboard=msg.message_id)
        return

    try:
        datetime.strptime(time_text, "%H:%M")
    except ValueError:
        msg = await message.reply("Некорректное время. Проверьте правильность ввода и попробуйте снова.", reply_markup=input_check_back2.as_markup())
        await state.update_data(delkeyboard=msg.message_id)
        return

    await state.set_state(InputCheckState.input_sum)
    await state.update_data(time=message.text)
    msg = await message.answer('Введите сумму с чека например 157.00 (157 рублей 00 копеек)', reply_markup=input_check_back3.as_markup())
    await state.update_data(delkeyboard=msg.message_id)


@router.message(InputCheckState.input_sum)
async def input_check_fn(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await edit_prev_msg(data, bot, message, state)
    await state.update_data(delkeyboard=None)

    sum_text = message.text.strip()

    try:
        sum_value = float(sum_text)
        if sum_value < 0:
            raise ValueError("Сумма не может быть отрицательной. Повторите ввод")
        formatted_sum = f"{sum_value:.2f}"

    except ValueError:
        msg = await message.reply(
            "Некорректный формат суммы. Введите сумму в виде целого числа или с двумя знаками после точки (например: 157 или 157.00).", reply_markup=input_check_back3.as_markup())
        await state.update_data(delkeyboard=msg.message_id)
        return

    await state.set_state(InputCheckState.input_fn)
    await state.update_data(sum=formatted_sum)
    msg = await message.answer('Введите ФН', reply_markup=input_check_back4.as_markup())
    await state.update_data(delkeyboard=msg.message_id)


@router.message(InputCheckState.input_fn)
async def input_check_fd(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await edit_prev_msg(data, bot, message, state)
    await state.update_data(delkeyboard=None)

    fn_text = message.text.strip()

    if not (fn_text.isdigit() and len(fn_text) == 16):
        msg = await message.reply("Некорректный формат ФН. Убедитесь, что он состоит ровно из 16 цифр.", reply_markup=input_check_back4.as_markup())
        await state.update_data(delkeyboard=msg.message_id)
        return

    await state.set_state(InputCheckState.input_fd)
    await state.update_data(fn=message.text)
    msg = await message.answer('Введите ФД', reply_markup=input_check_back5.as_markup())
    await state.update_data(delkeyboard=msg.message_id)


@router.message(InputCheckState.input_fd)
async def input_check_fp(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await edit_prev_msg(data, bot, message, state)
    await state.update_data(delkeyboard=None)

    fd_text = message.text.strip()

    if not fd_text.isdigit():
        msg = await message.reply("Некорректный формат ФД. Убедитесь, что он состоит из цифр.", reply_markup=input_check_back5.as_markup())
        await state.update_data(delkeyboard=msg.message_id)
        return

    await state.set_state(InputCheckState.input_fp)
    await state.update_data(fd=message.text)
    msg = await message.answer('Введите ФП', reply_markup=input_check_back6.as_markup())
    await state.update_data(delkeyboard=msg.message_id)


@router.message(InputCheckState.input_fp)
async def input_check_load_data(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await edit_prev_msg(data, bot, message, state)
    await state.update_data(delkeyboard=None)

    fp_text = message.text.strip()

    if not fp_text.isdigit():
        msg = await message.reply("Некорректный формат ФП. Убедитесь, что он состоит из цифр.", reply_markup=input_check_back6.as_markup())
        await state.update_data(delkeyboard=msg.message_id)
        return

    await state.update_data(fp=message.text)
    await state.set_state(ExpensesState.load_check)
    data = await state.get_data()

    date_obj = datetime.strptime(data['date'], "%d.%m.%Y")
    time_obj = datetime.strptime(data['time'], "%H:%M").time()

    combined_datetime = datetime.combine(date_obj.date(), time_obj)
    iso_format = combined_datetime.strftime("%Y%m%dT%H%M")

    sum_total = data['sum']
    fn = data['fn']
    fd = data['fd']
    fp = data['fp']
    query = f"t={iso_format}&s={sum_total}&fn={fn}&i={fd}&fp={fp}&n=1"
    print(query)
    try:
        client = NalogRuPython()
        ticket = client.get_ticket(query)
        ans = check_info(ticket)
        report_id = data["report"] if 'report' in data else message.message_id - 90
        await cmd_clear(message, bot, report_id)
        report = await message.answer(ans, parse_mode="HTML", reply_markup=to_start.as_markup())
        await state.update_data(report=report.message_id)

    except Exception as e:
        try:
            await message.edit_text("Не удалось получить информацию о чеке\nПроверьте введенные данные и попробуйте снова\nЛибо можете сформировать отчёт на основе введённых данных", reply_markup=check_failed.as_markup())
        except Exception:
            await message.answer(
                "Не удалось получить информацию о чеке\nПроверьте введенные данные и попробуйте снова\nЛибо можете сформировать отчёт на основе введённых данных",
                reply_markup=check_failed.as_markup())
        print(e)
        return


@router.callback_query(ExpensesState.load_check, F.data == 'make_report')
async def make_fake_report(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    ans = check_fake_info(data)
    report_id = data["report"] if 'report' in data else call.message.message_id - 90
    await cmd_clear(call.message, bot, report_id)
    try:
        report = await call.message.edit_text(ans, parse_mode="HTML", reply_markup=to_start.as_markup())
        await state.update_data(report=report.message_id)
    except Exception:
        report = await call.message.answer(ans, parse_mode="HTML", reply_markup=to_start.as_markup())
        await state.update_data(report=report.message_id)


@router.message(ExpensesState.load_check)
async def handle_post(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer('Неподдерживаемый формат, пожалуйста, отправьте фото')
        return

    # loading = await message.answer('Пожалуйста подождите, идет получение данных о чеке...')
    # check_photo = message.photo[-1]
    # bot = message.bot
    # photo_bytes = io.BytesIO()
    # await bot.download(check_photo.file_id, photo_bytes)
    # photo_bytes.seek(0)
    # nparr = np.frombuffer(photo_bytes.read(), np.uint8)
    # image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # reader = QReader()
    # decoded_text = reader.detect_and_decode(image=image)
    #
    # if not decoded_text or not decoded_text[0]:
    #     try:
    #         await message.edit_text("QR-код не распознан.\nМожете заполнить данные о чеке самостоятельно", reply_markup=fill_check.as_markup())
    #     except Exception:
    #         await bot.delete_message(chat_id=loading.chat.id, message_id=loading.message_id)
    #         await message.answer("QR-код не распознан.\nМожете заполнить данные о чеке самостоятельно", reply_markup=fill_check.as_markup())
    #     finally:
    #         return
    # else:
    #     try:
    #         client = NalogRuPython()
    #         ticket = client.get_ticket(decoded_text[0])
    #         ans = check_info(ticket)
    #         await bot.delete_message(chat_id=loading.chat.id, message_id=loading.message_id)
    #         data = await state.get_data()
    #         report_id = data["report"] if 'report' in data else message.message_id - 90
    #         await cmd_clear(message, bot, report_id)
    #         report = await message.answer(ans, parse_mode="HTML", reply_markup=to_start.as_markup())
    #         await state.update_data(report=report.message_id)
    #     except Exception as e:
    #         try:
    #             await message.edit_text("Не удалось получить информацию о чеке\nМожете заполнить данные о чеке самостоятельно", reply_markup=fill_check.as_markup())
    #         except Exception:
    #             await bot.delete_message(chat_id=loading.chat.id, message_id=loading.message_id)
    #             await message.answer("Не удалось получить информацию о чеке\nМожете заполнить данные о чеке самостоятельно", reply_markup=fill_check.as_markup())
    #         finally:
    #             print(e)
    #             return
