"""
Модуль для парсинга Google Docs и преобразования в Markdown.
"""
import os
import re
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import CREDENTIALS_FILE, SCOPES, DOCS_DIR, ORIGINAL_DOCS_DIR, FILENAME_TEMPLATE
from utils import (
    slugify_filename, format_as_markdown, save_markdown, 
    create_directories, save_original_and_clean, get_cleaning_stats
)


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


def parse_doc(document_id, cleaning_level="medium", save_original=True):
    """
    Основная функция парсинга документа.
    
    Args:
        document_id (str): ID документа Google Docs.
        cleaning_level (str): Уровень очистки документа (low, medium, high).
        save_original (bool): Сохранять ли оригинальную версию документа.
        
    Returns:
        tuple: (Путь к очищенному файлу, статистика очистки) или (None, None) в случае ошибки.
    """
    # Создаем необходимые директории
    create_directories()
    
    # Аутентификация
    service = authenticate_docs()
    if not service:
        return None, None
    
    # Получаем документ
    document = get_document(service, document_id)
    if not document:
        return None, None
    
    # Преобразуем документ в Markdown
    title, content = gdoc_to_markdown(document)
    
    # Форматируем документ в Markdown и получаем очищенную версию
    original_content, clean_content = format_as_markdown(title, content, cleaning_level)
    
    # Получаем статистику очистки
    stats = get_cleaning_stats(original_content, clean_content)
    
    # Формируем имя файла
    filename = FILENAME_TEMPLATE.format(slugify_filename(title))
    
    # Сохраняем файлы
    if save_original:
        original_path, clean_path = save_original_and_clean(original_content, clean_content, filename)
        return clean_path, stats
    else:
        clean_path = save_markdown(clean_content, filename, DOCS_DIR)
        return clean_path, stats


def main(document_ids, cleaning_level="medium", save_original=True):
    """
    Точка входа для обработки списка документов.
    
    Args:
        document_ids (list): Список ID документов для обработки.
        cleaning_level (str): Уровень очистки документа (low, medium, high).
        save_original (bool): Сохранять ли оригинальную версию документа.
        
    Returns:
        list: Список результатов обработки документов.
    """
    results = []
    
    for doc_id in document_ids:
        clean_path, stats = parse_doc(doc_id, cleaning_level, save_original)
        if clean_path:
            result = {
                "document_id": doc_id,
                "path": clean_path,
                "stats": stats
            }
            results.append(result)
            print(f"Документ {doc_id} успешно преобразован и сохранен:")
            print(f"  Путь: {clean_path}")
            print(f"  Размер оригинала: {stats['original_size']} символов")
            print(f"  Размер после очистки: {stats['cleaned_size']} символов")
            print(f"  Удалено: {stats['removed_chars']} символов ({stats['removed_percent']}%)")
        else:
            print(f"Не удалось обработать документ {doc_id}")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Парсинг Google Docs и преобразование в Markdown')
    parser.add_argument('--doc_ids', nargs='+', help='ID документов Google Docs для обработки')
    parser.add_argument('--cleaning_level', choices=['low', 'medium', 'high'], default='medium', 
                        help='Уровень очистки документа (low, medium, high)')
    parser.add_argument('--no_save_original', action='store_true', help='Не сохранять оригинальную версию документа')
    
    args = parser.parse_args()
    
    if args.doc_ids:
        doc_ids = args.doc_ids
    else:
        # Пример использования, если не указаны аргументы командной строки
        doc_ids = [
            "1QF_32LrnW-9mTy6u3FSHbguYon1nnlbqlt5hGvQ6NpY"  # Пример ID документа
        ]
    
    main(doc_ids, args.cleaning_level, not args.no_save_original) 