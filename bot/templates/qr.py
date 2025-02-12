from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

qr_service_error_text = """
Ошибка сервиса распознания QR.
"""

incorrect_type_text = """
Не верный тип данных.
"""

wait_text = """
Пожалуйста, подождите, идет получение данных о чеке…
"""

incorrect_qr_text = """
Не удалось получить информацию о чеке.
Можете заполнить данные о чеке самостоятельно
"""

send_qr_text = """
Отправьте фото чека, чтобы на нем было видно QR-код
"""

send_data_text = """
Пришлите данные с чека в формате:

<ФН>
<ФП>
<ФД>
<Дата с чека в формате "ДД.ММ.ГГ ЧЧ:ММ">
<Итого>
"""

send_date_text = """
Введите дату с чека в формате: ДД.ММ.ГГ ЧЧ:ММ:
"""

send_sum_text = """
Введите сумму с чека например 157.00 (157 рублей 00 копеек):
"""

send_fn_text = """
Введите ФН
"""

send_fd_text = """
Введите ФД
"""

send_fp_text = """
Введите ФП
"""

success_text = """
Статус чека: проверка пройдена✅
Дата чека: {date}
ФД: {fd}
Итого: {sum}
НДС: {nds}
Сумма без НДС: {sum_without_nds}

Для формирования отчета с этими данными подтвердите эти данные
"""


def success_ikb() -> InlineKeyboardMarkup:
    """
        Подтверждение данных
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='✅Подтвердить',
            callback_data='add_check'
        ),
        InlineKeyboardButton(
            text='↩️ Главное меню',
            callback_data='start'
        )
    )
    builder.adjust(1)
    return builder.as_markup()


incorrect_data_text = """
Не удалось получить информацию о чеке.

Проверьте введенные данные и попробуйте снова.
Либо можете сформировать отчёт на основе введённых данных
"""


def incorrect_data_ikb() -> InlineKeyboardMarkup:
    """
        Подтверждение данных
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='✅Заполнить данные ',
            callback_data='confirm_incorrect_data'
        ),
        InlineKeyboardButton(
            text='⬅️Назад',
            callback_data='send_qr'
        ),
        InlineKeyboardButton(
            text='↩️ Главное меню',
            callback_data='start'
        )
    )
    builder.adjust(1)
    return builder.as_markup()


not_success_text = """
Статус чека: проверка не пройдена❌
Дата чека: {date}
ФД: {fd}
Итого: {sum}

Для формирования отчета с этими данными подтвердите эти данные
"""


def not_success_ikb() -> InlineKeyboardMarkup:
    """
        Подтверждение данных
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='✅ Подтвердить',
            callback_data='add_check'
        ),
        InlineKeyboardButton(
            text='⬅️Назад',
            callback_data='send_qr'
        ),
        InlineKeyboardButton(
            text='↩️ Главное меню',
            callback_data='start'
        )
    )
    builder.adjust(1)
    return builder.as_markup()


check_added_text = """
🎉 Ваш расход успешно добавлен в отчет! 🎉

Вы можете продолжить заполнение авансового отчета, добавив другие виды расходов.
Хотите добавить новый тип расхода в существующий отчет?
"""


def check_added_ikb() -> InlineKeyboardMarkup:
    """
        Добавление чека в отчет
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='✅ Да, добавить новый',
            callback_data='add_check'
        ),
        InlineKeyboardButton(
            text='❌ Нет, завершить отчет',
            callback_data='create_report'
        )
    )
    builder.adjust(1)
    return builder.as_markup()


class QRState(StatesGroup):
    """ Состояния """
    qr = State()
    fn = State()
    fp = State()
    fd = State()
    date = State()
    sum = State()


def manual_filling_ikb() -> InlineKeyboardMarkup:
    """
        Заполнить данные вручную либо попробовать еще раз отправить фото чека
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='Заполнить данные',
            callback_data='check_manual_filling'
        ),
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data='send_qr'
        )
    )
    builder.adjust(1)
    return builder.as_markup()


create_report_text = """
🎉 Ваш авансовый отчет успешно сформирован! 🎉
Вы можете скачать его.
"""