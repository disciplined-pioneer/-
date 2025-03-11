from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from core.bot import bot
from bot.keyboards.events import *
from bot.handlers.check import ReportManagement
from bot.keyboards.biznes_zavtrak import preparations_keyboard

from utils.events import  *
from bot.templates.events import *


router = Router()


# Обработчик кнопки "📝 Сформировать", продолжаем работу с Check_photo.asking
@router.callback_query(F.data == "generate_documents")
async def generate_documents_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    if data['callback_data'] == 'biznes_zavtrak_farmkruzhok':
        await call.message.edit_text(enter_template_data, 
                                     reply_markup=preparations_keyboard)
    
    elif data['callback_data'] == 'entertainment':
        await call.message.edit_text(select_document_type, 
                                     reply_markup=report_category_keyboard)


# Обработка кнопки "1️⃣ Мероприятие"
@router.callback_query(F.data == "report_event")
@router.callback_query(F.data == "confirm")
async def event_callback(call: CallbackQuery, state: FSMContext):

    # Сохраняем данные в ReportManagement и уст. состояние
    await state.update_data(callback_data=call.data)
    data = await state.get_data()
    answers_check = data.get("answers_check", None)
    await state.update_data(answers_check=answers_check)    
    await state.set_state(ReportManagement.awaiting_documents)

    msg = await call.message.edit_text(questions_event['event_location'],
                                       reply_markup=event_back_keyboard)

    # Счётчик для вопросов и хранение ответов
    await state.update_data(current_question=0, answers={})
    await state.update_data(bot_message_id=msg.message_id)


# Обработка вопросов по циклу для ввода данных о новом участнике
@router.message(ReportManagement.awaiting_documents, F.text)
async def ask_next_question(message: Message, state: FSMContext):
    data = await state.get_data()
    current_question = data.get("current_question", 0)
    answers = data.get("answers", {})
    participants_count = data.get("participants_count", 0)
    participants = data.get("participants", [])
    bot_message_id = data.get("bot_message_id")

    # Сохраняем ответ на текущий вопрос
    list_key = list(questions_event.keys())
    answers[list_key[current_question]] = message.text

    print(f"\nСостояние: {data}\n")

    # Переход к следующему вопросу
    if current_question + 1 < len(questions_event):
        current_question += 1
        await state.update_data(current_question=current_question, answers=answers)

        # Добавляем ФИО участника к сообщению бота
        text = questions_event[list_key[current_question]]
        if current_question == 3:
            text += f'<b>{answers["guest_name"]}</b>'

        await message.delete()
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message_id,
            text=text,
            reply_markup=event_back_keyboard,
            parse_mode="HTML"
        )
        
    else:
        # Добавляем информацию об участнике в список
        participants.append({
            'guest_name': answers.get('guest_name'),
            'guest_workplace': answers.get('guest_workplace')
        })

        # Обновляем количество участников
        participants_count += 1
        await state.update_data(participants_count=participants_count, participants=participants)

        await message.delete()
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message_id,
            text=get_confirm_guest_addition(answers),
            reply_markup=confirmation_keyboard,
            parse_mode="HTML"
        )


