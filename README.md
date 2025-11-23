# YOLO-LLM 手势控制AI平台

## 项目简介

YOLO-LLM 是一个基于AI的手势控制平台，结合计算机视觉、机器学习和Web技术，实现手势识别与应用控制的智能系统。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend     │    │   AI Service    │
│   (Vue.js)      │◄──►│  (Spring Boot)  │◄──►│   (FastAPI)     │
│   Port: 5173    │    │   Port: 8080    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │     Agent       │
                                              │   (Python)      │
                                              │  手势识别+控制   │
                                              └─────────────────┘
```

## 核心功能

### 🎯 手势识别
- 支持8种手势：POINT_UP、THUMBS_UP、VICTORY、OK_SIGN等
- 基于MediaPipe的实时检测
- 可配置检测间隔和置信度
- 支持静态手势和动态滑动识别

### 🎮 动作执行
- 7种动作类型：热键、鼠标、点击、滚动、文本、窗口、系统
- 跨平台支持（Windows/Linux/Mac）
- 可扩展的动作框架
- 智能动作映射和配置

### 🤖 AI能力
- YOLOv8物体检测和跟踪
- MediaPipe姿态估计
- DeepFace情感识别
- WebSocket实时流处理
- 多模态数据分析

### 🎨 现代化界面
- 响应式Vue.js前端
- 实时性能监控仪表盘
- 现代化白色主题UI
- 丰富的数据可视化

## 快速开始

### 环境要求

- **Python 3.8+** (Agent & AI Service)
- **Java 17+** (Backend)
- **Node.js 18+** (Frontend)
- **MySQL 5.7+** (数据库)
- **摄像头** (手势检测)

### 一键启动

#### Windows
```bash
# 直接运行启动脚本
start-all.bat
```

#### Linux/Mac
```bash
# 给脚本执行权限
chmod +x start-all.sh

# 启动所有服务
./start-all.sh

# 停止所有服务
./stop-all.sh
```

### 手动启动

#### 1. 数据库准备
```sql
CREATE DATABASE yolo_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 2. 后端服务 (端口: 8080)
```bash
cd backend
# 设置环境变量
export KIMI_API_KEY=your_api_key  # 或 QWEN_API_KEY
mvn spring-boot:run
```

#### 3. AI服务 (端口: 8000)
```bash
cd ai
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### 4. 前端服务 (端口: 5173)
```bash
cd frontend
npm install
npm run dev
```

#### 5. Agent (可选)
```bash
cd agent
pip install -r requirements.txt

# 实时手势检测
python main.py --realtime

# 守护进程模式
python main.py --daemon

# 测试单个手势
python main.py --gesture THUMBS_UP

# 查看支持的动作
python main.py --actions
```

## 访问地址

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8080
- **AI服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 配置说明

### 环境变量
```bash
# 数据库配置
DB_URL=jdbc:mysql://127.0.0.1:3306/yolo_platform
DB_USER=root
DB_PASS=your_password

# LLM API配置 (二选一)
KIMI_API_KEY=your_kimi_api_key
QWEN_API_KEY=your_qwen_api_key
```

### Agent配置 (`agent/config.yaml`)
```yaml
backend:
  base_url: 'http://127.0.0.1:8080'
  username: 'admin'
  application: 'chrome.exe'
  os: 'windows'

agent:
  source: 'python-agent@dev'
  poll_interval: 60

video:
  camera_id: 1          # 摄像头ID
  width: 640           # 视频宽度
  height: 480          # 视频高度
  fps: 30              # 帧率
  show_preview: true   # 显示预览窗口
  flip_horizontal: true
  detection_interval: 0.1
