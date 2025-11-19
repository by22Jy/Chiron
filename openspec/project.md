# Project Context

## Purpose
YOLO-LLM是一个基于AI的**手势控制平台**，结合计算机视觉、机器学习和Web技术，实现基于手势的应用程序控制。系统能够检测对象、姿态、表情和手部手势，然后将这些手势映射到各种系统操作。

**主要目标**:
- 实现高精度的实时手势识别
- 提供端到端的手势到动作映射系统
- 支持多种手势类型（静态手势、动态手势）
- 构建可扩展的微服务架构
- 提供直观的Web界面进行配置和监控

## Tech Stack

### 后端服务
- **Spring Boot 3.3.4** (Java 17) - 主要API服务和配置管理
- **MySQL** - 手势映射数据库
- **Maven** - 项目构建和依赖管理

### AI服务
- **FastAPI** (Python) - 计算机视觉服务
- **MediaPipe** - 手部和姿态检测
- **OpenCV** - 图像处理和视频流
- **YOLOv8** - 目标检测
- **DeepFace** - 表情识别
- **TensorFlow Lite** - 轻量级推理引擎
- **NumPy** - 数值计算

### Agent组件
- **Python 3.8+** - 主要代理逻辑
- **pyautogui** - 系统控制自动化
- **threading** - 多线程视频处理
- **WebSocket** - 实时通信

### 前端
- **Vue.js 3** - Web界面
- **Vite** - 开发服务器和构建工具
- **JavaScript/TypeScript** - 前端逻辑

### 开发工具
- **PowerShell** - Windows自动化脚本
- **Git** - 版本控制
- **VS Code** - 主要IDE

## Project Conventions

### Code Style
- **Python**: 遵循PEP 8，使用snake_case命名
- **Java**: 遵循Spring Boot最佳实践，使用camelCase
- **JavaScript**: 使用现代ES6+语法，camelCase命名
- **配置文件**: YAML格式，使用kebab-case
- **文件命名**: 使用snake_case或kebab-case

### Architecture Patterns
- **微服务架构**: 4个独立服务（后端、AI服务、Agent、前端）
- **事件驱动**: 使用WebSocket进行实时通信
- **生产者-消费者**: 视频处理使用队列模式
- **RESTful API**: 后端提供标准的REST接口
- **配置驱动**: 所有映射关系通过数据库配置

### 服务端口约定
- **8081**: 后端服务 (Spring Boot)
- **8000**: AI服务 (FastAPI)
- **5173**: 前端开发服务器 (Vite)
- **3306**: MySQL数据库

### 日志系统
- **文件日志**: `agent/logs/{component}_{timestamp}.log`
- **组件分离**: agent、video、detector、standalone各组件独立日志
- **时间戳格式**: `YYYYMMDD_HHMMSS`
- **日志级别**: DEBUG、INFO、WARNING、ERROR

### 数据库约定
- **手势代码**: 使用snake_case (swipe_left, thumbs_up)
- **表结构**: gestures、mappings、actions三个核心表
- **优先级**: 使用priority字段处理映射冲突

### Testing Strategy
- **单元测试**: 各组件独立测试
- **集成测试**: 端到端的手势控制流程测试
- **手动测试**: 实时手势识别和浏览器控制测试
- **系统测试**: `test_system_simple.py` 验证所有组件状态

### Git Workflow
- **主分支**: `main` - 稳定的生产代码
- **提交格式**: 使用中文描述，包含技术说明
- **Co-authored标记**: 包含 `🤖 Generated with [Claude Code](https://claude.com/claude-code)`

## Domain Context

### 手势类型
- **静态手势**: POINT_UP、THUMBS_UP、VICTORY、CLOSED_FIST等
- **动态手势**: swipe_left、swipe_right、swipe_up、swipe_down
- **特殊手势**: pinch_close（捏合手势）

### 动作类型
- **hotkey**: 键盘快捷键 (ctrl+t, ctrl+pgup等)
- **mouse**: 鼠标操作 (left_click, right_click)
- **scroll**: 滚动操作 (5, -5表示滚动方向)
- **window**: 窗口操作
- **system**: 系统级操作

### 关键组件
- **MediaPipeDetector**: 手势识别核心，支持轨迹分析
- **VideoProcessor**: 视频流处理，多线程架构
- **ActionExecutor**: 动作执行引擎，跨平台支持
- **GestureAgent**: 主要代理，处理配置和协调

### 浏览器快捷键（Windows Chrome）
- **标签页切换**: ctrl+pgup（左）、ctrl+pgdn（右）
- **新标签页**: ctrl+t
- **关闭标签页**: ctrl+w

## Important Constraints

### 性能要求
- **实时处理**: 30fps视频流处理
- **延迟要求**: 手势到动作的延迟应小于100ms
- **准确率**: 手势识别准确率应大于90%
- **资源使用**: 内存使用应保持在合理范围

### 兼容性要求
- **操作系统**: 主要支持Windows，考虑跨平台
- **Python版本**: Python 3.8+
- **Java版本**: Java 17+
- **浏览器**: Chrome作为主要目标浏览器

### 安全考虑
- **摄像头权限**: 需要用户明确授权
- **系统控制**: 动作执行应限制在安全范围内
- **数据隐私**: 本地处理，不上传视频数据

### 端口管理
- **端口冲突检测**: 自动检测和处理端口占用
- **配置灵活性**: 支持端口配置和自动分配

## External Dependencies

### AI/ML框架
- **MediaPipe**: Google的手势检测库
- **OpenCV**: 计算机视觉基础库
- **TensorFlow**: 深度学习推理引擎
- **NumPy**: 数值计算基础库

### Web框架
- **Spring Boot**: Java Web框架
- **FastAPI**: Python高性能Web框架
- **Vue.js**: 前端框架

### 数据库
- **MySQL**: 主要数据存储
- **HikariCP**: 数据库连接池

### 系统自动化
- **pyautogui**: Python GUI自动化库
- **PowerShell**: Windows系统脚本

### 开发工具
- **MediaPipe模型**: 预训练的手势检测模型
- **YOLOv8模型**: 目标检测模型
- **DeepFace模型**: 表情识别模型

## 环境配置要求

### 系统要求
- **操作系统**: Windows 10/11 (主要), Linux, macOS (支持)
- **Python**: 3.8+ with pip
- **Java**: 17+ with Maven
- **Node.js**: 18+ with npm
- **MySQL**: 8.0+

### 硬件要求
- **摄像头**: USB摄像头或内置摄像头
- **内存**: 最少4GB，推荐8GB+
- **CPU**: 支持多核处理器以提升视频处理性能
- **GPU**: 可选，支持CUDA加速（如可用）

### 环境变量
- **KIMI_API_KEY** 或 **QWEN_API_KEY**: 用于AI功能增强
- **数据库配置**: MySQL连接参数
- **端口配置**: 各服务端口配置（支持8080、8081等）
