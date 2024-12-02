import argparse
import os
from docx import Document
import win32com.client

class DocumentConverter:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Убедимся, что выходной каталог существует
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def docx_to_md(self, docx_path):
        """
        Преобразует документ .docx в .md и сохраняет в указанном выходном каталоге.
        """
        output_md_path = os.path.join(self.output_dir, os.path.splitext(os.path.basename(docx_path))[0] + '.md')
        doc = Document(docx_path)

        with open(output_md_path, 'w', encoding='utf-8') as md_file:
            for para in doc.paragraphs:
                md_file.write(para.text + '\n\n')  # Пишем текст, добавляем пустую строку для разделения абзацев
        print(f'Конвертирован {docx_path} в {output_md_path}')

    def doc_to_docx(self, doc_path):
        """
        Преобразует .doc в .docx с использованием Microsoft Word через COM API.
        """
        output_docx_path = os.path.splitext(doc_path)[0] + '.docx'
        word = win32com.client.Dispatch("Word.Application")
        try:
            doc = word.Documents.Open(doc_path)
            doc.SaveAs(output_docx_path, FileFormat=16)  # 16 - это формат .docx
            doc.Close()
        except Exception as e:
            print(f"Ошибка при конвертации {doc_path} в .docx: {e}")
            raise
        finally:
            word.Quit()
        return output_docx_path

    def convert_documents(self):
        """
        Конвертирует все .doc и .docx файлы в указанном каталоге в .md.
        """
        for filename in os.listdir(self.input_dir):
            input_file = os.path.join(self.input_dir, filename)

            # Пропускаем папки
            if os.path.isdir(input_file):
                continue

            if filename.endswith('.docx'):
                # Если файл .docx, конвертируем его в .md
                self.docx_to_md(input_file)
                continue

            if filename.endswith('.doc'):
                # Если файл .doc, конвертируем его в .docx, затем в .md
                docx_path = self.doc_to_docx(input_file)
                self.docx_to_md(docx_path)
                os.remove(docx_path)  # Удаляем временный .docx файл
                continue

if __name__ == "__main__":
    # Получаем директорию, где находится скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Создание парсера аргументов командной строки
    parser = argparse.ArgumentParser(description="Конвертировать файлы .doc и .docx в .md.")
    parser.add_argument(
        "input_dir",
        type=str,
        nargs="?",
        default=os.path.join(script_dir, "data_doc"),
        help="Путь к каталогу с документами .doc и .docx. (по умолчанию: data_doc)"
    )
    parser.add_argument(
        "output_dir",
        type=str,
        nargs="?",
        default=os.path.join(script_dir, "data"),
        help="Путь к каталогу для сохранения файлов .md. (по умолчанию: data)"
    )
    args = parser.parse_args()

    # Инициализация и вызов метода конвертации
    converter = DocumentConverter(args.input_dir, args.output_dir)
    converter.convert_documents()
