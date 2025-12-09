# MCP工具使用指南

## 概述

YOLO-LLM项目集成了Model Context Protocol (MCP)服务器，提供了强大的工具生态系统，包括新闻获取、天气查询、邮件发送、文件操作等功能。

## 服务器架构

我们有多个MCP服务器版本：

1. **基础版** (`fixed_mcp_server.py`) - 端口8082
2. **增强版** (`enhanced_mcp_server.py`) - 端口8083 ⭐推荐

增强版包含：
- ✅ 错误处理和重试机制
- ✅ 智能缓存系统
- ✅ 性能监控
- ✅ 详细的日志记录

## 快速开始

### 启动服务器

```bash
# 启动增强版MCP服务器（推荐）
set NEWS_API_KEY=%NEWS_API_KEY% && set WEATHER_API_KEY=%WEATHER_API_KEY% && set BREVO_API_KEY=%BREVO_API_KEY% && python mcp/enhanced_mcp_server.py
```

### 健康检查

```bash
curl http://localhost:8083/health
```

## 可用工具

### 1. 新闻工具 (news)

获取最新新闻，支持真实API和模拟数据。

#### 请求示例
```bash
curl -X POST http://localhost:8083/mcp/news \
  -H "Content-Type: application/json" \
  -d '{
    "action": "execute",
    "parameters": {
      "count": 5,
      "country": "us",
      "use_cache": true
    }
  }'
```

#### 参数说明
- `count`: 新闻数量 (默认: 10)
- `country`: 国家代码 (默认: "us")
- `use_cache`: 是否使用缓存 (默认: true)

#### 响应示例
```json
{
  "success": true,
  "data": {
    "news": [
      "1. 新闻标题 - 描述... (来源: 媒体名称)"
    ],
    "count": 1,
    "source": "real_api",
    "cache_hit": false,
    "timestamp": "2025-12-09T18:33:00.897639"
  }
}
```

### 2. 天气工具 (weather)

获取实时天气信息。

#### 请求示例
```bash
curl -X POST http://localhost:8083/mcp/weather \
  -H "Content-Type: application/json" \
  -d '{
    "action": "execute",
    "parameters": {
      "city": "Beijing",
      "units": "metric",
      "lang": "zh_cn",
      "use_cache": true
    }
  }'
```

#### 参数说明
- `city`: 城市名称 (必需)
- `units`: 单位制 (metric/imperial, 默认: "metric")
- `lang`: 语言代码 (默认: "zh_cn")
- `use_cache`: 是否使用缓存 (默认: true)

#### 响应示例
```json
{
  "success": true,
  "data": {
    "weather": {
      "city": "Beijing",
      "temperature": 4.94,
      "description": "clear sky",
      "humidity": 65,
      "wind_speed": 3.09,
      "units": "metric"
    },
    "source": "real_api",
    "cache_hit": false,
    "timestamp": "2025-12-09T18:33:00.897639"
  }
}
```

### 3. 邮件工具 (email)

发送邮件通知。

#### 请求示例
```bash
curl -X POST http://localhost:8083/mcp/email \
  -H "Content-Type: application/json" \
  -d '{
    "action": "execute",
    "parameters": {
      "to": "recipient@example.com",
      "subject": "测试邮件",
      "content": "这是一封测试邮件内容"
    }
  }'
```

#### 参数说明
- `to`: 收件人邮箱 (必需)
- `subject`: 邮件主题 (必需)
- `content`: 邮件内容 (必需，支持HTML)

#### 响应示例
```json
{
  "success": true,
  "data": {
    "email_id": "20251209183300@example.com",
    "to": "recipient@example.com",
    "subject": "测试邮件",
    "source": "real_api",
    "timestamp": "2025-12-09T18:33:00.897639"
  }
}
```

### 4. 文件系统工具 (filesystem)

文件读写操作。

#### 写入文件
```bash
curl -X POST http://localhost:8083/mcp/filesystem \
  -H "Content-Type: application/json" \
  -d '{
    "action": "execute",
    "parameters": {
      "operation": "write",
      "path": "output.txt",
      "content": "Hello, MCP!"
    }
  }'
```

#### 读取文件
```bash
curl -X POST http://localhost:8083/mcp/filesystem \
  -H "Content-Type: application/json" \
  -d '{
    "action": "execute",
    "parameters": {
      "operation": "read",
      "path": "output.txt"
    }
  }'
```

## 高级功能

### 性能监控

获取详细的性能统计数据：

```bash
curl http://localhost:8083/admin/stats
```

#### 响应示例
```json
{
  "performance": {
    "news": {
      "total_requests": 2,
      "successful_requests": 2,
      "success_rate": 100.0,
      "avg_duration": 0.28,
      "min_duration": 0.0,
      "max_duration": 0.57
    }
  },
  "cache": {
    "total_entries": 1,
    "active_entries": 1,
    "expired_entries": 0
  },
  "errors": {
    "total_errors": 0,
    "error_rate": 0.0
  }
}
```

### 缓存管理

#### 清除所有缓存
```bash
curl -X POST http://localhost:8083/admin/cache/clear
```

#### 清除特定工具缓存
```bash
curl -X POST http://localhost:8083/admin/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "news"}'
```

## 错误处理

MCP服务器提供智能错误处理和重试机制：

### 错误类型

1. **TIMEOUT** - 请求超时
   - 建议5秒后重试

2. **RETRY_EXHAUSTED** - 重试次数已用完
   - 建议30秒后重试

