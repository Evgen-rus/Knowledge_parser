# Knowledge Parser

Утилита для парсинга Google Docs и Google Sheets в Markdown файлы.

## Описание

Knowledge Parser подключается к Google API, загружает и преобразует документы Google Docs и таблицы Google Sheets в Markdown формат. Утилита выполняет:

- Подключение к Google API с помощью сервисного аккаунта
- Загрузку документов и таблиц по их ID
- Очистку контента от метаданных и служебной информации
- Удаление секции "Термины" из документов
- Преобразование в формат Markdown
- Сохранение результата в соответствующие папки

## Структура проекта

```
.
├── credentials/        # Учетные данные для API
│   └── sheets-data-bot-b8f4cc6634fc.json
├── data/
│   ├── docs/           # Markdown-файлы из Google Docs
│   └── sheets/         # Markdown-файлы из Google Sheets
├── parse_google_doc.py # Модуль для работы с Google Docs
├── parse_google_sheet.py # Модуль для работы с Google Sheets
├── utils.py            # Вспомогательные функции
├── config.py           # Настройки проекта
├── requirements.txt    # Зависимости проекта
└── README.md
```

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Убедитесь, что файл учетных данных сервисного аккаунта находится в папке `credentials/`

## Использование

### Для парсинга Google Docs

```python
from parse_google_doc import main as parse_docs

document_ids = [
    "1QF_32LrnW-9mTy6u3FSHbguYon1nnlbqlt5hGvQ6NpY",  # ID документа
    # Добавьте другие ID документов
]

results = parse_docs(document_ids)
```

### Для парсинга Google Sheets

```python
from parse_google_sheet import main as parse_sheets

sheet_ids = [
    "1cGFr1_uNrBXP7LgYAIcnO-ywfZbvnFvK2pNY4Z3J3Z0",  # ID таблицы
    # Добавьте другие ID таблиц
]

results = parse_sheets(sheet_ids)
```

### Пример запуска из командной строки

Для Google Docs:
```bash
python parse_google_doc.py
```

Для Google Sheets:
```bash
python parse_google_sheet.py
```

## Настройка

Основные настройки проекта находятся в файле `config.py`. Здесь можно изменить:

- Пути к директориям
- Паттерны для очистки метаданных
- Шаблон имени файла для сохранения

## Требования

- Python 3.6+
- Доступ к Google API (сервисный аккаунт с необходимыми разрешениями)
- Установленные зависимости из requirements.txt 