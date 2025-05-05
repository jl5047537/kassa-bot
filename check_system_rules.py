"""
Скрипт проверки системных правил.
Запускается перед каждым действием ассистента.
"""

import os
import sys
import datetime
import logging
from SYSTEM_RULES import RULES, check_rules, get_next_action

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_rules():
    """Проверка всех правил"""
    logger.info("=== ПРОВЕРКА СИСТЕМНЫХ ПРАВИЛ ===")
    
    # Проверка наличия RULES.md
    if not os.path.exists("RULES.md"):
        logger.error("❌ ОШИБКА: Файл RULES.md не найден")
        return False
        
    # Проверка времени последнего чтения правил
    last_read = get_last_read_time()
    if (datetime.datetime.now() - last_read).total_seconds() > 3600:  # 1 час
        logger.warning("⚠️ ВНИМАНИЕ: Правила не читались более часа")
        
    # Проверка соблюдения правил
    if not check_rules():
        logger.error("❌ ОШИБКА: Правила не соблюдаются")
        return False
        
    logger.info("✅ Правила проверены и соблюдаются")
    return True

def get_last_read_time():
    """Получение времени последнего чтения правил"""
    try:
        with open(".last_rules_read", "r") as f:
            return datetime.datetime.fromisoformat(f.read())
    except:
        return datetime.datetime.min

def update_last_read():
    """Обновление времени последнего чтения правил"""
    with open(".last_rules_read", "w") as f:
        f.write(datetime.datetime.now().isoformat())

if __name__ == "__main__":
    if verify_rules():
        update_last_read()
        sys.exit(0)
    else:
        sys.exit(1) 