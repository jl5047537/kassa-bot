# KASSA_BOT

Telegram бот для управления кассой и реферальной системой.

## Содержание
- [Установка](#установка)
- [Настройка](#настройка)
- [Запуск](#запуск)
- [Структура проекта](#структура-проекта)
- [Система логирования](#система-логирования)
- [Разработка](#разработка)
- [Тестирование](#тестирование)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/KASSA_BOT.git
cd KASSA_BOT
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

1. Создайте файл `config.env` на основе примера:
```env
# Database settings
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=kassa_bot

# Bot settings
TELEGRAM_BOT_TOKEN=your_bot_token
USER_CONFIG_FILE=user_config.json

# JWT settings
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application settings
PROJECT_NAME=Kassa Bot
VERSION=1.0.0
API_V1_STR=/api/v1

# Logging settings
LOG_LEVEL=DEBUG
LOG_FILE=kassa_bot.log

# Admin settings
MAIN_ADMIN_ID=your_admin_id
ADMIN_NOTIFICATION_ENABLED=true
```

2. Настройте базу данных:
```bash
python create_db.py
```

## Запуск

```bash
python run.py
```

## Структура проекта

```
KASSA_BOT/
├── bot/                    # Основной код бота
│   ├── core/              # Основные модули
│   │   ├── config.py      # Конфигурация
│   │   ├── logger.py      # Система логирования
│   │   └── db_logger.py   # Логирование в БД
│   ├── database/          # Работа с БД
│   ├── handlers/          # Обработчики команд
│   └── keyboards/         # Клавиатуры
├── docs/                  # Документация
├── logs/                  # Логи
├── tests/                 # Тесты
└── backups/              # Резервные копии
```

## Система логирования

Проект использует многоуровневую систему логирования:

### 1. Уровни логирования
- DEBUG: Детальная информация для отладки
- INFO: Общая информация о работе
- WARNING: Предупреждения
- ERROR: Ошибки
- CRITICAL: Критические ошибки

### 2. Настройка логирования
Логирование настраивается через переменные окружения:
```env
LOG_LEVEL=DEBUG          # Уровень логирования
LOG_FILE=kassa_bot.log   # Имя файла логов
```

### 3. Форматы логов
- JSON формат для файлов
- Текстовый формат для консоли
- Структурированное хранение в БД

### 4. Ротация логов
- Максимальный размер файла: 10MB
- Хранится 5 бэкапов
- Автоматическое создание новых файлов

### 5. Хранение в базе данных
Логи уровня INFO и выше сохраняются в БД с дополнительной информацией:
- Временная метка
- Уровень логирования
- Имя логгера
- Сообщение
- Модуль и функция
- Дополнительные данные

### 6. Мониторинг
- Отслеживание ошибок
- Анализ производительности
- Статистика использования

## Разработка

1. Создайте ветку для новой функции:
```bash
git checkout -b feature/your-feature
```

2. Внесите изменения и закоммитьте:
```bash
git add .
git commit -m "Описание изменений"
```

3. Отправьте изменения:
```bash
git push origin feature/your-feature
```

## Тестирование

```bash
python -m pytest tests/
```

## Функциональность

- Регистрация пользователей
- Реферальная система
- Уровни пользователей
- Административная панель
- Управление пользователями
- Статистика и аналитика

## Лицензия

MIT 