-- Добавляем админа в preset_users
INSERT INTO preset_users (level, username, first_name, last_name, phone_number, is_active)
VALUES (0, 'main_admin', 'Main', 'Admin', '79165047537', true);

-- Обновляем наставника для уровня 1
UPDATE preset_users 
SET mentor_id = (SELECT id FROM preset_users WHERE level = 0)
WHERE level = 1;

-- Проверяем результат
SELECT id, level, username, first_name, last_name, phone_number, is_active, mentor_id 
FROM preset_users 
ORDER BY level; 