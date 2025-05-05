-- Обновляем уровень админа на -1
UPDATE preset_users 
SET level = -1 
WHERE username = 'main_admin';

-- Проверяем результат
SELECT id, level, username, first_name, last_name, phone_number, is_active, mentor_id 
FROM preset_users 
ORDER BY level; 