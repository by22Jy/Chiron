-- comprehensive_gesture_mappings.sql
-- 为YOLO-LLM项目添加完整的手势控制映射
-- 包含静态手势和所有动态手势的实际应用场景

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
INSERT IGNORE INTO `actions` (`os_type`, `action_type`, `action_value`, `description`, `payload_json`)
VALUES
    -- Windows系统快捷键
    ('windows', 'hotkey', 'alt+tab', '切换应用程序'),
    ('windows', 'hotkey', 'win+d', '显示桌面'),
    ('windows', 'hotkey', 'win+tab', '任务视图'),
    ('windows', 'hotkey', 'alt+f4', '关闭当前窗口'),
    ('windows', 'hotkey', 'f11', '全屏切换'),
    ('windows', 'hotkey', 'ctrl+t', '浏览器新标签页'),
    ('windows', 'hotkey', 'ctrl+w', '关闭浏览器标签页'),
    ('windows', 'hotkey', 'ctrl+r', '浏览器刷新'),
    ('windows', 'hotkey', 'ctrl+tab', '浏览器标签页切换'),
    ('windows', 'hotkey', 'ctrl+shift+t', '恢复关闭的标签页'),
    ('windows', 'hotkey', 'space', '播放/暂停 (视频/音乐)'),
    ('windows', 'hotkey', 'escape', '退出/取消'),
    ('windows', 'hotkey', 'enter', '确认/执行'),

    -- macOS系统快捷键
    ('macos', 'hotkey', 'command+tab', '切换应用程序'),
    ('macos', 'hotkey', 'command+f3', '显示桌面'),
    ('macos', 'hotkey', 'command+tab', '任务视图'),
    ('macos', 'hotkey', 'command+q', '关闭当前应用'),
    ('macos', 'hotkey', 'ctrl+command+f', '全屏切换'),
    ('macos', 'hotkey', 'command+t', '浏览器新标签页'),
    ('macos', 'hotkey', 'command+w', '关闭浏览器标签页'),
    ('macos', 'hotkey', 'command+r', '浏览器刷新'),
    ('macos', 'hotkey', 'ctrl+tab', '浏览器标签页切换'),
    ('macos', 'hotkey', 'command+shift+t', '恢复关闭的标签页'),
    ('macos', 'hotkey', 'space', '播放/暂停 (视频/音乐)'),
    ('macos', 'hotkey', 'escape', '退出/取消'),
    ('macos', 'hotkey', 'return', '确认/执行'),

    -- 鼠标动作
    ('any', 'mouse', 'left_click', '鼠标左键单击'),
    ('any', 'mouse', 'right_click', '鼠标右键单击'),
    ('any', 'mouse', 'double_click', '鼠标双击'),

    -- 滚轮动作
    ('any', 'scroll', 'scroll_up', '向上滚动', '{"clicks": 3}'),
    ('any', 'scroll', 'scroll_down', '向下滚动', '{"clicks": 3}'),
    ('any', 'scroll', 'scroll_left', '向左滚动', '{"clicks": 1}'),
    ('any', 'scroll', 'scroll_right', '向右滚动', '{"clicks": 1}'),

    -- 浏览器导航 (暂时使用hotkey类型，因为web_navigation不在actions表中)
    ('any', 'hotkey', 'alt+left', '浏览器后退'),
    ('any', 'hotkey', 'alt+right', '浏览器前进'),
    ('any', 'hotkey', 'alt+home', '浏览器主页'),

    -- 窗口管理 (暂时使用hotkey类型)
    ('any', 'hotkey', 'alt+space', '窗口菜单'),
    ('any', 'hotkey', 'alt+f4', '关闭窗口'),
    ('any', 'hotkey', 'win+down', '窗口恢复'),

    -- 音量控制 (暂时使用hotkey类型)
    ('any', 'hotkey', 'volume_up', '增加音量'),
    ('any', 'hotkey', 'volume_down', '减小音量'),
    ('any', 'hotkey', 'volume_mute', '静音切换');

-- 3. 创建通用的手势映射配置（适用于所有用户和应用程序）
-- 静态手势映射
INSERT IGNORE INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`, `enabled`)
SELECT
    NULL as user_id,  -- 所有用户
    NULL as application_id,  -- 所有应用程序
    g.id as gesture_id,
    a.id as action_id,
    10 as priority,  -- 优先级
    1 as enabled
FROM gestures g, actions a
WHERE (g.code, a.action_value, a.os_type) IN (
    -- 基本控制手势
    ('POINT_UP', 'left_click', 'any'),
    ('THUMBS_UP', 'enter', 'any'),
    ('THUMBS_DOWN', 'escape', 'any'),

    -- 窗口管理
    ('OPEN_PALM', 'win+d', 'windows'),
    ('OPEN_PALM', 'command+f3', 'macos'),
    ('CLOSED_FIST', 'alt+f4', 'windows'),
    ('CLOSED_FIST', 'command+q', 'macos'),

    -- 浏览器控制
    ('VICTORY', 'ctrl+t', 'windows'),
    ('VICTORY', 'command+t', 'macos'),
    ('OK_SIGN', 'f11', 'windows'),
    ('OK_SIGN', 'ctrl+command+f', 'macos'),

    -- 标签页管理
    ('POINT_INDEX', 'ctrl+w', 'windows'),
    ('POINT_INDEX', 'command+w', 'macos')
);

-- 动态手势映射
INSERT IGNORE INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`, `enabled`)
SELECT
    NULL as user_id,
    NULL as application_id,
    g.id as gesture_id,
    a.id as action_id,
    5 as priority,  -- 更高优先级
    1 as enabled
