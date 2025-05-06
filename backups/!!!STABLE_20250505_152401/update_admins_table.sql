-- Добавляем столбец phone_number, если его нет
ALTER TABLE admins 
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20);

-- Создаем индекс для номера телефона
CREATE INDEX IF NOT EXISTS idx_admin_phone ON admins(phone_number);

-- Проверяем результат
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'admins' 
ORDER BY ordinal_position; 