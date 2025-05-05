"""
Скрипт для добавления предустановленных пользователей в БД.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def add_preset_users():
    """Добавление предустановленных пользователей в БД."""
    try:
        # Создаем подключение к БД
        engine = create_engine(
            'postgresql://postgres:postgres123@localhost:5432/kassa_bot_test'
        )
        Session = sessionmaker(bind=engine)
        session = Session()

        # Создаем пользователей
        users = [
            {
                'level': 1,
                'username': 'level1_mentor',
                'first_name': 'Наставник',
                'last_name': 'Уровень 1',
                'phone_number': '79683327001',
                'is_active': True
            },
            {
                'level': 2,
                'username': 'level2_mentor',
                'first_name': 'Наставник',
                'last_name': 'Уровень 2',
                'phone_number': '79684286626',
                'is_active': True
            },
            {
                'level': 3,
                'username': 'level3_mentor',
                'first_name': 'Наставник',
                'last_name': 'Уровень 3',
                'phone_number': '79253498238',
                'is_active': True
            },
            {
                'level': 4,
                'username': 'level4_mentor',
                'first_name': 'Наставник',
                'last_name': 'Уровень 4',
                'phone_number': '79363030567',
                'is_active': True
            }
        ]

        # Добавляем пользователей
        for user_data in users:
            session.execute(
                """
                INSERT INTO preset_users (level, username, first_name, last_name, phone_number, is_active)
                VALUES (:level, :username, :first_name, :last_name, :phone_number, :is_active)
                ON CONFLICT (level) DO UPDATE
                SET phone_number = EXCLUDED.phone_number,
                    is_active = EXCLUDED.is_active
                """,
                user_data
            )
        
        # Сохраняем изменения
        session.commit()
        print("Предустановленные пользователи успешно добавлены")

        # Обновляем mentor_id
        session.execute("""
            UPDATE preset_users p2
            SET mentor_id = p1.id
            FROM preset_users p1
            WHERE p1.level = p2.level - 1
        """)
        session.commit()
        print("Иерархия наставничества успешно установлена")

    except Exception as e:
        print(f"Ошибка при добавлении предустановленных пользователей: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    add_preset_users() 