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
    date_str = data.get("answers_check")['date']

    # Q9: Целая часть от sum
    Q9 = int(sum_value)  # Целая часть суммы
    
    # W9: Копейки от sum
    W9 = round(sum_value - Q9, 2) * 100  # Копейки (умножаем на 100 для получения числа с копейками)

    # I13: Дата в формате 'ДД.ММ.ГГ'
    date_obj = datetime.strptime(date_str, '%Y%m%dT%H%M')
    I13 = date_obj.strftime('%d.%m.%y')  # Преобразуем в нужный формат

    # I33: Сумма (просто отображаем sum_value)
    I33 = sum_value
    
    # P23: Форматированное слово "Расход" + месяц и год
    date_obj_month_year = datetime.strptime(date_str, '%Y%m%dT%H%M')
    # Переводим месяц на русский
    P23 = f"Расход {date_obj_month_year.strftime('%B %Y').capitalize()}"
    # Переводим месяц на русский вручную
    months = {
        'January': 'Январь', 'February': 'Февраль', 'March': 'Март', 'April': 'Апрель', 
        'May': 'Май', 'June': 'Июнь', 'July': 'Июль', 'August': 'Август', 'September': 'Сентябрь', 
        'October': 'Октябрь', 'November': 'Ноябрь', 'December': 'Декабрь'
    }
    P23 = P23.replace(date_obj_month_year.strftime('%B'), months[date_obj_month_year.strftime('%B')])

    # I39: Преобразуем сумму в текст
    rub, kop = divmod(sum_value, 1)  # Разделяем на рубли и копейки
    kop = round(kop * 100)  # Преобразуем копейки в целое число
    # Форматируем сумму в текст
    I39 = f"{convert_number_to_text(rub)} рублей {kop} копеек ({int(rub)} руб. {kop} коп.)"

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