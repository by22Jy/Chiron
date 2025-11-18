-- fix_browser_navigation.sql
-- 修正浏览器导航手势映射，使用正确的快捷键

USE `yolo_platform`;

-- 1. 首先添加正确的浏览器标签页切换动作
INSERT IGNORE INTO `actions` (`os_type`, `action_type`, `action_value`, `description`)
VALUES
    ('windows', 'hotkey', 'ctrl+pgup', '浏览器标签页左切换 (Windows)'),
    ('windows', 'hotkey', 'ctrl+pgdn', '浏览器标签页右切换 (Windows)'),
    ('windows', 'hotkey', 'ctrl+tab', '浏览器标签页循环切换 (Windows)'),
    ('windows', 'hotkey', 'ctrl+shift+tab', '浏览器标签页反向循环切换 (Windows)'),
    ('windows', 'hotkey', 'ctrl+w', '关闭当前标签页 (Windows)'),
    ('windows', 'hotkey', 'ctrl+t', '新建标签页 (Windows)'),
    ('macos', 'hotkey', 'ctrl+tab', '浏览器标签页左切换 (macOS)'),
    ('macos', 'hotkey', 'ctrl+shift+tab', '浏览器标签页右切换 (macOS)'),
    ('macos', 'hotkey', 'command+w', '关闭当前标签页 (macOS)'),
    ('macos', 'hotkey', 'command+t', '新建标签页 (macOS)');

-- 2. 删除错误的映射
DELETE FROM `mappings`
WHERE gesture_id IN (
    SELECT id FROM gestures WHERE code IN ('swipe_left', 'swipe_right')
) AND action_id IN (
    SELECT id FROM actions WHERE action_value IN ('ctrl+left', 'ctrl+right')
);

-- 3. 添加正确的浏览器标签页切换映射
-- 左滑 -> 标签页左切换
INSERT IGNORE INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`, `enabled`)
SELECT
    NULL as user_id,
    NULL as application_id,
    g.id as gesture_id,
    a.id as action_id,
    20 as priority,
    1 as enabled
FROM gestures g, actions a
WHERE (g.code, a.action_value, a.os_type) IN (
    ('swipe_left', 'ctrl+pgup', 'windows'),
    ('swipe_left', 'ctrl+tab', 'macos')
);

-- 右滑 -> 标签页右切换
INSERT IGNORE INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`, `enabled`)
SELECT
    NULL as user_id,
    NULL as application_id,
    g.id as gesture_id,
    a.id as action_id,
    20 as priority,
    1 as enabled
FROM gestures g, actions a
WHERE (g.code, a.action_value, a.os_type) IN (
    ('swipe_right', 'ctrl+pgdn', 'windows'),
    ('swipe_right', 'ctrl+shift+tab', 'macos')
);

-- 4. 为Chrome浏览器添加专门的映射
-- 确保Chrome应用存在
INSERT IGNORE INTO `applications` (`code`, `name`, `description`)
VALUES ('chrome.exe', 'Google Chrome', '网页浏览器')
ON DUPLICATE KEY UPDATE name = 'Google Chrome', description = '网页浏览器';

-- Chrome浏览器的高优先级映射
INSERT IGNORE INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`, `enabled`)
SELECT
    u.id as user_id,
    app.id as application_id,
    g.id as gesture_id,
    a.id as action_id,
    30 as priority,  -- 最高优先级
    1 as enabled
FROM users u, applications app, gestures g, actions a
WHERE u.username = 'admin'
  AND app.code = 'chrome.exe'
  AND (g.code, a.action_value, a.os_type) IN (
    -- Chrome标签页切换
    ('swipe_left', 'ctrl+pgup', 'windows'),
    ('swipe_left', 'ctrl+tab', 'macos'),
    ('swipe_right', 'ctrl+pgdn', 'windows'),
    ('swipe_right', 'ctrl+shift+tab', 'macos'),

    -- 其他有用的手势
    ('victory', 'ctrl+t', 'windows'),
    ('victory', 'command+t', 'macos'),
    ('closed_fist', 'ctrl+w', 'windows'),
    ('closed_fist', 'command+w', 'macos')
  );

-- 5. 清理不支持的WEB_ACTION映射（可选）
-- 如果actions执行器不支持WEB_ACTION类型，可以考虑删除这些映射
DELETE FROM `mappings`
WHERE action_id IN (
    SELECT id FROM actions WHERE action_type = 'WEB_ACTION'
);

-- 完成
SELECT '浏览器导航映射修复完成!' as status;

-- 显示当前的手势映射配置
SELECT
    g.code as '手势代码',
    g.name as '手势名称',
    a.action_value as '动作值',
    a.action_type as '动作类型',
    a.os_type as '操作系统',
    m.priority as '优先级'
FROM gestures g
JOIN mappings m ON g.id = m.gesture_id
JOIN actions a ON m.action_id = a.id
WHERE g.code IN ('swipe_left', 'swipe_right', 'victory', 'closed_fist')
ORDER BY g.code, m.priority DESC, a.os_type;