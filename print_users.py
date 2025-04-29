from bot.database import db

print('Список всех пользователей:')
users = db.get_all_users()
for user in users:
    print(f'ID: {user["telegram_id"]}, '
          f'Имя: {user["first_name"]} {user["last_name"]}, '
          f'Уровень: {user["level"]}, '
          f'Username: {user["username"]}') 