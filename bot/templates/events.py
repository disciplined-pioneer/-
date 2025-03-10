enter_template_data = "Введите данные для заполнения шаблона:\n💊 Выберите препарат из списка ниже"

select_document_type = "✨ Выберите тип документа: ✨"

def get_confirm_guest_addition(answers: dict) -> str:
    return (
        f"📋 Вы добавили участника:\n\n• ФИО: <b>{answers['guest_name']}</b>"
        f"\n• Место работы: <b>{answers['guest_workplace']}</b>"
        "\n\n🤔 Подтвердите добавление участника"
    )

max_participants_reached = "🚫 Достигнут предел по количеству участников. Максимум 10 человек."

participant_added_success = (
    "🥳 Участник успешно добавлен!"
    "\n\n• 🔄 Хотите добавить еще одного участника? Максимальное количество - 10 человек"
)

participant_addition_cancelled = "❌ Добавление участника отменено.\n\n🔄 Хотите попробовать снова?"

meeting_document_created = (
    "📄 Документ по встрече успешно создан!\n\n"
    "• 📂 Вы можете скачать файл:\n"
    "  • Файл 1:  [Прикрепленный файл подтверждающий документ(мероприятие)]\n\n"
    "Вы можете продолжить заполнение авансового отчета, добавив другие виды расходов.\n\n"
    "Хотите добавить новый тип расхода в существующий отчет?"
)

no_participants_for_document = "🚫 У вас нет добавленных участников для формирования документа."

def generate_meeting_confirmation_message(data, participants):

    # Формируем список участников
    participants_info = "\n".join(
        [f"\t\t• <b>{p['guest_name']}</b> ({p['guest_workplace']})" for p in participants]
    )
    
    # Получаем данные из 'data' и используем их для формирования сообщения
    message = (
        "📄 Все данные собраны!"
        "\n\nПожалуйста, подтвердите информацию перед отправкой:"
        f"\n\n- Место проведения: {data.get('answers', {}).get('meeting_theme', 'Не указано')}"
        f"\n\n - Тема собрания: {data.get('answers', {}).get('event_location', 'Не указано')}"
        f"\n\n - Приглашённые участники:\n{participants_info}"
    )
    
    return message

advance_report_generated = (
    '🎉 Ваш авансовый отчет успешно сформирован! 🎉'
    '\nВы можете скачать его по ссылке ниже:'
    '\n\n🔗 Скачать отчет'
)

advance_report_title = "Ваш авансовый отчёт 😊"

