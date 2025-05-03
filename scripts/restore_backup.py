"""
Скрипт для восстановления проекта из бэкапа.
"""

import logging
import argparse
from pathlib import Path
from bot.core.backup_manager import BackupManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Основная функция скрипта.
    """
    parser = argparse.ArgumentParser(description='Восстановление проекта из бэкапа')
    parser.add_argument('backup_path', type=str,
                      help='Путь к файлу бэкапа')
    parser.add_argument('--target-dir', type=str, default='.',
                      help='Директория для восстановления')
    args = parser.parse_args()
    
    try:
        # Создаем менеджер бэкапов
        backup_manager = BackupManager()
        
        # Проверяем существование бэкапа
        backup_path = Path(args.backup_path)
        if not backup_path.exists():
            logger.error(f"Бэкап не найден: {args.backup_path}")
            return
            
        # Восстанавливаем бэкап
        backup_manager.restore_backup(
            backup_path=str(backup_path),
            target_dir=args.target_dir
        )
        
        logger.info(f"Проект успешно восстановлен из бэкапа: {args.backup_path}")
        
    except Exception as e:
        logger.error(f"Ошибка при восстановлении из бэкапа: {str(e)}")
        raise

if __name__ == "__main__":
    main() 