# YOLO-LLM 开发指南

## 🚀 快速开始

### 环境要求

**基础环境**
- **Python 3.8+** - AI服务和智能代理开发
- **Java 17+** - Spring Boot后端开发
- **Node.js 18+** - Vue.js前端开发
- **MySQL 8.0+** - 数据存储 (可选)
- **摄像头设备** - 手势识别功能
- **麦克风** - 语音控制功能

**开发工具推荐**
- **IDE**: IntelliJ IDEA (Java) + VS Code (Python/Vue.js)
- **数据库工具**: MySQL Workbench 或 DBeaver
- **API测试**: Postman 或 Insomnia
- **版本控制**: Git + GitHub/GitLab

### 🛠️ 一键启动开发环境

```powershell
# Windows - 克隆项目并启动所有服务
git clone https://github.com/your-repo/yolo-llm.git
cd yolo-llm
.\start-all.ps1

# 等待所有服务启动完成，然后访问:
# Web界面: http://localhost:5173
# API文档: http://localhost:8000/docs
# 后端API: http://localhost:8080
```

### 🔧 手动启动 (调试模式)

如果启动脚本失败，可以手动启动各个服务：

```bash
# 1. 启动MCP服务器 (端口8083)
cd mcp
python main.py

# 2. 启动后端服务 (端口8080)
cd backend
mvn spring-boot:run

# 3. 启动AI服务 (端口8000)
cd ai
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# 4. 启动前端开发服务器 (端口5173)
cd frontend
npm install
npm run dev

# 5. 启动智能代理 (可选，本地系统控制)
cd agent
python main.py --realtime
```

## 🏗️ 项目架构概览

### **Monorepo结构**
```
yolo-llm/
├── agent/          # Python智能代理 (本地系统控制)
├── backend/        # Spring Boot后端 (业务API)
├── ai/            # FastAPI AI服务 (计算机视觉)
├── frontend/      # Vue.js前端 (Web界面)
├── mcp/           # MCP服务器 (工具扩展)
├── docs/          # 项目文档
└── start-all.ps1  # 一键启动脚本
```

### **服务通信架构**
```
Frontend (5173) ←→ Backend (8080) ←→ AI Service (8000) ←→ Agent (本地)
     ↓                    ↓                    ↓
Web界面              业务编排              AI推理
     ↓                    ↓                    ↓
WebSocket         REST API            HTTP/WebSocket
     ↓                    ↓                    ↓
实时监控           数据持久化          计算机视觉
```

## 🎯 核心组件开发

### 1. **前端开发 (Vue.js)**

#### **技术栈**
- Vue 3 + Composition API
- Vite (构建工具)
- Element Plus (UI组件)
- Pinia (状态管理)
- Socket.IO Client (WebSocket)

#### **开发工作流**
```bash
cd frontend
npm install                    # 安装依赖
npm run dev                    # 启动开发服务器 (热重载)
npm run build                  # 构建生产版本
npm run preview                # 预览生产构建
```

#### **项目结构**
```
src/
├── main.js                    # 应用入口
├── App.vue                    # 根组件
├── router/index.js           # 路由配置
├── stores/                   # Pinia状态管理
├── services/                 # API服务
├── components/               # Vue组件
└── views/                    # 页面组件
```

#### **添加新功能**
```javascript
// 1. 创建新组件 (src/components/NewFeature.vue)
<template>
  <div class="new-feature">
    <!-- 组件内容 -->
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 组件逻辑
const featureData = ref('')
</script>

// 2. 添加路由 (src/router/index.js)
{
  path: '/new-feature',
  name: 'NewFeature',
  component: () => import('../views/NewFeature.vue')
}

// 3. 创建状态管理 (src/stores/newFeature.js)
import { defineStore } from 'pinia'

export const useNewFeatureStore = defineStore('newFeature', () => {
  const data = ref('')

  const fetchData = async () => {
    // API调用逻辑
  }

  return { data, fetchData }
})
```

#### **API集成**
```javascript
// src/services/api.js
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8080'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(config => {
  // 添加认证token等
  return config
})

// 响应拦截器
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API方法
export const api = {
  // 配置API
  getConfig: (params) => apiClient.get('/api/config', { params }),

  // LLM API
  analyzeGesture: (data) => apiClient.post('/api/llm/gesture-analysis', data),

  // 监控API
  getSystemStatus: () => apiClient.get('/api/monitor/status')
}
```

