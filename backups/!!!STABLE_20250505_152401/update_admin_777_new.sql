-- Удаляем старую запись админа
DELETE FROM preset_users WHERE username = 'main_admin';

-- Добавляем новую запись админа с ID и уровнем 777
INSERT INTO preset_users (id, level, username, first_name, last_name, phone_number, is_active)
VALUES (777, 777, 'main_admin', 'Main', 'Admin', '+79165047537', true);

-- Обновляем ссылки на наставника
UPDATE preset_users 
SET mentor_id = 777 
WHERE level = 1;

-- Проверяем результат
SELECT id, level, username, first_name, last_name, phone_number, is_active, mentor_id 
FROM preset_users 
ORDER BY level; 