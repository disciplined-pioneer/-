
import re
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.bot import bot
from bot.keyboards.check import *
from integrations.check_info import CheckApi
from datetime import datetime

from bot.templates.check import *

router = Router()
check_api = CheckApi()


# Функция для вывода успешного результата обработки чека
def format_receipt_text(result: dict) -> str:
    sum_total = str(result['sum']) if '.00' in result['sum'] else result['sum'] + '.00'

    return (
        f"Статус чека: <b>проверка пройдена✅</b>\n"
        f"Дата чека: <b>{result['date']}</b>\n"
        f"ФН: <b>{result['fn']}</b>\n"
        f"ФД: <b>{result['fd']}</b>\n"
        f"ФП: <b>{result['fp']}</b>\n"
        f"Итого: <b>{sum_total}</b>\n"
    )


# Список вопросов для пользователя
questions = {
    'date': "Введите дату с чека в формате: ДД.ММ.ГГГГ ДД:ММ (например: 02.02.2020 15:30)",
    'sum': "Введите сумму с чека например 157.00 (157 рублей 00 копеек)",
    'fn': "Введите ФН",
    'fd': "Введите ФД",
    'fp': "Введите ФП"
}


# Обработка кнопки "Представительские расходы"
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
    await state.update_data(original_message_id=message.message_id, callback_data=callback.data)
    await state.set_state(Check_photo.check)


# Обрабатываем фото чека
@router.message(Check_photo.check, F.photo)
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
        data = check_info["request"]["manual"]
        iso_format = datetime.strptime(check_info["data"]["json"]["dateTime"], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%dT%H%M")
        fn = data["fn"]
        fd = data["fd"]
        fp = data["fp"]
        sum_total = data["sum"]

        result = {'date': iso_format,
                'fn': fn,
                'fd': fd,
                'fp': fp,
                'sum': sum_total}
        

        #query = f"t={iso_format}&s={sum_total}&fn={fn}&i={fd}&fp={fp}&n=1"
        result_text = format_receipt_text(result)
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=result_text,
            reply_markup=confirm_receipt_butt,
            parse_mode="HTML"
        )
        await state.update_data(answers_check=result)

    except KeyError:
        await bot.edit_message_text(
                chat_id=message.chat.id, 
                message_id=msg.message_id, 
                text=receipt_data_error,
                reply_markup=fill_check_butt
            )
        

# Если пользователь отправил не фото
@router.message(Check_photo.check, F.text)
async def handle_non_photo(message: Message):
    await message.answer(request_receipt_photo_only)


# Обработка кнопки "Заполнить данные"
@router.callback_query(Check_photo.check, F.data == "fill_check")
async def fill_details(callback: CallbackQuery, state: FSMContext):

    await state.clear()  # Очищаем старое состояние
    await callback.answer()

    # Обновляем состояние для записи ответов с их счётчиком
    await state.update_data(current_question=0, answers_check={})
    msg = await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=questions['date'],
        reply_markup=check_back_butt
    )
    
    await state.set_state(Check_photo.asking)
    await state.update_data(bot_message_id=msg.message_id,
                            bot_message_text=questions['date'])


# Обработка следующих вопросов по циклу
@router.message(Check_photo.asking, F.text)
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
        iso_format = datetime.strptime(result['date'], "%d.%m.%Y %H:%M").strftime("%Y%m%dT%H%M")
        sum_total = str(result['sum']) if '.00' in result['sum'] else result['sum'] + '.00'
        fn = result['fn']
        fd = result['fd']
        fp = result['fp']
        query = f"t={iso_format}&s={sum_total}&fn={fn}&i={fd}&fp={fp}&n=1"

        result_text = format_receipt_text(result)

        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message_id,
            text=result_text,
            reply_markup=confirm_receipt_butt,
            parse_mode="HTML"
        )


# Обработка кнопки "✅ Подтвердить" или "⬅️ Назад" в ReportManagement
@router.callback_query(Check_photo.check, F.data == "confirm_receipt")
@router.callback_query(Check_photo.asking, F.data == "confirm_receipt")
@router.callback_query(F.data == "report_back")
async def back(callback: CallbackQuery, state: FSMContext):

    # Получаем данные из Check_photo
    data = await state.get_data()
    print(f'\n{data}\n')

    # Отправляем сообщение пользователю
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=expense_added_success,
        reply_markup=confirm_buttons
    )


# Обработка кнопки "⬅️ Назад"
@router.callback_query(Check_photo.asking, F.data == "check_back")
@router.callback_query(Check_photo.check, F.data == "check_back")
async def back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await handle_entertainment(callback, state)  # Передаем callback и state
