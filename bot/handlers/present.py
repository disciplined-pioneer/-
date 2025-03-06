from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from core.bot import bot

from bot.keyboards.present import *

router = Router()

# Новый класс состояния для обработки подарков
class GiftReport(StatesGroup):
    check = State()
    awaiting_event = State()
    awaiting_recipient_info = State()
    awaiting_document_confirmation = State()


# Для обработки кнопки "2️⃣ Подарки"
@router.callback_query(F.data == "report_gifts")
async def gifts_callback(call: CallbackQuery, state: FSMContext):

    # Сохраняем данные в GiftReport и уст. состояние
    data = await state.get_data()
    answers_check = data.get("answers_check", None)
    await state.update_data(answers_check=answers_check)    
    await state.set_state(GiftReport.check)

    # Отправляем сообщение с вопросом
    msg = await call.message.edit_text(
        "💭 В связи с каким событием были приобретены подарки? (например, день рождения, юбилей, праздник и т.д.) 🗓", 
        reply_markup=event_back_keyboard
    )
    
    # Инициализируем состояние для ввода данных
    await state.update_data(current_question=0, answers={})
    await state.update_data(bot_message_id=msg.message_id)
    
    # Переходим к состоянию ожидания события
    await state.set_state(GiftReport.awaiting_event)


# Обработчик ввода данных о событии
@router.message(GiftReport.awaiting_event, F.text)
async def event_message_handler(message: types.Message, state: FSMContext):
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
        text="Давайте соберем информацию о получателях подарков! 🎁\n\n"
             "• 📋 Введите наименование юридического лица и количество подарков в формате: [Наименование юридического лица] - [Количество] \n\n"
             "Например: ООО 'Ромашка' - 10",
        reply_markup=event_back_keyboard
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
        text=f"Спасибо! Вы указали:\n\n{recipient_info}\n\n🔄 Хотите добавить еще?",
        reply_markup=gift_action_keyboard
    )


# Обработчик нажатия кнопки "🔘 Добавить инф о получателе подарков"
@router.callback_query(GiftReport.awaiting_recipient_info, F.data == "add_gift_info")
async def add_gift_info_callback(call: CallbackQuery, state: FSMContext):
    # Возвращаем пользователя к вводу информации о получателях
    await call.message.edit_text(
        "📋 Введите наименование юридического лица и количество подарков в формате: [Наименование юридического лица] - [Количество]\n\nНапример: ООО 'Ромашка' - 10",
        reply_markup=event_back_keyboard
    )


# Обработчик нажатия кнопки "✅ Сформировать документы по встрече"
@router.callback_query(GiftReport.awaiting_recipient_info, F.data == "gen_documents")
async def gen_documents_callback(call: CallbackQuery, state: FSMContext):

    # Получаем данные состояния
    data = await state.get_data()
    gifts_info = "\n".join([f"• {gift}" for gift in data.get("answers", {}).get("gifts", [])])

    message = f"📄 Вы готовы сформировать подтверждающий документ с следующими данными:\n\n{gifts_info}\n\n🔄 Подтвердите:"

    await call.message.edit_text(
        message,
        reply_markup=conf_keyboard
    )

    # Переходим к состоянию подтверждения документа
    await state.set_state(GiftReport.awaiting_document_confirmation)


# Обработчик подтверждения документов
@router.callback_query(GiftReport.awaiting_document_confirmation, F.data == "confirm_document")
async def confirm_document_callback(call: CallbackQuery, state: FSMContext):

    # Создаем документ
    message = (
        "Документ по встрече успешно создан! 📄\n\n"
        "• 📂 Вы можете скачать файл:\n"
        "  • Файл 1: [Прикрепленный файл с подтверждением подарков]\n\n"
        "Хотите добавить новый тип расхода в существующий отчет?"
    )
    data = await state.get_data()
    print(f'\n{data}\n')

    await call.message.edit_text(message, reply_markup=new_expense_keyboard)

    # ВРЕМЕННО
    await call.message.answer(f"Данные о чеке: {data['answers_check']}\n\nДанные о получателях: {data['answers']['gifts']}")


# Обработчик отмены документа
@router.callback_query(GiftReport.awaiting_document_confirmation, F.data == "cancel_document")
async def cancel_document_callback(call: CallbackQuery, state: FSMContext):
    # Возвращаемся к добавлению информации о получателях
    await call.message.edit_text(
        "❌ Отмена добавления документов.\n\n🔄 Хотите попробовать снова?",
        reply_markup=gift_info_keyboard
    )

# Обработчик кнопки "⬅️ Назад" на шаге отчета
@router.callback_query(F.data == "question_present_back")
async def back_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_state = await state.get_state()

    print('попал')

    # Возвращаем в состояние в зависимости от текущего этапа
    if current_state == GiftReport.awaiting_event.state:
        # Если пользователь на этапе ввода события, возвращаем на этап "check"
        await state.set_state(GiftReport.check)
        await call.message.edit_text(
            "💭 В связи с каким событием были приобретены подарки? (например, день рождения, юбилей, праздник и т.д.) 🗓", 
            reply_markup=event_back_keyboard
        )
    elif current_state == GiftReport.awaiting_recipient_info.state:
        # Если на этапе ввода информации о получателе подарков, возвращаемся на предыдущий шаг
        await state.set_state(GiftReport.awaiting_event)
        await call.message.edit_text(
            "💭 В связи с каким событием были приобретены подарки? (например, день рождения, юбилей, праздник и т.д.) 🗓", 
            reply_markup=event_back_keyboard
        )
    elif current_state == GiftReport.awaiting_document_confirmation.state:
        # Если на этапе подтверждения документов, возвращаем в этап ввода информации о получателе
        await state.set_state(GiftReport.awaiting_recipient_info)
        await call.message.edit_text(
            "📋 Введите наименование юридического лица и количество подарков в формате: [Наименование юридического лица] - [Количество]\n\nНапример: ООО 'Ромашка' - 10",
            reply_markup=gift_info_keyboard
        )
    else:
        # Если по каким-то причинам пользователь не в известном состоянии, выводим стандартное сообщение
        await call.message.edit_text(
            "❌ Что-то пошло не так, попробуйте еще раз.",
            reply_markup=gift_info_keyboard
        )
