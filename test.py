from docx import Document
from weasyprint import HTML

def docx_to_html(input_file):
    doc = Document(input_file)
    html_content = ""
    
    for para in doc.paragraphs:
        html_content += f"<p>{para.text}</p>"
        
    return html_content

def convert_docx_to_pdf(input_file, output_file):
    # Конвертируем .docx в HTML
    html_content = docx_to_html(input_file)
    
    # Конвертируем HTML в PDF с помощью WeasyPrint
    HTML(string=html_content).write_pdf(output_file)
    print(f"Файл успешно конвертирован в: {output_file}")

# Пример использования:
input_file = r"data/events.docx"
output_file = r"data/events.pdf"
convert_docx_to_pdf(input_file, output_file)
