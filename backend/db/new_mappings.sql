-- new_mappings.sql
USE `yolo_platform`;

-- 1. 为网页轮播定义新的“动作”
-- 我们使用 'any' 作为系统类型，因为这个动作与操作系统无关
-- 使用 'WEB_ACTION' 作为新的动作类型
INSERT INTO `actions` (`os_type`, `action_type`, `action_value`, `description`)
VALUES
    ('any', 'WEB_ACTION', 'carousel_prev', '网页图片轮播：上一张'),
    ('any', 'WEB_ACTION', 'carousel_next', '网页图片轮播：下一张');

-- 2. 将“挥手”手势映射到新的“网页动作”
-- 这里我们不指定用户和应用，使其成为一个全局默认配置

-- 将 swipe_left -> carousel_prev
INSERT INTO `mappings` (`gesture_id`, `action_id`)
SELECT g.id, a.id
FROM `gestures` g, `actions` a
WHERE g.code = 'swipe_left' AND a.action_value = 'carousel_prev' AND a.action_type = 'WEB_ACTION'
LIMIT 1;

-- 将 swipe_right -> carousel_next
INSERT INTO `mappings` (`gesture_id`, `action_id`)
SELECT g.id, a.id
FROM `gestures` g, `actions` a
WHERE g.code = 'swipe_right' AND a.action_value = 'carousel_next' AND a.action_type = 'WEB_ACTION'
LIMIT 1;
