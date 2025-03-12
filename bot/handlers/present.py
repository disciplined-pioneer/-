from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from core.bot import bot
from bot.handlers.events import generate_documents_callback
from utils.events import process_data, add_data_to_cell
from bot.keyboards.present import *

from utils.present import *
from bot.templates.present import *
from db.crud.base import *
from utils.events import process_document


router = Router()


# Для обработки кнопки "2️⃣ Подарки"
@router.callback_query(F.data == "report_gifts")
async def gifts_callback(call: CallbackQuery, state: FSMContext):

    # Сохраняем данные в GiftReport и уст. состояние
    await state.update_data(callback_data=call.data)
    data = await state.get_data()
    print(f"\n{data}\n")

    answers_check = data.get("answers_check", None)
    await state.update_data(answers_check=answers_check)    
    await state.set_state(GiftReport.check)

    # Отправляем сообщение с вопросом
    msg = await call.message.edit_text(
        gift_purpose_question, 
        reply_markup=event_back_keyboard
    )
    
    # Инициализируем состояние для ввода данных
    await state.update_data(current_question=0, answers={})
    await state.update_data(bot_message_id=msg.message_id)
    
    # Переходим к состоянию ожидания события
    await state.set_state(GiftReport.awaiting_gift)


# Обработчик ввода данных о навзаниии и количестве подарка
@router.message(GiftReport.awaiting_gift, F.text)
async def gift_message_handler(message: types.Message, state: FSMContext):

    data = await state.get_data()
    answers = data.get("answers", {})

    # Сохраняем ответ о событии
    answers["event"] = message.text

    # Переходим к следующему вопросу
    await state.update_data(answers=answers)

    # Отправляем новый вопрос
    await message.delete()
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["bot_message_id"],
        text=gift_recipients_prompt,
        reply_markup=back_keyboard
    )
    
    # Переходим к состоянию ожидания события
    await state.set_state(GiftReport.awaiting_event)


# Обработчик ввода данных о событии
@router.message(GiftReport.awaiting_event, F.text)
async def event_message_handler(message: types.Message, state: FSMContext):

    data = await state.get_data()
    answers = data.get("answers", {})

    # Сохраняем ответ о событии
    answers["name_gift"] = message.text

    # Переходим к следующему вопросу
    await state.update_data(answers=answers)

    # Отправляем новый вопрос
    await message.delete()
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["bot_message_id"],
        text=gift_recipients_info_request,
        reply_markup=back_keyboard
    )

    # Переходим к состоянию ожидания информации о получателях
    await state.set_state(GiftReport.awaiting_recipient_info)


# Обработка ввода данных о получателях подарков
@router.message(GiftReport.awaiting_recipient_info, F.text)
async def gifts_recipient_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get("answers", {})

    # Сохраняем информацию о получателе
    recipient_info = message.text
    answers.setdefault("gifts", []).append(recipient_info)

    # Обновляем состояние
    await state.update_data(answers=answers)

    # Отправляем сообщение с добавленной информацией
    await message.delete()
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["bot_message_id"],
        text=generate_thank_you_message(recipient_info),
        reply_markup=gift_action_keyboard
    )

    data = await state.get_data()
    print(f"\n{data}\n")


# Обработчик нажатия кнопки "🔘 Добавить инф о получателе подарков"
@router.callback_query(GiftReport.awaiting_recipient_info, F.data == "add_gift_info")
async def add_gift_info_callback(call: CallbackQuery, state: FSMContext):

    # Возвращаем пользователя к вводу информации о получателях
    await call.message.edit_text(
        gift_recipient_info_request,
        reply_markup=event_back_keyboard
    )

    data = await state.get_data()
    print(f"\n{data}\n")


# Обработчик нажатия кнопки "✅ Сформировать документы по встрече"
@router.callback_query(GiftReport.awaiting_recipient_info, F.data == "gen_documents")
async def gen_documents_callback(call: CallbackQuery, state: FSMContext):

    # Получаем данные состояния
    data = await state.get_data()
    
    gifts_info = "\n".join([f"• {gift}" for gift in data.get("answers", {}).get("gifts", [])])
    await call.message.edit_text(
        generate_confirmation_document_message(gifts_info),
        reply_markup=conf_keyboard
    )

    # Переходим к состоянию подтверждения документа
    await state.set_state(GiftReport.awaiting_document_confirmation)


