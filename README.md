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
│   ├── docs/           # Очищенные Markdown-файлы из Google Docs
│   ├── docs_original/  # Оригинальные Markdown-файлы из Google Docs
│   └── sheets/         # Markdown-файлы из Google Sheets
├── parse_google_doc.py # Модуль для работы с Google Docs
├── parse_google_sheet.py # Модуль для работы с Google Sheets
├── parse_links.py      # Модуль для парсинга ссылок из текстового файла
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

# Базовый вариант
results = parse_docs(document_ids)

# С указанием параметров очистки
results = parse_docs(
    document_ids,
    cleaning_level="high",  # Доступные уровни: low, medium, high
    save_original=True      # Сохранять ли оригинал
)
```

Запуск из командной строки с параметрами:

```bash
# Базовое использование
python parse_google_doc.py

# С указанием ID документов
python parse_google_doc.py --doc_ids ID1 ID2 ID3

# С выбором уровня очистки
python parse_google_doc.py --cleaning_level high

# Без сохранения оригиналов
python parse_google_doc.py --no_save_original
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

### Для парсинга ссылок из текстового файла

```bash
# Базовое использование (откроется диалоговое окно)
python parse_links.py
python parse_links.py --cleaning_level high --no_save_original

# Указание пути к файлу с ссылками
python parse_links.py --file path/to/your/links.txt

# Выбор уровня очистки
python parse_links.py --cleaning_level high

# Отключение сохранения оригиналов
python parse_links.py --no_save_original

# Комбинация параметров
python parse_links.py --file path/to/your/links.txt --cleaning_level high --no_save_original
```

После запуска откроется диалоговое окно для выбора текстового файла со ссылками (если не указан параметр `--file`). 
Скрипт автоматически определит, какие ссылки ведут на Google Docs, а какие на Google Sheets, 
и вызовет соответствующие парсеры.

## Уровни очистки документов

Knowledge Parser поддерживает несколько уровней очистки документов:

- **low**: базовая очистка (удаление метаданных и секции "Термины")
- **medium** (по умолчанию): средняя очистка (дополнительно удаляет технические вставки и ссылки)
- **high**: интенсивная очистка (дополнительно удаляет упоминания CRM, внутренние инструкции и пустые таблицы)

## Настройка

Основные настройки проекта находятся в файле `config.py`. Здесь можно изменить:

- Пути к директориям
- Паттерны для очистки метаданных
- Паттерны для других типов очистки
- Шаблон имени файла для сохранения
- Настройки уровней очистки

## Требования

- Python 3.6+
- Доступ к Google API (сервисный аккаунт с необходимыми разрешениями)
- Установленные зависимости из requirements.txt


## Как включить Google Docs API для своего проекта

### 1. Перейти в Google Cloud Console
- Открой ссылку: https://console.cloud.google.com/
- Войди в свой аккаунт Google, если нужно.

### 2. Выбрать правильный проект
- Вверху панели нажми на выпадающий список рядом с именем проекта.
- Убедись, что выбран проект с ID `............`в котором ты работаешь.

### 3. Включить Google Docs API
- Перейди сюда: https://console.cloud.google.com/apis/api/docs.googleapis.com/overview
- Проверь, какой проект выбран вверху.
- Нажми кнопку **"Enable"** (или **"Включить"**).

### 4. Проверить права доступа
- Убедись, что у сервисного аккаунта есть роли:
  - `Editor` или
  - специфические права к **Google Docs API**.
- Если нет, добавь через IAM-панель (IAM & Admin → IAM → Add).

### 5. Убедиться в подключении к Google Drive API (если нужно получать доступ через Drive)
- Если ты загружаешь документы по ID из Drive, ещё нужно включить Google Drive API:
  - https://console.cloud.google.com/apis/api/drive.googleapis.com/overview
  - Нажать **"Enable"**.

### Быстрая проверка
- После активации подожди 1–2 минуты.
- Попробуй снова запустить свой скрипт.
- Ошибка 403 должна исчезнуть.
