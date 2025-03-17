from aiogram.fsm.state import StatesGroup, State

# Определяем состояния FSM
class ExpenseState(StatesGroup):
    choosing_type = State()
    entering_foreign_amount = State()
    entering_rub_amount = State()
    confirming = State()

VALID_CURRENCIES = {"USD", "EUR", "GBP", "CNY", "JPY"}

expense_type_message = "📝Пожалуйста, укажи тип расхода. Например: \"покупка\", \"услуга\", \"командировка\" и т.д. 💼"

foreign_amount_message = "💵Введите сумму в валюте, в которой был произведен расход. Например: 100 USD, 50 EUR и т.д. 💱"

incorrect_format_message = '❌ Некорректный формат. Используйте: "100 USD" или "50 EUR"'

incorrect_amount_message = "❌ Некорректная сумма. Введите число, например: 7500.50"

expense_added_message = "🎉 Ваш расход успешно добавлен в отчет! 🎉\n\n" \
                        "Вы можете продолжить заполнение авансового отчета, добавив другие виды расходов.\n" \
                        "Хотите добавить новый тип расхода в существующий отчет?"

def generate_expense_summary(data):
    return (
        f"📝Данные по расходу\n"
        f"Тип расхода: {data['expense_type']}\n"
        f"Сумма в валюте документа: {data['foreign_amount']}\n"
        f"Сумма в рублях для включения в отчет: {data['rub_amount']}\n\n"
        "Пожалуйста, проверьте информацию выше"
    )
