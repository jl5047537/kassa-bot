# Kassa Bot

Телеграм-бот для управления пользователями и администраторами.

## Функциональность

- Регистрация пользователей
- Управление пользователями (добавление, редактирование, удаление)
- Управление администраторами (добавление, удаление)
- Управление уровнями (редактирование предустановленных пользователей)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/kassa-bot.git
cd kassa-bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и заполните его:
```env
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username_here
DATABASE_URL=sqlite:///bot.db
LOG_LEVEL=INFO
MAIN_ADMIN_ID=0
```

## Запуск

```bash
python -m bot.run
```

## Структура проекта

```
bot/
├── core/
│   ├── config.py      # Конфигурация
│   └── database.py    # Работа с базой данных
├── handlers/
│   ├── admin.py       # Обработчики администраторов
│   ├── user.py        # Обработчики пользователей
│   └── main.py        # Основные обработчики
├── keyboards/
│   └── base.py        # Клавиатуры
├── states/
│   ├── admin.py       # Состояния администраторов
│   ├── user.py        # Состояния пользователей
│   └── main.py        # Основные состояния
├── utils/
│   └── validators.py  # Валидаторы
├── constants/
│   └── messages.py    # Константы сообщений
└── run.py             # Запуск бота
```

## Лицензия

MIT 