
import re
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from db.models.models import User

from core.bot import bot
from bot.keyboards.check import *
from integrations.check_info import CheckApi
from datetime import datetime
from utils.check import *

from bot.templates.check import *

from bot.templates.qr import check_added_text, check_added_ikb

router = Router()
check_api = CheckApi()


# Обработка кнопки "Представительские расходы" и "Бизнес завтраки"
@router.callback_query(F.data == "entertainment")
@router.callback_query(F.data == "biznes_zavtrak_farmkruzhok")
async def handle_entertainment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    # Изменение сообщения
    message = await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=request_receipt_photo_with_qr,
        reply_markup=start_back_butt
    )

    # Сохраняем ID сообщения, чтобы удалить его в следующем шаге
    await state.update_data(original_message_id=message.message_id,
                            callback_data=callback.data)
    await state.set_state(Checkphoto.check)


# Обрабатываем фото чека
@router.message(Checkphoto.check, F.photo)
async def handle_photo(message: Message, state: FSMContext):

    # Получаем ID исходного сообщения, которое нужно удалить
    data = await state.get_data()
    original_message_id = data.get("original_message_id")

    # Удаляем старое сообщение
    if original_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=original_message_id)

    # Формируем ссылку
    photo_id = message.photo[-1].file_id
    file = await bot.get_file(photo_id)
    img_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
    msg = await message.answer(waiting_for_receipt_data)

    # Удаляем сообщение с фото
    await message.delete()

    # Получаем данные чека
    check_info = await check_api.info_by_img(img_url)
    try:
        result = await extract_receipt_data(check_info)
        request = await check_api.info_by_raw(fn=result['fn'], fp=result['fp'], fd=result['fd'], date=result['date'], sum=result['sum'], type=1)
        
        if request.get('error'):
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text=check_info_error_message,
                reply_markup=response_keyboard,
                parse_mode="HTML"
            )
            return

        result_text = format_receipt_text(result, 'проверка пройдена ✅')
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=result_text,
            reply_markup=confirm_receipt_butt,
            parse_mode="HTML"
        )

        # Обновляем состояние
        expense_type = await determine_expense_type((await state.get_data()).get('callback_data'))
        await state.update_data(answers_check=result, expense_type=expense_type, check_data=check_info)

    except KeyError:
        await bot.edit_message_text(
                chat_id=message.chat.id, 
                message_id=msg.message_id, 
                text=receipt_data_error,
                reply_markup=fill_check_butt
            )
        

# Если пользователь отправил не фото
@router.message(Checkphoto.check, F.text)
async def handle_non_photo(message: Message):
    await message.answer(request_receipt_photo_only)


# Обработка кнопки "Заполнить данные"
@router.callback_query(F.data == "fill_check")
async def fill_details(callback: CallbackQuery, state: FSMContext):

    await callback.answer()

    # Обновляем состояние для записи ответов с их счётчиком
    await state.update_data(current_question=0, answers_check={})
    msg = await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=questions['date'],
        reply_markup=check_back_butt
    )
    
    await state.set_state(Checkphoto.asking)
    await state.update_data(bot_message_id=msg.message_id,
                            bot_message_text=questions['date'])


