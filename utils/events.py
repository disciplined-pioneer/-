import locale
import openpyxl
from datetime import datetime

MAX_PARTICIPANTS = 10  # Максимальное количество участников

# Функция для преобразования суммы в текст
def convert_number_to_text(number):

    # Выводим сумму как текст
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    currency_text = locale.currency(number, grouping=True).replace('₽', '')
    return currency_text.replace('\xa0', ' ')


# Функция для перевода суммы в нужный формат
def process_data(data):

    # Получение значений
    sum_value = float(data.get("answers_check")['sum']) 
    date_input = data.get("answers_check")['date']

    # Q9: Целая часть от sum
    Q9 = int(sum_value) 
    
    # W9: Копейки от sum
    W9 = round((sum_value - Q9) * 100)

    # Определяем формат входящей даты
    if isinstance(date_input, datetime): 
        date_obj = date_input
    else:
        try:
            date_obj = datetime.strptime(date_input, '%Y%m%dT%H%M') 
        except ValueError:
            date_obj = datetime.strptime(date_input, '%d.%m.%Y %H:%M') 

    # I13: Дата в формате 'ДД.ММ.ГГ'
    I13 = date_obj.strftime('%d.%m.%y') 

    # I33: Сумма (просто отображаем sum_value)
    I33 = sum_value

    # P23: Форматированное слово "Расход" + месяц и год
    months = {
        'January': 'Январь', 'February': 'Февраль', 'March': 'Март', 'April': 'Апрель', 
        'May': 'Май', 'June': 'Июнь', 'July': 'Июль', 'August': 'Август', 'September': 'Сентябрь', 
        'October': 'Октябрь', 'November': 'Ноябрь', 'December': 'Декабрь'
    }

    month_eng = date_obj.strftime('%B')  # Получаем название месяца на английском
    P23 = f"Расход {months.get(month_eng, month_eng)} {date_obj.strftime('%Y')}"

    # I39: Преобразуем сумму в текст
    rub, kop = divmod(sum_value, 1) 
    kop = round(kop * 100)
    I39 = f"{convert_number_to_text(int(rub))} рублей {kop} копеек ({int(rub)} руб. {kop} коп.)"

    # Результат в виде словаря
    return {
        'Q9': Q9,
        'W9': W9,
        'I13': I13,
        'I33': I33,
        'I35': I33,
        'I39': I39,
        'P23': P23
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