FROM gestures g, actions a
WHERE (g.code, a.action_value, a.os_type) IN (
    -- 浏览器导航
    ('swipe_left', 'ctrl+left', 'windows'),
    ('swipe_left', 'command+option+left', 'macos'),
    ('swipe_right', 'ctrl+right', 'windows'),
    ('swipe_right', 'command+option+right', 'macos'),

    -- 页面滚动
    ('swipe_up', 'scroll_up', 'any'),
    ('swipe_down', 'scroll_down', 'any'),

    -- 应用切换
    ('swipe_up', 'alt+tab', 'windows'),
    ('swipe_up', 'command+tab', 'macos')
);

-- 4. 为Chrome浏览器创建专门的应用配置
-- 首先确保Chrome应用存在
INSERT IGNORE INTO `applications` (`code`, `name`, `description`)
VALUES ('chrome.exe', 'Google Chrome', '网页浏览器'),
       ('firefox.exe', 'Mozilla Firefox', '网页浏览器'),
       ('edge.exe', 'Microsoft Edge', '网页浏览器'),
       ('powerpnt.exe', 'Microsoft PowerPoint', '演示软件'),
       ('explorer.exe', 'Windows Explorer', '文件管理器');

-- 5. 创建特定应用的手势映射
INSERT IGNORE INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`, `enabled`)
SELECT
    u.id as user_id,
    app.id as application_id,
    g.id as gesture_id,
    a.id as action_id,
    20 as priority,  -- 最高优先级
    1 as enabled
FROM users u, applications app, gestures g, actions a
WHERE u.username = 'admin'
  AND app.code IN ('chrome.exe', 'firefox.exe', 'edge.exe')
  AND (g.code, a.action_value, a.os_type) IN (
    -- 浏览器专用手势
    ('swipe_left', 'web_navigation', 'any'),  -- 后退
    ('swipe_right', 'web_navigation', 'any'), -- 前进
    ('swipe_up', 'ctrl+t', 'windows'),        -- 新标签页
    ('swipe_up', 'command+t', 'macos'),
    ('swipe_down', 'ctrl+w', 'windows'),      -- 关闭标签页
    ('swipe_down', 'command+w', 'macos'),

    -- 演示模式手势
    ('VICTORY', 'f5', 'windows'),             -- 切换幻灯片
    ('VICTORY', 'shift+f5', 'macos'),
    ('CLOSED_FIST', 'escape', 'any'),         -- 退出演示
    ('THUMBS_UP', 'right_click', 'any'),      -- 下一页
    ('THUMBS_DOWN', 'left_click', 'any')      -- 上一页
  )
  AND (a.os_type = 'any' OR a.os_type = CASE
    WHEN app.code LIKE 'chrome.exe' THEN 'windows'
    WHEN app.code LIKE 'firefox.exe' THEN 'windows'
    WHEN app.code LIKE 'edge.exe' THEN 'windows'
    ELSE a.os_type
  END);

-- 6. 为演示软件创建专门配置
INSERT IGNORE INTO `mappings` (`user_id`, `application_id`, `gesture_id`, `action_id`, `priority`, `enabled`)
SELECT
    u.id as user_id,
    app.id as application_id,
    g.id as gesture_id,
    a.id as action_id,
    30 as priority,  -- 演示模式最高优先级
    1 as enabled
FROM users u, applications app, gestures g, actions a
WHERE u.username = 'admin'
  AND app.code = 'powerpnt.exe'
  AND (g.code, a.action_value) IN (
    -- PowerPoint演示控制
    ('THUMBS_UP', 'right_click'),     -- 下一页
    ('THUMBS_DOWN', 'left_click'),    -- 上一页
    ('VICTORY', 'f5'),                -- 开始演示
    ('OPEN_PALM', 'escape'),          -- 退出演示
    ('CLOSED_FIST', 'escape'),        -- 退出演示
    ('OK_SIGN', 'b'),                 -- 黑屏
    ('POINT_UP', 'w')                 -- 白屏
  );

-- 完成
SELECT '手势映射配置完成!' as status;

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