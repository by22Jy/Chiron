# YOLO-LLM 系统问题修复指南

## 问题分析

根据日志分析，系统存在以下主要问题：

### 1. 数据库字段长度问题 ✅ 已修复
**问题**: `logs.action_value` 字段长度不足 (VARCHAR(2000))，导致LLM返回的长JSON响应被截断

**错误信息**:
```
Data truncation: Data too long for column 'action_value' at row 1
```

**修复方案**:
1. 更新 schema.sql 中的字段类型
2. 执行数据库迁移脚本

### 2. MCP工具模块未加载问题 ✅ 已分析
**问题**: MCP服务器未启动，导致所有MCP工具调用失败

**错误信息**:
```
电脑控制模块未加载
健康监控模块未加载
DeepSeek LLM模块未加载
```

**原因**: MCP服务器在端口8083运行，但服务未启动

### 3. 语音识别处理流程 ✅ 正常
**状态**: 语音识别工作正常，能够正确识别用户请求
- 语音片段整合正常
- LLM分析响应正常
- 事件发送到后端

## 修复步骤

### 步骤1: 修复数据库字段长度

1. **执行数据库迁移脚本**:
```bash
mysql -u root -p yolo_platform < backend/db/fix-action-value-length.sql
```

2. **验证修复**:
```sql
USE yolo_platform;
DESCRIBE logs;
-- 确认 action_value 字段类型为 TEXT
```

### 步骤2: 启动MCP服务器

1. **启动MCP服务器**:
```bash
cd mcp
start_mcp_server.bat
```

2. **或手动启动**:
```bash
cd mcp
.venv\Scripts\activate
pip install -r requirements.txt
python enhanced_mcp_server.py
```

3. **验证MCP服务器运行**:
```bash
curl http://localhost:8083/health
```

### 步骤3: 系统重启顺序

确保以下服务按顺序启动：

1. **数据库服务** (MySQL)
2. **后端服务** (Spring Boot, 端口8080)
   ```bash
   cd backend
   mvn spring-boot:run
   ```
3. **AI服务** (FastAPI, 端口8000)
   ```bash
   cd ai
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```
4. **MCP服务器** (Python, 端口8083)
   ```bash
   cd mcp
   python enhanced_mcp_server.py
   ```
5. **Agent** (Python语音识别)
   ```bash
   cd agent
   python main.py
   ```

## 系统架构验证

### 端口分配
- **8080**: Backend (Spring Boot)
- **8000**: AI Service (FastAPI)
- **8083**: MCP Server (Python FastAPI)
- **5173**: Frontend (Vue.js Dev Server)

### API端点测试
```bash
# 后端健康检查
curl http://localhost:8080/actuator/health

# MCP服务器状态
curl http://localhost:8083/health

# AI服务状态
curl http://localhost:8000/
```

## 环境变量配置

确保以下环境变量已设置：

**后端** (application.yml):
- `DB_URL`: 数据库连接URL
- `DB_USER`: 数据库用户名
- `DB_PASS`: 数据库密码
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `MCP_SERVER_URL`: http://localhost:8083

**MCP服务器**:
- `NEWS_API_KEY`: 新闻API密钥
- `WEATHER_API_KEY`: 天气API密钥
- `BREVO_API_KEY`: 邮件发送API密钥

## 故障排除

### 如果MCP服务器启动失败
1. 检查Python依赖: `pip install -r mcp/requirements.txt`
2. 检查端口8083是否被占用
3. 查看MCP服务器日志

### 如果数据库连接失败
1. 确认MySQL服务运行
2. 检查数据库连接参数
3. 确认数据库schema已更新

### 如果语音识别无响应
1. 检查麦克风权限
2. 确认Agent服务运行
3. 查看Agent日志输出

## 后续优化建议

1. **错误处理增强**: 在MCP集成中添加更好的错误处理和重试机制
2. **日志优化**: 实现日志轮转和结构化日志
3. **监控**: 添加系统健康监控和告警
4. **配置管理**: 使用配置中心统一管理环境变量
5. **容器化**: 考虑使用Docker简化部署

## 验证测试

完成修复后，测试以下功能：

1. **语音命令**: "帮我搜一下今天北京的天气"
2. **手势控制**: 执行手势操作
3. **日志记录**: 确认操作日志正常记录
4. **MCP工具**: 验证各种MCP工具可用性

---

**注意**: 在生产环境中部署前，请确保：
- 所有API密钥已正确配置
- 数据库备份已创建
- 安全配置已检查
- 监控系统已部署