# Java MCP集成方案

## 🎯 集成架构

按照推荐方案，我们实现了 **Java Backend + Python MCP HTTP服务器** 的集成架构：

```
用户请求 → Java Spring Boot → HTTP调用 → Python MCP服务器 → 实际工具执行 → 返回结果 → Java LLM整合 → 响应用户
```

## 📁 新增文件

### Java Backend
- `MCPIntegrationService.java` - MCP工具集成服务
- `MCPController.java` - MCP HTTP接口控制器
- 更新了 `AiOrchestratorService.java` - 添加MCP增强方法
- 更新了 `application.yml` - 添加MCP配置

### Python MCP服务器
- `mcp_http_server.py` - FastAPI HTTP服务器
- `test_java_mcp_integration.py` - 集成测试脚本

## 🚀 启动步骤

### 1. 启动Python MCP服务器
```bash
cd d:/yolo-llm/mcp
python mcp_http_server.py
```

服务器将在 `http://localhost:8081` 启动

### 2. 启动Java Backend
```bash
cd d:/yolo-llm/backend
mvn spring-boot:run
```

Backend将在 `http://localhost:8080` 启动

### 3. 运行集成测试
```bash
cd d:/yolo-llm/mcp
python test_java_mcp_integration.py
```

## 🔗 可用的HTTP接口

### Java Backend接口 (端口8080)

#### 1. MCP状态检查
```bash
GET http://localhost:8080/api/mcp/status
```

#### 2. MCP增强对话
```bash
POST http://localhost:8080/api/mcp/enhanced-chat
Content-Type: application/json

{
  "message": "帮我查询北京的天气并发送到邮箱",
  "context": "用户想了解天气和邮件功能",
  "required_tools": ["weather", "email"]
}
```

#### 3. 执行复杂工作流
```bash
POST http://localhost:8080/api/mcp/execute-workflow
Content-Type: application/json

{
  "workflow_name": "news_weather_email",
  "context": {
    "email": "1730495747@qq.com",
    "city": "北京"
  }
}
```

#### 4. 快速新闻邮件工作流
```bash
POST http://localhost:8080/api/mcp/news-email-workflow
Content-Type: application/json

{
  "email": "1730495747@qq.com",
  "city": "北京"
}
```

#### 5. 单独工具调用
```bash
# 天气查询
POST http://localhost:8080/api/mcp/weather
Content-Type: application/json
{"city": "北京"}

# 发送邮件
POST http://localhost:8080/api/mcp/send-email
Content-Type: application/json
{
  "to": "1730495747@qq.com",
  "subject": "测试邮件",
  "content": "这是测试内容"
}
```

### Python MCP服务器接口 (端口8081)

#### 1. 健康检查
```bash
GET http://localhost:8081/health
```

#### 2. 获取可用工具
```bash
GET http://localhost:8081/tools
```

#### 3. 直接调用工具
```bash
# 天气工具
POST http://localhost:8081/mcp/weather
Content-Type: application/json
{
  "action": "execute",
  "parameters": {"city": "北京"}
}

# 邮件工具
POST http://localhost:8081/mcp/email
Content-Type: application/json
{
  "action": "execute",
  "parameters": {
    "to": "1730495747@qq.com",
    "subject": "测试邮件",
    "content": "这是测试内容"
  }
}

# 文件系统工具
POST http://localhost:8081/mcp/filesystem
Content-Type: application/json
{
  "action": "execute",
  "parameters": {
    "operation": "write",
    "path": "test.txt",
    "content": "Hello World"
  }
}

# 截图工具
POST http://localhost:8081/mcp/screenshot
Content-Type: application/json
{
  "action": "execute",
  "parameters": {"save_path": "screenshot.png"}
}
```

## ⚙️ 环境变量配置

创建 `.env` 文件或设置环境变量：

```bash
# DeepSeek API密钥 (必需)
DEEPSEEK_API_KEY=your-deepseek-api-key

# 新闻API密钥 (可选，如需新闻功能)
NEWS_API_KEY=your-newsapi-key

# 天气API密钥 (可选，如需天气功能)
WEATHER_API_KEY=your-openweather-key

# MCP服务器URL (可选)
MCP_SERVER_URL=http://localhost:8081
```

## 🧪 测试示例

### 1. 测试基础连接
```bash
# 测试Python MCP服务器
curl http://localhost:8081/health

# 测试Java Backend
curl http://localhost:8080/api/mcp/status
```

### 2. 测试完整工作流
```bash
curl -X POST http://localhost:8080/api/mcp/news-email-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "email": "1730495747@qq.com",
    "city": "北京"
  }'
```

### 3. 测试增强对话
```bash
curl -X POST http://localhost:8080/api/mcp/enhanced-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "帮我查询北京天气并发送新闻到邮箱",
    "context": "用户想了解天气和新闻",
    "required_tools": ["weather", "news", "email"]
  }'
```

## 🔧 集成原理

### 1. Java Backend 职责
- 接收用户HTTP请求
- 调用DeepSeek LLM进行智能分析
- 通过HTTP调用Python MCP服务器
- 整合LLM分析和工具执行结果
- 返回最终响应给用户

### 2. Python MCP服务器 职责
- 提供HTTP接口供Java调用
- 执行具体的工具任务（邮件、天气、新闻等）
- 管理工具的生命周期和错误处理
- 支持多种工作流组合

### 3. 工作流程
```
用户请求 → Java Backend分析 → DeepSeek LLM决策 → 调用Python MCP工具 → 获取工具结果 → LLM整合 → 响应用户
```

## 📊 优势

1. **保持现有架构** - Java继续负责LLM调用和业务逻辑
2. **语言优势互补** - Java负责Web服务，Python负责工具执行
3. **松耦合设计** - 通过HTTP接口连接，易于扩展
4. **错误隔离** - Python工具失败不影响Java主要功能
5. **易于测试** - 可以独立测试各个组件

## 🐛 故障排除

### 1. MCP服务器连接失败
```bash
# 检查Python服务器是否运行
curl http://localhost:8081/health

# 检查Java是否能访问Python
curl -v http://localhost:8081/health
```

### 2. LLM调用失败
```bash
# 检查DeepSeek API密钥
echo $DEEPSEEK_API_KEY

# 测试LLM接口
curl -X POST http://localhost:8080/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "测试"}'
```

### 3. 工具执行失败
- 检查相关API密钥是否设置
- 查看Python服务器日志
- 确认网络连接正常

## 📝 使用示例

现在您可以：

1. **继续使用Java现有的LLM功能** - 所有原有功能保持不变
2. **通过新的MCP接口调用Python工具** - 增强了Java的能力
3. **实现复杂的多步骤工作流** - 结合LLM智能分析和工具执行
4. **保持代码的模块化和可维护性** - 各组件职责清晰

这种方案完美结合了Java的Web服务优势和Python的AI工具生态！