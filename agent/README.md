# YOLO-LLM Gesture Control Agent

## 概述

这是YOLO-LLM项目的手势控制Agent，能够通过摄像头实时识别手势并执行相应的动作。

## 功能特性

### 手势识别
支持以下8种手势（基于MediaPipe）:
- POINT_UP - 食指向上指
- POINT_INDEX - 食指指向前方
- THUMBS_UP - 竖起大拇指
- THUMBS_DOWN - 大拇指向下
- OPEN_PALM - 张开手掌
- CLOSED_FIST - 握拳
- VICTORY - V字手势
- OK_SIGN - OK手势

### 动作执行
支持7种动作类型:
- hotkey: 键盘快捷键 (ctrl+c, alt+tab等)
- mouse: 鼠标移动到指定坐标
- click: 鼠标点击 (左键/右键/中键)
- scroll: 鼠标滚轮 (正数向下/负数向上)
- text: 自动输入文本
- window: 窗口操作 (maximize/minimize/close/switch)
- system: 系统操作 (volume_up/down/mute/screenshot)

## 使用方法

### 1. 安装依赖
pip install -r requirements.txt

### 2. 运行模式
# 实时手势检测 (默认)
python main.py --realtime

# 后台守护模式
python main.py --daemon

# 交互式测试模式
python main.py --watch

# 单次执行手势
python main.py --gesture THUMBS_UP

# 查看支持的动作类型
python main.py --actions

详细配置请参考 config.yaml 文件。
