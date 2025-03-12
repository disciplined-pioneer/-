from aiogram.fsm.state import StatesGroup, State

# Новый класс состояния для обработки подарков
class GiftReport(StatesGroup):
    check = State()
    awaiting_gift = State()
    awaiting_event = State()
    awaiting_recipient_info = State()
    awaiting_document_confirmation = State()

