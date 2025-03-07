import re
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from core.bot import bot
from bot.keyboards.events import *
from bot.keyboards.check import confirm_buttons
from bot.handlers.check import ReportManagement

router = Router()

MAX_PARTICIPANTS = 10  # Максимальное количество участников

questions_event = {
    "event_location": ('Введите данные для заполнения шаблона:\n\n🏢 Место проведения:'),
    "meeting_theme": ("📝 Тема собрания. Введите тему: "),
    "guest_name": ("Пожалуйста, введите ФИО приглашенного участника: "),
    "guest_workplace": ("Пожалуйста, введите место работы для участника: ")
}

# Обработчик кнопки "📝 Сформировать", продолжаем работу с Check_photo.asking
@router.callback_query(ReportManagement.awaiting_documents, F.data == "generate_documents")
async def generate_documents_callback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("✨ Выберите тип документа: ✨", reply_markup=report_category_keyboard)


# Обработка кнопки "1️⃣ Мероприятие"
@router.callback_query(ReportManagement.awaiting_documents, F.data == "report_event")
async def event_callback(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(questions_event['event_location'],
                                       reply_markup=event_back_keyboard)

    # Счётчик для вопросов и хранение ответов
    await state.update_data(current_question=0, answers={})
    await state.update_data(bot_message_id=msg.message_id)


# Обработчик кнопки "🔘 Добавить участника"
@router.callback_query(ReportManagement.awaiting_documents, F.data == "add_participant")
async def add_participant_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    participants_count = data.get("participants_count", 0)

    if participants_count >= MAX_PARTICIPANTS:
        await call.message.edit_text("🚫 Достигнут предел по количеству участников. Максимум 10 человек.", reply_markup=None)
        return

    # Запускаем процесс ввода данных для нового участника, начиная с ФИО
    await state.update_data(current_question=2, participants_count=participants_count)
    msg = await call.message.edit_text(questions_event['guest_name'], reply_markup=event_back_keyboard)


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

        text = (f"📋 Вы добавили участника:\n\n• ФИО: <b>{answers['guest_name']}</b>"
                f"\n• Место работы: <b>{answers['guest_workplace']}</b>"
                "\n\n🤔 Подтвердите добавление участника")

        await message.delete()
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message_id,
            text=text,
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
        participants = data.get("participants", 0)
        participants_count = data.get("participants_count", 0)
        await state.update_data(participants_count=participants_count-1, participants=participants[:-1])

        await state.update_data(current_question=current_question)
        await callback.message.edit_text(questions_event[list_key[current_question]], reply_markup=event_back_keyboard)

    elif current_question > 0:
        current_question -= 1
        await state.update_data(current_question=current_question)
        await callback.message.edit_text(questions_event[list_key[current_question]], reply_markup=event_back_keyboard)
        

# Обработчик нажатия кнопки "✅ Подтвердить"
@router.callback_query(F.data == 'confirm_action')
async def confirm_action(callback: types.CallbackQuery):
    message = (f"🥳 Участник успешно добавлен!"
               "\n\n• 🔄 Хотите добавить еще одного участника? Максимальное количество - 10 человек")
    await callback.message.edit_text(message,
                                     reply_markup=meeting_keyboard)


# Обработчик нажатия кнопки "❌ Отменить"
@router.callback_query(F.data == 'cancel_action')
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    message = "❌ Добавление участника отменено.\n\n🔄 Хотите попробовать снова?"
    
    # Удаление участника
    data = await state.get_data()
    print(f"\n{data}\n")
    participants = data.get("participants", 0)
    participants_count = data.get("participants_count", 0)
    await state.update_data(participants_count=participants_count-1, participants=participants[:-1])
    await callback.message.edit_text(message, reply_markup=meeting_keyboard)


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

    # Проверяем, есть ли участники
    if participants:
        message = (
            f"📄 Документ по встрече успешно создан!\n\n"
            f"• 📂 Вы можете скачать файл:\n"
            f"  • Файл 1:  [Прикрепленный файл подтверждающий документ(мероприятие)]\n\n"
            f"Вы можете продолжить заполнение авансового отчета, добавив другие виды расходов.\n\n"
            f"Хотите добавить новый тип расхода в существующий отчет?"
        )
    else:
        message = "🚫 У вас нет добавленных участников для формирования документа."

    # Отправляем сообщение
    await call.message.edit_text(message, reply_markup=None)

    # ВРЕМЕННО
    await call.message.answer(f"Данные о чеке: {data['answers_check']}\n\nДанные о событии: {data['answers']}\n\nДанные о пользователях: {data['participants']}")


# Обработка кнопки "✅ Сформировать документы по встрече"
@router.callback_query(ReportManagement.awaiting_documents, F.data == "generate_documents_two")
async def generate_documents_callback_two(call: CallbackQuery, state: FSMContext):
    
    # Получаем все данные из состояния
    data = await state.get_data()
    participants = data.get("participants", [])
    print(f"\n{data}\n")

    # Если участники есть, формируем список
    if participants:
        participants_info = "\n".join(
            [f"• <b>{p['guest_name']}</b> ({p['guest_workplace']})" for p in participants]
        )
        message = (f"📄 Вы готовы сформировать документ по встрече с следующими участниками:\n\n"
                   f"{participants_info}\n\n"
                   "🔄 Подтвердите создание отчета:")
    else:
        message = "🚫 У вас нет добавленных участников."

    # Отправляем информацию о всех участниках
    await call.message.edit_text(message, reply_markup=confirmation_keyboard_two , parse_mode="HTML")


# ОТПРАВКА ОТЧЁТА - ДОРАБОТАТЬ
# Обработка кнопки "Пропустить"
@router.callback_query(F.data == "skip")
async def skip_callback(call: CallbackQuery, state: FSMContext):
    mass_text = (f'🎉 Ваш авансовый отчет успешно сформирован! 🎉'
                'Вы можете скачать его по ссылке ниже:'
                '\n\n🔗 Скачать отчет'
                )
    await call.message.edit_text(mass_text, reply_markup=confirm_buttons)
