from bot.database import db

# Словарь с реферальными связями
referral_chain = {
    # Главный админ -> Уровень 1
    "7806482506": "7963523915",  # Alex_Level_1 -> JanLevy (главный админ)
    
    # Уровень 1 -> Уровень 2
    "7355173647": "7806482506",  # Nastiya_Level_2 -> Alex_Level_1
    
    # Уровень 2 -> Уровень 3
    "7651819044": "7355173647",  # travelercinema -> Nastiya_Level_2
    
    # Уровень 3 -> Уровень 4
    "7694850355": "7651819044"   # Mark_Level_4 -> travelercinema
}

def setup_referrals():
    print("Установка реферальных связей...")
    for user_id, referrer_id in referral_chain.items():
        if db.update_user(user_id, referral_id=referrer_id):
            print(f"Успешно: Пользователь {user_id} теперь реферал пользователя {referrer_id}")
        else:
            print(f"Ошибка: Не удалось установить связь для пользователя {user_id}")

if __name__ == "__main__":
    setup_referrals() 