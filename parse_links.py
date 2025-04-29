"""
Модуль для парсинга ссылок на Google Docs и Google Sheets из текстового файла.
Позволяет пользователю выбрать файл через проводник и автоматически обрабатывает
все найденные ссылки на документы и таблицы.
"""
import os
import re
import tkinter as tk
from tkinter import filedialog

from parse_google_doc import main as parse_docs
from parse_google_sheet import main as parse_sheets


def select_file():
    """
    Открывает диалоговое окно для выбора файла со ссылками.
    
    Returns:
        str: Путь к выбранному файлу или None, если выбор отменен.
    """
    root = tk.Tk()
    root.withdraw()  # Скрываем основное окно tkinter
    
    file_path = filedialog.askopenfilename(
        title="Выберите файл со ссылками",
        filetypes=[
            ("Текстовые файлы", "*.txt"), 
            ("Markdown файлы", "*.md"),
            ("Все файлы", "*.*")
        ]
    )
    
    return file_path if file_path else None


def extract_document_id_from_url(url):
    """
    Извлекает ID документа из URL Google Docs или Google Sheets.
    
    Args:
        url (str): URL документа.
        
    Returns:
        str: ID документа или None, если ID не найден.
    """
    # Шаблоны для извлечения ID документов из URL
    patterns = [
        r'document/d/([a-zA-Z0-9_-]+)',  # Для Google Docs
        r'spreadsheets/d/([a-zA-Z0-9_-]+)'  # Для Google Sheets
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def determine_resource_type(url):
    """
    Определяет тип ресурса (Google Docs или Google Sheets) по URL.
    
    Args:
        url (str): URL документа.
        
    Returns:
        str: 'doc' для Google Docs, 'sheet' для Google Sheets, или None для других URL.
    """
    if '/document/' in url:
        return 'doc'
    elif '/spreadsheets/' in url:
        return 'sheet'
    return None


def parse_links_file(file_path):
    """
    Парсит файл со ссылками и вызывает соответствующие парсеры.
    
    Args:
        file_path (str): Путь к файлу со ссылками.
        
    Returns:
        tuple: (список обработанных документов, список обработанных таблиц)
    """
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return [], []
    
    doc_ids = []
    sheet_ids = []
    
    # Извлекаем URL и определяем типы документов
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            
            # Ищем ссылки в строке
            urls = re.findall(r'https?://[^\s]+', line)
            
            for url in urls:
                doc_id = extract_document_id_from_url(url)
                if not doc_id:
                    continue
                
                resource_type = determine_resource_type(url)
                if resource_type == 'doc':
                    doc_ids.append(doc_id)
                elif resource_type == 'sheet':
                    sheet_ids.append(doc_id)
    
    # Обрабатываем найденные документы
    doc_results = []
    sheet_results = []
    
    if doc_ids:
        print(f"Найдено {len(doc_ids)} документов Google Docs. Обработка...")
        doc_results = parse_docs(doc_ids)
    
    if sheet_ids:
        print(f"Найдено {len(sheet_ids)} таблиц Google Sheets. Обработка...")
        sheet_results = parse_sheets(sheet_ids)
    
    return doc_results, sheet_results


def main():
    """
    Основная функция программы. Открывает диалоговое окно выбора файла
    и запускает обработку ссылок.
    """
    print("Запуск парсера ссылок Knowledge Parser...")
    
    file_path = select_file()
    if not file_path:
        print("Выбор файла отменен.")
        return
    
    print(f"Выбран файл: {file_path}")
    doc_results, sheet_results = parse_links_file(file_path)
    
    # Выводим итоги обработки
    total_docs = len(doc_results)
    total_sheets = len(sheet_results)
    
    print("\nИтоги обработки:")
    print(f"Обработано документов: {total_docs}")
    print(f"Обработано таблиц: {total_sheets}")
    print(f"Всего обработано: {total_docs + total_sheets}")


if __name__ == "__main__":
    main() 