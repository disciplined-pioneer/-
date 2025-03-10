from integrations.check_info import CheckApi
from datetime import datetime
import asyncio

# Асинхронная функция для проверки чека
async def check_info():
    # Инициализируем объект CheckApi
    check_api = CheckApi()

    # Данные для запроса
    # 29.12.2024 14:50
    # 490.00
    fn = 7384440800253921
    fd = 3937
    fp = 267131368
    date = datetime(2024, 12, 29, 14, 50)  # Пример даты
    sum_check = 490.00
    type_check = 1  # Тип чека (обычный)

    # Отправляем запрос с указанными данными
    result = await check_api.info_by_raw(fn=fn, fp=fp, fd=fd, date=date, sum=sum_check, type=type_check)

    # Проверка на ошибку в ответе
    if result.get('error'):
        print("Ошибка")
    else:
        print("Все ок")

# Запускаем асинхронную функцию
asyncio.run(check_info())
