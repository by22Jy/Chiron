#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版AI服务 - 用于测试
避免MediaPipe依赖问题
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import asyncio
import time

app = FastAPI(
    title="YOLO-LLM AI Service (Simplified)",
    description="简化版AI服务用于测试",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    features: list

class AnalyzeRequest(BaseModel):
    image_path: str = None
    description: str = None

@app.get("/")
async def root():
    return {
        "message": "YOLO-LLM AI Service (Simplified)",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="ai_service_simplified",
        features=["basic_endpoints", "test_mode"]
    )

@app.post("/analyze")
async def analyze_image(request: AnalyzeRequest):
    """模拟图像分析"""
    await asyncio.sleep(0.5)  # 模拟处理时间

    return {
        "success": True,
        "detections": [
            {"class": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]},
            {"class": "gesture", "confidence": 0.87, "bbox": [150, 120, 250, 320]}
        ],
        "pose_estimation": {
            "keypoints": [[120, 130], [125, 135], [130, 140]],
            "confidence": 0.92
        },
        "timestamp": datetime.now().isoformat(),
        "processing_time": 0.5
    }

@app.post("/gesture")
async def detect_gesture(request: AnalyzeRequest):
    """模拟手势检测"""
    await asyncio.sleep(0.3)

    return {
        "success": True,
        "gesture": "thumbs_up",
        "confidence": 0.91,
        "hand_position": [180, 250],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "message": "AI服务测试成功",
        "features": ["图像检测", "手势识别", "姿态估计"],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)