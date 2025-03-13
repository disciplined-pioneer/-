from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from core.bot import bot
from bot.keyboards.events import *
from bot.handlers.check import ReportManagement

from bot.keyboards.present import new_expense_keyboard
from bot.keyboards.biznes_zavtrak import preparations_keyboard

from collections import defaultdict
from db.crud.base import get_user_data

import os
from utils.report import create_report

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

    msg = await call.message.edit_text(questions_event['company_meeting'],
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
        
        if current_question == 4:
            text += f'<b>{answers["guest_name"]}</b>'
            keyboard = get_company_keyboard(answers.get('company_meeting'))
        else:
            keyboard = event_back_keyboard

        await message.delete()
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    else:
        try:
            await message.delete()
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=bot_message_id,
                text=instruction_text + f'<b>{answers["guest_name"]}</b>',
                reply_markup=get_company_keyboard(answers.get('company_meeting')),
                parse_mode="HTML"
            )
        except:
            pass


# Обработка кнопок для выбора компании
@router.callback_query(F.data.startswith("company_"))
async def handle_company_callback(callback: types.CallbackQuery, state: FSMContext):

    # Получаем данные из состояния
    data = await state.get_data()
    answers = data.get("answers", {})
    participants = data.get("participants", [])

    # Получаем текст нажатой кнопки
    if callback.data == "company_alphasigma":
        button_text = "ООО «Альфасигма Рус»"
    elif callback.data == "company_meeting_choice":
        button_text = answers.get("company_meeting")

    # Добавляем нового участника
    participants.append({
        'guest_name': answers.get('guest_name', 'Неизвестно'),
        'guest_workplace': button_text
    })

    # Обновляем состояние
    await state.update_data(participants_count=len(participants), participants=participants)


    # Редактируем предыдущее сообщение
    await callback.message.edit_text(
        text=get_confirm_guest_addition(answers, button_text),
        reply_markup=confirmation_keyboard,
        parse_mode="HTML"
    )

    await callback.answer()
    

# Обработка кнопки "⬅️ Назад" при заполнении вопросов
@router.callback_query(ReportManagement.awaiting_documents, F.data == "question_event_back")
async def back_question(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_question = data["current_question"]
    list_key = list(questions_event.keys())

    # Переходим на один вопрос назад
    if current_question == 0:
        await generate_documents_callback(callback, state)

    elif current_question == 4:
        
        # Удаление участника
        current_question = 3
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
    await state.update_data(current_question=3,
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
    await call.message.edit_text(message, reply_markup=new_expense_keyboard)


    # Группируем участников по их месту работы
    company_dict = defaultdict(list)
    for participant in data['participants']:
        company_dict[participant['guest_workplace']].append(participant['guest_name'])
    list_participants = dict(company_dict)

    # Определяем путь к файлу заранее
    file_path = f"data/output_{user_id}.docx"
    doc = None  

    # Заполняем отчёт в таблицах
    if data['callback_data'] == 'report_event':
        doc_path = "data/events.docx"
        table_list_our_company = [0, 4]  
        table_list_another_company = [1, 5] 

    else:
        doc_path = "data/business_breakfasts.docx"
        table_list_our_company = [0]
        table_list_another_company = [1] 

    # Заполняем отчёт словами
    process_document(doc_path, data, user, file_path)

    # Открываем файл и работаем с таблицами
    doc = Document(file_path)

    for company, employees in list_participants.items():
        tables = table_list_our_company if company == "ООО «Альфасигма Рус»" else table_list_another_company  # Выбираем таблицы

        for num_table in tables:
            table = doc.tables[num_table]

            if company == "ООО «Альфасигма Рус»":  # Если это наша компания
                for i, employee in enumerate(employees, start=1):
                    add_row_with_borders(table, [str(i+1), employee])

            else:  # Если это другая компания
                update_last_row(table, [str(1), employees[0]])  # Первый сотрудник обновляет последнюю строку
                for i, employee in enumerate(employees[1:], start=2):
                    add_row_with_borders(table, [str(i), employee])


    # Сохраняем изменения только если doc был создан
    if doc:
        doc.save(file_path)

        # Создание отчёта
        file_path_excel = await create_report(call.from_user.id)

        await call.message.delete()
        await call.message.answer_document(
            caption=advance_report_generated,
            document=FSInputFile(file_path_excel)
        )

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

        os.remove(file_path)

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

    # Создание отчёта
    path = await create_report(call.from_user.id)

    await call.message.delete()
    await call.message.answer_document(
        caption=advance_report_generated,
        document=FSInputFile(path)
    )

    os.remove(path)
    await state.clear()
