from datetime import datetime
from db.models.models import Check, User

def get_nds(check_data: dict) -> int:
    data = check_data['data']['json']

    if nds := data.get('nds'):
        return nds
    elif nds := data.get('nds18'):
        return nds
    elif nds := data.get('nds0'):
        return nds
    elif data.get('ndsNo'):
        return 0


# Функция для вывода успешного результата обработки чека
def format_receipt_text(result: dict, verification_status: str) -> str:
    sum_total = f"{result['sum']:.2f}"  # Преобразуем число в строку с 2 знаками после запятой

    return (
        f"Статус чека: <b>{verification_status}</b>\n"
        f"Дата чека: <b>{result['date']}</b>\n"
        f"ФН: <b>{result['fn']}</b>\n"
        f"ФД: <b>{result['fd']}</b>\n"
        f"ФП: <b>{result['fp']}</b>\n"
        f"Итого: <b>{sum_total}</b>\n"
    )


# Список вопросов для пользователя
questions = {
    'date': "Введите дату с чека в формате: ДД.ММ.ГГГГ ДД:ММ (например: 02.02.2020 15:30)",
    'sum': "Введите сумму с чека например 157.00 (157 рублей 00 копеек)",
    'fn': "Введите ФН",
    'fd': "Введите ФД",
    'fp': "Введите ФП"
}


# Извлекает данные из JSON-структуры чека.
async def extract_receipt_data(check_info):
    data_qr = check_info["request"]["manual"]
    date = datetime.strptime(check_info["data"]["json"]["dateTime"], "%Y-%m-%dT%H:%M:%S")
    return {
        'date': date,
        'fn': data_qr["fn"],
        'fd': data_qr["fd"],
        'fp': data_qr["fp"],
        'sum': float(data_qr["sum"])
    }


# Определяет категорию расходов на основе callback_data.
async def determine_expense_type(callback_data):
    return 'Представительские расходы' if callback_data == "entertainment" else 'Бизнес-завтрак / Фармкружок'


# Сохраняет чек в базу данных.
async def save_check_to_db(state_data, user_id):
    
    try:
        
        check_data = state_data['check_data']
        json_data = check_data['data']['json']

        await Check.create(
            user_id=user_id,
            date=datetime.strptime(json_data['dateTime'], '%Y-%m-%dT%H:%M:%S'),
            fd=check_data['request']['manual']['fd'],
            fn=check_data['request']['manual']['fn'],
            fp=check_data['request']['manual']['fp'],
            kkt_reg_id=json_data.get('kktRegId'),
            inn=json_data.get('userInn'),
            salesman=json_data.get('user'),
            operator=json_data.get('operator'),
            address=json_data['metadata'].get('address'),
            sum=json_data.get('totalSum'),
            nds=get_nds(check_data),
            type=state_data['expense_type']
        )

    except KeyError:
        state = state_data['answers_check']
        await Check.create(
            user_id=user_id,
            date=datetime.strptime(state["date"], "%d.%m.%Y %H:%M"),
            sum=state['sum'],
            fn=state['fn'],
            fd=state['fd'],
            fp=state['fp'],
            type=state['expense_type']
        )
