# Agent (手势控制代理)

本目录用于“本地控制代理”，它负责：

1. 从中台拉取手势 → 动作配置 (`GET /api/config`)
2. 在本地执行动作（例如触发热键）
3. 上报执行日志 (`POST /api/audit/log`)
4. 后续可扩展：调用 `/api/event`、接入 MediaPipe/YOLO 手势识别

## 准备

```powershell
cd agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

编辑 `config.yaml`，配置后端地址、用户名、应用、操作系统等信息。

## 运行

*同步配置并进入交互模式*：

```powershell
python main.py --watch
```

之后可以在终端输入手势编码（如 `swipe_left`），代理会查找配置中的动作并执行，同时把执行日志发回后端。

*仅同步配置*：

```powershell
python main.py --sync
```

## TODO

- 接入真实的手势识别（MediaPipe Hands / YOLO Pose）
- 支持 WebSocket/长轮询方式的配置热更新
- 增强动作执行器（宏、脚本、Webhook）
- 接入 `/api/event` 以触发智能编排