# Обработчик подтверждения документов
@router.callback_query(GiftReport.awaiting_document_confirmation, F.data == "confirm_document")
async def confirm_document_callback(call: CallbackQuery, state: FSMContext):

    # Создаем документ
    data = await state.get_data()
    print(f'\n{data}\n')
    await call.message.edit_text(meeting_document_creation_message, reply_markup=new_expense_keyboard)

    # Получаем данные о пользователе по его id
    user_id = call.from_user.id
    user_obj = await get_user_data(user_id)
    user = user_obj.__dict__ if user_obj else {}

    print(f"Данные пользователя: {user}")

    # Заполняем отчёт
    file_path = f"data/present_{call.from_user.id}.docx"
    doc_path = "data/present.docx"
    process_document(doc_path, data, user, file_path)


    # Добавляем данные в таблицу excel
    result = process_data(data)
    for key, value in result.items():
        add_data_to_cell(r"data/advance_report.xlsx", key, value)
    file_path_excel = rf"data/advance_report.xlsx" 

    # Пути к файлам
    file_paths = [
        file_path,
        file_path_excel
    ]

    # Создаём медиа-группу
    media_group = MediaGroupBuilder()

    # Добавляем файлы в группу
    for file_path in file_paths:
        file = FSInputFile(file_path)
        media_group.add_document(file)

    # Отправляем все файлы одним сообщением
    await call.message.answer_media_group(media_group.build())
    await state.clear()


# Обработчик кнопки "❌ Отменить"
@router.callback_query(GiftReport.awaiting_document_confirmation, F.data == "cancel_document")
async def cancel_document_callback(call: CallbackQuery, state: FSMContext):

    # Возвращаемся к добавлению информации о получателях
    await call.message.edit_text(
        document_addition_canceled,
        reply_markup=gift_info_keyboard
    )

    data = await state.get_data()
    print(f"\n{data}\n")


# Обработчик кнопки "⬅️ Назад" на шаге отчета
@router.callback_query(F.data == "question_present_back")
async def back_callback(call: CallbackQuery, state: FSMContext):

    await state.update_data(answers={})  
    data = await state.get_data()
    print(f"\n{data}\n")
    
    current_state = await state.get_state()

    print('попал')

    # Возвращаем в состояние в зависимости от текущего этапа
    if current_state == GiftReport.awaiting_event.state:
        # Если пользователь на этапе ввода события, возвращаем на этап "check"
        await state.set_state(GiftReport.check)
        await call.message.edit_text(
            gift_purpose_question, 
            reply_markup=event_back_keyboard
        )
    elif current_state == GiftReport.awaiting_recipient_info.state:
        # Если на этапе ввода информации о получателе подарков, возвращаемся на предыдущий шаг
        await state.set_state(GiftReport.awaiting_event)
        await call.message.edit_text(
            gift_purpose_question,
            reply_markup=event_back_keyboard
        )
    elif current_state == GiftReport.awaiting_document_confirmation.state:
        # Если на этапе подтверждения документов, возвращаем в этап ввода информации о получателе
        if "answers" in data and "gifts" in data["answers"] and isinstance(data["answers"]["gifts"], list):
            if data["answers"]["gifts"]:  # Проверяем, не пуст ли список
                data["answers"]["gifts"].pop()  # Удаляем последний элемент

        # Обновляем состояние
        await state.update_data(answers=data["answers"])

        await state.set_state(GiftReport.awaiting_recipient_info)
        await call.message.edit_text(
            gift_recipient_info_request,
            reply_markup=gift_info_keyboard
        )
    else:
        # Если по каким-то причинам пользователь не в известном состоянии, выводим стандартное сообщение
        await call.message.edit_text(
            something_went_wrong,
            reply_markup=gift_info_keyboard
        )


# Обработчик кнопки "⬅️ Назад"
@router.callback_query(F.data == "report_back_two")
async def back_callback(call: CallbackQuery, state: FSMContext):
    await state.update_data(answers={})  
    data = await state.get_data()
    print(f"\n{data}\n")

    await generate_documents_callback(call, state)