import os
import shutil
from datetime import datetime

import openpyxl
from babel.dates import format_date
from num2words import num2words
from openpyxl.styles import Border, Side, Font, Alignment
import pandas as pd
import pdfkit

from db.models.models import Check, User


async def create_report(user_tg_id: int) -> str:
    user = await User.get(tg_id=user_tg_id)
    checks = await Check.filter(
        user_id=user.id,
        used=False
    )
    print('len(checks)', len(checks))

    file_path = f'data/{user.id}.xlsx'
    html_file_path = f'data/{user.id}.html'
    pdf_file_path = f'data/{user.id}.pdf'
    shutil.copy2('data/report.xlsx', file_path)

    workbook = openpyxl.load_workbook(filename=file_path)
    sheet = workbook.active

    now = datetime.now()
    amount = sum([check.sum for check in checks]) / 100
    today = datetime.now().strftime('%d.%m.%Y')
    name = short_name(user.full_name)
    boss_name = short_name(user.boss_name)
    rub_amount = format_amount(amount)
    print('str(amount).split()', str(amount).split('.'))
    cop_amount = str(amount).split('.')[1]
    text_amount = f'{num2words(int(amount), lang='ru')} рублей {cop_amount} копеек ({rub_amount} руб. {cop_amount} коп.)'

    # Отчет о сумме
    sheet.cell(row=9, column=18).value = rub_amount
    sheet.cell(row=9, column=24).value = cop_amount
    # Дата формирования
    sheet.cell(row=13, column=10).value = today
    sheet.cell(row=15, column=15).value = today
    # Подразделение
    sheet.cell(row=19, column=8).value = user.subdivision
    # Подотчетное лицо
    sheet.cell(row=21, column=6).value = name
    # Назначение аванса
    sheet.cell(row=23, column=17).value = 'Расходы ' + format_date(now, format='MMMM yyyy', locale='ru')
    # Израсходовано
    sheet.cell(row=33, column=10).value = f'{rub_amount},{cop_amount}'
    sheet.cell(row=39, column=10).value = text_amount
    # Принят к проверке от
    sheet.cell(row=55, column=9).value = name
    # От
    print("f'{datetime.now().strftime('%d %B %Y г.')}'", format_date(now, format='d MMMM yyyy г.', locale='ru'))
    sheet.cell(row=56, column=4).value = format_date(now, format='d MMMM yyyy г.', locale='ru')
    # На сумму
    sheet.cell(row=56, column=11).value = text_amount

    # Создание таблицы
    start_row, start_column, end_row, end_column = 66, 2, 66, 24

    source_row = [cell.value for cell in sheet[66]]
    sheet.delete_rows(66)

    for i, check in enumerate(checks):
        end_row = 66 + i
        sheet.insert_rows(end_row)
        print(end_row)

        for col_num, value in enumerate(source_row, start=1):
            sheet.cell(row=end_row, column=col_num, value=value)

        sheet.merge_cells(start_row=end_row, start_column=2, end_row=end_row, end_column=3)
        sheet.merge_cells(start_row=end_row, start_column=4, end_row=end_row, end_column=5)
        sheet.merge_cells(start_row=end_row, start_column=6, end_row=end_row, end_column=7)
        sheet.merge_cells(start_row=end_row, start_column=8, end_row=end_row, end_column=11)
        sheet.merge_cells(start_row=end_row, start_column=12, end_row=end_row, end_column=14)
        sheet.merge_cells(start_row=end_row, start_column=15, end_row=end_row, end_column=17)
        sheet.merge_cells(start_row=end_row, start_column=18, end_row=end_row, end_column=20)
        sheet.merge_cells(start_row=end_row, start_column=21, end_row=end_row, end_column=23)
        sheet.merge_cells(start_row=end_row, start_column=24, end_row=end_row, end_column=25)

        float_sum = check.sum / 100
        check_rub_amount = format_amount(float_sum)
        check_cop_amount = str(float_sum).split('.')[1]

        sheet.cell(row=end_row, column=2).value = i + 1
        sheet.cell(row=end_row, column=4).value = check.date.strftime('%d.%m.%Y')
        sheet.cell(row=end_row, column=6).value = check.id
        sheet.cell(row=end_row, column=8).value = check.type
        sheet.cell(row=end_row, column=12).value = f'{check_rub_amount},{check_cop_amount}'
        sheet.cell(row=end_row, column=18).value = f'{check_rub_amount},{check_cop_amount}'

    sheet.merge_cells(start_row=end_row + 1, start_column=8, end_row=end_row + 1, end_column=11)
    sheet.merge_cells(start_row=end_row + 1, start_column=8, end_row=end_row + 1, end_column=11)

    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for row in range(start_row, end_row + 1):
        for col in range(start_column, end_column + 2):
            print(row, ',', col)
            sheet.cell(row=row, column=col).border = thin_border

    # Сумма таблицы
    table_summ_row = end_row + 1
    sheet.cell(row=table_summ_row, column=12).value = f'{rub_amount},{cop_amount}'
    sheet.cell(row=table_summ_row, column=18).value = f'{rub_amount},{cop_amount}'
    sheet.merge_cells(start_row=table_summ_row, start_column=12, end_row=table_summ_row, end_column=14)
    sheet.merge_cells(start_row=table_summ_row, start_column=15, end_row=table_summ_row, end_column=17)
    sheet.merge_cells(start_row=table_summ_row, start_column=18, end_row=table_summ_row, end_column=20)
    sheet.merge_cells(start_row=table_summ_row, start_column=21, end_row=table_summ_row, end_column=23)

    # Область для подписи
    user_signature_row = end_row + 3

    sheet.merge_cells(start_row=user_signature_row, start_column=2, end_row=user_signature_row, end_column=5)
    sheet.merge_cells(start_row=user_signature_row, start_column=6, end_row=user_signature_row, end_column=12)
    sheet.merge_cells(start_row=user_signature_row, start_column=14, end_row=user_signature_row, end_column=25)
    sheet.merge_cells(start_row=user_signature_row + 1, start_column=6, end_row=user_signature_row + 1, end_column=12)
    sheet.merge_cells(start_row=user_signature_row + 1, start_column=14, end_row=user_signature_row + 1, end_column=25)

    boss_signature_row = end_row + 7

    sheet.merge_cells(start_row=boss_signature_row, start_column=2, end_row=boss_signature_row, end_column=5)
    sheet.merge_cells(start_row=boss_signature_row, start_column=6, end_row=boss_signature_row, end_column=12)
    sheet.merge_cells(start_row=boss_signature_row, start_column=14, end_row=boss_signature_row, end_column=25)

    # Заголовки
    sheet.cell(row=user_signature_row, column=2).value = 'Подотчетное лицо'
    user_signature_cell = sheet.cell(row=user_signature_row + 1, column=6)
    user_decryption_cell = sheet.cell(row=user_signature_row + 1, column=14)

    thin_line = Border(top=Side(style='thin'))
    font = Font(size=6)
    alignment = Alignment(horizontal='center', vertical='center')

    user_signature_cell.value = 'подпись'
    user_signature_cell.font = font
    user_signature_cell.alignment = alignment
    for column in range(6, 13):
        sheet.cell(row=user_signature_row + 1, column=column).border = thin_line

    user_decryption_cell.value = 'расшифровка подписи'
    user_decryption_cell.font = font
    user_decryption_cell.alignment = alignment
    for column in range(14, 26):
        sheet.cell(row=user_signature_row + 1, column=column).border = thin_line

    sheet.cell(row=user_signature_row, column=14).value = name

    sheet.cell(row=boss_signature_row, column=2).value = 'Руководитель'
    thin_line = Border(bottom=Side(style='thin'))

    for column in range(6, 13):
        sheet.cell(row=boss_signature_row, column=column).border = thin_line

    for column in range(14, 26):
        sheet.cell(row=boss_signature_row, column=column).border = thin_line

    sheet.cell(row=boss_signature_row, column=14).value = boss_name

    workbook.save(file_path)

    # df = pd.read_excel(file_path)
    # df.to_html(html_file_path)
    # pdfkit.from_file(html_file_path, pdf_file_path)
    #
    # os.remove(file_path)
    # os.remove(html_file_path)

    # return pdf_file_path

    for check in checks:
        await check.update(used=True)

    return file_path


def format_amount(amount: float):
    return f"{int(str(amount).split('.')[0]):,}".replace(",", " ")


def short_name(full_name: str) -> str:
    name_parts = full_name.split()
    return f"{name_parts[0]} {name_parts[1][0]}. {name_parts[2][0]}."
