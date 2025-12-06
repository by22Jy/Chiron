"""
MCP 配置文件
"""

import os
from typing import Dict, Any

# DeepSeek API 配置
DEEPSEEK_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "max_tokens": 4000,
    "temperature": 0.7,
    "timeout": 30
}

# MCP 服务器配置
MCP_CONFIG = {
    "host": "localhost",
    "port": 8081,
    "debug": True,
    "log_level": "INFO"
}

# 工具配置
TOOLS_CONFIG = {
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "default_sender": "",
        "default_password": "",
        "use_tls": True
    },
    "news": {
        "api_key": os.getenv("NEWS_API_KEY", ""),
        "base_url": "https://newsapi.org/v2",
        "country": "cn",
        "language": "zh",
        "page_size": 10
    },
    "weather": {
        "api_key": os.getenv("WEATHER_API_KEY", ""),
        "base_url": "https://api.openweathermap.org/data/2.5",
        "units": "metric",
        "lang": "zh_cn"
    },
    "screenshot": {
        "save_dir": "./screenshots",
        "format": "png",
        "quality": 95
    }
}

# 工作流配置
WORKFLOW_CONFIG = {
    "default_steps": [
        "获取新闻",
        "获取天气",
        "打开记事本",
        "记录信息",
        "截图",
        "发送邮件"
    ],
    "max_retries": 3,
    "retry_delay": 2,
    "error_handling": "intelligent"
}

# 提示词配置
PROMPT_CONFIG = {
    "system_prompt": """你是一个智能助手，专门帮助用户完成各种任务。你可以使用以下工具：

1. email_tool - 发送邮件
2. news_tool - 获取新闻
3. weather_tool - 查询天气
4. system_tool - 系统操作
5. screenshot_tool - 截图功能

请根据用户需求，智能选择和组合使用这些工具来完成请求。

注意事项：
- 理解用户真实意图
- 优先考虑用户体验
- 出现错误时提供解决方案
- 保持对话友好和专业
""",
    "workflow_prompt": """请分析用户需求，制定合适的工作流程。

用户需求: {user_request}

可用工具:
- email_tool: 发送邮件
- news_tool: 获取新闻
- weather_tool: 查询天气
- system_tool: 系统操作
- screenshot_tool: 截图

请返回工作流程JSON格式：
{
    "steps": [
        {
            "tool": "tool_name",
            "action": "action_description",
            "parameters": {...},
            "expected_result": "expected_output"
        }
    ],
    "fallback_plan": "backup_plan_if_fails"
}
"""
}

# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "mcp.log",
            "formatter": "default"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        }
    },
    "loggers": {
        "mcp": {
            "level": "INFO",
            "handlers": ["file", "console"]
        }
    }
}