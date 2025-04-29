from typing import Optional, List
from datetime import datetime

class Database:
    def get_user_by_referral_code(self, code: str) -> Optional[dict]:
        """
        Получает пользователя по реферальному коду
        
        Args:
            code: Реферальный код
            
        Returns:
            Optional[dict]: Данные пользователя или None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, created_at, referral_code 
                FROM users 
                WHERE referral_code = %s
            """, (code,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'created_at': result[1],
                    'referral_code': result[2]
                }
            return None

    def get_referrals_count(self, user_id: str) -> int:
        """
        Получает количество рефералов пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            int: Количество рефералов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM referrals 
                WHERE referrer_id = %s
            """, (user_id,))
            return cursor.fetchone()[0]

    def get_user_last_action(self, user_id: str) -> Optional[datetime]:
        """
        Получает дату последнего действия пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[datetime]: Дата последнего действия или None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MAX(action_date) 
                FROM user_actions 
                WHERE user_id = %s
            """, (user_id,))
            result = cursor.fetchone()[0]
            return result

    def get_referral_chain(self, user_id: str) -> List[dict]:
        """
        Получает цепочку рефералов пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            List[dict]: Список рефералов в цепочке
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                WITH RECURSIVE referral_chain AS (
                    SELECT r.referral_id, r.created_at, 1 as level
                    FROM referrals r
                    WHERE r.referrer_id = %s
                    
                    UNION ALL
                    
                    SELECT r.referral_id, r.created_at, rc.level + 1
                    FROM referrals r
                    JOIN referral_chain rc ON r.referrer_id = rc.referral_id
                )
                SELECT rc.referral_id, rc.created_at, rc.level
                FROM referral_chain rc
                ORDER BY rc.level, rc.created_at
            """, (user_id,))
            return [{
                'id': row[0],
                'created_at': row[1],
                'level': row[2]
            } for row in cursor.fetchall()] 