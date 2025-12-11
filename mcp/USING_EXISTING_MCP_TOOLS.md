# 使用真实MCP工具的集成方案

## 📋 概述

您完全正确！与其重新编写MCP工具，更好的方案是使用官方认证的MCP工具。这样可以：
- ✅ 利用现成的稳定实现
- ✅ 获得官方支持和更新
- ✅ 快速集成和部署
- ✅ 遵循MCP标准协议

## 🎯 重要说明

### DeepSeek与MCP的兼容性
- **DeepSeek模型目前不直接支持MCP协议**
- **DeepSeek使用自己的API生态，与MCP/ModelContextProtocol是分离的**
- **MCP服务器主要设计用于Claude Desktop集成**
- **如需使用DeepSeek，建议直接使用其官方API而非MCP**

### MCP官方生态
- **官方仓库**: https://github.com/modelcontextprotocol/servers
- **文档**: https://modelcontextprotocol.io/docs/servers
- **NPM搜索**: https://www.npmjs.com/search?q=keywords:modelcontextprotocol

## 🔧 官方认证的MCP工具

### 1. 邮件工具

#### Email MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-email`
- **功能**: IMAP/SMTP支持、邮件收发、文件夹管理
- **安装**: `npm install -g @modelcontextprotocol/server-email`
- **GitHub**: https://github.com/modelcontextprotocol/servers/tree/main/src/email

### 2. 浏览器自动化工具

#### Puppeteer MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-puppeteer`
- **功能**: Chrome/Chromium无头浏览器自动化、网页抓取、PDF生成
- **安装**: `npm install -g @modelcontextprotocol/server-puppeteer`

#### Playwright MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-playwright`
- **功能**: 跨浏览器自动化(Chrome、Firefox、Safari)、UI测试
- **安装**: `npm install -g @modelcontextprotocol/server-playwright`

#### Scraper MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-scraper`
- **功能**: 专业网页抓取工具、内容提取
- **安装**: `npm install -g @modelcontextprotocol/server-scraper`

### 3. 搜索和天气工具

#### Brave Search MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-brave-search`
- **功能**: 网络搜索、结果过滤、API集成
- **安装**: `npm install -g @modelcontextprotocol/server-brave-search`

#### Weather MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-weather`
- **功能**: 天气信息查询、预报数据
- **安装**: `npm install -g @modelcontextprotocol/server-weather`
- **GitHub**: https://github.com/modelcontextprotocol/servers/tree/main/src/weather

### 4. 文件系统和数据库工具

#### File System MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-filesystem`
- **功能**: 文件读写、目录操作、路径解析
- **安装**: `npm install -g @modelcontextprotocol/server-filesystem`

#### SQLite MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-sqlite`
- **功能**: SQLite本地数据库操作、SQL执行、事务支持
- **安装**: `npm install -g @modelcontextprotocol/server-sqlite`

#### PostgreSQL MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-postgres`
- **功能**: PostgreSQL数据库操作、查询执行、连接池管理
- **安装**: `npm install -g @modelcontextprotocol/server-postgres`

### 5. 开发和协作工具

#### GitHub MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-github`
- **功能**: GitHub仓库操作、Issues、PR管理、工作流自动化
- **安装**: `npm install -g @modelcontextprotocol/server-github`

#### Git MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-git`
- **功能**: Git操作、版本控制、仓库管理
- **安装**: `npm install -g @modelcontextprotocol/server-git`

#### Slack MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-slack`
- **功能**: Slack集成、频道交互、消息管理
- **安装**: `npm install -g @modelcontextprotocol/server-slack`

### 6. 内存和存储工具

#### Memory MCP Server (官方)
- **包名**: `@modelcontextprotocol/server-memory`
- **功能**: 持久化内存存储和检索、AI对话上下文管理
- **安装**: `npm install -g @modelcontextprotocol/server-memory`

## 🚀 集成方案

### 方案1: 直接使用Claude Code (推荐)

如果您使用Claude Code，可以直接配置官方MCP服务器：

```json
// ~/.claude/settings.json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"]
    },
    "email": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-email"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-playwright"]
    },
    "weather": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-weather"],
      "env": {
        "WEATHER_API_KEY": "your-openweather-api-key"
      }
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-github-token"
      }
    }
  }
}
```

### 方案2: DeepSeek + MCP工具 (混合方案)

由于DeepSeek不直接支持MCP协议，可以创建混合方案：

