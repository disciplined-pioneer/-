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
