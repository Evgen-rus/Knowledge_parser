"""
Модуль для парсинга Google Sheets и преобразования в Markdown.
"""
import os
import gspread
from google.oauth2 import service_account

from config import CREDENTIALS_FILE, SCOPES, SHEETS_DIR, FILENAME_TEMPLATE
from utils import slugify_filename, format_as_markdown, save_markdown, create_directories


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


def parse_sheet(sheet_id):
    """
    Основная функция парсинга таблицы.
    
    Args:
        sheet_id (str): ID таблицы Google Sheets.
        
    Returns:
        str: Путь к сохраненному Markdown файлу или None в случае ошибки.
    """
    # Создаем необходимые директории
    create_directories()
    
    # Аутентификация
    client = authenticate_sheets()
    if not client:
        return None
    
    # Получаем таблицу
    sheet = get_sheet(client, sheet_id)
    if not sheet:
        return None
    
    # Получаем название таблицы
    title = extract_sheet_title(sheet)
    
    # Преобразуем таблицу в Markdown
    content = sheet_to_markdown(sheet)
    
    # Форматируем документ в Markdown
    markdown_content = format_as_markdown(title, content)
    
    # Формируем имя файла и сохраняем
    filename = FILENAME_TEMPLATE.format(slugify_filename(title))
    return save_markdown(markdown_content, filename, SHEETS_DIR)


def main(sheet_ids):
    """
    Точка входа для обработки списка таблиц.
    
    Args:
        sheet_ids (list): Список ID таблиц для обработки.
        
    Returns:
        list: Список путей к сохраненным файлам.
    """
    results = []
    
    for sheet_id in sheet_ids:
        result = parse_sheet(sheet_id)
        if result:
            results.append(result)
            print(f"Таблица {sheet_id} успешно преобразована и сохранена: {result}")
        else:
            print(f"Не удалось обработать таблицу {sheet_id}")
    
    return results


if __name__ == "__main__":
    # Пример использования
    sheets_to_parse = [
        "1pEMXESx81j47G4MZef5fWXSxkVsUSvuZ6Ig4a1NHY3k"  # Пример ID таблицы
    ]
    main(sheets_to_parse) 