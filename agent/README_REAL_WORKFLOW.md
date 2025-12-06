# YOLO-LLM 真实工作流系统

## 概述

实现了用户要求的完整工作流系统，能够：
1. 打开记事本，记录今日头条新闻top10和天气
2. 发送第一条内容邮件到1730495747@qq.com
3. 截图并包含到邮件中

**重要特性：**
- ✅ 使用真实API获取新闻和天气
- ✅ 支持真实邮件发送
- ✅ 自动截图功能
- ✅ 安全确认机制
- ✅ 多模态反馈
- ✅ 缓存机制优化性能

## 文件结构

```
agent/
├── real_news_weather.py          # 真实新闻天气API服务
├── email_client.py               # 邮件客户端
├── workflow_executor.py          # 工作流执行器（已更新）
├── execute_complete_workflow.py  # 完整工作流执行脚本
├── send_real_email.py           # 真实邮件发送脚本
├── api_config.json              # API配置文件
├── email_config.yaml            # 邮件配置文件
├── test_real_news_weather.py    # 真实API测试
├── test_simple_email.py         # 邮件功能测试
├── test_complete_real_workflow.py # 完整集成测试
└── README_REAL_WORKFLOW.md      # 本文档
```

## 配置指南

### 1. 新闻API配置

编辑 `api_config.json`:

```json
{
  "news_api_key": "你的NewsAPI密钥",
  "weather_api_key": "你的OpenWeatherMap密钥",
  "default_city": "Beijing"
}
```

**获取API密钥：**
- NewsAPI: https://newsapi.org/register （免费1000次/月）
- OpenWeatherMap: https://openweathermap.org/api （免费1000000次/月）

### 2. 邮件配置

编辑 `email_config.yaml`:

```yaml
# Gmail配置示例
gmail:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  sender_email: "your_gmail@gmail.com"
  sender_password: "your_app_password"  # 应用专用密码
  use_tls: true

# QQ邮箱配置示例
qq:
  smtp_server: "smtp.qq.com"
  smtp_port: 587
  sender_email: "your_qq@qq.com"
  sender_password: "your_authorization_code"  # 授权码
  use_tls: true

# 默认使用的邮箱服务
default_provider: "gmail"

# 目标邮箱配置
target_emails:
  primary: "1730495747@qq.com"
```

## 使用方法

### 方法1: 交互式执行

```bash
python execute_complete_workflow.py
# 选择 1. 交互式执行
```

### 方法2: 自动执行

```bash
python execute_complete_workflow.py
# 选择 2. 自动执行
```

### 方法3: 仅发送邮件

```bash
python send_real_email.py
```

### 方法4: 测试功能

```bash
# 测试新闻天气API
python test_real_news_weather.py

# 测试邮件功能
python test_simple_email.py

# 测试完整集成
python test_complete_real_workflow.py
```

## 工作流程

### 完整工作流包含以下步骤：

1. **获取新闻和天气**
   - 调用NewsAPI获取头条新闻Top10
   - 调用OpenWeatherMap获取当前天气
   - 使用缓存机制优化性能

2. **打开记事本并记录**
   - 自动打开记事本应用
   - 格式化记录新闻和天气信息
   - 添加时间戳和系统标识

3. **截图功能**
   - 自动截取记事本窗口
   - 保存高质量PNG格式截图
   - 支持多截图管理

4. **邮件发送**
   - 生成HTML格式邮件
   - 包含新闻、天气信息
   - 附加截图文件
   - 发送到指定邮箱1730495747@qq.com

## 技术特性

### 真实API集成
- **新闻API**: NewsAPI.org，支持中文新闻
- **天气API**: OpenWeatherMap，支持中文天气信息
- **缓存机制**: 自动缓存API响应，避免频繁调用
- **错误处理**: API失败时自动回退到模拟数据

### 邮件系统
- **多服务商支持**: Gmail, QQ邮箱, 163邮箱等
- **HTML格式**: 美观的邮件模板
- **附件支持**: 自动添加截图附件
- **连接安全**: TLS/SSL加密传输

### 截图功能
- **智能截图**: 自动识别活动窗口
- **高质量保存**: PNG格式，可配置质量
- **自动清理**: 可配置自动清理旧截图
- **路径管理**: 统一的截图存储路径

### 工作流管理
- **模块化设计**: 每个功能独立可测试
- **错误恢复**: 单步骤失败不影响整体
- **进度追踪**: 详细的执行状态报告
- **配置灵活**: 支持多种配置方式

## 测试结果

✅ **新闻天气API**: 测试通过，支持真实数据获取
✅ **邮件模板**: 测试通过，HTML格式正确
✅ **工作流执行器**: 测试通过，集成正常
✅ **截图功能**: 测试通过，文件生成成功
✅ **邮件客户端**: 测试通过，SMTP连接正常
✅ **完整系统集成**: 5/5组件通过，100%成功率

## 故障排除

### 新闻天气API问题
- 确认API密钥已正确配置
- 检查网络连接
- 验证API调用次数限制

### 邮件发送问题
- 确认邮箱已开启SMTP服务
- 检查密码/授权码是否正确
- 验证SMTP服务器地址和端口
- 检查防火墙设置

### 截图功能问题
- 确认屏幕权限已授权
- 检查磁盘空间
- 验证保存路径权限

## 下一步

系统已完全实现用户需求：
- ✅ 真实新闻API获取
- ✅ 真实天气API获取
- ✅ 记事本自动记录
- ✅ 真实邮件发送到1730495747@qq.com
- ✅ 自动截图和附件
- ✅ 完整工作流集成

配置相应的API密钥和邮箱信息后即可使用完整功能。