# Обработка следующих вопросов по циклу
@router.message(Checkphoto.asking, F.text)
async def ask_next_question(message: Message, state: FSMContext):

    # Получаем текущий вопрос и ответ
    data = await state.get_data()
    current_question = data.get("current_question", 0)
    answers_check = data.get("answers_check", {})

    # Сообщения бота + id
    bot_message_id = data.get("bot_message_id")
    bot_message_text = data.get("bot_message_text")

    print(f'\n{data}\n')

    # Проверка на дату
    list_key = list(questions.keys())
    if list_key[current_question] == 'date':

        try:
            datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        except ValueError:
            await message.delete()

            # Чтобы избежать ошибку при повторной неправильной дате
            if bot_message_text != invalid_date_format:
                msg = await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=bot_message_id,
                    text=invalid_date_format,
                    reply_markup=check_back_butt
                )
                await state.update_data(bot_message_id=msg.message_id,
                                        bot_message_text=invalid_date_format)
            return
    
    # Проверка на правильную сумму
    elif list_key[current_question] == 'sum':
        sum_pattern = r'^\d+(\.\d{2})?$'

        # Если сумма не соответствует формату
        if not re.match(sum_pattern, message.text):
            await message.delete()

            # Чтобы избежать ошибку при повторной неправильной сумме
            error_text = "Неверный формат суммы. Пожалуйста, введите сумму в формате 157.00 (например, 157 рублей 00 копеек)."
            if bot_message_text != error_text:
                msg = await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=bot_message_id,
                    text=error_text,
                    reply_markup=check_back_butt
                )
                await state.update_data(bot_message_id=msg.message_id,
                                        bot_message_text=error_text)
            return
        
    # Проверка на правильный 'fn' (16 цифр)
    elif list_key[current_question] == 'fn':
        fn_pattern = r'^\d{16}$'

        # Если 'fn' не соответствует формату
        if not re.match(fn_pattern, message.text):
            await message.delete()

            # Чтобы избежать ошибку при повторной неправильной 'fn'
            error_text = "Неверный формат ФН. Пожалуйста, введите 16 цифр."
            if bot_message_text != error_text:
                msg = await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=bot_message_id,
                    text=error_text,
                    reply_markup=check_back_butt
                )
                await state.update_data(bot_message_id=msg.message_id,
                                        bot_message_text=error_text)
            return

    # Сохраняем ответ на текущий вопрос
    answers_check[list_key[current_question]] = message.text

    # Переход к следующему вопросу
    if current_question + 1 < len(questions):
        current_question += 1
        await state.update_data(current_question=current_question, answers_check=answers_check)

        # Удаляем сообщение с ответом пользователя
        await message.delete()

        # Редактирование сообщения
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message_id,
            text=questions[list_key[current_question]],
            reply_markup=check_back_butt
        )
        
    else:

        await message.delete()

        # Получаем все данные пользователя
        result = data['answers_check']
        date = datetime.strptime(result['date'], "%d.%m.%Y %H:%M")
        sum_total = float(data['answers_check']['sum'])
        fn = result['fn']
        fd = result['fd']
        fp = result['fp']

        # Сохраняем тип чека
        expense_type = await determine_expense_type((await state.get_data()).get('callback_data'))
        answers_check['expense_type'] = expense_type
        await state.update_data(answers_check=answers_check)

        result = {'date': date,
                  'fn': fn,
                  'fd': fd,
                  'fp': fp,
                  'sum': sum_total}
        
        # Проверяем чек
        request = await check_api.info_by_raw(fn=fn, fp=fp, fd=fd, date=date, sum=sum_total, type=1)
        if request.get('error'):
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=bot_message_id,
                text=check_info_error_message,
                reply_markup=response_keyboard,
                parse_mode="HTML"
            )

        else:
            result_text = format_receipt_text(result, 'проверка пройдена ✅')
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=bot_message_id,
                text=result_text,
                reply_markup=confirm_receipt_butt,
                parse_mode="HTML"
            )


# Обработка кнопки "Сформировать отчёт"
@router.callback_query(F.data == "generate_report_check")
async def generate_report_check(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    result = data.get("answers_check", {})
    print(result)
    result['sum'] = float(result['sum'])

    result_text = format_receipt_text(result, 'проверка не пройдена ❌')
    await callback.message.edit_text(
        text=result_text, 
        reply_markup=confirm_receipt_butt,
        parse_mode="HTML"
    )
    

# Обработка кнопки "✅ Подтвердить" или "⬅️ Назад" в ReportManagement
@router.callback_query(Checkphoto.check, F.data == "confirm_receipt")
@router.callback_query(Checkphoto.asking, F.data == "confirm_receipt")
@router.callback_query(F.data == "report_back")
async def back(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()

    if data.get("callback_data") in ('expense_hotel_services', 'expense_other', 'expense_taxi'):
        message = check_added_text
        button = check_added_ikb()
        data['expense_type'] = data['type']
    else:
        message = expense_added_success
        button = confirm_buttons

    # Сохраняем чек в БД
    user = await User.get(tg_id=callback.from_user.id)
    await save_check_to_db(data, user.id)

    print(f"\nСостояние: {data}\n")

    # Отправляем сообщение пользователю
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=message,
        reply_markup=button
    )


# Обработка кнопки "⬅️ Назад"
@router.callback_query(Checkphoto.asking, F.data == "check_back")
@router.callback_query(Checkphoto.check, F.data == "check_back")
async def back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await handle_entertainment(callback, state)  # Передаем callback и state
