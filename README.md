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


Вот чёткие пошаговые инструкции, как исправить ошибку 403:

---

# ✅ Как включить Google Docs API для своего проекта

### 1. Перейти в Google Cloud Console
- Открой ссылку: https://console.cloud.google.com/
- Войди в свой аккаунт Google, если нужно.

### 2. Выбрать правильный проект
- Вверху панели нажми на выпадающий список рядом с именем проекта.
- Убедись, что выбран проект с ID `1040645545549` (или тот, в котором ты работаешь).

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

---

# ⚙️ Быстрая проверка
- После активации подожди 1–2 минуты.
- Попробуй снова запустить свой скрипт.
- Ошибка 403 должна исчезнуть.

---
