# YOLO-LLM 项目架构与用户指南

## 📋 项目概述

YOLO-LLM 已经从一个简单的手势识别项目发展成为一个**多模态智能代理平台**，集成了手势识别、语音控制、AI对话、计算机视觉和MCP工具集成等先进功能。

## 🏗️ 完整架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层                                  │
├─────────────────────────────────────────────────────────────┤
│  Web界面(5173)  │  手势控制  │  语音控制  │  AI对话  │  Agent  │
│   (Vue.js)     │   (Agent)   │   (Agent)   │ (LLM)   │ (Python)│
└─────────────────┼─────────────────┼─────────────────┼─────────┘
                  │                 │                 │
┌─────────────────▼─────────────────▼─────────────────▼─────────┐
│                     核心服务层                                 │
├─────────────────────────────────────────────────────────────┤
│  Backend(8080)  │   AI Service(8000)   │  MCP Server(8082)  │
│  (Spring Boot)  │    (FastAPI)         │   (Python/FastAPI) │
│  - 配置管理      │    - YOLO检测         │   - 新闻API         │
│  - 事件处理      │    - 姿态识别         │   - 天气API         │
│  - 数据存储      │    - 情绪识别         │   - 邮件发送        │
│  - MCP集成       │    - 实时流处理       │   - 文件操作        │
│                 │                      │   - 高级电脑控制     │
└─────────────────┼──────────────────────┼─────────────────────┘
                  │                      │
