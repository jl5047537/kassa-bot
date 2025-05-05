-- Добавление предустановленных пользователей
INSERT INTO preset_users (level, username, first_name, last_name, phone_number, is_active, created_at, updated_at)
VALUES 
    (1, 'level1_mentor', 'Наставник', 'Уровень 1', '79683327001', true, NOW(), NOW()),
    (2, 'level2_mentor', 'Наставник', 'Уровень 2', '79684286626', true, NOW(), NOW()),
    (3, 'level3_mentor', 'Наставник', 'Уровень 3', '79253498238', true, NOW(), NOW()),
    (4, 'level4_mentor', 'Наставник', 'Уровень 4', '79363030567', true, NOW(), NOW());

-- Обновление mentor_id для создания иерархии
UPDATE preset_users SET mentor_id = 1 WHERE level = 2;
UPDATE preset_users SET mentor_id = 2 WHERE level = 3;
UPDATE preset_users SET mentor_id = 3 WHERE level = 4; 