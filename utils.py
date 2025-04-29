"""
Вспомогательные функции для парсера Google Docs и Google Sheets.
"""
import os
import re
from slugify import slugify
from config import (
    METADATA_PATTERNS, TERMS_SECTION_PATTERN, 
    TECHNICAL_INTRO_PATTERNS, CRM_REFERENCE_PATTERNS,
    LINK_PATTERNS, INTERNAL_INSTRUCTION_PATTERNS,
    DOCS_DIR, SHEETS_DIR, ORIGINAL_DOCS_DIR,
    CLEANING_LEVELS, EMPTY_TABLE_THRESHOLD
)


def create_directories():
    """
    Создает необходимые директории, если они не существуют.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(SHEETS_DIR, exist_ok=True)
    os.makedirs(ORIGINAL_DOCS_DIR, exist_ok=True)


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
    
    return text


def remove_terms_section(text):
    """
    Удаляет секцию "Термины" из текста.
    
    Args:
        text (str): Исходный текст.
        
    Returns:
        str: Текст без секции "Термины".
    """
    return re.sub(TERMS_SECTION_PATTERN, '', text, flags=re.MULTILINE)


def clean_technical_intros(text):
    """
    Очищает текст от технических вставок (Причина создания, Задача).
    
    Args:
        text (str): Исходный текст.
        
    Returns:
        str: Очищенный текст.
    """
    for pattern in TECHNICAL_INTRO_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.MULTILINE | re.DOTALL)
    
    return text


def clean_crm_references(text):
    """
    Очищает текст от упоминаний CRM-систем и этапов Битрикс24.
    
    Args:
        text (str): Исходный текст.
        
    Returns:
        str: Очищенный текст.
    """
    for pattern in CRM_REFERENCE_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    return text


def clean_links(text):
    """
    Очищает текст от прямых ссылок.
    
    Args:
        text (str): Исходный текст.
        
    Returns:
        str: Очищенный текст.
    """
    for pattern in LINK_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    
    return text


def clean_internal_instructions(text):
    """
    Очищает текст от внутренних инструкций и служебных меток.
    
    Args:
        text (str): Исходный текст.
        
    Returns:
        str: Очищенный текст.
    """
    for pattern in INTERNAL_INSTRUCTION_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.MULTILINE | re.DOTALL)
    
    return text


def clean_empty_tables(text):
    """
    Удаляет пустые и недозаполненные таблицы.
    
    Args:
        text (str): Исходный текст.
        
    Returns:
        str: Очищенный текст.
    """
    def is_empty_table(table_match):
        table_text = table_match.group(0)
        # Подсчитываем количество ячеек с содержимым
        total_cells = len(re.findall(r'\|[^|]+\|', table_text))
        empty_cells = len(re.findall(r'\|\s*\|', table_text))
        
        if total_cells == 0:
            return True
        
        empty_percent = (empty_cells / total_cells) * 100
        return empty_percent > EMPTY_TABLE_THRESHOLD
    
    # Находим все таблицы и проверяем их на пустоту
    table_pattern = r'\n\|[^\n]+\|\n\|[\s-]+\|\n(?:\|[^\n]+\|\n)+'
    return re.sub(table_pattern, lambda m: '' if is_empty_table(m) else m.group(0), text)


def standardize_placeholders(text):
    """
    Стандартизирует плейсхолдеры в тексте.
    
    Args:
        text (str): Исходный текст.
        
    Returns:
        str: Текст со стандартизированными плейсхолдерами.
    """
    # Заменяем различные форматы плейсхолдеров на единый формат {{placeholder}}
    text = re.sub(r'__([^_]+)__', r'{{{\1}}}', text)  # __placeholder__ -> {{placeholder}}
    text = re.sub(r'___(.*?)___', r'{{{\1}}}', text)  # ___placeholder___ -> {{placeholder}}
    text = re.sub(r'\[ВСТАВКА:\s*([^\]]+)\]', r'{{{\1}}}', text)  # [ВСТАВКА: placeholder] -> {{placeholder}}
    
    return text


def clean_formatting_artifacts(text):
    """
    Удаляет артефакты форматирования из текста.
    
    Args:
        text (str): Исходный текст.
        
    Returns:
        str: Очищенный текст.
    """
    # Удаляем множественные переносы строк
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Удаляем пустые строки в начале и конце
    text = re.sub(r'^\s+', '', text)
    text = re.sub(r'\s+$', '', text)
    
    # Удаляем лишние пробелы
    text = re.sub(r' {2,}', ' ', text)
    
    # Удаляем неразрывные пробелы и другие специальные символы
    text = text.replace('\xa0', ' ')
    
    return text


def apply_cleaning(text, cleaning_level="medium"):
    """
    Применяет очистку к тексту в соответствии с указанным уровнем.
    
    Args:
        text (str): Исходный текст.
        cleaning_level (str): Уровень очистки (low, medium, high).
        
    Returns:
        str: Очищенный текст.
    """
    cleaning_functions = {
        "metadata": lambda t: clean_metadata(t),
        "terms": lambda t: remove_terms_section(t),
        "technical_intro": lambda t: clean_technical_intros(t),
        "links": lambda t: clean_links(t),
        "crm_references": lambda t: clean_crm_references(t),
        "internal_instructions": lambda t: clean_internal_instructions(t),
        "empty_tables": lambda t: clean_empty_tables(t),
    }
    
    clean_text = text
    
    # Получаем список функций для применения
    functions_to_apply = CLEANING_LEVELS.get(cleaning_level, CLEANING_LEVELS["medium"])
    
    # Применяем функции очистки
    for func_name in functions_to_apply:
        if func_name in cleaning_functions:
            clean_text = cleaning_functions[func_name](clean_text)
    
    # Всегда применяем дополнительные очистки
    clean_text = standardize_placeholders(clean_text)
    clean_text = clean_formatting_artifacts(clean_text)
    
    return clean_text


def format_as_markdown(title, content, cleaning_level="medium"):
    """
    Форматирует текст по правилам Markdown и применяет очистку.
    
    Args:
        title (str): Заголовок документа.
        content (str): Содержимое документа.
        cleaning_level (str): Уровень очистки (low, medium, high).
        
    Returns:
        tuple: (Форматированный Markdown текст, очищенный Markdown текст).
    """
    # Форматируем основной заголовок
    markdown_content = f"# {title}\n\n{content}"
    
    # Создаем очищенную версию
    clean_content = apply_cleaning(markdown_content, cleaning_level)
    
    return markdown_content, clean_content


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


def save_original_and_clean(original_content, clean_content, filename):
    """
    Сохраняет оригинальную и очищенную версии документа.
    
    Args:
        original_content (str): Оригинальное содержимое.
        clean_content (str): Очищенное содержимое.
        filename (str): Имя файла.
        
    Returns:
        tuple: (Путь к оригинальному файлу, путь к очищенному файлу).
    """
    original_path = save_markdown(original_content, filename, ORIGINAL_DOCS_DIR)
    clean_path = save_markdown(clean_content, filename, DOCS_DIR)
    
    return original_path, clean_path


def get_cleaning_stats(original_text, cleaned_text):
    """
    Возвращает статистику очистки.
    
    Args:
        original_text (str): Исходный текст.
        cleaned_text (str): Очищенный текст.
        
    Returns:
        dict: Статистика очистки.
    """
    original_len = len(original_text)
    cleaned_len = len(cleaned_text)
    removed_chars = original_len - cleaned_len
    removed_percent = (removed_chars / original_len) * 100 if original_len > 0 else 0
    
    return {
        "original_size": original_len,
        "cleaned_size": cleaned_len,
        "removed_chars": removed_chars,
        "removed_percent": round(removed_percent, 2)
    } 