# Обработка кнопки "⬅️ Назад" при заполнении вопросов
@router.callback_query(ReportManagement.awaiting_documents, F.data == "question_event_back")
async def back_question(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_question = data["current_question"]
    list_key = list(questions_event.keys())

    # Переходим на один вопрос назад
    if current_question == 0:
        await generate_documents_callback(callback, state)

    elif current_question == 3:
        
        # Удаление участника
        current_question = 2
        data = await state.get_data()

        await state.update_data(current_question=current_question)
        await callback.message.edit_text(questions_event[list_key[current_question]],
                                         reply_markup=event_back_keyboard)

    elif current_question > 0:
        current_question -= 1
        await state.update_data(current_question=current_question)
        await callback.message.edit_text(questions_event[list_key[current_question]],
                                         reply_markup=event_back_keyboard)


# Обработчик кнопки "🔘 Добавить участника"
@router.callback_query(ReportManagement.awaiting_documents, F.data == "add_participant")
async def add_participant_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    participants_count = data.get("participants_count", 0)

    if participants_count >= MAX_PARTICIPANTS:
        await call.message.edit_text(max_participants_reached,
                                     reply_markup=None)
        return

    # Запускаем процесс ввода данных для нового участника, начиная с ФИО
    await state.update_data(current_question=2,
                            participants_count=participants_count)
    
    await call.message.edit_text(questions_event['guest_name'],
                                reply_markup=event_back_keyboard)


# Обработчик нажатия кнопки "✅ Подтвердить"
@router.callback_query(F.data == 'confirm_action')
async def confirm_action(callback: types.CallbackQuery):
    await callback.message.edit_text(participant_added_success,
                                     reply_markup=meeting_keyboard)


# Обработчик нажатия кнопки "❌ Отменить"
@router.callback_query(F.data == 'cancel_action')
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    
    # Удаление участника
    data = await state.get_data()
    print(f"\n{data}\n")

    participants = data.get("participants", 0)
    participants_count = data.get("participants_count", 0)

    await state.update_data(participants_count=participants_count-1,
                            participants=participants[:-1])
    
    await callback.message.edit_text(participant_addition_cancelled,
                                     reply_markup=meeting_keyboard)


# Обработчик нажатия кнопки "❌ Отменить"
@router.callback_query(F.data == 'cancel_action_two')
async def cancel_action_two(callback: CallbackQuery, state: FSMContext):
    # Вызов функции skip_callback
    await state.update_data(participants_count=0, participants=[])
    await skip_callback(callback, state)



# ВОЗМОЖНО ПОМЕНЯТЬ ИМПОРТ В СВЯЗИ С РЕГЛАМЕНТОВ
from db.crud.base import get_user_data


# Обработчик нажатия кнопки "✅ Сформировать документы по встрече"
@router.callback_query(ReportManagement.awaiting_documents, F.data == "generate_documents_tree")
async def generate_documents_tree_callback(call: CallbackQuery, state: FSMContext):
    
    # Получаем данные состояния
    data = await state.get_data()
    participants = data.get("participants", [])
    print(f"\nСостояние: {data}\n")

    # Получаем данные о пользователе по его id
    user_id = call.from_user.id
    user_obj = await get_user_data(user_id)
    user = user_obj.__dict__ if user_obj else {}

    print(f"Данные пользователя: {user}")

    # Проверяем, есть ли участники
    if participants:
        message = meeting_document_created
    else:
        message = no_participants_for_document

    # Отправляем сообщение
    await call.message.edit_text(message, reply_markup=None)


    list_participants = [
        [str(i + 1), participant['guest_name'], participant['guest_workplace']]
        for i, participant in enumerate(data['participants'])
    ]
    
    # Заполняем отчёт
    if data['callback_data'] == 'report_event':
        doc_path = "data/events_test.docx"

    # Заполняем отчёт словами
    process_document(doc_path, data, user)
    
    # Заполняем отчёт в таблицах
    file_path = "data/output.docx"
    doc = Document(file_path)
    
    table_list = [0, 4]
    for num_table in table_list:
        table = doc.tables[num_table]

        f = True
        for data_user in list_participants:
            if f:
                f = False
                update_last_row(table, data_user)
            else:
                add_row_with_borders(table, data_user)

    doc.save(file_path) 
    await state.clear()


# Обработка кнопки "✅ Сформировать документы по встрече"
@router.callback_query(ReportManagement.awaiting_documents, F.data == "generate_documents_two")
async def generate_documents_callback_two(call: CallbackQuery, state: FSMContext):
    
    # Получаем все данные из состояния
    data = await state.get_data()
    participants = data.get("participants", [])
    print(f"\n{data}\n")

    # Если участники есть, формируем список
    if participants:

        message = generate_meeting_confirmation_message(data, participants)
        if data.get('callback_data') == 'biznes_zavtrak_farmkruzhok':
            message += f"\n\n - Препарат: {data.get('selected_drug', 'Не выбран')}"


    else:
        message = "🚫 У вас нет добавленных участников."

    # Отправляем информацию о всех участниках
    await call.message.edit_text(message, reply_markup=confirmation_keyboard_two , parse_mode="HTML")


# Обработка кнопки "Пропустить"
@router.callback_query(F.data == "skip")
async def skip_callback(call: CallbackQuery, state: FSMContext):

    await call.message.edit_text(advance_report_generated)

    data = await state.get_data()
    print(f"\nСостояние: {data}\n")

    # Добавляем данные в таблицу
    result = process_data(data)
    print(result)

    for key, value in result.items():
        add_data_to_cell(r"data/advance_report.xlsx", key, value)
    
    # Используем FSInputFile для отправки файла
    file_path = r"data/advance_report.xlsx" 
    file = FSInputFile(file_path)
    
    await call.message.answer_document(
        document=file,
        caption=advance_report_title
    )
