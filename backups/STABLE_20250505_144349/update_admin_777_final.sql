-- Обновляем все ссылки на старую запись админа
UPDATE preset_users 
SET mentor_id = 777 
WHERE mentor_id = 5;

-- Удаляем старую запись админа
DELETE FROM preset_users WHERE id = 5;

-- Проверяем результат
SELECT id, level, username, first_name, last_name, phone_number, is_active, mentor_id 
FROM preset_users 
ORDER BY level; 