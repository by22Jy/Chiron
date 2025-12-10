-- Fix for action_value field length issue in logs table
-- Run this script to update existing database

USE `yolo_platform`;

-- Modify action_value column to TEXT to support longer content
ALTER TABLE `logs`
MODIFY COLUMN `action_value` TEXT NULL;

-- Also update the actions table to prevent similar issues
ALTER TABLE `actions`
MODIFY COLUMN `action_value` TEXT NOT NULL;

SHOW WARNINGS;