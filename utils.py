"""
Вспомогательные функции для парсера Google Docs и Google Sheets.
"""
import os
import re
from slugify import slugify
from config import METADATA_PATTERNS, TERMS_SECTION_PATTERN, DOCS_DIR, SHEETS_DIR


def create_directories():
    """
    Создает необходимые директории, если они не существуют.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(SHEETS_DIR, exist_ok=True)


def slugify_filename(title):
    """
    Преобразует название документа в валидное имя файла.
    
    Args:
        title (str): Название документа.
        
    Returns:
        str: Имя файла для сохранения.
    """
    # Удаляем обозначения версии типа [ЛидгенБюро ИП 1.3 ]
    title = re.sub(r'\[.*?\]', '', title).strip()
    return slugify(title)


def clean_metadata(text, patterns=METADATA_PATTERNS):
    """
    Очищает текст от метаданных по шаблонам.
    
    Args:
        text (str): Исходный текст.
        patterns (list): Список регулярных выражений для удаления.
        
    Returns:
        str: Очищенный текст.
    """
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    
    # Удаляем пустые строки в начале и дополнительные пробелы
    text = re.sub(r'^\s+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def remove_terms_section(text):
    """
    Удаляет секцию "Термины" из текста.
    
    Args:
        text (str): Исходный текст.
        
    Returns:
        str: Текст без секции "Термины".
    """
    return re.sub(TERMS_SECTION_PATTERN, '', text, flags=re.MULTILINE)


def format_as_markdown(title, content):
    """
    Форматирует текст по правилам Markdown.
    
    Args:
        title (str): Заголовок документа.
        content (str): Содержимое документа.
        
    Returns:
        str: Форматированный Markdown текст.
    """
    # Удаляем метаданные и секцию терминов
    clean_content = clean_metadata(content)
    clean_content = remove_terms_section(clean_content)
    
    # Форматируем основной заголовок
    markdown_content = f"# {title}\n\n"
    
    # Добавляем очищенное содержимое
    markdown_content += clean_content
    
    return markdown_content


def save_markdown(content, filename, directory):
    """
    Сохраняет Markdown в файл.
    
    Args:
        content (str): Содержимое для сохранения.
        filename (str): Имя файла.
        directory (str): Директория для сохранения.
        
    Returns:
        str: Путь к сохраненному файлу.
    """
    filepath = os.path.join(directory, filename)
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return filepath 