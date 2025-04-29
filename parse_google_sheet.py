"""
Модуль для парсинга Google Sheets и преобразования в Markdown.
"""
import os
import argparse
import gspread
from google.oauth2 import service_account

from config import CREDENTIALS_FILE, SCOPES, SHEETS_DIR, ORIGINAL_DOCS_DIR, FILENAME_TEMPLATE
from utils import (
    slugify_filename, format_as_markdown, save_markdown, 
    create_directories, save_original_and_clean, get_cleaning_stats
)


def authenticate_sheets():
    """
    Аутентификация в Google Sheets API с использованием существующих учётных данных.
    
    Returns:
        gspread.Client: Авторизованный клиент gspread.
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        print(f"Ошибка аутентификации: {e}")
        return None


def get_sheet(client, sheet_id):
    """
    Загрузка таблицы по ID.
    
    Args:
        client (gspread.Client): Авторизованный клиент gspread.
        sheet_id (str): ID таблицы Google Sheets.
        
    Returns:
        gspread.Spreadsheet: Таблица Google Sheets.
    """
    try:
        sheet = client.open_by_key(sheet_id)
        return sheet
    except Exception as e:
        print(f"Ошибка при загрузке таблицы {sheet_id}: {e}")
        return None


def extract_sheet_title(sheet):
    """
    Извлечение названия таблицы.
    
    Args:
        sheet (gspread.Spreadsheet): Таблица Google Sheets.
        
    Returns:
        str: Название таблицы.
    """
    return sheet.title


def sheet_to_markdown(sheet):
    """
    Преобразование данных таблицы в Markdown.
    
    Args:
        sheet (gspread.Spreadsheet): Таблица Google Sheets.
        
    Returns:
        str: Содержимое таблицы в формате Markdown.
    """
    content = ""
    
    # Обрабатываем все листы таблицы
    for worksheet in sheet.worksheets():
        worksheet_title = worksheet.title
        content += f"## {worksheet_title}\n\n"
        
        # Получаем все значения таблицы
        values = worksheet.get_all_values()
        
        if not values:
            content += "*Пустой лист*\n\n"
            continue
        
        # Создаем markdown-таблицу
        markdown_table = ""
        
        # Добавляем заголовок таблицы
        header_row = values[0]
        markdown_table += "| " + " | ".join(header_row) + " |\n"
        markdown_table += "| " + " | ".join(["---"] * len(header_row)) + " |\n"
        
        # Добавляем данные
        for row in values[1:]:
            markdown_table += "| " + " | ".join(row) + " |\n"
        
        content += markdown_table + "\n\n"
    
    return content


def parse_sheet(sheet_id, cleaning_level="medium", save_original=True):
    """
    Основная функция парсинга таблицы.
    
    Args:
        sheet_id (str): ID таблицы Google Sheets.
        cleaning_level (str): Уровень очистки (low, medium, high).
        save_original (bool): Сохранять ли оригинальную версию документа.
        
    Returns:
        tuple: (Путь к очищенному файлу, статистика очистки) или (None, None) в случае ошибки.
    """
    # Создаем необходимые директории
    create_directories()
    
    # Аутентификация
    client = authenticate_sheets()
    if not client:
        return None, None
    
    # Получаем таблицу
    sheet = get_sheet(client, sheet_id)
    if not sheet:
        return None, None
    
    # Получаем название таблицы
    title = extract_sheet_title(sheet)
    
    # Преобразуем таблицу в Markdown
    content = sheet_to_markdown(sheet)
    
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
        clean_path = save_markdown(clean_content, filename, SHEETS_DIR)
        return clean_path, stats


def main(sheet_ids, cleaning_level="medium", save_original=True):
    """
    Точка входа для обработки списка таблиц.
    
    Args:
        sheet_ids (list): Список ID таблиц для обработки.
        cleaning_level (str): Уровень очистки (low, medium, high).
        save_original (bool): Сохранять ли оригинальную версию документа.
        
    Returns:
        list: Список результатов обработки таблиц.
    """
    results = []
    
    for sheet_id in sheet_ids:
        clean_path, stats = parse_sheet(sheet_id, cleaning_level, save_original)
        if clean_path:
            result = {
                "sheet_id": sheet_id,
                "path": clean_path,
                "stats": stats
            }
            results.append(result)
            print(f"Таблица {sheet_id} успешно преобразована и сохранена:")
            print(f"  Путь: {clean_path}")
            print(f"  Размер оригинала: {stats['original_size']} символов")
            print(f"  Размер после очистки: {stats['cleaned_size']} символов")
            print(f"  Удалено: {stats['removed_chars']} символов ({stats['removed_percent']}%)")
        else:
            print(f"Не удалось обработать таблицу {sheet_id}")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Парсинг Google Sheets и преобразование в Markdown')
    parser.add_argument('--sheet_ids', nargs='+', help='ID таблиц Google Sheets для обработки')
    parser.add_argument('--cleaning_level', choices=['low', 'medium', 'high'], default='medium', 
                        help='Уровень очистки (low, medium, high)')
    parser.add_argument('--no_save_original', action='store_true', help='Не сохранять оригинальную версию')
    
    args = parser.parse_args()
    
    if args.sheet_ids:
        sheet_ids = args.sheet_ids
    else:
        # Пример использования, если не указаны аргументы командной строки
        sheet_ids = [
            "1pEMXESx81j47G4MZef5fWXSxkVsUSvuZ6Ig4a1NHY3k"  # Пример ID таблицы
        ]
    
    main(sheet_ids, args.cleaning_level, not args.no_save_original) 