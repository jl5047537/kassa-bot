import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def show_preset_users():
    # Загружаем переменные окружения
    load_dotenv()
    
    # Получаем параметры подключения из переменных окружения
    db_params = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres123'),
        'database': os.getenv('POSTGRES_DB', 'kassa_bot_test')
    }
    
    # Создаем строку подключения
    connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    
    try:
        # Создаем подключение к базе данных
        engine = create_engine(connection_string)
        
        # Выполняем запрос для получения данных из таблицы preset_users
        with engine.connect() as connection:
            # Получаем данные из таблицы
            result = connection.execute(text("""
                SELECT id, level, username, first_name, last_name, phone_number, 
                       is_active, mentor_id, created_at, updated_at
                FROM preset_users
                ORDER BY level;
            """))
            
            # Выводим заголовки
            print("\n{:<5} {:<5} {:<15} {:<15} {:<15} {:<15} {:<8} {:<8} {:<20} {:<20}".format(
                "ID", "Level", "Username", "First Name", "Last Name", "Phone", 
                "Active", "Mentor", "Created", "Updated"
            ))
            print("-" * 120)
            
            # Выводим данные
            for row in result:
                print("{:<5} {:<5} {:<15} {:<15} {:<15} {:<15} {:<8} {:<8} {:<20} {:<20}".format(
                    row[0], row[1], row[2] or '', row[3] or '', row[4] or '', row[5] or '',
                    row[6], row[7] or '', str(row[8])[:19], str(row[9])[:19]
                ))
            
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {str(e)}")

if __name__ == "__main__":
    show_preset_users() 