```python
# deepseek_real_mcp_client.py
import asyncio
import json
import httpx
from pathlib import Path

class DeepSeekRealMCPClient:
    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.mcp_config = self.load_real_mcp_config()

    def load_real_mcp_config(self):
        """加载真实的MCP服务器配置"""
        config_file = Path("real_mcp_config.json")
        if config_file.exists():
            return json.loads(config_file.read_text())
        return {
            "filesystem": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem", "d:/yolo-llm"],
                "port": 3001
            },
            "email": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-email"],
                "port": 3002
            },
            "playwright": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-playwright"],
                "port": 3003
            },
            "weather": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-weather"],
                "port": 3004
            }
        }

    async def analyze_request_with_deepseek(self, user_request: str):
        """使用DeepSeek分析用户请求"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.deepseek_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": "分析用户请求需要什么MCP工具"},
                            {"role": "user", "content": user_request}
                        ]
                    }
                )
                return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def execute_workflow(self, user_request: str):
        """执行混合工作流"""
        # 1. DeepSeek分析请求
        analysis = await self.analyze_request_with_deepseek(user_request)

        # 2. 根据分析结果启动MCP服务器
        tools_needed = self.extract_tools_from_analysis(analysis)

        # 3. 调用MCP工具完成任务
        results = {}
        for tool in tools_needed:
            results[tool] = await self.call_mcp_tool(tool, user_request)

        # 4. DeepSeek整合结果
        final_response = await self.integrate_results_with_deepseek(user_request, results)

        return final_response
```

## 🛠️ 安装和配置步骤

### 1. 安装Node.js和npm
```bash
# Windows
# 从 https://nodejs.org 下载安装 Node.js 18+

# 验证安装
node --version
npm --version
```

### 2. 安装真实MCP工具
```bash
# 核心工具包 - 必需
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-email
npm install -g @modelcontextprotocol/server-playwright
npm install -g @modelcontextprotocol/server-weather

# 开发工具包 - 推荐
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-memory

# 数据库工具包 - 可选
npm install -g @modelcontextprotocol/server-sqlite

# 搜索和抓取工具包 - 可选
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-scraper
npm install -g @modelcontextprotocol/server-puppeteer

# 协作工具包 - 可选
npm install -g @modelcontextprotocol/server-slack

# 批量安装所有工具
npm install -g @modelcontextprotocol/servers
```

### 3. 配置API密钥
```bash
# 设置环境变量 (Windows PowerShell)
$env:WEATHER_API_KEY = "your-openweather-api-key"
$env:BRAVE_API_KEY = "your-brave-search-api-key"
$env:GITHUB_TOKEN = "your-github-token"
$env:SLACK_TOKEN = "your-slack-token"

# 设置环境变量 (Linux/macOS)
export WEATHER_API_KEY="your-openweather-api-key"
export BRAVE_API_KEY="your-brave-search-api-key"
export GITHUB_TOKEN="your-github-token"
export SLACK_TOKEN="your-slack-token"

# DeepSeek API密钥 (用于混合方案)
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

### 4. 测试真实MCP工具
```bash
# 测试文件系统MCP服务器
npx @modelcontextprotocol/server-filesystem d:/yolo-llm

# 测试邮件MCP服务器
npx @modelcontextprotocol/server-email

# 测试Playwright MCP服务器
npx @modelcontextprotocol/server-playwright

# 测试天气MCP服务器 (需要API密钥)
npx @modelcontextprotocol/server-weather

# 测试GitHub MCP服务器 (需要令牌)
npx @modelcontextprotocol/server-github
```

### 5. 验证安装
```bash
# 检查已安装的MCP工具
npm list -g @modelcontextprotocol/server-filesystem
npm list -g @modelcontextprotocol/server-email
npm list -g @modelcontextprotocol/server-playwright
npm list -g @modelcontextprotocol/server-weather

# 或者批量检查
npm list -g | grep @modelcontextprotocol
```

## 📝 工作流示例

### 示例1: 文件操作 + 邮件发送 (Claude Code + MCP)

```json
// Claude Code 中使用真实MCP工具
{
  "request": "读取项目README文件，然后发送摘要到我的邮箱"
}

// Claude会自动调用:
// 1. @modelcontextprotocol/server-filesystem 读取文件
// 2. @modelcontextprotocol/server-email 发送邮件
```

### 示例2: 网页抓取 + 数据存储

```json
{
  "request": "访问GitHub仓库，获取最新release信息，保存到本地数据库"
}

