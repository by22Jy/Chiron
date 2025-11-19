# 日志系统使用指南

## 🎯 概述

现在YOLO-LLM系统具有全面的日志记录功能，每个组件都会生成带时间戳的独立日志文件，便于调试和分析问题。

## 📁 日志文件结构

```
agent/
├── logs/                          # 日志目录
│   ├── agent_20251118_180033.log   # 主agent日志
│   ├── video_processor_*.log      # 视频处理日志
│   ├── mediapipe_detector_*.log   # 手势检测日志
│   └── standalone_controller_*.log # 独立控制器日志
├── logger_config.py               # 日志配置管理器
├── log_viewer.py                  # 日志查看和分析工具
└── test_logging_system.py         # 日志系统测试工具
```

## 📋 日志组件说明

### 1. 组件日志分类

- **agent**: 主agent逻辑、配置同步、API调用
- **video**: 视频处理、摄像头操作、帧处理
- **detector**: MediaPipe手势检测、轨迹分析、手势识别
- **standalone**: 独立控制器操作

### 2. 日志格式

```
[2025-11-18 18:00:49] INFO     [agent] Syncing configuration from backend...
[2025-11-18 18:00:50] DEBUG    [detector] Dynamic gesture analysis: history_len=15, dx=0.234, dy=-0.156
[2025-11-18 18:00:51] WARNING  [video] Queue full, skipping frame
[2025-11-18 18:00:52] ERROR    [agent] Backend connection failed: ConnectionError
```

## 🛠️ 日志查看工具

### 基本命令

```bash
cd D:\yolo-llm\agent

# 查看所有日志文件列表
python log_viewer.py list

# 显示日志摘要信息
python log_viewer.py summary

# 查看最新日志内容（默认50行）
python log_viewer.py view

# 查看特定组件的日志
python log_viewer.py view -c agent

# 查看更多行数
python log_viewer.py view -n 100

# 搜索日志内容
python log_viewer.py search "SWIPE_LEFT"

# 搜索特定组件的日志
python log_viewer.py search "gesture detected" -c detector

# 清理7天前的旧日志（预览模式）
python log_viewer.py cleanup -d 7

# 实际执行清理
python log_viewer.py cleanup -d 7 --execute
```

### 高级搜索

```bash
# 搜索错误日志
python log_viewer.py search "ERROR"

# 搜索特定手势
python log_viewer.py search "SWIPE_RIGHT"

# 搜索动作执行
python log_viewer.py search "ACTION_RESULT"

# 显示搜索上下文（更多行）
python log_viewer.py search "MATCH" -C 5
```

## 🔧 使用场景

### 1. 调试手势识别问题

```bash
# 查看手势检测日志
python log_viewer.py view -c detector -n 100

# 搜索特定手势的识别过程
python log_viewer.py search "Recognized SWIPE_LEFT" -C 3
```

### 2. 分析动作执行问题

```bash
# 查看动作执行日志
python log_viewer.py search "ACTION_RESULT"

# 查找映射匹配问题
python log_viewer.py search "No action mapping"
```

### 3. 监控系统状态

```bash
# 查看最新系统日志
python log_viewer.py view -n 20

# 搜索错误和警告
python log_viewer.py search "ERROR\|WARNING"
```

## 📊 日志分析示例

### 查找手势识别问题

```bash
# 1. 搜索手势检测结果
python log_viewer.py search "DETECTOR" -C 2

# 2. 查看动态手势分析
python log_viewer.py search "Dynamic gesture analysis"

# 3. 检查映射匹配
python log_viewer.py search "MATCH" -C 1

# 4. 查看未匹配的手势
python log_viewer.py search "No action mapping"
```

### 分析性能问题

```bash
# 1. 查看帧处理日志
python log_viewer.py search "frame_count"

# 2. 查找队列满的警告
python log_viewer.py search "Queue full"

# 3. 检查处理延迟
python log_viewer.py search "delay"
```

## 🗂️ 日志文件管理

### 自动清理

```bash
# 预览7天前的文件
python log_viewer.py cleanup -d 7

# 清理30天前的文件
python log_viewer.py cleanup -d 30 --execute

# 只清理特定组件的旧日志
python log_viewer.py cleanup -d 7 -c agent --execute
```

### 手动管理

```bash
# 查看日志目录大小
python log_viewer.py summary

# 列出所有日志文件
python log_viewer.py list -n 50
```

## 🎯 调试技巧

### 1. 快速问题定位

```bash
# 查看最新的错误
python log_viewer.py search "ERROR" | tail -10

# 查看最新的手势识别
python log_viewer.py search "Recognized" | tail -5
```

### 2. 端到端流程跟踪

```bash
# 查找完整的手势处理流程
python log_viewer.py search "SWIPE_LEFT" -C 5

# 分析从检测到执行的完整过程
python log_viewer.py search "AGENT.*Gesture detected\|MATCH\|ACTION_RESULT"
```

### 3. 性能监控

```bash
# 监控处理统计
python log_viewer.py search "Stats\|frame_count\|gesture_count"
```

## ⚙️ 日志级别说明

- **DEBUG**: 详细的调试信息，包括轨迹分析、内部状态
- **INFO**: 一般信息，如配置加载、手势识别结果
- **WARNING**: 警告信息，如队列满、资源不足
- **ERROR**: 错误信息，如连接失败、执行异常

## 📝 最佳实践

1. **定期清理**: 建议每周清理一次旧的日志文件
2. **问题排查**: 出现问题时先查看错误日志，再回溯分析
3. **性能监控**: 关注WARNING级别的日志，可能指示性能问题
4. **日志搜索**: 使用具体的关键词搜索，如手势名称、错误类型
5. **上下文查看**: 使用-C参数查看日志前后的上下文信息

## 🆘 常见问题

### Q: 日志文件太大怎么办？
A: 使用cleanup命令定期清理旧日志，或者调整日志级别减少输出量。

### Q: 如何实时查看日志？
A: 使用`python log_viewer.py view -f`命令（如果实现了follow功能）。

### Q: 如何查找特定时间段的日志？
A: 根据文件名中的时间戳选择对应的日志文件。

### Q: 日志文件保存在哪里？
A: 默认保存在`D:\yolo-llm\agent\logs\`目录下。