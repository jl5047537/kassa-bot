"""
Скрипт для проверки соблюдения правил взаимодействия.
"""

import os
import sys
from datetime import datetime

def check_rules():
    """
    Проверяет соблюдение правил взаимодействия.
    """
    # Проверяем наличие файла с правилами
    if not os.path.exists('RULES.md'):
        print("ОШИБКА: Файл RULES.md не найден")
        return False
        
    # Проверяем последнее время чтения правил
    last_read = get_last_read_time()
    if not last_read or (datetime.now() - last_read).seconds > 3600:
        print("ПРЕДУПРЕЖДЕНИЕ: Правила не читались более часа")
        return False
        
    return True

def get_last_read_time():
    """
    Получает время последнего чтения правил.
    """
    try:
        with open('.last_read', 'r') as f:
            return datetime.fromisoformat(f.read())
    except:
        return None

def update_last_read():
    """
    Обновляет время последнего чтения правил.
    """
    with open('.last_read', 'w') as f:
        f.write(datetime.now().isoformat())

if __name__ == '__main__':
    if check_rules():
        print("Правила соблюдены")
        update_last_read()
    else:
        print("Правила нарушены")
        sys.exit(1) 