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

# Шаблон имени файла для сохранения
FILENAME_TEMPLATE = "leadgen_{}.md" 