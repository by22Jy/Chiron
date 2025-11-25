#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟LLM服务 - 用于测试智能控制功能
无需真实API密钥，提供模拟的LLM响应
"""

import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 预定义的智能响应模板
MOCK_RESPONSES = {
    # 应用启动类
    "打开微信": {
        "action_type": "open_app",
        "command": "WeChat.exe",
        "description": "启动微信应用程序",
        "confidence": 0.95,
        "safety_level": "safe",
        "alternatives": ["启动QQ", "打开钉钉"]
    },

    "启动微信": {
        "action_type": "open_app",
        "command": "WeChat.exe",
        "description": "启动微信应用程序",
        "confidence": 0.95,
        "safety_level": "safe",
        "alternatives": ["启动QQ", "打开钉钉"]
    },

    "打开记事本": {
        "action_type": "open_app",
        "command": "notepad.exe",
        "description": "启动记事本应用程序",
        "confidence": 1.0,
        "safety_level": "safe",
        "alternatives": ["打开写字板"]
    },

    "启动计算器": {
        "action_type": "open_app",
        "command": "calc.exe",
        "description": "启动计算器应用程序",
        "confidence": 1.0,
        "safety_level": "safe",
        "alternatives": ["打开系统计算器"]
    },

    "打开浏览器": {
        "action_type": "open_app",
        "command": "chrome.exe",
        "description": "启动谷歌浏览器",
        "confidence": 0.9,
        "safety_level": "safe",
        "alternatives": ["启动Edge浏览器", "打开Firefox"]
    },

    "打开chrome": {
        "action_type": "open_app",
        "command": "chrome.exe",
        "description": "启动谷歌浏览器",
        "confidence": 0.9,
        "safety_level": "safe",
        "alternatives": ["启动Edge浏览器", "打开Firefox"]
    },

    # 搜索类
    "搜索python教程": {
        "action_type": "web_search",
        "command": "https://www.google.com/search?q=Python编程教程",
        "description": "在Google搜索Python编程教程",
        "confidence": 0.85,
        "safety_level": "safe",
        "alternatives": ["搜索Python入门", "查找编程教程"]
    },

    "我想搜索python教程": {
        "action_type": "web_search",
        "command": "https://www.google.com/search?q=Python编程教程",
        "description": "在Google搜索Python编程教程",
        "confidence": 0.85,
        "safety_level": "safe",
        "alternatives": ["搜索Python入门", "查找编程教程"]
    },

    "搜索ai相关资料": {
        "action_type": "web_search",
        "command": "https://www.google.com/search?q=AI人工智能资料",
        "description": "在Google搜索AI人工智能相关资料",
        "confidence": 0.8,
        "safety_level": "safe",
        "alternatives": ["搜索机器学习", "查找深度学习资料"]
    },

    # 系统控制类
    "调高音量": {
        "action_type": "system_control",
        "command": "nircmd.exe setsysvolume 65535",
        "description": "调高系统音量到最大",
        "confidence": 0.9,
        "safety_level": "safe",
        "alternatives": ["增加音量", "调大音量"]
    },

    "调低音量": {
        "action_type": "system_control",
        "command": "nircmd.exe setsysvolume 32768",
        "description": "调低系统音量",
        "confidence": 0.9,
        "safety_level": "safe",
        "alternatives": ["降低音量", "调小音量"]
    },

    "调高屏幕亮度": {
        "action_type": "system_control",
        "command": "powershell.exe -Command \"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)\"",
        "description": "调高屏幕亮度到100%",
        "confidence": 0.8,
        "safety_level": "safe",
        "alternatives": ["增加亮度", "调亮屏幕"]
    },

    "关闭屏幕": {
        "action_type": "system_control",
        "command": "powershell.exe -Command \"Add-Type '[DllImport(\"user32.dll\")]public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam);' -Name a -Pas::SendMessage(-1,0x0112,0xF170,2)\"",
        "description": "关闭显示器屏幕",
        "confidence": 0.85,
        "safety_level": "warning",
        "alternatives": ["黑屏", "关闭显示器"]
    },

    "截图": {
        "action_type": "system_control",
        "command": "SnippingTool.exe",
        "description": "启动截图工具",
        "confidence": 0.9,
        "safety_level": "safe",
        "alternatives": ["屏幕截图", "打开截图工具"]
    },

    # 文件操作类
    "打开我的文档": {
        "action_type": "file_operation",
        "command": "explorer.exe %USERPROFILE%\\Documents",
        "description": "打开我的文档文件夹",
        "confidence": 1.0,
        "safety_level": "safe",
        "alternatives": ["打开Documents", "查看文档"]
    },

    "打开桌面": {
        "action_type": "file_operation",
        "command": "explorer.exe %USERPROFILE%\\Desktop",
        "description": "打开桌面文件夹",
        "confidence": 1.0,
        "safety_level": "safe",
        "alternatives": ["显示桌面", "查看桌面文件"]
    },

    # 娱乐控制类
    "播放音乐": {
        "action_type": "open_app",
        "command": "wmplayer.exe",
        "description": "启动Windows Media Player播放音乐",
        "confidence": 0.8,
        "safety_level": "safe",
        "alternatives": ["打开音乐播放器", "启动Spotify"]
    }
}

def find_best_response(user_input):
    """根据用户输入找到最佳响应"""
    user_lower = user_input.lower().strip()

    # 直接匹配
    if user_lower in MOCK_RESPONSES:
        return MOCK_RESPONSES[user_lower]

    # 模糊匹配
    for key, response in MOCK_RESPONSES.items():
        if key in user_input or user_input in key:
            return response

    # 关键词匹配
    if any(word in user_lower for word in ["微信", "wechat"]):
        return MOCK_RESPONSES.get("打开微信")
    elif any(word in user_lower for word in ["记事本", "notepad"]):
        return MOCK_RESPONSES.get("打开记事本")
    elif any(word in user_lower for word in ["计算器", "calculator"]):
        return MOCK_RESPONSES.get("启动计算器")
    elif any(word in user_lower for word in ["浏览器", "browser", "chrome"]):
        return MOCK_RESPONSES.get("打开浏览器")
    elif any(word in user_lower for word in ["搜索", "search", "查找"]):
        return MOCK_RESPONSES.get("搜索python教程")
    elif any(word in user_lower for word in ["音量", "volume"]):
        if any(word in user_lower for word in ["高", "大", "调高"]):
            return MOCK_RESPONSES.get("调高音量")
        else:
            return MOCK_RESPONSES.get("调低音量")
    elif any(word in user_lower for word in ["截图", "screenshot", "capture"]):
        return MOCK_RESPONSES.get("截图")
    elif any(word in user_lower for word in ["文档", "documents"]):
        return MOCK_RESPONSES.get("打开我的文档")
    elif any(word in user_lower for word in ["桌面", "desktop"]):
        return MOCK_RESPONSES.get("打开桌面")
    elif any(word in user_lower for word in ["音乐", "music", "播放"]):
        return MOCK_RESPONSES.get("播放音乐")

    # 默认响应
    return {
        "action_type": "unknown",
        "command": "",
        "description": f"无法识别的命令: {user_input}",
        "confidence": 0.1,
        "safety_level": "safe",
        "alternatives": ["请说得更具体一些", "尝试描述具体的应用或操作"]
    }

@app.route('/api/llm/chat', methods=['POST'])
def mock_chat():
    """模拟聊天API"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()

        # 模拟API延迟
        time.sleep(0.5)

        # 查找响应
        response_data = find_best_response(user_message)

        # 转换为JSON字符串模拟LLM响应
        response_json = json.dumps(response_data, ensure_ascii=False)

        return jsonify({
            "success": True,
            "response": response_json,
            "mock": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "mock": True
        }), 500

