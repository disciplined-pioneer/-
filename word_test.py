from docx import Document

def read_docx(file_path):
    doc = Document(file_path)
    text = []

    # Читаем все параграфы
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)

    # Читаем таблицы
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text for cell in row.cells]
            text.append(" | ".join(row_text))  # Форматируем таблицы в строку

    return "\n".join(text)

# Использование
file_path = "output.docx"
doc_text = read_docx(file_path)
print(doc_text)