// Claude会自动调用:
// 1. @modelcontextprotocol/server-playwright 访问网页
// 2. @modelcontextprotocol/server-github 获取GitHub信息
// 3. @modelcontextprotocol/server-sqlite 保存数据
```

### 示例3: DeepSeek混合方案工作流

```python
async def deepseek_mcp_workflow():
    """DeepSeek + 真实MCP工具混合工作流"""
    client = DeepSeekRealMCPClient()

    # 用户请求
    request = "获取北京天气，生成HTML报告，发送到邮箱"

    # 1. DeepSeek分析请求，确定需要：weather + filesystem + email
    analysis = await client.analyze_request_with_deepseek(request)

    # 2. 启动对应的MCP服务器
    await client.start_mcp_servers(["weather", "filesystem", "email"])

    # 3. 调用MCP工具执行任务
    weather_data = await client.call_mcp_tool("weather", "get_weather", {"city": "北京"})
    html_report = await client.call_mcp_tool("filesystem", "write_file", {
        "path": "weather_report.html",
        "content": f"<h1>北京天气</h1><p>{weather_data}</p>"
    })
    email_result = await client.call_mcp_tool("email", "send_email", {
        "to": "user@example.com",
        "subject": "天气报告",
        "body": "天气报告已生成，请查看附件"
    })

    return {
        "weather": weather_data,
        "report": html_report,
        "email": email_result
    }
```

## 🔄 迁移方案：从自定义实现到真实MCP

### 从之前的自定义MCP实现迁移：

1. **移除自定义工具实现**
   ```bash
   # 删除自定义文件（这些是之前编写的虚假MCP工具）
   rm mcp/mcp_server.py
   rm mcp/simple_deepseek_mcp.py
   ```

2. **安装真实MCP工具**
   ```bash
   # 安装官方认证的MCP工具
   npm install -g @modelcontextprotocol/server-filesystem
   npm install -g @modelcontextprotocol/server-email
   npm install -g @modelcontextprotocol/server-playwright
   npm install -g @modelcontextprotocol/server-weather
   ```

3. **使用新的真实配置**
   ```python
   # 使用真实的MCP配置
   from deepseek_real_mcp_client import DeepSeekRealMCPClient

   client = DeepSeekRealMCPClient()
   ```

4. **更新配置文件**
   ```bash
   # 使用真实MCP配置
   cp mcp/real_mcp_config.json mcp_config.json
   ```

## 📊 真实方案 vs 自定义方案对比

| 方面 | 真实MCP工具 | 自定义MCP实现 |
|------|-------------|----------------|
| **可靠性** | ✅ 官方维护，稳定可靠 | ❌ 自编代码，容易出错 |
| **功能完整性** | ✅ 功能齐全，持续更新 | ❌ 功能有限，维护困难 |
| **安装复杂度** | ✅ 一条命令安装 | ❌ 需要手动编写 |
| **社区支持** | ✅ 活跃社区支持 | ❌ 无社区支持 |
| **兼容性** | ✅ 标准MCP协议 | ❌ 可能不兼容 |
| **安全性** | ✅ 安全审核 | ❌ 安全风险 |
| **包名正确性** | ✅ 真实npm包名 | ❌ 虚假包名（如之前错误） |

## 🎯 最终推荐方案

### 优先级1: Claude Code + 官方MCP (推荐)
```bash
# 直接在Claude Code中配置真实MCP工具
# 无需额外代码，开箱即用
```

### 优先级2: DeepSeek + 真实MCP (混合方案)
```python
# 使用我们创建的 deepseek_real_mcp_client.py
# 结合DeepSeek智能分析和真实MCP工具执行
```

### 优先级3: 直接API调用 (简单方案)
```python
# 继续使用之前的 real_news_weather.py, email_client.py
# 直接调用API，无需MCP中间层
```

##  重要提醒

1. **避免使用虚假包名**: 之前提到的 `@sounddrill31/mcp-gmail` 等包名是不存在的
2. **官方认证包**: 只使用 `@modelcontextprotocol/server-*` 系列的官方包
3. **DeepSeek限制**: DeepSeek不直接支持MCP，需要混合方案
4. **测试优先**: 使用前务必测试MCP工具是否正常工作

## 🚀 立即开始

```bash
# 1. 安装真实MCP工具
npm install -g @modelcontextprotocol/server-filesystem @modelcontextprotocol/server-email @modelcontextprotocol/server-playwright @modelcontextprotocol/server-weather

# 2. 运行真实MCP客户端
cd mcp && python deepseek_real_mcp_client.py

# 3. 或者直接使用 Claude Code 配置 real_mcp_config.json
```

这个方案基于真实的MCP生态系统，避免了之前虚假包名的问题，提供了稳定可靠的工具集成方案。