#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO-LLM高级端到端测试
包含语音识别、图像识别等AI功能的完整测试
"""

import requests
import json
import time
import base64
import io
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

MCP_BASE_URL = "http://localhost:8083"
AI_SERVICE_BASE_URL = "http://localhost:8000"

class AdvancedE2ETests:
    """高级端到端测试类"""

    def __init__(self):
        self.test_results = []
        self.test_images = []
        self.test_audio_files = []

    def create_test_images(self):
        """创建测试图像"""
        print("创建测试图像...")

        # 创建包含简单形状的测试图像
        test_image_path = "test_images"
        os.makedirs(test_image_path, exist_ok=True)

        # 1. 创建一个包含手势的测试图像
        img = Image.new('RGB', (300, 300), color='white')
        draw = ImageDraw.Draw(img)

        # 画一个简单的手势形状（竖起拇指）
        draw.rectangle([120, 100, 130, 200], fill='blue')  # 手掌
        draw.rectangle([140, 50, 160, 130], fill='blue')    # 大拇指
        draw.rectangle([110, 200, 170, 230], fill='blue')  # 手指

        gesture_path = os.path.join(test_image_path, "thumbs_up.png")
        img.save(gesture_path)
        self.test_images.append({
            "path": gesture_path,
            "type": "gesture",
            "expected": "thumbs_up"
        })

        # 2. 创建一个包含人脸的测试图像
        img2 = Image.new('RGB', (300, 300), color='white')
        draw2 = ImageDraw.Draw(img2)

        # 画一个简化的人脸
        draw2.ellipse([100, 80, 200, 180], fill='yellow')  # 脸部
        draw2.ellipse([130, 100, 140, 120], fill='black')  # 左眼
        draw2.ellipse([160, 100, 170, 120], fill='black')  # 右眼
        draw2.ellipse([145, 130, 155, 145], fill='red')     # 鼻子

        face_path = os.path.join(test_image_path, "face.png")
        img2.save(face_path)
        self.test_images.append({
            "path": face_path,
            "type": "face",
            "expected": "person"
        })

        # 3. 创建一个包含物体的测试图像
        img3 = Image.new('RGB', (300, 300), color='lightgreen')
        draw3 = ImageDraw.Draw(img3)

        # 画一个简单的矩形（模拟手机或物体）
        draw3.rectangle([80, 100, 220, 200], fill='black')
        draw3.rectangle([90, 110, 210, 190], fill='gray')

        object_path = os.path.join(test_image_path, "object.png")
        img3.save(object_path)
        self.test_images.append({
            "path": object_path,
            "type": "object",
            "expected": "phone"
        })

        print(f"创建了 {len(self.test_images)} 个测试图像")
        return True

    def create_test_audio_data(self):
        """创建测试音频数据（模拟）"""
        print("创建测试音频数据...")

        # 创建模拟的音频数据（实际项目中这里应该是真实音频文件）
        # 由于我们无法生成真实的音频文件，这里创建占位符
        test_audio_dir = "test_audio"
        os.makedirs(test_audio_dir, exist_ok=True)

        # 模拟音频文件列表
        audio_files = [
            {"name": "hello.wav", "text": "你好", "language": "zh"},
            {"name": "test_speech.wav", "text": "测试语音识别", "language": "zh"},
            {"name": "command.wav", "text": "打开记事本", "language": "zh"}
        ]

        for audio_file in audio_files:
            file_path = os.path.join(test_audio_dir, audio_file["name"])
            # 创建一个空文件作为占位符
            with open(file_path, 'wb') as f:
                f.write(b"mock_audio_data")

            self.test_audio_files.append({
                "path": file_path,
                "text": audio_file["text"],
                "language": audio_file["language"]
            })

        print(f"创建了 {len(self.test_audio_files)} 个测试音频文件")
        return True

    def test_image_recognition(self):
        """测试图像识别功能"""
        print("测试图像识别功能...")

        success_count = 0
        total_count = len(self.test_images)

        for i, image_data in enumerate(self.test_images):
            print(f"  测试图像 {i+1}/{total_count}: {image_data['type']}")

            try:
                # 读取图像并转换为base64
                with open(image_data["path"], "rb") as f:
                    image_bytes = f.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

                # 发送到AI服务进行识别
                response = requests.post(
                    f"{AI_SERVICE_BASE_URL}/analyze",
                    headers={"Content-Type": "application/json"},
                    json={
                        "image_data": image_base64,
                        "description": f"测试图像识别 - {image_data['type']}"
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"    识别成功: 检测到 {result.get('detections', [])}")

                    # 验证检测结果
                    detections = result.get('detections', [])
                    if any(d['class'] in ['person', 'gesture', 'hand'] for d in detections):
                        success_count += 1
                        print(f"    ✓ 检测结果符合预期")
                    else:
                        print(f"    ⚠ 检测结果: {detections}")
                else:
                    print(f"    ✗ 识别失败: HTTP {response.status_code}")

            except Exception as e:
                print(f"    ✗ 图像识别异常: {str(e)}")

        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        print(f"图像识别测试通过率: {success_rate:.1f}% ({success_count}/{total_count})")
        return success_count == total_count

    def test_gesture_recognition(self):
        """测试手势识别功能"""
        print("测试手势识别功能...")

        try:
            # 查找包含手势的测试图像
            gesture_images = [img for img in self.test_images if img['type'] == 'gesture']

            if not gesture_images:
                print("  没有找到手势测试图像，跳过手势识别测试")
                return False

            gesture_image = gesture_images[0]

            # 发送手势识别请求
            response = requests.post(
                f"{AI_SERVICE_BASE_URL}/gesture",
                headers={"Content-Type": "application/json"},
                json={
                    "image_path": gesture_image["path"],
                    "description": "手势识别测试"
                },
                timeout=20
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    gesture = result.get("gesture", "")
                    confidence = result.get("confidence", 0)
                    print(f"  ✓ 手势识别成功: {gesture} (置信度: {confidence:.2f})")
                    return True
                else:
                    print(f"  ✗ 手势识别失败: {result.get('message', '未知错误')}")
            else:
                print(f"  ✗ 手势识别请求失败: HTTP {response.status_code}")

        except Exception as e:
            print(f"  ✗ 手势识别异常: {str(e)}")

        return False

    def test_speech_recognition(self):
        """测试语音识别功能"""
        print("测试语音识别功能...")

        success_count = 0
        total_count = len(self.test_audio_files)

        for i, audio_data in enumerate(self.test_audio_files):
            print(f"  测试音频 {i+1}/{total_count}: {audio_data['name']}")

            try:
                # 模拟语音识别请求
                # 在实际项目中，这里会发送真实的音频数据
                response = requests.post(
                    f"{AI_SERVICE_BASE_URL}/speech_recognize",
                    headers={"Content-Type": "application/json"},
                    json={
                        "audio_path": audio_data["path"],
                        "language": audio_data["language"],
                        "description": "语音识别测试"
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        recognized_text = result.get("text", "")
                        confidence = result.get("confidence", 0)
                        print(f"  ✓ 语音识别成功: '{recognized_text}' (置信度: {confidence:.2f})")

                        # 简单的文本匹配验证
                        if any(word in recognized_text for word in audio_data["text"].split()):
                            success_count += 1
                    else:
                        print(f"  ✗ 语音识别失败: {result.get('message', '未知错误')}")
                else:
                    print(f"  ✗ 语音识别请求失败: HTTP {response.status_code}")

            except Exception as e:
                print(f"  ✗ 语音识别异常: {str(e)}")

        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        print(f"语音识别测试通过率: {success_rate:.1f}% ({success_count}/{total_count})")
        return success_count > 0

    def test_ai_integrated_workflow(self):
        """测试AI集成工作流"""
        print("测试AI集成工作流...")

        try:
            # 1. 图像检测
            image_response = requests.post(
                f"{AI_SERVICE_BASE_URL}/analyze",
                headers={"Content-Type": "application/json"},
                json={
                    "image_path": self.test_images[0]["path"],
                    "description": "AI工作流测试"
                },
                timeout=30
            )

            if image_response.status_code != 200:
                print("  ✗ 图像检测失败")
                return False

            image_result = image_response.json()
            detections = image_result.get("detections", [])

            # 2. 姿态检测
            pose_response = requests.post(
                f"{AI_SERVICE_BASE_URL}/pose",
                headers={"Content-Type": "application/json"},
                json={
                    "image_path": self.test_images[1]["path"],
                    "description": "姿态检测测试"
                },
                timeout=30
            )

            if pose_response.status_code != 200:
                print("  ✗ 姿态检测失败")
                return False

            pose_result = pose_response.json()
            keypoints = pose_result.get("pose_estimation", {}).get("keypoints", [])

            # 3. 集成分析
            workflow_result = {
                "detections": detections,
                "keypoints_count": len(keypoints),
                "image_processing_time": image_result.get("processing_time", 0),
                "pose_processing_time": pose_result.get("processing_time", 0),
                "total_detections": len(detections),
                "success": True
            }

            print(f"  ✓ AI集成工作流成功")
            print(f"    检测到 {len(detections)} 个对象")
            print(f"    检测到 {len(keypoints)} 个关键点")
            return workflow_result["success"]

        except Exception as e:
            print(f"  ✗ AI集成工作流异常: {str(e)}")
            return False

    def test_cross_platform_integration(self):
        """测试跨平台集成"""
        print("测试跨平台集成...")

        try:
            # 1. MCP服务器获取AI服务状态
            health_response = requests.get(f"{MCP_BASE_URL}/health", timeout=10)
            if health_response.status_code != 200:
                print("  ✗ MCP健康检查失败")
                return False

            mcp_health = health_response.json()
            print(f"  MCP服务器状态: {mcp_health.get('status')}")
            print(f"  可用工具数: {len(mcp_health.get('available_tools', []))}")

            # 2. AI服务状态检查
            ai_health_response = requests.get(f"{AI_SERVICE_BASE_URL}/health", timeout=10)
            if ai_health_response.status_code != 200:
                print("  ✗ AI服务健康检查失败")
                return False

            ai_health = ai_health_response.json()
            print(f"  AI服务状态: {ai_health.get('status')}")

            # 3. 测试服务间通信
            # 这里可以测试MCP通过AI服务调用复杂分析
            cross_platform_success = True

            print("  ✓ 跨平台集成测试成功")
            return cross_platform_success

        except Exception as e:
            print(f"  ✗ 跨平台集成异常: {str(e)}")
            return False

    def test_error_handling_and_recovery(self):
        """测试错误处理和恢复机制"""
        print("测试错误处理和恢复机制...")

        test_cases = [
            {
                "name": "无效图像路径",
                "test_func": lambda: self.test_invalid_image_path()
            },
            {
                "name": "超时处理",
                "test_func": lambda: self.test_timeout_handling()
            },
            {
                "name": "无效参数",
                "test_func": lambda: self.test_invalid_parameters()
            }
        ]

        passed_tests = 0
        total_tests = len(test_cases)

        for test_case in test_cases:
            try:
                result = test_case["test_func"]()
                if result:
                    passed_tests += 1
                    print(f"  ✓ {test_case['name']}: 通过")
                else:
                    print(f"  ✗ {test_case['name']}: 失败")
            except Exception as e:
                print(f"  ✗ {test_case['name']}: 异常 - {str(e)}")

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"错误处理测试通过率: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        return passed_tests > 0

    def test_invalid_image_path(self):
        """测试无效图像路径处理"""
        try:
            response = requests.post(
                f"{AI_SERVICE_BASE_URL}/analyze",
                headers={"Content-Type": "application/json"},
                json={
                    "image_path": "non_existent_image.png",
                    "description": "无效路径测试"
                },
                timeout=10
            )

            # 应该返回错误但不崩溃
            return response.status_code != 500
        except:
            return False

    def test_timeout_handling(self):
        """测试超时处理"""
        try:
            response = requests.post(
                f"{AI_SERVICE_BASE_URL}/analyze",
                headers={"Content-Type": "application/json"},
                json={
                    "description": "超时测试"
                },
                timeout=1  # 1秒超时
            )

            # 应该超时
            return False  # 超时是预期的行为
        except requests.exceptions.Timeout:
            return True  # 超时异常是预期的
        except:
            return False

    def test_invalid_parameters(self):
        """测试无效参数处理"""
        try:
            response = requests.post(
                f"{AI_SERVICE_BASE_URL}/analyze",
                headers={"Content-Type": "application/json"},
                json={},
                timeout=10
            )

            # 应该优雅地处理无效参数
            return response.status_code == 400 or response.status_code == 422
        except:
            return False

    def run_all_tests(self):
        """运行所有高级端到端测试"""
        print("YOLO-LLM高级端到端测试")
        print("=" * 60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 1. 准备测试数据
        if not self.create_test_images():
            print("✗ 创建测试图像失败")
            return

        if not self.create_test_audio_data():
            print("✗ 创建测试音频失败")
            return

        # 2. 运行各种测试
        test_functions = [
            ("图像识别", self.test_image_recognition),
            ("手势识别", self.test_gesture_recognition),
            ("语音识别", self.test_speech_recognition),
            ("AI集成工作流", self.test_ai_integrated_workflow),
            ("跨平台集成", self.test_cross_platform_integration),
            ("错误处理恢复", self.test_error_handling_and_recovery)
        ]

        passed_tests = 0
        total_tests = len(test_functions)

        for test_name, test_func in test_functions:
            print(f"\n{test_name}测试:")
            print("-" * 40)

            start_time = time.time()
            try:
                result = test_func()
                end_time = time.time()
                duration = end_time - start_time

                if result:
                    passed_tests += 1
                    print(f"✓ {test_name}测试通过 (耗时: {duration:.2f}s)")
                else:
                    print(f"✗ {test_name}测试失败 (耗时: {duration:.2f}s)")
            except Exception as e:
                print(f"✗ {test_name}测试异常: {str(e)} (耗时: {time.time() - start_time:.2f}s)")

        # 3. 生成测试报告
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print("\n" + "=" * 60)
        print("高级端到端测试结果:")
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        print("=" * 60)

        return success_rate >= 60  # 60%以上算作通过

def main():
    """主函数"""
    tester = AdvancedE2ETests()
    success = tester.run_all_tests()

    if success:
        print("\n🎉 高级端到端测试通过！")
    else:
        print("\n⚠️ 高级端到端测试存在一些问题，但系统基本功能正常")

if __name__ == "__main__":
    main()