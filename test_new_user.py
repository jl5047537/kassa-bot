from bot.database import db

def test_new_user():
    # Создаем тестового пользователя
    test_id = "1234567890"
    print("Создаем тестового пользователя...")
    db.create_user(test_id, phone_number="+79999999999")
    
    # Проверяем созданного пользователя
    print("\nПроверяем созданного пользователя:")
    user = db.get_user(test_id)
    if user:
        print(f"ID: {user['telegram_id']}")
        print(f"Уровень: {user['level']}")
        print(f"Наставник: {user['referrer_id']}")
        print(f"Телефон: {user['phone_number']}")
    else:
        print("Ошибка: Пользователь не создан")

if __name__ == "__main__":
    test_new_user() 