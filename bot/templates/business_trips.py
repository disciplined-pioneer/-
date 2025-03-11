from aiogram.fsm.state import State, StatesGroup

class BusinessTripState(StatesGroup):
    waiting_for_expense_name = State()

expense_type_message = "🧾 Выберите тип расхода для командировочных расходов"
