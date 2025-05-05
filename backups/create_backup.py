import os
import shutil
import datetime
from pathlib import Path

def create_backup(label="STABLE"):
    """
    Создает бэкап текущего состояния проекта
    """
    try:
        # Создаем имя папки с текущей датой и временем
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{label}_{timestamp}"
        backup_dir = Path("backups") / backup_name
        
        # Создаем директорию для бэкапа
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Копируем основные файлы и директории
        items_to_copy = [
            "bot",
            "*.py",
            "*.sql",
            "*.md",
            "requirements.txt",
            "config.env",
            "run.py"
        ]
        
        root_dir = Path(".")
        print(f"Создание бэкапа: {backup_name}")
        
        for item in items_to_copy:
            if "*" in item:
                # Копируем файлы по маске
                for file in root_dir.glob(item):
                    if file.is_file():
                        print(f"Копирование: {file.name}")
                        shutil.copy2(file, backup_dir / file.name)
            else:
                # Копируем директорию или файл
                source = root_dir / item
                if source.exists():
                    print(f"Копирование: {item}")
                    if source.is_dir():
                        shutil.copytree(source, backup_dir / item)
                    else:
                        shutil.copy2(source, backup_dir / item)
        
        # Копируем скрипт восстановления
        restore_script = Path(__file__).parent / "STABLE_20250504_104122" / "restore.py"
        if restore_script.exists():
            shutil.copy2(restore_script, backup_dir / "restore.py")
        
        print(f"\nБэкап успешно создан: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"Ошибка при создании бэкапа: {str(e)}")
        return None

if __name__ == "__main__":
    create_backup() 