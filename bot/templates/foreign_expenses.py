from aiogram.fsm.state import StatesGroup, State

# Определяем состояния FSM
class ExpenseState(StatesGroup):
    choosing_type = State()
    entering_foreign_amount = State()
    entering_rub_amount = State()
    confirming = State()