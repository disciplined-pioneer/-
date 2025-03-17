from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import start_options
from core.bot import bot
from db.models.models import User

from bot.templates import auth as tauth

router = Router()

# @router.message()
# async def cmd_start(message: Message, state: FSMContext):
#     """
#         Запуск бота
#     :param message:
#     :param state:
#     """
#     print(message.photo[-1].file_id)
#     # AgACAgIAAxkBAAM-Z6sfUzSD-9eJPIeYt6W5v_6j2UMAAgjtMRtpj1hJPWx7lSgtcSEBAAMCAAN5AAM2BA


@router.message(Command("start", ignore_case=True))
async def cmd_start(message: Message, state: FSMContext):
    """
        Запуск бота
    :param message:
    :param state:
    """

    await state.clear()

    if not await User.get(tg_id=message.from_user.id):
        last_msg = await message.answer(tauth.start_text)
        await message.delete()
        await state.set_state(tauth.AuthState.email)
        await state.update_data(last_msg=last_msg)
        return last_msg

    data = await state.get_data()
    report_id = data["report"] if 'report' in data else message.message_id - 90
    try:
        await bot.delete_messages(message.chat.id,
                                  list(range(max(1, message.message_id - 90, report_id + 1), message.message_id + 1)))
    except Exception:
        pass
    await state.clear()
    await state.update_data(report=report_id)
    await message.answer(text='Выберите тип расхода', reply_markup=start_options.as_markup())


@router.callback_query(F.data == "start")
async def return_to_menu(call: CallbackQuery, state: FSMContext):
    """
        Возврат к начальной позиции
    :param call:
    :param state:
    """
    await state.clear()
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        reply_markup=None)
    report_id = data["report"] if 'report' in data else call.message.message_id - 90
    try:
        await bot.delete_messages(
            call.message.chat.id,
            list(range(max(1, call.message.message_id - 90, report_id + 1),
                       call.message.message_id + 1))
        )
    except Exception:
        pass
    await state.clear()
    await state.update_data(report=report_id)
    await call.message.answer(text='Выберите тип расхода', reply_markup=start_options.as_markup())