3. **CONNECTION_ERROR** - 网络连接错误
   - 建议10秒后重试

4. **INVALID_PARAMETER** - 参数错误
   - 不需要重试，修正参数即可

### 错误响应示例
```json
{
  "success": false,
  "error": "TIMEOUT",
  "message": "请求超时: operation timed out",
  "retry_after": 5
}
```

## 重试机制

增强版MCP服务器自动实现：
- **指数退避**: 1秒 → 2秒 → 4秒
- **最大重试次数**: 3次
- **超时保护**: 15秒新闻API, 10秒天气API, 30秒邮件API

## 缓存策略

### 缓存时间
- **新闻**: 10分钟 (快速变化的新闻内容)
- **天气**: 30分钟 (天气变化相对较慢)
- **邮件**: 不缓存 (每次都需要真实发送)

### 缓存键生成
缓存键基于工具名称和参数的MD5哈希值，确保参数不同时缓存不同。

## 集成示例

### Java Backend集成

```java
@Service
public class MCPIntegrationService {
    @Value("${mcp.server.url:http://localhost:8083}")
    private String mcpServerUrl;

    public Map<String, Object> getNews(int count, String country) {
        String url = mcpServerUrl + "/mcp/news";
        Map<String, Object> params = Map.of(
            "count", count,
            "country", country,
            "use_cache", true
        );

        Map<String, Object> request = Map.of(
            "action", "execute",
            "parameters", params
        );

        ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);
        return response.getBody();
    }
}
```

### Python客户端集成

```python
import requests

class MCPClient:
    def __init__(self, base_url="http://localhost:8083"):
        self.base_url = base_url

    def get_news(self, count=10, country="us", use_cache=True):
        response = requests.post(
            f"{self.base_url}/mcp/news",
            json={
                "action": "execute",
                "parameters": {
                    "count": count,
                    "country": country,
                    "use_cache": use_cache
                }
            }
        )
        return response.json()

    def get_weather(self, city, use_cache=True):
        response = requests.post(
            f"{self.base_url}/mcp/weather",
            json={
                "action": "execute",
                "parameters": {
                    "city": city,
                    "units": "metric",
                    "lang": "zh_cn",
                    "use_cache": use_cache
                }
            }
        )
        return response.json()

    def send_email(self, to, subject, content):
        response = requests.post(
            f"{self.base_url}/mcp/email",
            json={
                "action": "execute",
                "parameters": {
                    "to": to,
                    "subject": subject,
                    "content": content
                }
            }
        )
        return response.json()
```

## 完整工作流示例

### 智能信息助手工作流

```python
# 1. 获取北京天气
weather_result = mcp_client.get_weather("Beijing")
print(f"北京天气: {weather_result['data']['weather']['temperature']}°C")

# 2. 获取科技新闻
news_result = mcp_client.get_news(count=5, country="us")
print(f"获取到 {len(news_result['data']['news'])} 条新闻")

# 3. 生成邮件内容
email_content = f"""
天气报告:
{weather_result['data']['weather']['description']}, 温度 {weather_result['data']['weather']['temperature']}°C

今日新闻热点:
{chr(10).join(news_result['data']['news'][:3])}
"""

# 4. 发送邮件
email_result = mcp_client.send_email(
    to="1730495747@qq.com",
    subject="每日智能报告",
    content=email_content
)

print(f"邮件发送成功: {email_result['data']['email_id']}")
```

## 环境配置

### 必需的环境变量

```bash
# NewsAPI.org API密钥
export NEWS_API_KEY=your_news_api_key_here

# OpenWeatherMap API密钥
export WEATHER_API_KEY=your_weather_api_key_here

# Brevo邮件服务API密钥
export BREVO_API_KEY=your_brevo_api_key_here
```

### API密钥获取

1. **NewsAPI**: https://newsapi.org/register
2. **OpenWeatherMap**: https://openweathermap.org/api
3. **Brevo**: https://www.brevo.com/

## 故障排除

### 常见问题

1. **端口冲突**
   - 确保端口8082/8083未被占用
   - 修改服务器代码中的端口配置

2. **API密钥未配置**
   - 检查环境变量是否正确设置
   - 使用健康检查端点验证配置

3. **缓存问题**
   - 使用管理员接口清除缓存
   - 检查缓存统计信息

4. **网络问题**
   - 增强版会自动重试
   - 检查防火墙和代理设置

### 日志分析

增强版服务器提供详细日志：
- 请求处理时间
- 缓存命中情况
- 重试详情
- 错误诊断信息

## 性能优化建议

1. **合理使用缓存**
   - 对频繁查询的数据启用缓存
   - 根据数据更新频率调整缓存时间

2. **批量请求**
   - 尽量在单个请求中获取多个数据项
   - 避免频繁的小请求

3. **错误处理**
   - 实现客户端重试逻辑
   - 监控错误率并及时告警

4. **监控指标**
   - 定期检查性能统计
   - 设置关键指标的告警阈值

## 扩展开发

### 添加新工具

1. 在服务器中添加新的端点
2. 实现错误处理和重试逻辑
3. 添加缓存支持（如需要）
4. 更新工具列表和文档

### 集成新API

1. 在`mcp_utils.py`中添加重试装饰器
2. 实现API调用逻辑
3. 添加参数验证
4. 测试错误处理和重试机制

---

## 联系支持

如有问题或建议，请查看项目文档或联系开发团队。

**最后更新**: 2025-12-09
**版本**: 2.0.0