┌─────────────────▼──────────────────────▼─────────────────────┐
│                   数据层                                     │
├─────────────────────────────────────────────────────────────┤
│    MySQL数据库     │    模型文件      │     API服务          │
│   (用户/配置/日志)  │  (YOLO/MediaPipe) │ (News/Weather/Email)│
└─────────────────────────────────────────────────────────────┘
```

## 🎯 用户视角功能矩阵

### 核心功能模块

| 功能模块 | 用户接口 | 主要功能 | 状态 | 使用方式 |
|---------|---------|---------|------|----------|
| **手势识别控制** | 摄像头+Agent | 8种手势→7种动作映射 | ✅ 完整 | `python main.py --realtime` |
| **语音控制** | 麦克风+Agent | 语音命令→系统操作 | ✅ 完整 | `python voice_simple_final.py` |
| **Web界面** | 浏览器http://localhost:5173 | 可视化监控+配置 | ✅ 完整 | `npm run dev` |
| **AI智能对话** | API接口 | DeepSeek LLM集成 | ✅ 完整 | `/api/llm/chat` |
| **计算机视觉** | API接口 | YOLO检测+姿态+情绪 | ✅ 完整 | `/detect/*`, `/analyze/*` |
| **MCP工具集** | API接口 | 新闻/天气/邮件/文件操作 | ✅ 完整 | `/mcp/*` |
| **高级电脑控制** | API接口 | 应用启动+工作流执行 | ✅ 新增 | `/mcp/computer_control` |

### 支持的具体功能

#### 🖐️ 手势识别功能
```
👆 POINT_UP     → 热键动作 (如音量+)
👍 THUMBS_UP    → 点击动作 (确认/选择)
✌️ VICTORY      → 滚动动作 (页面滚动)
👌 OK_SIGN      → 文本输入 (输入预设文本)
🤘 ROCK_SIGN    → 鼠标移动 (定位到目标)
🤙 CALL_ME      → 窗口操作 (切换/最大化)
✋ PALM         → 系统命令 (锁屏/截图)
✊ FIST         → 自定义动作 (打开应用)
```

#### 🎤 语音控制功能
```
"打开记事本"     → 启动notepad.exe
"音量增加"       → 系统音量+10%
"切换窗口"       → Alt+Tab
"截图"           → 保存屏幕截图
"搜索XXX"        → 打开浏览器搜索
"播放音乐"       → 启动音乐应用
```

#### 🤖 AI智能功能
```
自然语言对话     → DeepSeek LLM响应
场景分析         → YOLO物体检测结果
手势理解         → MediaPipe手势识别
情绪分析         → DeepFace情绪检测
```

#### 🌐 MCP工具功能
```
新闻获取         → NewsAPI.org 实时新闻
天气查询         → OpenWeatherMap 天气信息
邮件发送         → SMTP邮件服务
文件操作         → 读写系统文件
屏幕截图         → 屏幕捕获功能
浏览器控制       → 自动化网页操作
高级电脑控制     → 应用启动+工作流执行
```

## 🚀 用户启动指南

### 方式1: 一键启动（推荐新手）

```bash
# Windows用户
start-all.bat

# Linux/Mac用户
./start-all.sh
```

**启动流程**:
1. ✅ 检查MySQL连接
2. ✅ 启动Backend服务 (8080端口)
3. ✅ 启动AI服务 (8000端口)
4. ✅ 启动Frontend服务 (5173端口)
5. ✅ 安装Agent依赖
6. ❓ 询问是否启动语音控制

### 方式2: 完整手动启动（推荐开发者）

#### 1. 环境准备
```bash
# 检查环境
mysql --version
java --version
python --version
node --version
npm --version
```

#### 2. 数据库准备
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE yolo_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE yolo_platform;
SOURCE setup-database.sql;
```

#### 3. 启动核心服务

**Backend服务** (端口8080):
```bash
cd backend
export KIMI_API_KEY=your_api_key  # 或 QWEN_API_KEY
mvn spring-boot:run
```

**AI服务** (端口8000):
```bash
cd ai
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend服务** (端口5173):
```bash
cd frontend
npm install
npm run dev
```

**MCP服务** (端口8082) - 新增!
```bash
cd mcp
# 设置API密钥
export NEWS_API_KEY=your_news_api_key
export WEATHER_API_KEY=your_weather_api_key
export BREVO_API_KEY=your_email_api_key
python real_mcp_server.py
```

#### 4. 启动Agent (选择其一)

**手势控制Agent**:
```bash
cd agent
pip install -r requirements.txt
python main.py --realtime
```

**语音控制Agent**:
```bash
cd agent
python voice_simple_final.py
```

**智能Agent** (LLM+视觉+控制):
```bash
cd agent
python main.py --chat
```

### 方式3: 最小化启动（测试验证）

如果只想快速验证核心功能：

```bash
# 只启动Backend + MCP (最简配置)
cd backend
mvn spring-boot:run &

cd mcp
python simple_mcp_server.py &
```

## 🌐 用户访问地址

启动成功后，用户可通过以下地址访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **Web管理界面** | http://localhost:5173 | 主要用户界面 |
| **后端API** | http://localhost:8080 | 系统核心API |
| **AI服务API** | http://localhost:8000 | 计算机视觉API |
| **MCP服务** | http://localhost:8082 | 工具集成API |
| **API文档** | http://localhost:8000/docs | 交互式API文档 |

## 🎮 使用场景示例

### 场景1: 手势控制工作流
```
1. 启动Agent: python main.py --realtime
2. 做出👍手势 → 系统确认
3. 做出✌️手势 → 滚动页面
4. 做出🤙手势 → 切换窗口
5. 做出✋手势 → 系统截图
```

### 场景2: 语音智能助手
```
1. 启动Agent: python voice_simple_final.py
2. 用户说: "帮我打开Chrome"
3. 系统响应: 自动启动Chrome浏览器
4. 用户说: "今天天气怎么样"
5. 系统响应: 语音播报天气信息
```

### 场景3: Web界面管理
```
1. 访问: http://localhost:5173
2. 查看实时系统监控
3. 配置手势映射规则
4. 查看AI分析结果
5. 管理用户偏好设置
```

### 场景4: AI智能对话
```
1. POST http://localhost:8080/api/llm/chat
2. Body: {"message": "分析这张图片并描述"}
3. 系统响应: YOLO检测 + LLM分析 + 结果描述
```

### 场景5: MCP智能工作流
```
1. POST http://localhost:8080/mcp/enhanced-chat
2. Body: {
   "message": "获取北京天气并发送到我的邮箱",
   "required_tools": ["weather", "email"]
}
3. 系统自动执行: 天气查询 → 邮件撰写 → 发送完成
```

## 🔧 配置要求

### 最低配置
- **CPU**: 双核2.0GHz
- **内存**: 4GB RAM
- **存储**: 2GB可用空间
- **系统**: Windows 10/11, Linux, macOS

### 推荐配置
- **CPU**: 四核3.0GHz+
- **内存**: 8GB+ RAM
- **GPU**: NVIDIA GPU (支持CUDA)
- **存储**: 5GB+ SSD
- **外设**: 摄像头、麦克风

### API密钥配置 (可选)
```bash
# LLM服务
KIMI_API_KEY=your_kimi_api_key
# 或
QWEN_API_KEY=your_qwen_api_key

# MCP工具
NEWS_API_KEY=your_newsapi_key
WEATHER_API_KEY=your_openweather_key
BREVO_API_KEY=your_brevo_key

# 邮件SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_app_password
```

## 🚨 故障排除

### 常见问题及解决方案

1. **端口占用冲突**
   ```bash
   # 查看端口占用
   netstat -ano | findstr :8080
   # 终止占用进程
   taskkill /PID <进程ID> /F
   ```

2. **摄像头无法访问**
   ```bash
   # 检查摄像头设备
   # Windows: 设备管理器 → 摄像头
   # Linux: ls /dev/video*
   # 修改agent/config.yaml中的camera_id
   ```

3. **API密钥错误**
   ```bash
   # 检查环境变量
   echo $KIMI_API_KEY
   # 或在Backend的application.yml中配置
   ```

4. **依赖安装失败**
   ```bash
   # 清理缓存重装
   pip cache purge
   pip install -r requirements.txt --no-cache-dir
   ```

5. **数据库连接失败**
   ```bash
   # 检查MySQL服务状态
   mysql -u root -p -e "SHOW PROCESSLIST;"
   # 重启MySQL服务
   # Windows: services.msc → MySQL
   # Linux: sudo systemctl restart mysql
   ```

## 📊 性能优化建议

1. **GPU加速**: 安装CUDA版本的PyTorch
2. **模型缓存**: 首次运行后模型会缓存，后续启动更快
3. **网络优化**: 配置CDN或镜像加速模型下载
4. **资源限制**: 调整config.yaml中的检测参数平衡性能和精度

## 🎯 下一步发展方向

1. **增强MCP工具**: 集成更多第三方API服务
2. **智能工作流**: 支持用户自定义复杂工作流
3. **移动端支持**: 开发移动应用实现远程控制
4. **云端部署**: 支持Docker容器化部署
5. **多语言支持**: 国际化和本地化支持

---

**YOLO-LLM 不仅仅是一个手势识别系统，而是一个完整的多模态智能代理平台，为用户提供了从基础手势控制到高级AI工作流的全方位智能体验！** 🚀