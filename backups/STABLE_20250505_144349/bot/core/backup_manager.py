"""
Модуль для управления бэкапами проекта.
"""

import os
import shutil
import logging
import datetime
import zipfile
import hashlib
import asyncio
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from aiogram import Bot

from .backup_config import BACKUP_CONFIG
from .config import settings

logger = logging.getLogger(__name__)

class BackupManager:
    """
    Класс для управления бэкапами проекта.
    """
    
    def __init__(self, bot: Optional[Bot] = None):
        """
        Инициализация менеджера бэкапов.
        
        Args:
            bot: Объект бота для отправки уведомлений
        """
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.bot = bot
        self.config = BACKUP_CONFIG
        
    async def create_backup(self) -> Dict[str, Any]:
        """
        Создание бэкапа проекта.
        
        Returns:
            Dict[str, Any]: Информация о созданном бэкапе
        """
        try:
            start_time = datetime.datetime.now()
            
            # Создаем имя файла бэкапа с временной меткой
            timestamp = start_time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.zip"
            backup_path = self.backup_dir / backup_name
            
            # Создаем ZIP архив
            total_size = 0
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for source_dir in self.config["source_dirs"]:
                    source_path = Path(source_dir)
                    if not source_path.exists():
                        logger.warning(f"Директория {source_dir} не существует")
                        continue
                        
                    for root, dirs, files in os.walk(source_path):
                        # Исключаем директории
                        if self.config["exclude_dirs"]:
                            dirs[:] = [d for d in dirs if d not in self.config["exclude_dirs"]]
                            
                        # Исключаем файлы
                        if self.config["exclude_files"]:
                            files = [f for f in files if not any(f.endswith(ext) for ext in self.config["exclude_files"])]
                            
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(source_path)
                            zipf.write(file_path, arcname)
                            total_size += file_path.stat().st_size
                            
            # Вычисляем контрольную сумму
            with open(backup_path, 'rb') as f:
                checksum = hashlib.md5(f.read()).hexdigest()
                
            # Создаем метаданные бэкапа
            backup_info = {
                "path": str(backup_path),
                "size": total_size,
                "checksum": checksum,
                "created_at": start_time,
                "duration": (datetime.datetime.now() - start_time).total_seconds()
            }
            
            # Сохраняем метаданные
            self._save_metadata(backup_info)
            
            # Очищаем старые бэкапы
            self.cleanup_old_backups()
            
            # Отправляем уведомление
            await self._send_notification(backup_info)
            
            logger.info(f"Бэкап создан: {backup_path}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Ошибка при создании бэкапа: {str(e)}")
            await self._send_error_notification(str(e))
            raise
            
    def _save_metadata(self, backup_info: Dict[str, Any]) -> None:
        """
        Сохранение метаданных бэкапа.
        
        Args:
            backup_info: Информация о бэкапе
        """
        metadata_path = self.backup_dir / "metadata.json"
        metadata = []
        
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                
        metadata.append(backup_info)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, default=str)
            
    async def _send_notification(self, backup_info: Dict[str, Any]) -> None:
        """
        Отправка уведомления о бэкапе.
        
        Args:
            backup_info: Информация о бэкапе
        """
        if not self.bot or not self.config["notifications"]["enabled"]:
            return
            
        try:
            # Проверяем наличие chat_id
            if not self.config["notifications"].get("chat_id"):
                logger.error("Chat_id is empty")
                return
                
            message = (
                f"✅ Бэкап успешно создан\n"
                f"📅 Дата: {backup_info['created_at']}\n"
                f"📦 Размер: {backup_info['size'] / 1024 / 1024:.2f} MB\n"
                f"⏱ Время создания: {backup_info['duration']:.2f} сек\n"
                f"🔍 Контрольная сумма: {backup_info['checksum']}"
            )
            
            await self.bot.send_message(
                chat_id=self.config["notifications"]["chat_id"],
                text=message
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления: {str(e)}")
            
    async def _send_error_notification(self, error: str) -> None:
        """
        Отправка уведомления об ошибке.
        
        Args:
            error: Текст ошибки
        """
        if not self.bot or not self.config["notifications"]["enabled"]:
            return
            
        try:
            # Проверяем наличие chat_id
            if not self.config["notifications"].get("chat_id"):
                logger.error("Chat_id is empty")
                return
                
            message = (
                f"❌ Ошибка при создании бэкапа\n"
                f"📅 Дата: {datetime.datetime.now()}\n"
                f"⚠️ Ошибка: {error}"
            )
            
            await self.bot.send_message(
                chat_id=self.config["notifications"]["chat_id"],
                text=message
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления об ошибке: {str(e)}")
            
    def cleanup_old_backups(self) -> None:
        """
        Удаление старых бэкапов.
        """
        try:
            backups = self.list_backups()
            if len(backups) > self.config["schedule"]["keep_last"]:
                for backup_path in backups[self.config["schedule"]["keep_last"]:]:
                    self.delete_backup(backup_path)
                logger.info(f"Удалено {len(backups) - self.config['schedule']['keep_last']} старых бэкапов")
        except Exception as e:
            logger.error(f"Ошибка при очистке старых бэкапов: {str(e)}")
            raise
            
    def list_backups(self) -> List[str]:
        """
        Получение списка доступных бэкапов.
        
        Returns:
            List[str]: Список путей к бэкапам
        """
        try:
            backups = []
            for file in self.backup_dir.glob("backup_*.zip"):
                backups.append(str(file))
            return sorted(backups, reverse=True)
        except Exception as e:
            logger.error(f"Ошибка при получении списка бэкапов: {str(e)}")
            raise
            
    def restore_backup(self, backup_path: str, target_dir: Optional[str] = None, 
                      files: Optional[List[str]] = None) -> None:
        """
        Восстановление из бэкапа.
        
        Args:
            backup_path: Путь к файлу бэкапа
            target_dir: Директория для восстановления
            files: Список файлов для восстановления
        """
        try:
            # Проверяем существование бэкапа
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Бэкап не найден: {backup_path}")
                
            # Определяем целевую директорию
            target_path = Path(target_dir or self.config["restore"]["default_target"])
            target_path.mkdir(exist_ok=True)
            
            # Проверяем целостность
            if self.config["restore"]["verify_integrity"]:
                self._verify_backup(backup_path)
                
            # Восстанавливаем файлы
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if files:
                    # Восстанавливаем только указанные файлы
                    for file in files:
                        if file in zipf.namelist():
                            zipf.extract(file, target_path)
                else:
                    # Восстанавливаем все файлы
                    zipf.extractall(target_path)
                    
            logger.info(f"Бэкап восстановлен в {target_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при восстановлении бэкапа: {str(e)}")
            raise
            
    def _verify_backup(self, backup_path: str) -> None:
        """
        Проверка целостности бэкапа.
        
        Args:
            backup_path: Путь к файлу бэкапа
        """
        try:
            # Проверяем, что файл является валидным ZIP архивом
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Проверяем целостность каждого файла
                for file in zipf.namelist():
                    zipf.getinfo(file)
                    
            logger.info(f"Целостность бэкапа проверена: {backup_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при проверке целостности бэкапа: {str(e)}")
            raise
            
    def delete_backup(self, backup_path: str) -> None:
        """
        Удаление бэкапа.
        
        Args:
            backup_path: Путь к файлу бэкапа
        """
        try:
            backup_file = Path(backup_path)
            if backup_file.exists():
                backup_file.unlink()
                logger.info(f"Бэкап удален: {backup_path}")
            else:
                logger.warning(f"Бэкап не найден: {backup_path}")
        except Exception as e:
            logger.error(f"Ошибка при удалении бэкапа: {str(e)}")
            raise 