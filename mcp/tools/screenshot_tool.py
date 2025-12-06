"""
截图 MCP 工具

通过DeepSeek大模型智能处理截图相关任务
"""

import asyncio
import os
import time
from typing import Dict, Any, List, Optional
import logging

try:
    import pyautogui
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger = logging.getLogger(__name__).warning("PIL not available, screenshot functionality limited")

logger = logging.getLogger(__name__)


class ScreenshotTool:
    """截图工具"""

    def __init__(self):
        self.default_save_dir = "./screenshots"
        self.default_format = "png"
        self.default_quality = 95

        # 确保保存目录存在
        os.makedirs(self.default_save_dir, exist_ok=True)

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行截图工具操作"""

        action = parameters.get("action", "")
        logger.info(f"执行截图工具操作: {action}")

        try:
            if action == "capture_fullscreen":
                return await self._capture_fullscreen(parameters)
            elif action == "capture_window":
                return await self._capture_window(parameters)
            elif action == "capture_region":
                return await self._capture_region(parameters)
            elif action == "process_screenshot":
                return await self._process_screenshot(parameters)
            elif action == "analyze_screenshot":
                return await self._analyze_screenshot(parameters)
            elif action == "batch_capture":
                return await self._batch_capture(parameters)
            else:
                return {
                    "success": False,
                    "error": f"未知的截图操作: {action}",
                    "available_actions": [
                        "capture_fullscreen", "capture_window", "capture_region",
                        "process_screenshot", "analyze_screenshot", "batch_capture"
                    ]
                }

        except Exception as e:
            logger.error(f"截图工具执行错误: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "action": action
            }

    async def _capture_fullscreen(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """全屏截图"""

        filename = params.get("filename", f"screenshot_{int(time.time())}")
        save_dir = params.get("save_dir", self.default_save_dir)
        file_format = params.get("format", self.default_format)
        quality = params.get("quality", self.default_quality)

        try:
            # 确保保存目录存在
            os.makedirs(save_dir, exist_ok=True)

            if not PIL_AVAILABLE:
                return {
                    "success": False,
                    "error": "截图功能需要安装PIL库: pip install Pillow"
                }

            # 截图
            screenshot = pyautogui.screenshot()

            # 构建文件路径
            if not filename.endswith(f".{file_format}"):
                filename = f"{filename}.{file_format}"

            file_path = os.path.join(save_dir, filename)

            # 保存截图
            if file_format.lower() in ['jpg', 'jpeg']:
                screenshot.save(file_path, quality=quality, optimize=True)
            else:
                screenshot.save(file_path)

            # 获取文件信息
            file_size = os.path.getsize(file_path)
            image_size = screenshot.size

            return {
                "success": True,
                "message": f"全屏截图已保存",
                "file_path": file_path,
                "filename": filename,
                "file_size": file_size,
                "image_size": image_size,
                "format": file_format,
                "capture_time": time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"全屏截图失败: {str(e)}")
            return {
                "success": False,
                "error": f"全屏截图失败: {str(e)}"
            }

    async def _capture_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """窗口截图"""

        filename = params.get("filename", f"window_{int(time.time())}")
        save_dir = params.get("save_dir", self.default_save_dir)
        window_title = params.get("window_title", "")
        file_format = params.get("format", self.default_format)

        try:
            if not PIL_AVAILABLE:
                return {
                    "success": False,
                    "error": "截图功能需要安装PIL库: pip install Pillow"
                }

            # 获取活动窗口
            try:
                window = pyautogui.getActiveWindow()
                if not window:
                    return {
                        "success": False,
                        "error": "无法获取活动窗口信息"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"获取窗口信息失败: {str(e)}"
                }

            # 如果指定了窗口标题，检查是否匹配
            if window_title and window_title.lower() not in window.title.lower():
                # 可以在这里添加搜索特定窗口的逻辑
                logger.info(f"当前窗口标题: {window.title}, 查找目标: {window_title}")

            # 截取窗口区域
            try:
                screenshot = pyautogui.screenshot(region=(
                    window.left, window.top, window.width, window.height
                ))
            except Exception as e:
                # 如果窗口截图失败，回退到全屏截图
                logger.warning(f"窗口截图失败，使用全屏截图: {str(e)}")
                screenshot = pyautogui.screenshot()

            # 保存截图
            os.makedirs(save_dir, exist_ok=True)
            if not filename.endswith(f".{file_format}"):
                filename = f"{filename}.{file_format}"

            file_path = os.path.join(save_dir, filename)
            screenshot.save(file_path)

            # 获取窗口信息
            file_size = os.path.getsize(file_path)
            window_info = {
                "title": window.title,
                "size": (window.width, window.height),
                "position": (window.left, window.top)
            }

            return {
                "success": True,
                "message": f"窗口截图已保存",
                "file_path": file_path,
                "filename": filename,
                "file_size": file_size,
                "window_info": window_info,
                "format": file_format,
                "capture_time": time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"窗口截图失败: {str(e)}")
            return {
                "success": False,
                "error": f"窗口截图失败: {str(e)}"
            }

    async def _capture_region(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """区域截图"""

        filename = params.get("filename", f"region_{int(time.time())}")
        save_dir = params.get("save_dir", self.default_save_dir)
        region = params.get("region", {})
        file_format = params.get("format", self.default_format)

        try:
            if not PIL_AVAILABLE:
                return {
                    "success": False,
                    "error": "截图功能需要安装PIL库: pip install Pillow"
                }

            # 解析区域参数
            left = region.get("left", 0)
            top = region.get("top", 0)
            width = region.get("width", 800)
            height = region.get("height", 600)

            # 验证区域参数
            screen_width, screen_height = pyautogui.size()
            if left < 0 or top < 0 or width <= 0 or height <= 0:
                return {
                    "success": False,
                    "error": "无效的区域参数"
                }

            if left + width > screen_width or top + height > screen_height:
                return {
                    "success": False,
                    "error": "区域超出屏幕范围"
                }

            # 截取指定区域
            screenshot = pyautogui.screenshot(region=(left, top, width, height))

            # 保存截图
            os.makedirs(save_dir, exist_ok=True)
            if not filename.endswith(f".{file_format}"):
                filename = f"{filename}.{file_format}"

            file_path = os.path.join(save_dir, filename)
            screenshot.save(file_path)

            # 获取文件信息
            file_size = os.path.getsize(file_path)
            region_info = {
                "left": left,
                "top": top,
                "width": width,
                "height": height
            }

            return {
                "success": True,
                "message": f"区域截图已保存",
                "file_path": file_path,
                "filename": filename,
                "file_size": file_size,
                "region_info": region_info,
                "format": file_format,
                "capture_time": time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"区域截图失败: {str(e)}")
            return {
                "success": False,
                "error": f"区域截图失败: {str(e)}"
            }

    async def _process_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理截图"""

        input_file = params.get("input_file", "")
        operations = params.get("operations", [])
        output_file = params.get("output_file", "")

        if not input_file or not os.path.exists(input_file):
            return {
                "success": False,
                "error": "输入文件不存在"
            }

        try:
            if not PIL_AVAILABLE:
                return {
                    "success": False,
                    "error": "图片处理功能需要安装PIL库: pip install Pillow"
                }

            # 打开图片
            image = Image.open(input_file)
            original_size = image.size

            # 应用处理操作
            processed_image = image.copy()

            for operation in operations:
                op_type = operation.get("type", "")

                if op_type == "resize":
                    size = operation.get("size", (800, 600))
                    processed_image = processed_image.resize(size, Image.Resampling.LANCZOS)

                elif op_type == "crop":
                    box = operation.get("box", (0, 0, 800, 600))
                    processed_image = processed_image.crop(box)

                elif op_type == "rotate":
                    angle = operation.get("angle", 0)
                    processed_image = processed_image.rotate(angle, expand=True)

                elif op_type == "grayscale":
                    processed_image = processed_image.convert('L')

                elif op_type == "blur":
                    from PIL import ImageFilter
                    radius = operation.get("radius", 2)
                    processed_image = processed_image.filter(ImageFilter.GaussianBlur(radius))

            # 保存处理后的图片
            if not output_file:
                name, ext = os.path.splitext(input_file)
                output_file = f"{name}_processed{ext}"

            processed_image.save(output_file)

            return {
                "success": True,
                "message": "截图处理完成",
                "input_file": input_file,
                "output_file": output_file,
                "original_size": original_size,
                "processed_size": processed_image.size,
                "operations_applied": len(operations)
            }

        except Exception as e:
            logger.error(f"截图处理失败: {str(e)}")
            return {
                "success": False,
                "error": f"截图处理失败: {str(e)}"
            }

    async def _analyze_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """分析截图"""

        image_file = params.get("image_file", "")
        analysis_type = params.get("analysis_type", "basic")

        if not image_file or not os.path.exists(image_file):
            return {
                "success": False,
                "error": "图片文件不存在"
            }

        try:
            if not PIL_AVAILABLE:
                return {
                    "success": False,
                    "error": "图片分析功能需要安装PIL库: pip install Pillow"
                }

            # 打开图片
            image = Image.open(image_file)

            analysis = {
                "file_info": {
                    "filename": os.path.basename(image_file),
                    "file_size": os.path.getsize(image_file),
                    "format": image.format,
                    "mode": image.mode,
                    "size": image.size
                }
            }

            if analysis_type == "basic":
                # 基本分析
                analysis["basic_info"] = {
                    "width": image.size[0],
                    "height": image.size[1],
                    "aspect_ratio": f"{image.size[0]}:{image.size[1]}",
                    "total_pixels": image.size[0] * image.size[1]
                }

            elif analysis_type == "color":
                # 颜色分析
                if image.mode == 'RGB':
                    # 简单的颜色分析
                    colors = image.getcolors(maxcolors=256*256*256)
                    if colors:
                        analysis["color_info"] = {
                            "unique_colors": len(colors),
                            "dominant_colors": sorted(colors, key=lambda x: x[0], reverse=True)[:5]
                        }

            elif analysis_type == "quality":
                # 质量分析
                analysis["quality_info"] = {
                    "resolution": f"{image.size[0]}x{image.size[1]}",
                    "pixel_density": "N/A",  # 需要EXIF信息
                    "compression": "N/A"      # 需要EXIF信息
                }

            return {
                "success": True,
                "message": "截图分析完成",
                "analysis_type": analysis_type,
                "analysis": analysis
            }

        except Exception as e:
            logger.error(f"截图分析失败: {str(e)}")
            return {
                "success": False,
                "error": f"截图分析失败: {str(e)}"
            }

    async def _batch_capture(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """批量截图"""

        capture_configs = params.get("configs", [])
        save_dir = params.get("save_dir", self.default_save_dir)
        interval = params.get("interval", 2)

        if not capture_configs:
            return {
                "success": False,
                "error": "截图配置不能为空"
            }

        try:
            results = []
            os.makedirs(save_dir, exist_ok=True)

            for i, config in enumerate(capture_configs):
                # 等待间隔
                if i > 0 and interval > 0:
                    await asyncio.sleep(interval)

                # 执行单次截图
                if config.get("type") == "fullscreen":
                    result = await self._capture_fullscreen({
                        "filename": f"batch_{i}_{config.get('filename', 'screenshot')}",
                        "save_dir": save_dir,
                        "format": config.get("format", self.default_format)
                    })
                elif config.get("type") == "window":
                    result = await self._capture_window({
                        "filename": f"batch_{i}_{config.get('filename', 'window')}",
                        "save_dir": save_dir,
                        "format": config.get("format", self.default_format)
                    })
                else:
                    result = {
                        "success": False,
                        "error": f"不支持的截图类型: {config.get('type')}"
                    }

                results.append({
                    "index": i,
                    "config": config,
                    "result": result,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                })

            # 统计结果
            successful_captures = sum(1 for r in results if r["result"]["success"])
            failed_captures = len(results) - successful_captures

            return {
                "success": True,
                "message": f"批量截图完成，成功: {successful_captures}, 失败: {failed_captures}",
                "total_configs": len(capture_configs),
                "successful_captures": successful_captures,
                "failed_captures": failed_captures,
                "results": results
            }

        except Exception as e:
            logger.error(f"批量截图失败: {str(e)}")
            return {
                "success": False,
                "error": f"批量截图失败: {str(e)}"
            }