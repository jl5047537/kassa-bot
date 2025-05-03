import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from urllib.parse import parse_qs
from datetime import datetime
from app.core.config import settings

def validate_telegram_data(init_data: str) -> Optional[Dict[str, Any]]:
    """
    Валидация данных от Telegram Web App
    """
    try:
        # Парсим данные
        parsed_data = parse_qs(init_data)
        
        # Проверяем наличие hash
        if 'hash' not in parsed_data:
            return None
            
        # Получаем hash и удаляем его из данных
        hash_value = parsed_data['hash'][0]
        parsed_data.pop('hash')
        
        # Проверяем время (не старше 3 часов)
        if 'auth_date' in parsed_data:
            auth_date = int(parsed_data['auth_date'][0])
            if datetime.now().timestamp() - auth_date > 3 * 3600:
                return None
        
        # Сортируем данные
        data_check_string = '\n'.join(
            f"{k}={v[0]}" for k, v in sorted(parsed_data.items())
        )
        
        # Создаем секретный ключ
        secret_key = hmac.new(
            'WebAppData'.encode(),
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Проверяем hash
        if calculated_hash == hash_value:
            # Парсим user данные
            if 'user' in parsed_data:
                try:
                    user_data = json.loads(parsed_data['user'][0])
                    parsed_data['user'] = user_data
                except json.JSONDecodeError:
                    return None
            return parsed_data
            
        return None
        
    except Exception:
        return None 