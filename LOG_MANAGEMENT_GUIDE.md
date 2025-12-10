# YOLO-LLM 日志管理系统使用指南

## 概述

为了解决每次启动系统后需要手动复制日志的问题，我们实现了一个自动化的日志管理系统。该系统会在每次启动时自动创建日志会话目录，收集各模块的日志，并提供便捷的查看和分析工具。

## 目录结构

```
d:\yolo-llm\
├── logs\                          # 主日志目录
│   ├── session_20251210_154543\   # 按时间戳命名的会话目录
│   │   ├── backend\              # 后端日志
│   │   │   └── spring-boot.log
│   │   ├── ai_service\           # AI服务日志
│   │   │   └── fastapi.log
│   │   ├── mcp\                  # MCP服务器日志
│   │   │   └── mcp_server.log
│   │   ├── agent\                # 语音Agent日志
│   │   │   └── agent.log
│   │   ├── frontend\             # 前端日志
│   │   │   └── frontend.log
│   │   └── session_info.json     # 会话信息文件
│   └── session_20251210_154621\   # 最新的会话目录
│       └── ...
├── log_manager.py                # 日志管理器核心
├── log_reader.py                 # 日志读取和分析工具
├── start_system_with_logging.py  # 带日志管理的启动器
├── start_with_logging.bat        # Windows启动脚本
├── view_logs.bat                 # Windows日志查看脚本
└── test_log_system.py            # 测试脚本
```

## 快速开始

### 1. 启动系统（带日志管理）

```bash
# 方法1: 使用批处理脚本（推荐）
start_with_logging.bat

# 方法2: 直接运行Python脚本
python start_system_with_logging.py
```

### 2. 查看日志

```bash
# 方法1: 使用交互式菜单（推荐）
view_logs.bat

# 方法2: 直接使用命令行工具
python log_reader.py                    # 查看最新日志
python log_reader.py -m mcp            # 查看MCP模块日志
python log_reader.py -e                # 只查看错误信息
python log_reader.py --info            # 查看会话信息
python log_reader.py --list            # 列出所有会话
python log_reader.py --watch           # 实时监控日志
```

## 命令行工具详细说明

### log_reader.py 参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--module` | `-m` | 指定模块名称 | `-m backend` |
| `--lines` | `-l` | 显示行数（默认50） | `-l 100` |
| `--errors` | `-e` | 只显示错误信息 | `--errors` |
| `--session` | `-s` | 指定会话名称 | `-s session_20251210_154543` |
| `--info` | `-i` | 显示会话信息 | `--info` |
| `--list` | | 列出所有会话 | `--list` |
| `--watch` | `-w` | 实时监控日志 | `--watch` |

### 可用模块名称

- `backend` - Spring Boot后端服务
- `ai_service` - FastAPI AI服务
- `mcp` - MCP服务器
- `agent` - 语音识别Agent
- `frontend` - Vue.js前端服务

## 使用示例

### 查看最新错误
```bash
python log_reader.py -e
```

### 查看MCP服务器最后100行日志
```bash
python log_reader.py -m mcp -l 100
```

### 实时监控后端日志
```bash
python log_reader.py -m backend --watch
```

### 查看特定会话的错误信息
```bash
python log_reader.py -e -s session_20251210_154543
```

### 列出所有历史会话
```bash
python log_reader.py --list
```

## 会话信息

每个会话都包含一个 `session_info.json` 文件，记录了：

- 会话ID和开始时间
- 系统平台信息
- 各模块启动状态和端口信息
- 模块最后更新时间

示例：
```json
{
  "session_id": "session_20251210_154543",
  "start_time": "2025-12-10T15:45:43.123456",
  "platform": "win32",
  "modules": {
    "backend": {
      "status": "completed",
      "port": 8080,
      "last_update": "2025-12-10T15:46:12.789012"
    },
    "mcp_server": {
      "status": "logging",
      "port": 8083
    }
  }
}
```

## 错误检测和告警

系统自动检测以下错误关键词：
- `error`
- `exception`
- `failed`
- `错误`
- `失败`
- `异常`

当发现错误时，会在日志中标记并可以通过 `--errors` 参数快速查看。

## 日志清理

系统会自动清理旧的会话日志，默认保留最新的10个会话。可以通过修改 `LogManager.cleanup_old_sessions()` 方法的参数来调整保留数量。

## 最佳实践

### 1. 定期查看错误摘要
```bash
python log_reader.py -e
```

### 2. 问题排查流程
1. 使用 `view_logs.bat` 选择"查看错误信息"
2. 如果需要详细信息，查看具体模块日志
3. 使用实时监控观察运行状态

### 3. 性能监控
- 系统会每分钟自动保存系统状态快照
- 包含磁盘使用情况和进程信息

### 4. 开发调试
- 使用实时监控功能：`python log_reader.py --watch`
- 专注于特定模块：`python log_reader.py -m <module> --watch`

## 故障排除

### 问题：日志显示乱码
**解决方案**：确保系统支持UTF-8编码，或使用Windows批处理脚本

### 问题：找不到日志文件
**解决方案**：
1. 确认使用了带日志管理的启动器
2. 检查 `logs/` 目录是否存在
3. 使用 `--list` 参数查看所有会话

### 问题：实时监控不工作
**解决方案**：
1. 确保有活动的日志会话
2. 检查日志文件是否有写入权限
3. 使用Ctrl+C退出监控

## 开发者信息

### 扩展日志收集
如需为新的模块添加日志收集，请在 `start_system_with_logging.py` 中添加相应的启动方法。

### 自定义错误检测
可以修改 `LogReader` 中的错误关键词列表来调整错误检测规则。

### 集成到CI/CD
日志文件可以轻松集成到持续集成流程中，用于自动化测试和部署监控。