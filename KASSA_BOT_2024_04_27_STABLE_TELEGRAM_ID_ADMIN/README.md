# Kassa Bot

Веб-приложение для управления кассой и реферальной системой.

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example`

4. Примените миграции базы данных:
```bash
alembic upgrade head
```

## Установка зависимостей

### Production
```bash
pip install -r requirements.txt
```

### Development
```bash
pip install -r requirements-dev.txt
```

## Запуск

1. Запуск сервера разработки:
```bash
uvicorn app.main:app --reload
```

2. Запуск бота:
```bash
python bot/main.py
```

## Структура проекта

```
kassa_bot/
├── alembic/              # Миграции базы данных
├── app/                  # Основное приложение
│   ├── api/             # API эндпоинты
│   ├── core/            # Основные настройки
│   ├── db/              # Настройки базы данных
│   ├── models/          # SQLAlchemy модели
│   ├── schemas/         # Pydantic схемы
│   └── templates/       # Jinja2 шаблоны
├── bot/                 # Telegram бот
├── static/              # Статические файлы
├── tests/               # Тесты
├── .env                 # Переменные окружения
├── alembic.ini         # Конфигурация Alembic
└── main.py             # Точка входа
```

- `requirements.txt` - основные зависимости для production
- `requirements-dev.txt` - дополнительные зависимости для разработки
- `bot/` - код Telegram бота
- `app/` - FastAPI приложение
- `alembic/` - миграции базы данных

## Технологии

- FastAPI - веб-фреймворк
- SQLAlchemy - ORM
- Alembic - миграции базы данных
- python-telegram-bot - Telegram бот
- Jinja2 - шаблонизатор
- PostgreSQL - база данных 

## Запуск

1. Установите зависимости:
   ```bash
   # Для production
   pip install -r requirements.txt
   
   # Для разработки
   pip install -r requirements-dev.txt
   ```

2. Настройте переменные окружения (скопируйте .env.example в .env)

3. Запустите бота:
   ```bash
   python bot.py
   ```

4. Запустите FastAPI приложение:
   ```bash
   uvicorn app.main:app --reload
   ```

## Тестирование

```bash
pytest
```

## Линтинг

```bash
# Форматирование кода
black .

# Сортировка импортов
isort .

# Проверка типов
mypy .
``` 