### 2. **后端开发 (Spring Boot)**

#### **技术栈**
- Spring Boot 3.3.4
- Java 17
- MyBatis-Plus 3.5.6
- MySQL 8.0+
- Maven

#### **开发工作流**
```bash
cd backend
mvn clean install              # 编译项目
mvn spring-boot:run            # 启动开发服务器
mvn test                      # 运行测试
mvn package                  # 构建JAR包
```

#### **项目结构**
```
src/main/java/com/example/aiorchestrator/
├── Application.java           # 启动类
├── controller/               # REST控制器
├── service/                  # 业务逻辑
├── domain/                   # 实体模型
├── mapper/                   # 数据访问
└── dto/                      # 数据传输对象
```

#### **添加新API端点**
```java
// 1. 创建DTO (dto/NewFeatureDto.java)
@Data
public class NewFeatureDto {
    private String name;
    private String description;
    private Map<String, Object> parameters;
}

// 2. 创建实体 (domain/NewFeature.java)
@Data
@TableName("new_features")
public class NewFeature {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;
    private String description;
    private String parameters; // JSON格式
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

// 3. 创建Mapper (mapper/NewFeatureMapper.java)
@Mapper
public interface NewFeatureMapper extends BaseMapper<NewFeature> {
    // 自定义查询方法
    List<NewFeature> selectByCondition(@Param("condition") String condition);
}

// 4. 创建Service (service/NewFeatureService.java)
@Service
@Transactional
public class NewFeatureService {

    @Autowired
    private NewFeatureMapper newFeatureMapper;

    public List<NewFeature> getAllFeatures() {
        return newFeatureMapper.selectList(null);
    }

    public NewFeature createFeature(NewFeatureDto dto) {
        NewFeature feature = new NewFeature();
        BeanUtils.copyProperties(dto, feature);
        feature.setCreatedAt(LocalDateTime.now());
        feature.setUpdatedAt(LocalDateTime.now());

        newFeatureMapper.insert(feature);
        return feature;
    }
}

// 5. 创建Controller (controller/NewFeatureController.java)
@RestController
@RequestMapping("/api/new-feature")
@Validated
public class NewFeatureController {

    @Autowired
    private NewFeatureService newFeatureService;

    @GetMapping
    public ResponseEntity<List<NewFeature>> getAllFeatures() {
        List<NewFeature> features = newFeatureService.getAllFeatures();
        return ResponseEntity.ok(features);
    }

    @PostMapping
    public ResponseEntity<NewFeature> createFeature(
        @Valid @RequestBody NewFeatureDto dto) {
        NewFeature feature = newFeatureService.createFeature(dto);
        return ResponseEntity.ok(feature);
    }
}
```

#### **配置管理**
```yaml
# src/main/resources/application.yml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC
    username: root
    password: ${DB_PASS:Wangjiayi1}
    driver-class-name: com.mysql.cj.jdbc.Driver

  # MyBatis-Plus配置
mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  global-config:
    db-config:
      id-type: auto
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0

# 自定义配置
app:
  ai:
    service-url: http://localhost:8000
    timeout: 30000
  mcp:
    server-url: http://localhost:8083
  gesture:
    confidence-threshold: 0.7
```

### 3. **AI服务开发 (FastAPI)**

#### **技术栈**
- FastAPI
- Python 3.8+
- YOLOv8 (目标检测)
- MediaPipe (手势识别)
- DeepFace (情绪识别)

#### **开发工作流**
```bash
cd ai
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### **添加新AI模型**
```python
# 1. 创建模型加载器 (models/new_model.py)
import torch
from transformers import AutoModel, AutoProcessor

class NewAIModel:
    def __init__(self, model_path: str):
        self.model = AutoModel.from_pretrained(model_path)
        self.processor = AutoProcessor.from_pretrained(model_path)

    def predict(self, input_data):
        """模型预测方法"""
        inputs = self.processor(input_data, return_tensors="pt")
        outputs = self.model(**inputs)

        # 后处理逻辑
        return self.post_process(outputs)

    def post_process(self, outputs):
        """后处理方法"""
        # 根据模型类型实现后处理
        return {"result": "processed_output"}

# 2. 集成到主应用 (main.py)
from models.new_model import NewAIModel

# 全局模型实例
new_model = NewAIModel("path/to/model")

