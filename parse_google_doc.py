"""
Модуль для парсинга Google Docs и преобразования в Markdown.
"""
import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import CREDENTIALS_FILE, SCOPES, DOCS_DIR, FILENAME_TEMPLATE
from utils import slugify_filename, format_as_markdown, save_markdown, create_directories


def authenticate_docs():
    """
    Аутентификация в Google Docs API с использованием существующих учётных данных.
    
    Returns:
        service: Авторизованный сервис Google Docs API.
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        service = build('docs', 'v1', credentials=credentials)
        return service
    except Exception as e:
        print(f"Ошибка аутентификации: {e}")
        return None


def get_document(service, document_id):
    """
    Загрузка документа по ID.
    
    Args:
        service: Авторизованный сервис Google Docs API.
        document_id (str): ID документа Google Docs.
        
    Returns:
        dict: Документ в формате JSON.
    """
    try:
        document = service.documents().get(documentId=document_id).execute()
        return document
    except HttpError as e:
        print(f"Ошибка при загрузке документа {document_id}: {e}")
        return None


def extract_document_title(document):
    """
    Извлечение заголовка документа.
    
    Args:
        document (dict): Документ в формате JSON.
        
    Returns:
        str: Заголовок документа.
    """
    return document.get('title', 'Untitled Document')


def process_paragraph(paragraph):
    """
    Обработка абзаца документа.
    
    Args:
        paragraph (dict): Абзац документа в формате JSON.
        
    Returns:
        str: Текст абзаца в формате Markdown.
    """
    text = ""
    elements = paragraph.get('elements', [])
    
    for element in elements:
        if 'textRun' in element:
            content = element['textRun'].get('content', '')
            text += content
    
    return text


def process_table(table):
    """
    Обработка таблицы в документе.
    
    Args:
        table (dict): Таблица документа в формате JSON.
        
    Returns:
        str: Таблица в формате Markdown.
    """
    markdown_table = ""
    table_rows = table.get('tableRows', [])
    
    # Обрабатываем каждую строку таблицы
    for i, row in enumerate(table_rows):
        row_content = []
        cells = row.get('tableCells', [])
        
        for cell in cells:
            cell_content = ""
            for paragraph in cell.get('content', []):
                if 'paragraph' in paragraph:
                    cell_content += process_paragraph(paragraph['paragraph'])
            row_content.append(cell_content.strip())
        
        markdown_table += "| " + " | ".join(row_content) + " |\n"
        
        # Добавляем разделитель после заголовка таблицы
        if i == 0:
            markdown_table += "| " + " | ".join(["---"] * len(cells)) + " |\n"
    
    return markdown_table


def gdoc_to_markdown(document):
    """
    Преобразование структуры документа в Markdown.
    
    Args:
        document (dict): Документ в формате JSON.
        
    Returns:
        tuple: (заголовок документа, содержимое в формате Markdown).
    """
    title = extract_document_title(document)
    content = ""
    
    # Обрабатываем содержимое документа
    for item in document.get('body', {}).get('content', []):
        if 'paragraph' in item:
            paragraph = item['paragraph']
            paragraph_style = paragraph.get('paragraphStyle', {})
            
            # Обрабатываем стили заголовков
            if 'namedStyleType' in paragraph_style:
                style = paragraph_style['namedStyleType']
                text = process_paragraph(paragraph)
                
                if style == 'HEADING_1':
                    content += f"## {text}\n\n"
                elif style == 'HEADING_2':
                    content += f"### {text}\n\n"
                elif style == 'HEADING_3':
                    content += f"#### {text}\n\n"
                else:
                    content += f"{text}\n\n"
            else:
                text = process_paragraph(paragraph)
                content += f"{text}\n\n"
                
        elif 'table' in item:
            table = item['table']
            content += process_table(table) + "\n\n"
    
    return title, content


def parse_doc(document_id):
    """
    Основная функция парсинга документа.
    
    Args:
        document_id (str): ID документа Google Docs.
        
    Returns:
        str: Путь к сохраненному Markdown файлу или None в случае ошибки.
    """
    # Создаем необходимые директории
    create_directories()
    
    # Аутентификация
    service = authenticate_docs()
    if not service:
        return None
    
    # Получаем документ
    document = get_document(service, document_id)
    if not document:
        return None
    
    # Преобразуем документ в Markdown
    title, content = gdoc_to_markdown(document)
    
    # Форматируем документ в Markdown
    markdown_content = format_as_markdown(title, content)
    
    # Формируем имя файла и сохраняем
    filename = FILENAME_TEMPLATE.format(slugify_filename(title))
    return save_markdown(markdown_content, filename, DOCS_DIR)


def main(document_ids):
    """
    Точка входа для обработки списка документов.
    
    Args:
        document_ids (list): Список ID документов для обработки.
        
    Returns:
        list: Список путей к сохраненным файлам.
    """
    results = []
    
    for doc_id in document_ids:
        result = parse_doc(doc_id)
        if result:
            results.append(result)
            print(f"Документ {doc_id} успешно преобразован и сохранен: {result}")
        else:
            print(f"Не удалось обработать документ {doc_id}")
    
    return results


if __name__ == "__main__":
    # Пример использования
    docs_to_parse = [
        "1QF_32LrnW-9mTy6u3FSHbguYon1nnlbqlt5hGvQ6NpY"  # Пример ID документа
    ]
    main(docs_to_parse) 