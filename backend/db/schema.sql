-- Schema for "无触控"实时交互平台
-- MySQL 8.0+ recommended. Run:  mysql -u <user> -p < backend/db/schema.sql

CREATE DATABASE IF NOT EXISTS `yolo_platform`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `yolo_platform`;

-- 1. users：平台账户
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `username`      VARCHAR(64)     NOT NULL UNIQUE,
    `display_name`  VARCHAR(128)    NULL,
    `email`         VARCHAR(128)    NULL,
    `password_hash` VARCHAR(255)    NOT NULL,
    `status`        TINYINT         NOT NULL DEFAULT 1 COMMENT '1=active,0=disabled',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. applications：受控应用/场景
DROP TABLE IF EXISTS `applications`;
CREATE TABLE `applications` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `code`          VARCHAR(128)    NOT NULL UNIQUE COMMENT '应用唯一标识, 如 chrome.exe',
    `name`          VARCHAR(128)    NOT NULL,
    `description`   VARCHAR(255)    NULL,
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. gestures：手势/姿态定义
DROP TABLE IF EXISTS `gestures`;
CREATE TABLE `gestures` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `code`          VARCHAR(64)     NOT NULL UNIQUE COMMENT '如 swipe_left、pinch_close',
    `name`          VARCHAR(128)    NOT NULL,
    `description`   VARCHAR(255)    NULL,
    `gesture_type`  VARCHAR(32)     NULL COMMENT 'static/dynamic/pose 等',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. actions：执行动作定义
DROP TABLE IF EXISTS `actions`;
CREATE TABLE `actions` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `os_type`       VARCHAR(16)     NOT NULL DEFAULT 'any' COMMENT 'windows/macos/linux/any',
    `action_type`   VARCHAR(64)     NOT NULL COMMENT 'hotkey,keypress,macro,webhook 等',
    `action_value`  VARCHAR(255)    NOT NULL COMMENT '如 ctrl+- 或 JSON',
    `description`   VARCHAR(255)    NULL,
    `payload_json`  JSON            NULL,
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_actions_os_type` (`os_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. mappings：手势→动作映射（可按用户与应用粒度配置）
DROP TABLE IF EXISTS `mappings`;
CREATE TABLE `mappings` (
    `id`             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id`        BIGINT UNSIGNED NULL COMMENT 'NULL 表示所有用户',
    `application_id` BIGINT UNSIGNED NULL COMMENT 'NULL 表示所有应用',
    `gesture_id`     BIGINT UNSIGNED NOT NULL,
    `action_id`      BIGINT UNSIGNED NOT NULL,
    `priority`       INT             NOT NULL DEFAULT 0,
    `enabled`        TINYINT         NOT NULL DEFAULT 1,
    `created_at`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_mapping_user` (`user_id`),
    KEY `idx_mapping_app` (`application_id`),
    KEY `idx_mapping_gesture` (`gesture_id`),
    KEY `idx_mapping_action` (`action_id`),
    CONSTRAINT `fk_mapping_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_mapping_app` FOREIGN KEY (`application_id`) REFERENCES `applications`(`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_mapping_gesture` FOREIGN KEY (`gesture_id`) REFERENCES `gestures`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_mapping_action` FOREIGN KEY (`action_id`) REFERENCES `actions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. logs：代理上报的行为日志
DROP TABLE IF EXISTS `logs`;
CREATE TABLE `logs` (
    `id`             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id`        BIGINT UNSIGNED NULL,
    `application_id` BIGINT UNSIGNED NULL,
    `gesture_code`   VARCHAR(64)     NULL,
    `action_type`    VARCHAR(64)     NULL,
    `action_value`   VARCHAR(255)    NULL,
    `status`         VARCHAR(32)     NULL COMMENT 'success,failure,pending',
    `message`        VARCHAR(500)    NULL,
    `source_agent`   VARCHAR(128)    NULL COMMENT 'agent 标识/版本',
    `created_at`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_logs_user` (`user_id`),
    KEY `idx_logs_app` (`application_id`),
    KEY `idx_logs_gesture` (`gesture_code`),
    CONSTRAINT `fk_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_logs_app` FOREIGN KEY (`application_id`) REFERENCES `applications`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. 基础数据样例（可按需修改/删除）
INSERT INTO `users` (`username`, `display_name`, `email`, `password_hash`)
VALUES ('admin', '系统管理员', 'admin@example.com', '{noop}admin');

INSERT INTO `applications` (`code`, `name`, `description`)
VALUES ('chrome.exe', 'Google Chrome', '浏览器'),
       ('powerpnt.exe', 'Microsoft PowerPoint', '演示软件');

INSERT INTO `gestures` (`code`, `name`, `description`, `gesture_type`)
VALUES ('swipe_left', '左挥手', '向左挥动手臂/手掌', 'dynamic'),
       ('swipe_right', '右挥手', '向右挥动手臂/手掌', 'dynamic'),
       ('pinch_close', '五指汇聚', '五指收拢动作', 'static');

INSERT INTO `actions` (`os_type`, `action_type`, `action_value`, `description`)
VALUES ('windows', 'hotkey', 'ctrl+left', 'Chrome 标签页左切换 (Win)'),
       ('macos',   'hotkey', 'command+option+left', 'Chrome 标签页左切换 (Mac)'),
       ('windows', 'hotkey', 'ctrl+right', 'Chrome 标签页右切换 (Win)'),
       ('macos',   'hotkey', 'command+option+right', 'Chrome 标签页右切换 (Mac)'),
       ('windows', 'hotkey', 'ctrl+-', '页面缩小 (Win)'),
       ('macos',   'hotkey', 'command+-', '页面缩小 (Mac)');

INSERT INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`)
SELECT u.id, a.id, g.id, act.id, 0
FROM `users` u, `applications` a, `gestures` g, `actions` act
WHERE u.username='admin' AND a.code='chrome.exe'
      AND g.code='swipe_left' AND act.action_value='ctrl+left' AND act.os_type='windows'
LIMIT 1;

INSERT INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`)
SELECT u.id, a.id, g.id, act.id, 0
FROM `users` u, `applications` a, `gestures` g, `actions` act
WHERE u.username='admin' AND a.code='chrome.exe'
      AND g.code='swipe_left' AND act.action_value='command+option+left' AND act.os_type='macos'
LIMIT 1;

INSERT INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`)
SELECT u.id, a.id, g.id, act.id, 0
FROM `users` u, `applications` a, `gestures` g, `actions` act
WHERE u.username='admin' AND a.code='chrome.exe'
      AND g.code='swipe_right' AND act.action_value='ctrl+right' AND act.os_type='windows'
LIMIT 1;

INSERT INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`)
SELECT u.id, a.id, g.id, act.id, 0
FROM `users` u, `applications` a, `gestures` g, `actions` act
WHERE u.username='admin' AND a.code='chrome.exe'
      AND g.code='swipe_right' AND act.action_value='command+option+right' AND act.os_type='macos'
LIMIT 1;

INSERT INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`)
SELECT u.id, a.id, g.id, act.id, 0
FROM `users` u, `applications` a, `gestures` g, `actions` act
WHERE u.username='admin' AND a.code='chrome.exe'
      AND g.code='pinch_close' AND act.action_value='ctrl+-' AND act.os_type='windows'
LIMIT 1;

INSERT INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`)
SELECT u.id, a.id, g.id, act.id, 0
FROM `users` u, `applications` a, `gestures` g, `actions` act
WHERE u.username='admin' AND a.code='chrome.exe'
      AND g.code='pinch_close' AND act.action_value='command+-' AND act.os_type='macos'
LIMIT 1;