```

## API接口

### 后端接口 (端口: 8080)
- `GET /api/config` - 获取手势映射配置
- `POST /api/audit/log` - 记录手势执行日志
- `POST /api/event` - 发送事件
- `GET /api/monitor/*` - 系统监控接口

### AI服务接口 (端口: 8000)
- `POST /detect/file` - 物体检测（文件上传）
- `POST /analyze/file` - 综合分析（检测+姿态+手势+情感）
- `GET /ws/analyze` - WebSocket实时分析流

## 手势类型

### 静态手势
```python
# 支持的手势代码
POINT_UP = "point_up"        # 👆 指向上方
THUMBS_UP = "thumbs_up"      # 👍 点赞
VICTORY = "victory"          # ✌️ 胜利手势
OK_SIGN = "ok_sign"          # 👌 OK手势
ROCK_SIGN = "rock_sign"      # 🤘 摇滚手势
CALL_ME = "call_me"          # 🤙 打电话
PALM = "palm"                # ✋ 手掌
FIST = "fist"                # ✊ 拳头
```

### 动态手势
```python
# 支持的动态手势
SWIPE_UP = "swipe_up"        # 向上滑动
SWIPE_DOWN = "swipe_down"    # 向下滑动
SWIPE_LEFT = "swipe_left"    # 向左滑动
SWIPE_RIGHT = "swipe_right"  # 向右滑动
```

## 动作类型
```python
# 支持的动作类型
hotkey  # 热键组合 (Ctrl+C, Alt+Tab等)
mouse   # 鼠标移动和定位
click   # 鼠标点击 (左键/右键/中键)
scroll  # 鼠标滚动 (向上/向下)
text    # 文本输入和键盘输入
window  # 窗口操作 (最大化/最小化/关闭)
system  # 系统命令 (音量控制/锁屏等)
```

## 开发说明

### 项目结构
```
yolo-llm/
├── backend/          # Spring Boot后端服务
│   ├── src/         # Java源代码
│   └── pom.xml      # Maven配置
├── ai/              # FastAPI AI服务
│   ├── main.py      # FastAPI应用入口
│   └── requirements.txt
├── agent/           # Python手势控制Agent
│   ├── main.py      # Agent主程序
│   ├── config.yaml  # Agent配置文件
│   └── requirements.txt
├── frontend/        # Vue.js前端应用
│   ├── src/        # Vue源代码
│   ├── package.json
│   └── vite.config.js
├── start-all.bat    # Windows一键启动脚本
├── start-all.sh     # Linux/Mac一键启动脚本
├── stop-all.sh      # 停止服务脚本
└── README.md        # 项目说明文档
```

### 技术栈
- **Backend**: Spring Boot, MySQL, WebSocket
- **AI Service**: FastAPI, MediaPipe, YOLO, DeepFace
- **Agent**: OpenCV, PyAutoGUI, MediaPipe
- **Frontend**: Vue.js 3, Element Plus, ECharts
- **Database**: MySQL 5.7+

## 故障排除

### 常见问题

1. **摄像头无法访问**
   - 检查摄像头权限和设备状态
   - 修改config.yaml中的camera_id（尝试0、1、2等）
   - 确认没有其他应用占用摄像头

2. **模型加载失败**
   - 确保网络连接正常（首次运行会下载YOLO模型）
   - 检查ultralytics和mediapipe包是否正确安装
   - 尝试手动下载模型文件到models/目录

3. **后端连接失败**
   - 确认后端服务在8080端口正常运行
   - 检查数据库连接配置和数据库服务状态
   - 查看后端日志确认具体错误信息

4. **CORS跨域错误**
   - 检查FastAPI的CORS中间件配置
   - 确认前端请求地址和端口正确
   - 检查防火墙和网络配置

5. **手势识别精度低**
   - 调整config.yaml中的detection_interval参数
   - 确保光线充足且手势清晰可见
   - 检查摄像头分辨率和帧率设置

### 日志查看
- **Backend**: 控制台输出或日志文件
- **AI Service**: 控制台输出或 `ai.log`
- **Frontend**: 浏览器开发者工具Console面板
- **Agent**: 控制台输出

### 性能优化建议
- 使用GPU加速模型推理（安装CUDA版本的PyTorch）
- 调整视频分辨率和帧率以平衡性能和精度
- 启用模型缓存减少重复加载时间
- 优化网络请求和WebSocket连接

## 贡献指南

1. Fork项目到个人仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 发起Pull Request

### 开发规范
- 遵循现有代码风格和架构设计
- 添加适当的注释和文档
- 编写单元测试和集成测试
- 确保所有测试通过后再提交

## 许可证

本项目采用MIT许可证，详见[LICENSE](LICENSE)文件。

## 更新日志

### v1.0.0 (最新)
- ✅ 完成基础手势识别和动作执行
- ✅ 集成MediaPipe和YOLO模型
- ✅ 实现现代化Vue.js前端界面
- ✅ 添加实时监控和性能分析
- ✅ 支持Windows/Linux/Mac跨平台
- ✅ 完整的API文档和使用说明

---

**开始使用YOLO-LLM，体验下一代手势交互技术！** 🚀
