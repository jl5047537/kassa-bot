"""
Модуль для планирования автоматических бэкапов.
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Optional

from .backup_manager import BackupManager
from .backup_config import BACKUP_CONFIG

logger = logging.getLogger(__name__)

class BackupScheduler:
    """
    Класс для планирования автоматических бэкапов.
    """
    
    def __init__(self, backup_manager: BackupManager):
        """
        Инициализация планировщика.
        
        Args:
            backup_manager: Менеджер бэкапов
        """
        self.backup_manager = backup_manager
        self.config = BACKUP_CONFIG
        self._task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """
        Запуск планировщика.
        """
        if not self.config["schedule"]["enabled"]:
            logger.info("Автоматические бэкапы отключены")
            return
            
        self._task = asyncio.create_task(self._run_scheduler())
        logger.info("Планировщик бэкапов запущен")
        
    async def stop(self) -> None:
        """
        Остановка планировщика.
        """
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.info("Планировщик бэкапов остановлен")
            
    async def _run_scheduler(self) -> None:
        """
        Основной цикл планировщика.
        """
        while True:
            try:
                # Получаем текущее время
                now = datetime.now().time()
                backup_time = self.config["schedule"]["daily_time"]
                
                # Проверяем, нужно ли создавать бэкап
                if now.hour == backup_time.hour and now.minute == backup_time.minute:
                    logger.info("Начинаем создание автоматического бэкапа")
                    await self.backup_manager.create_backup()
                    
                # Ждем следующей проверки (каждую минуту)
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в планировщике бэкапов: {str(e)}")
                await asyncio.sleep(60)  # Ждем перед следующей попыткой 