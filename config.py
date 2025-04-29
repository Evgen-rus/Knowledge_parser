"""
Конфигурационный файл для парсера Google Docs и Google Sheets.
Содержит пути, настройки API и паттерны для обработки документов.
"""
import os
from pathlib import Path

# Пути к директориям
BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials', 'sheets-data-bot-b8f4cc6634fc.json')
DOCS_DIR = os.path.join(BASE_DIR, 'data', 'docs')
SHEETS_DIR = os.path.join(BASE_DIR, 'data', 'sheets')
ORIGINAL_DOCS_DIR = os.path.join(BASE_DIR, 'data', 'docs_original')

# API настройки
SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

# Паттерны для очистки метаданных
METADATA_PATTERNS = [
    r"Конфиденциально\s*",
    r"Автор:.*",
    r"Для кого предназначено:.*",
    r"Дата издания:.*",
    r"Версия:.*",
]

# Паттерн для удаления секции "Термины"
TERMS_SECTION_PATTERN = r"Термины:[\s\S]*?(?=\n\s*\n\S|\Z)"

# Паттерны для очистки технических вставок
TECHNICAL_INTRO_PATTERNS = [
    r"Причина создания:.*?(?=\n\s*\n)",
    r"Задача:.*?(?=\n\s*\n)",
]

# Паттерны для очистки упоминаний CRM
CRM_REFERENCE_PATTERNS = [
    r"Б24|B24|Битрикс24",
    r"карточк[а-я]+ сделки",
    r"этап[а-я]* \"[^\"]+\"",
    r"сделк[а-я]+ в этап",
]

# Паттерны для очистки ссылок
LINK_PATTERNS = [
    r"https?://(?:www\.)?(?:docs\.google\.com|t\.me|bit\.ly|goo\.gl)[^\s)]+",
    r"\bhttps?://\S+",
]

# Паттерны для очистки внутренних инструкций
INTERNAL_INSTRUCTION_PATTERNS = [
    r"\[см\. [^\]]+\]",
    r"\[Пояснение для [^\]]+\]",
    r"\[ДЕЙСТВИЯ В Б24[^\]]*\]",
    r"Смотреть таблицу.*",
    r"ВНИМАНИЕ!.*?(?=\n)",
]

# Шаблон имени файла для сохранения
FILENAME_TEMPLATE = "leadgen_{}.md"

# Уровни очистки
CLEANING_LEVELS = {
    "low": ["metadata", "terms"],
    "medium": ["metadata", "terms", "technical_intro", "links"],
    "high": ["metadata", "terms", "technical_intro", "links", "crm_references", "internal_instructions", "empty_tables"],
}

# Порог пустой таблицы (% пустых ячеек)
EMPTY_TABLE_THRESHOLD = 70 