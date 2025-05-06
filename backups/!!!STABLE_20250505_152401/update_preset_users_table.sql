-- Добавляем недостающие поля в таблицу preset_users
ALTER TABLE preset_users 
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS telegram_id VARCHAR(50) UNIQUE;

-- Очищаем таблицу
TRUNCATE TABLE preset_users;

-- Добавляем предустановленных пользователей
INSERT INTO preset_users (level, phone_number, is_active, mentor_id) VALUES
(1, '79683327001', true, NULL),
(2, '79684286626', true, 1),
(3, '79253498238', true, 2),
(4, '79363030567', true, 3);

-- Проверяем результат
SELECT level, phone_number, is_active, mentor_id, telegram_id FROM preset_users ORDER BY level; 