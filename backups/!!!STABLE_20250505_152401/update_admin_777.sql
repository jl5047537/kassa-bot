-- Сначала обновляем ссылки на админа в preset_users
UPDATE preset_users 
SET mentor_id = 777 
WHERE mentor_id = 5;

-- Затем обновляем ID и уровень админа
UPDATE preset_users 
SET id = 777, level = 777 
WHERE username = 'main_admin';

-- Проверяем результат
SELECT id, level, username, first_name, last_name, phone_number, is_active, mentor_id 
FROM preset_users 
ORDER BY level; 