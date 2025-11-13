-- YOLO-LLM Database Setup Script
-- Usage: mysql -u root -p < setup-database.sql

-- 创建数据库
CREATE DATABASE IF NOT EXISTS yolo_platform
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE yolo_platform;

-- 显示数据库信息
SELECT
    SCHEMA_NAME as 'Database Name',
    DEFAULT_CHARACTER_SET_NAME as 'Character Set',
    DEFAULT_COLLATION_NAME as 'Collation'
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE SCHEMA_NAME = 'yolo_platform';

-- 提示用户
SELECT 'YOLO-LLM database setup completed!' as 'Status';