@app.route('/api/llm/gesture-analysis', methods=['POST'])
def mock_gesture_analysis():
    """模拟手势分析API"""
    try:
        data = request.get_json()
        gesture_code = data.get('gesture_code', '').lower()

        # 手势分析响应
        analysis_responses = {
            "thumbs_up": {
                "intent": "表达赞同或肯定",
                "emotion": "积极正面",
                "confidence": 0.9,
                "suggestions": ["继续当前操作", "保持积极状态"]
            },
            "victory": {
                "intent": "表达胜利或和平",
                "emotion": "愉快兴奋",
                "confidence": 0.85,
                "suggestions": ["庆祝成功", "保持良好心情"]
            },
            "point_up": {
                "intent": "指示方向或强调",
                "emotion": "专注认真",
                "confidence": 0.8,
                "suggestions": ["关注目标", "集中注意力"]
            }
        }

        analysis = analysis_responses.get(gesture_code, {
            "intent": "未知手势",
            "emotion": "中性",
            "confidence": 0.5,
            "suggestions": ["需要更多上下文"]
        })

        time.sleep(0.3)  # 模拟处理时间

        return jsonify({
            "success": True,
            "response": json.dumps(analysis, ensure_ascii=False),
            "mock": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "mock": True
        }), 500

@app.route('/api/llm/voice-command', methods=['POST'])
def mock_voice_command():
    """模拟语音命令分析API"""
    try:
        data = request.get_json()
        command = data.get('command', '').lower()

        # 直接使用聊天API的逻辑
        response_data = find_best_response(command)

        time.sleep(0.4)  # 模拟处理时间

        return jsonify({
            "success": True,
            "response": json.dumps(response_data, ensure_ascii=False),
            "mock": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "mock": True
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "mock_llm_server": True,
        "available_responses": len(MOCK_RESPONSES)
    })

def start_mock_server(port=8081):
    """启动模拟服务器"""
    print(f"🤖 启动模拟LLM服务器 (端口: {port})")
    print("📋 可用的模拟响应:")
    for key in MOCK_RESPONSES.keys():
        print(f"   • {key}")
    print("\n💡 使用说明:")
    print("1. 修改智能控制器的URL为 http://localhost:8081")
    print("2. 或设置环境变量 BACKEND_URL=http://localhost:8081")
    print(f"3. 访问 http://localhost:{port}/health 检查服务状态")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)

    app.run(host='127.0.0.1', port=port, debug=False)

if __name__ == '__main__':
    start_mock_server()