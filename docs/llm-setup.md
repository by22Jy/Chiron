# 🔑 LLM API配置指南

## 问题说明

当前遇到502错误是因为后端LLM服务缺少有效的API密钥配置。

## 解决方案

### 方法1: 使用KIMI API (推荐)

1. **获取API密钥**
   - 访问 [KIMI开放平台](https://platform.moonshot.cn/)
   - 注册账号并获取API密钥

2. **设置环境变量**
   ```bash
   # Windows CMD
   set KIMI_API_KEY=your_actual_kimi_api_key_here

   # Windows PowerShell
   $env:KIMI_API_KEY="your_actual_kimi_api_key_here"

   # Linux/Mac
   export KIMI_API_KEY="your_actual_kimi_api_key_here"
   ```

3. **重启后端服务**
   ```bash
   cd backend
   mvn spring-boot:run
   ```

### 方法2: 使用通义千问API

1. **获取API密钥**
   - 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
   - 注册账号并获取API密钥

2. **设置环境变量**
   ```bash
   # Windows
   set QWEN_API_KEY=your_actual_qwen_api_key_here

   # Linux/Mac
   export QWEN_API_KEY="your_actual_qwen_api_key_here"
   ```

3. **更新配置文件**
   修改 `backend/src/main/resources/application.yml`:
   ```yaml
   ai:
     llm:
       provider: qwen  # 改为qwen
   ```

### 方法3: 临时测试解决方案

如果你暂时没有API密钥，可以创建一个模拟的LLM服务来测试功能。

1. **创建模拟LLM服务**
   ```bash
   cd agent
   python mock_llm_server.py
   ```

2. **修改智能控制器使用模拟服务**
   在 `intelligent_controller.py` 中使用本地模拟API。

## 验证配置

配置完成后，测试API是否可用：

```bash
curl -X POST http://localhost:8080/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好","context":"测试"}'
```

期望返回类似：
```json
{
  "success": true,
  "response": "你好！有什么可以帮助你的吗？"
}
```

## 完整测试流程

1. **配置API密钥**
2. **启动后端服务**
   ```bash
   cd backend
   mvn spring-boot:run
   ```
3. **测试智能控制**
   ```bash
   python test_intelligent_control.py
   ```
4. **启动智能语音控制**
   ```bash
   python smart_voice_control.py
   ```

## 常见问题

### Q: API密钥设置后仍然502错误？
A:
- 检查环境变量是否正确设置
- 重启后端服务
- 确认API密钥有效且有足够余额

### Q: 没有API密钥怎么测试？
A:
- 使用离线测试模式: `python test_intelligent_offline.py`
- 或者申请免费API密钥进行测试

### Q: API调用失败？
A:
- 检查网络连接
- 确认API服务地址正确
- 查看后端日志获取详细错误信息

## 免费API推荐

1. **KIMI API** - 有免费额度
2. **通义千问** - 阿里云提供免费额度
3. **智谱AI GLM** - 有免费试用

---

**配置完成后，你就可以体验完整的智能语音控制功能了！** 🚀