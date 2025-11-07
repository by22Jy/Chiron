# AI Service (FastAPI)

1) python -m venv .venv
2) .\\.venv\\Scripts\\pip install -r requirements.txt
3) .\\.venv\\Scripts\\uvicorn main:app --reload --host 127.0.0.1 --port 8000


分析点:
1. 投票展示
    核心想法：不要用“当前这一帧”的检测结果直接显示，而是看“最近几帧”的结果，谁出现得多，就显示谁。
    做法：维护一个最近 N 帧的窗口（比如 5 帧），把每帧检测到的物体集合记录下来；对这些集合做计数，出现次数 ≥ 阈值（如半数以上）的类别才显示。

