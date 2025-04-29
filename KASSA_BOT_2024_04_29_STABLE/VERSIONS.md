# Версии и зависимости проекта Kassa Bot

## Зависимости проекта

### Основные зависимости
- Python 3.11+
- PostgreSQL 15+
- PowerShell 7.0+

### Версии пакетов

#### Основные пакеты
- FastAPI==0.109.2
- Uvicorn==0.27.1
- SQLAlchemy==2.0.27
- Alembic==1.13.1
- python-telegram-bot==20.8
- python-dotenv==1.0.1
- pydantic==2.6.1
- pydantic-settings==2.1.0
- psycopg2-binary==2.9.9
- python-multipart==0.0.9
- jinja2==3.1.3
- aiofiles==23.2.1

#### Пакеты для разработки
- pytest==7.4.4
- pytest-asyncio==0.23.5
- black==24.2.0
- isort==5.13.2
- mypy==1.8.0
- pytest-cov==4.1.0
- flake8==7.0.0
- pre-commit==3.6.0

### Версии API
- Telegram Bot API: последняя стабильная
- TON API: последняя стабильная

### Версии конфигурационных файлов
- requirements.txt: 1.0.0
- requirements-dev.txt: 1.0.0
- .env.example: 1.0.0

### Версии миграций базы данных
- Текущая версия: 001
- Последняя миграция: initial

## Системные требования

### Минимальные требования
- Windows 10/11
- PowerShell 7.0+
- Python 3.11+
- 2GB RAM
- 1GB свободного места на диске

### Рекомендуемые требования
- Windows 10/11
- PowerShell 7.2+
- Python 3.11+
- 4GB RAM
- 2GB свободного места на диске

## Процесс обновления

### Обновление зависимостей
```powershell
# Обновление production зависимостей
pip install -r requirements.txt --upgrade

# Обновление development зависимостей
pip install -r requirements-dev.txt --upgrade
```

### Обновление базы данных
```powershell
# Применение миграций
alembic upgrade head
```

## История версий

### 1.0.0 (Текущая)
- Первоначальный релиз
- Разделение зависимостей на production и development
- Адаптация команд для PowerShell
- Обновление документации

# Версии бота

## Стабильная версия от 27.04.2024
- Добавлена обработка повторной регистрации пользователей
- Улучшена система администрирования через Telegram ID
- Добавлено информативное сообщение о статусе пользователя при повторной регистрации
- Автоматическое направление пользователя к нужному действию в зависимости от его уровня 