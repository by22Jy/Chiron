-- simple_gesture_mappings.sql
-- 为YOLO-LLM项目添加基础的手势控制映射

USE `yolo_platform`;

-- 1. 添加缺失的手势定义
INSERT IGNORE INTO `gestures` (`code`, `name`, `description`, `gesture_type`)
VALUES
    -- 静态手势
    ('POINT_UP', '食指指上', '食指向上指向', 'static'),
    ('POINT_INDEX', '食指指前', '食指向前指向', 'static'),
    ('THUMBS_UP', '点赞', '大拇指向上', 'static'),
    ('THUMBS_DOWN', '点踩', '大拇指向下', 'static'),
    ('OPEN_PALM', '张开手掌', '五指张开', 'static'),
    ('CLOSED_FIST', '握拳', '五指握紧', 'static'),
    ('VICTORY', '胜利手势', 'V字手势', 'static'),
    ('OK_SIGN', 'OK手势', '拇指食指相接成圆圈', 'static'),

    -- 动态手势 - 添加缺失的上下滑动
    ('swipe_up', '上滑', '向上滑动', 'dynamic'),
    ('swipe_down', '下滑', '向下滑动', 'dynamic');

-- 2. 添加实用的系统控制动作
INSERT IGNORE INTO `actions` (`os_type`, `action_type`, `action_value`, `description`)
VALUES
    -- 基础鼠标动作
    ('any', 'mouse', 'left_click', '鼠标左键单击'),
    ('any', 'mouse', 'right_click', '鼠标右键单击'),
    ('any', 'click', 'double_click', '鼠标双击'),

    -- Windows系统快捷键
    ('windows', 'hotkey', 'alt+tab', '切换应用程序'),
    ('windows', 'hotkey', 'win+d', '显示桌面'),
    ('windows', 'hotkey', 'alt+f4', '关闭当前窗口'),
    ('windows', 'hotkey', 'f11', '全屏切换'),
    ('windows', 'hotkey', 'ctrl+t', '浏览器新标签页'),
    ('windows', 'hotkey', 'ctrl+w', '关闭浏览器标签页'),
    ('windows', 'hotkey', 'ctrl+r', '浏览器刷新'),
    ('windows', 'hotkey', 'enter', '确认/执行'),
    ('windows', 'hotkey', 'escape', '退出/取消'),

    -- macOS系统快捷键
    ('macos', 'hotkey', 'command+tab', '切换应用程序'),
    ('macos', 'hotkey', 'command+f3', '显示桌面'),
    ('macos', 'hotkey', 'command+q', '关闭当前应用'),
    ('macos', 'hotkey', 'ctrl+command+f', '全屏切换'),
    ('macos', 'hotkey', 'command+t', '浏览器新标签页'),
    ('macos', 'hotkey', 'command+w', '关闭浏览器标签页'),
    ('macos', 'hotkey', 'command+r', '浏览器刷新'),
    ('macos', 'hotkey', 'return', '确认/执行'),
    ('macos', 'hotkey', 'escape', '退出/取消'),

    -- 滚轮动作
    ('any', 'scroll', '5', '向上滚动5格'),
    ('any', 'scroll', '-5', '向下滚动5格'),

    -- 窗口管理
    ('any', 'window', 'maximize', '窗口最大化'),
    ('any', 'window', 'minimize', '窗口最小imize'),
    ('any', 'window', 'close', '窗口关闭'),
    ('any', 'window', 'switch', '窗口切换'),

    -- 系统操作
    ('any', 'system', 'volume_up', '增加音量'),
    ('any', 'system', 'volume_down', '减小音量'),
    ('any', 'system', 'mute', '静音切换');

-- 3. 创建通用手势映射 (仅添加几个关键映射作为示例)
-- 静态手势映射
INSERT IGNORE INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`, `enabled`)
SELECT
    NULL, NULL, g.id, a.id, 10, 1
FROM gestures g, actions a
WHERE (g.code, a.action_value, a.os_type) IN (
    ('POINT_UP', 'left_click', 'any'),
    ('THUMBS_UP', 'enter', 'any'),
    ('THUMBS_DOWN', 'escape', 'any'),
    ('OPEN_PALM', 'win+d', 'windows'),
    ('OPEN_PALM', 'command+f3', 'macos'),
    ('CLOSED_FIST', 'alt+f4', 'windows'),
    ('CLOSED_FIST', 'command+q', 'macos')
);

-- 动态手势映射
INSERT IGNORE INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`, `enabled`)
SELECT
    NULL, NULL, g.id, a.id, 5, 1
FROM gestures g, actions a
WHERE (g.code, a.action_value, a.os_type) IN (
    ('swipe_left', 'alt+left', 'any'),
    ('swipe_right', 'alt+right', 'any'),
    ('swipe_up', '5', 'any'),
    ('swipe_down', '-5', 'any')
);

-- 完成
SELECT '基础手势映射配置完成!' as status;

-- 显示配置统计
SELECT
    '手势总数' as item,
    COUNT(*) as count
FROM gestures
UNION ALL
SELECT
    '动作总数' as item,
    COUNT(*) as count
FROM actions
UNION ALL
SELECT
    '映射总数' as item,
    COUNT(*) as count
FROM mappings;