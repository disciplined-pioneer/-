from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.inline import start_options
from bot.templates import auth as tauth
from db.models.models import User

router = Router()


@router.message(F.text, tauth.AuthState.email)
async def get_email(message: Message, state: FSMContext):
    """
        Получить почту
    :param message: Message
    :param state: FSMContext
    """
    state_data = await state.get_data()
    await state_data['last_msg'].edit_text(tauth.send_snils_text)
    await message.delete()

    await state.update_data(email=message.text)
    await state.set_state(tauth.AuthState.snils)


@router.message(F.text, tauth.AuthState.snils)
async def get_snils(message: Message, state: FSMContext):
    """
        Получить снилс
    :param message: Message
    :param state: FSMContext
    """
    state_data = await state.get_data()

    if not message.text.isdigit():
        await message.delete()
        return await state_data['last_msg'].edit_text(
            tauth.error_text + tauth.send_snils_text
        )

    user = await User.get(
        email=state_data['email'],
        snils=int(message.text)
    )

    if user:
        await user.update(tg_id=message.from_user.id)
        await state_data['last_msg'].edit_text(
            text=tauth.success_text,
            reply_markup=start_options.as_markup()
        )
        await state.set_state(None)
    else:
        await state_data['last_msg'].edit_text(
            text=tauth.not_success_text + tauth.send_email_text,
        )
        await state.set_state(tauth.AuthState.email)

    await message.delete()
