from aiogram.fsm.state import StatesGroup, State

# Определяем состояния FSM
class ExpenseState(StatesGroup):
    choosing_type = State()
    entering_foreign_amount = State()
    entering_rub_amount = State()
    confirming = State()

    
expense_type_massege = "📝 Пожалуйста, укажи тип расхода. Например: \"покупка\", \"услуга\", \"командировка\" и т.д. 💼"

expense_amount_message = "💵 Введите сумму в валюте, в которой был произведен расход.\nНапример: 100 USD, 50 EUR и т.д. 💱"

rubles_amount_message = "💲 Сумма в рублях для включения в отчет:\nПожалуйста, укажи сумму в рублях, которая будет включена в отчет. (Используй курс ЦБ на дату расхода) 📊"

expense_added_message = "🎉 Ваш расход успешно добавлен в отчет! 🎉\n\nВы можете продолжить заполнение авансового отчета, добавив другие виды расходов.\nХотите добавить новый тип расхода в существующий отчет?"

def generate_expense_report(data):
    text = (
        f"📝 Данные по расходу\n"
        f"Тип расхода: {data['expense_type']}\n"
        f"Сумма в валюте документа: {data['foreign_amount']}\n"
        f"Сумма в рублях для включения в отчет: {data['rub_amount']}\n\n"
        "Пожалуйста, проверьте информацию выше"
    )
    return text