@app.post("/api/new-feature")
async def new_feature_endpoint(request: NewFeatureRequest):
    """新的AI功能端点"""
    try:
        # 模型推理
        result = new_model.predict(request.input_data)

        return {
            "status": "success",
            "result": result,
            "model_version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### **WebSocket实时处理**
```python
# 实时处理新数据类型
@app.websocket("/ws/new-feature")
async def websocket_new_feature(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # 接收数据
            data = await websocket.receive_json()

            # 处理数据
            result = await process_new_feature_data(data)

            # 发送结果
            await websocket.send_json({
                "type": "new_feature_result",
                "data": result,
                "timestamp": datetime.now().isoformat()
            })

    except WebSocketDisconnect:
        # 清理资源
        cleanup_websocket_resources(websocket)

async def process_new_feature_data(data):
    """处理新功能数据"""
    # 实现数据处理逻辑
    return {"processed": True, "data": data}
```

### 4. **智能代理开发 (Python)**

#### **技术栈**
- Python 3.8+
- MediaPipe (手势识别)
- SpeechRecognition (语音识别)
- PyAutoGUI (系统控制)

#### **添加新的手势动作**
```python
# 1. 定义新手势 (config.yaml)
gestures:
  NEW_GESTURE:
    name: "新姿势"
    description: "新功能手势"
    confidence_threshold: 0.7
    action_type: "custom"

# 2. 实现手势检测 (gesture_detector.py)
def detect_new_gesture(hand_landmarks):
    """检测新手势"""
    # 实现手势识别逻辑
    if is_new_gesture_pattern(hand_landmarks):
        return {
            "gesture": "NEW_GESTURE",
            "confidence": calculate_confidence(hand_landmarks),
            "landmarks": hand_landmarks
        }
    return None

# 3. 实现动作执行 (action_executor.py)
def execute_new_gesture_action(params):
    """执行新手势对应的动作"""
    try:
        # 实现具体动作
        result = perform_custom_action(params)

        # 记录执行日志
        log_gesture_execution("NEW_GESTURE", result)

        return result
    except Exception as e:
        log_error(f"执行NEW_GESTURE失败: {str(e)}")
        return {"status": "failed", "error": str(e)}

# 4. 集成到主路由 (gesture_router.py)
class GestureRouter:
    def route_gesture(self, gesture_data):
        gesture = gesture_data.get('gesture')

        if gesture == 'NEW_GESTURE':
            return self.execute_new_gesture_action(gesture_data)

        # 其他手势路由逻辑...
```

## 🔧 配置管理

### **环境变量配置**
```bash
# .env 文件
# 数据库配置
DB_URL=jdbc:mysql://localhost:3306/yolo_platform
DB_USER=root
DB_PASS=your_password

# LLM API配置
DEEPSEEK_API_KEY=your_deepseek_api_key
KIMI_API_KEY=your_kimi_api_key

# MCP服务配置
MCP_SERVER_URL=http://localhost:8083

# 新闻API
NEWS_API_KEY=your_newsapi_key

# 天气API
WEATHER_API_KEY=your_openweathermap_key
```

### **Agent配置文件**
```yaml
# agent/config.yaml
backend:
  base_url: 'http://127.0.0.1:8080'
  username: 'admin'
  application: 'chrome.exe'
  os: 'windows'

agent:
  source: 'python-agent@dev'
  poll_interval: 60

video:
  camera_id: 0
  width: 1280
  height: 960
  fps: 60
  show_preview: true
  flip_horizontal: true
  detection_interval: 0.1

gestures:
  confidence_threshold: 0.7
  cooldown_period: 1.0

safety:
  enable_confirmations: true
  risk_levels:
    high: ['shutdown', 'delete', 'format']
    medium: ['reboot', 'install']
    low: ['open', 'close']
```

## 🧪 测试

### **前端测试**
```bash
cd frontend

# 单元测试
npm run test:unit

# E2E测试
npm run test:e2e

# 类型检查
npm run type-check

# 代码规范检查
npm run lint
npm run lint:fix
```

### **后端测试**
```bash
cd backend

# 运行单元测试
mvn test

# 运行集成测试
mvn test -Dspring.profiles.active=integration

# 生成测试报告
mvn jacoco:report

# 代码质量检查
mvn sonar:sonar
```

### **AI服务测试**
```bash
cd ai

# 运行单元测试
pytest tests/

# 运行性能测试
pytest tests/performance/

# 生成覆盖率报告
pytest --cov=. tests/
```

### **集成测试**
```python
# tests/integration/test_gesture_flow.py
import pytest
import requests
import asyncio

class TestGestureFlow:

    @pytest.fixture
    def services(self):
        """启动所有服务"""
        # 启动后端服务
        # 启动AI服务
        # 启动前端
        yield
        # 清理服务

    async def test_gesture_recognition_flow(self, services):
        """测试手势识别完整流程"""
        # 1. 发送手势图像到AI服务
        image_data = load_test_image("victory_gesture.jpg")

        response = requests.post(
            "http://localhost:8000/analyze/file",
            files={"image": image_data}
        )

        assert response.status_code == 200
        result = response.json()

        # 2. 验证手势识别结果
        assert "gestures" in result
        assert any(g["gesture"] == "VICTORY" for g in result["gestures"])

        # 3. 测试Backend处理
        backend_response = requests.post(
            "http://localhost:8080/api/llm/gesture-analysis",
            json={"gesture": "VICTORY", "context": []}
        )

        assert backend_response.status_code == 200
```

## 📊 监控与调试

### **日志管理**
```python
# 统一日志配置
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "service": "yolo-llm",
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry, ensure_ascii=False)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)

logger = logging.getLogger(__name__)
logger.handlers[0].setFormatter(JSONFormatter())
```

### **性能监控**
```python
# 性能监控装饰器
import time
import functools

def monitor_performance(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        duration = end_time - start_time
        logger.info(f"Performance: {func.__name__} took {duration:.3f}s")

        # 发送监控数据到监控系统
        send_metrics({
            "function": func.__name__,
            "duration": duration,
            "status": "success"
        })

        return result
    return wrapper

# 使用示例
@monitor_performance
def process_gesture(gesture_data):
    # 手势处理逻辑
    return result
```

### **错误追踪**
```python
# 全局异常处理
import traceback

class YoloLlmException(Exception):
    """自定义异常基类"""
    pass

def handle_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except YoloLlmException as e:
            logger.error(f"Business error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            # 发送错误报告
            send_error_report({
                "function": func.__name__,
                "error": str(e),
                "traceback": traceback.format_exc()
            })

            raise YoloLlmException(f"Internal server error: {str(e)}")
    return wrapper
```

## 🚀 部署

### **开发环境部署**
```powershell
# 一键启动所有服务
.\start-all.ps1

# 检查服务状态
curl http://localhost:8080/actuator/health
curl http://localhost:8000/health
curl http://localhost:8083/health
```

### **生产环境部署**
```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production

  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=production
      - DB_URL=jdbc:mysql://mysql:3306/yolo_platform
      - DB_USER=root
      - DB_PASS=${DB_PASSWORD}
    depends_on:
      - mysql

  ai-service:
    build: ./ai
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models

  mcp-server:
    build: ./mcp
    ports:
      - "8083:8083"

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_PASSWORD}
      - MYSQL_DATABASE=yolo_platform
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

```bash
# 生产环境启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 扩展服务
docker-compose up -d --scale backend=3 --scale ai-service=2
```

## 📚 开发最佳实践

### **代码规范**
- **Python**: 遵循PEP 8，使用Black格式化
- **Java**: 遵循Google Java Style，使用Checkstyle
- **JavaScript/Vue**: 遵循Airbnb Style，使用ESLint + Prettier
- **提交信息**: 遵循Conventional Commits规范

### **Git工作流**
```bash
# 功能开发分支
git checkout -b feature/new-gesture-recognition

# 提交代码
git add .
git commit -m "feat: add new gesture recognition capability"

# 推送分支
git push origin feature/new-gesture-recognition

# 创建Pull Request
# 代码审查通过后合并到main分支
```

### **性能优化建议**
1. **前端**: 使用懒加载、代码分割、图片优化
2. **后端**: 数据库索引优化、缓存策略、连接池配置
3. **AI服务**: 模型量化、GPU加速、批处理优化
4. **网络**: CDN加速、HTTP/2、压缩传输

### **安全开发**
1. **输入验证**: 严格验证所有用户输入
2. **权限控制**: 实施最小权限原则
3. **数据保护**: 敏感数据加密存储和传输
4. **安全扫描**: 定期进行代码安全扫描

这份开发指南为YOLO-LLM项目提供了完整的开发环境搭建、核心组件开发、测试、部署和最佳实践指导，帮助开发者快速上手并高效参与项目开发。