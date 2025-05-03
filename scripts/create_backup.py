"""
Скрипт для автоматического создания бэкапов проекта.
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
    parser = argparse.ArgumentParser(description='Создание бэкапа проекта')
    parser.add_argument('--max-backups', type=int, default=5,
                      help='Максимальное количество хранимых бэкапов')
    args = parser.parse_args()
    
    try:
        # Создаем менеджер бэкапов
        backup_manager = BackupManager()
        
        # Директории для бэкапа
        source_dirs = [
            "bot",
            "docs",
            "scripts",
            "tests"
        ]
        
        # Директории для исключения
        exclude_dirs = [
            "__pycache__",
            ".pytest_cache",
            "venv",
            "node_modules"
        ]
        
        # Файлы для исключения
        exclude_files = [
            ".env",
            ".gitignore",
            "*.pyc",
            "*.pyo",
            "*.pyd"
        ]
        
        # Создаем бэкап
        backup_path = backup_manager.create_backup(
            source_dirs=source_dirs,
            exclude_dirs=exclude_dirs,
            exclude_files=exclude_files
        )
        
        # Очищаем старые бэкапы
        backup_manager.cleanup_old_backups(max_backups=args.max_backups)
        
        logger.info(f"Бэкап успешно создан: {backup_path}")
        
    except Exception as e:
        logger.error(f"Ошибка при создании бэкапа: {str(e)}")
        raise

if __name__ == "__main__":
    main() 