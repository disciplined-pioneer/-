import locale
import openpyxl
from datetime import datetime

MAX_PARTICIPANTS = 10  # Максимальное количество участников

# Функция для преобразования суммы в текст
def convert_number_to_text(number):
    # Выводим сумму как текст
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')  # Устанавливаем локаль для русского языка
    currency_text = locale.currency(number, grouping=True).replace('₽', '')
    # Заменяем неразрывные пробелы на обычные
    return currency_text.replace('\xa0', ' ')


# Функция для перевода суммы в нужный формат
def process_data(data):
    
    # Получение значений
    sum_value = float(data.get("answers_check")['sum'])  # Преобразуем строку в число
    date_input = data.get("answers_check")['date']  # Может быть str или datetime

    # Q9: Целая часть от sum
    Q9 = int(sum_value)  # Целая часть суммы
    
    # W9: Копейки от sum
    W9 = round((sum_value - Q9) * 100)  # Копейки (умножаем на 100 для получения целого числа)

    # Определяем формат входящей даты
    if isinstance(date_input, datetime):  # Если уже объект datetime
        date_obj = date_input
    else:
        try:
            date_obj = datetime.strptime(date_input, '%Y%m%dT%H%M')  # Если формат ISO (например, 20250310T1530)
        except ValueError:
            date_obj = datetime.strptime(date_input, '%d.%m.%Y %H:%M')  # Если формат "01.01.2025 15:30"

    # I13: Дата в формате 'ДД.ММ.ГГ'
    I13 = date_obj.strftime('%d.%m.%y')  # Преобразуем в нужный формат

    # I33: Сумма (просто отображаем sum_value)
    I33 = sum_value

    # P23: Форматированное слово "Расход" + месяц и год
    months = {
        'January': 'Январь', 'February': 'Февраль', 'March': 'Март', 'April': 'Апрель', 
        'May': 'Май', 'June': 'Июнь', 'July': 'Июль', 'August': 'Август', 'September': 'Сентябрь', 
        'October': 'Октябрь', 'November': 'Ноябрь', 'December': 'Декабрь'
    }

    month_eng = date_obj.strftime('%B')  # Получаем название месяца на английском
    P23 = f"Расход {months.get(month_eng, month_eng)} {date_obj.strftime('%Y')}"  # Переводим на русский

    # I39: Преобразуем сумму в текст
    rub, kop = divmod(sum_value, 1)  # Разделяем на рубли и копейки
    kop = round(kop * 100)  # Преобразуем копейки в целое число
    I39 = f"{convert_number_to_text(int(rub))} рублей {kop} копеек ({int(rub)} руб. {kop} коп.)"

    # Результат в виде словаря
    return {
        'Q9': Q9,
        'W9': W9,
        'I13': I13,
        'I33': I33,
        'P23': P23,
        'I39': I39
    }


# Функция для добавления данных в ячейку Excel по указанным координатам.
def add_data_to_cell(file_path, cell, value):

    # Открытие или создание рабочего файла
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active  # Выбираем активный лист

    # Запись значения в указанную ячейку
    sheet[cell] = value

    # Сохранение изменений
    workbook.save(file_path)


questions_event = {
    "event_location": ('Введите данные для заполнения шаблона:\n\n🏢 Место проведения:'),
    "meeting_theme": ("📝 Тема собрания. Введите тему: "),
    "guest_name": ("Пожалуйста, введите ФИО приглашенного участника: "),
    "guest_workplace": ("Пожалуйста, введите место работы для участника: ")
}