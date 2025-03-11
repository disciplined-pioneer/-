from aiogram.fsm.state import StatesGroup, State

# Состояние для чека
class Checkphoto(StatesGroup):
    check = State()
    asking = State()


# Состояние для сохранения всех ответов
class ReportManagement(StatesGroup):
    awaiting_documents = State()


request_receipt_photo_with_qr = "Отправьте фото чека, чтобы на нем был виден QR-код:"

waiting_for_receipt_data = "Пожалуйста, подождите, идёт получение данных о чеке…"

receipt_data_error = "Не удалось получить информацию о чеке\nМожете заполнить данные о чеке самостоятельно"

request_receipt_photo_only = "Пожалуйста, отправьте фото чека, а не текст или другие файлы"

invalid_date_format = "Неверный формат даты. Пожалуйста, введите дату в формате ДД.MM.ГГГГ ЧЧ:ММ."

expense_added_success = (
    "🎉 Ваш расход успешно добавлен в отчет!🎉"
    "\n\n⬇️ Пожалуйста, прикрепите подтверждающие документы, нажав на кнопку ниже:"
)

check_info_error_message = (
    "Не удалось получить информацию о чеке\n"
    "Проверьте введенные данные и попробуйте снова\n"
    "Либо можете сформировать отчёт на основе введённых данных"
)