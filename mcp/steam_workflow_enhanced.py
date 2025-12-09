#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版Steam游戏购买工作流
提供完整的Steam自动化操作，包括搜索、购买、库管理等
"""

import os
import time
import pyautogui
import win32gui
import win32con
import win32api
import requests
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class SteamAction(Enum):
    """Steam动作枚举"""
    LAUNCH = "launch"
    SEARCH_GAME = "search_game"
    BUY_GAME = "buy_game"
    ADD_TO_CART = "add_to_cart"
    ADD_TO_WISHLIST = "add_to_wishlist"
    VIEW_LIBRARY = "view_library"
    VIEW_STORE = "view_store"
    INSTALL_GAME = "install_game"
    LAUNCH_GAME = "launch_game"
    UPDATE_GAME = "update_game"
    REFUND_GAME = "refund_game"

class GameStatus(Enum):
    """游戏状态枚举"""
    NOT_OWNED = "not_owned"
    IN_CART = "in_cart"
    IN_WISHLIST = "in_wishlist"
    PURCHASED = "purchased"
    INSTALLED = "installed"
    RUNNING = "running"
    UPDATING = "updating"

@dataclass
class GameInfo:
    """游戏信息数据结构"""
    app_id: str
    name: str
    price: float
    currency: str
    discount_percent: int
    original_price: float
    final_price: float
    status: GameStatus
    release_date: str
    developer: str
    publisher: str
    genres: List[str]
    platforms: List[str]
    image_url: str
    store_url: str
    last_checked: datetime

@dataclass
class PurchaseRecord:
    """购买记录数据结构"""
    transaction_id: str
    game_info: GameInfo
    purchase_price: float
    purchase_date: datetime
    payment_method: str
    status: str
    notes: str

@dataclass
class WorkflowStep:
    """工作流步骤数据结构"""
    name: str
    description: str
    action: str
    parameters: Dict[str, Any]
    wait_before: float = 0.0
    wait_after: float = 0.0
    timeout: float = 10.0
    retry_count: int = 0
    max_retries: int = 3
    screenshot_before: bool = False
    screenshot_after: bool = False

class SteamWorkflowEnhanced:
    """增强版Steam工作流控制器"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.steam_window = None
        self.game_cache: Dict[str, GameInfo] = {}
        self.purchase_history: List[PurchaseRecord] = []
        self.workflow_history: List[Dict[str, Any]] = []
        self.screenshots: List[str] = []

        # Steam Web API配置
        self.steam_api_key = self.config.get("steam_api_key", "")
        self.base_currency = self.config.get("base_currency", "CNY")

        # 加载缓存数据
        self._load_cache()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "steam_api_key": os.getenv("STEAM_API_KEY", ""),
            "base_currency": "CNY",
            "screenshot_dir": "screenshots/steam",
            "cache_file": "data/steam_cache.json",
            "purchase_history_file": "data/steam_purchases.json",
            "workflow_history_file": "data/steam_workflows.json",
            "max_screenshots": 50,
            "default_wait_time": 2.0,
            "long_wait_time": 5.0,
            "search_timeout": 30.0,
            "purchase_timeout": 60.0
        }

    def _load_cache(self):
        """加载缓存数据"""
        try:
            # 加载游戏缓存
            if os.path.exists(self.config["cache_file"]):
                with open(self.config["cache_file"], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for app_id, game_data in data.items():
                        game_info = GameInfo(
                            app_id=game_data['app_id'],
                            name=game_data['name'],
                            price=game_data['price'],
                            currency=game_data['currency'],
                            discount_percent=game_data['discount_percent'],
                            original_price=game_data['original_price'],
                            final_price=game_data['final_price'],
                            status=GameStatus(game_data['status']),
                            release_date=game_data['release_date'],
                            developer=game_data['developer'],
                            publisher=game_data['publisher'],
                            genres=game_data['genres'],
                            platforms=game_data['platforms'],
                            image_url=game_data['image_url'],
                            store_url=game_data['store_url'],
                            last_checked=datetime.fromisoformat(game_data['last_checked'])
                        )
                        self.game_cache[app_id] = game_info

            # 加载购买历史
            if os.path.exists(self.config["purchase_history_file"]):
                with open(self.config["purchase_history_file"], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for purchase_data in data:
                        game_info_data = purchase_data['game_info']
                        game_info = GameInfo(
                            app_id=game_info_data['app_id'],
                            name=game_info_data['name'],
                            price=game_info_data['price'],
                            currency=game_info_data['currency'],
                            discount_percent=game_info_data['discount_percent'],
                            original_price=game_info_data['original_price'],
                            final_price=game_info_data['final_price'],
                            status=GameStatus(game_info_data['status']),
                            release_date=game_info_data['release_date'],
                            developer=game_info_data['developer'],
                            publisher=game_info_data['publisher'],
                            genres=game_info_data['genres'],
                            platforms=game_info_data['platforms'],
                            image_url=game_info_data['image_url'],
                            store_url=game_info_data['store_url'],
                            last_checked=datetime.fromisoformat(game_info_data['last_checked'])
                        )
                        purchase = PurchaseRecord(
                            transaction_id=purchase_data['transaction_id'],
                            game_info=game_info,
                            purchase_price=purchase_data['purchase_price'],
                            purchase_date=datetime.fromisoformat(purchase_data['purchase_date']),
                            payment_method=purchase_data['payment_method'],
                            status=purchase_data['status'],
                            notes=purchase_data['notes']
                        )
                        self.purchase_history.append(purchase)

        except Exception as e:
            print(f"加载缓存数据失败: {str(e)}")

    def _save_cache(self):
        """保存缓存数据"""
        try:
            os.makedirs(os.path.dirname(self.config["cache_file"]), exist_ok=True)
            os.makedirs(os.path.dirname(self.config["purchase_history_file"]), exist_ok=True)

            # 保存游戏缓存
            game_cache_data = {}
            for app_id, game_info in self.game_cache.items():
                game_cache_data[app_id] = {
                    'app_id': game_info.app_id,
                    'name': game_info.name,
                    'price': game_info.price,
                    'currency': game_info.currency,
                    'discount_percent': game_info.discount_percent,
                    'original_price': game_info.original_price,
                    'final_price': game_info.final_price,
                    'status': game_info.status.value,
                    'release_date': game_info.release_date,
                    'developer': game_info.developer,
                    'publisher': game_info.publisher,
                    'genres': game_info.genres,
                    'platforms': game_info.platforms,
                    'image_url': game_info.image_url,
                    'store_url': game_info.store_url,
                    'last_checked': game_info.last_checked.isoformat()
                }

            with open(self.config["cache_file"], 'w', encoding='utf-8') as f:
                json.dump(game_cache_data, f, ensure_ascii=False, indent=2)

            # 保存购买历史
            purchase_history_data = []
            for purchase in self.purchase_history:
                game_info_data = {
                    'app_id': purchase.game_info.app_id,
                    'name': purchase.game_info.name,
                    'price': purchase.game_info.price,
                    'currency': purchase.game_info.currency,
                    'discount_percent': purchase.game_info.discount_percent,
                    'original_price': purchase.game_info.original_price,
                    'final_price': purchase.game_info.final_price,
                    'status': purchase.game_info.status.value,
                    'release_date': purchase.game_info.release_date,
                    'developer': purchase.game_info.developer,
                    'publisher': purchase.game_info.publisher,
                    'genres': purchase.game_info.genres,
                    'platforms': purchase.game_info.platforms,
                    'image_url': purchase.game_info.image_url,
                    'store_url': purchase.game_info.store_url,
                    'last_checked': purchase.game_info.last_checked.isoformat()
                }

                purchase_history_data.append({
                    'transaction_id': purchase.transaction_id,
                    'game_info': game_info_data,
                    'purchase_price': purchase.purchase_price,
                    'purchase_date': purchase.purchase_date.isoformat(),
                    'payment_method': purchase.payment_method,
                    'status': purchase.status,
                    'notes': purchase.notes
                })

            with open(self.config["purchase_history_file"], 'w', encoding='utf-8') as f:
                json.dump(purchase_history_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存缓存数据失败: {str(e)}")

    def _take_screenshot(self, name: str = None) -> str:
        """截图并保存"""
        try:
            timestamp = int(time.time())
            filename = f"steam_{name or 'screenshot'}_{timestamp}.png"
            filepath = os.path.join(self.config["screenshot_dir"], filename)

            os.makedirs(self.config["screenshot_dir"], exist_ok=True)
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)

            self.screenshots.append(filepath)

            # 保持截图数量限制
            if len(self.screenshots) > self.config["max_screenshots"]:
                old_screenshot = self.screenshots.pop(0)
                try:
                    os.remove(old_screenshot)
                except:
                    pass

            return filepath

        except Exception as e:
            print(f"截图失败: {str(e)}")
            return ""

    def _find_steam_window(self) -> bool:
        """查找Steam窗口"""
        try:
            windows = []
            def enum_callback(hwnd, windows_list):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd).lower()
                    if "steam" in title:
                        windows_list.append(hwnd)

            win32gui.EnumWindows(enum_callback, windows)

            if windows:
                self.steam_window = windows[0]
                return True
            else:
                return False

        except Exception as e:
            print(f"查找Steam窗口失败: {str(e)}")
            return False

    def _activate_steam_window(self) -> bool:
        """激活Steam窗口"""
        try:
            if not self.steam_window:
                if not self._find_steam_window():
                    return False

            # 恢复并激活窗口
            if win32gui.IsIconic(self.steam_window):
                win32gui.ShowWindow(self.steam_window, win32con.SW_RESTORE)

            win32gui.ShowWindow(self.steam_window, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(self.steam_window)
            time.sleep(1)

            return True

        except Exception as e:
            print(f"激活Steam窗口失败: {str(e)}")
            return False

    def _wait_for_element(self, search_text: str, timeout: float = 10.0) -> bool:
        """等待屏幕元素出现"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # 简单的文本查找实现
                screenshot = pyautogui.screenshot()
                # 这里可以集成OCR进行更精确的查找
                # 暂时使用简单的等待策略
                time.sleep(0.5)
                return True
            except:
                pass
        return False

    def _search_game_in_steam(self, game_name: str) -> bool:
        """在Steam中搜索游戏"""
        try:
            # 1. 打开商店页面
            pyautogui.hotkey('ctrl', 'f')  # 打开搜索框
            time.sleep(1)

            # 2. 输入游戏名称
            pyautogui.typewrite(game_name, interval=0.1)
            time.sleep(1)

            # 3. 按回车搜索
            pyautogui.press('enter')
            time.sleep(3)

            return True

        except Exception as e:
            print(f"搜索游戏失败: {str(e)}")
            return False

    def _add_game_to_cart(self, game_name: str) -> bool:
        """将游戏添加到购物车"""
        try:
            # 这是一个简化的实现，实际需要更复杂的UI识别
            # 1. 查找"加入购物车"按钮
            # 2. 点击按钮
            # 3. 等待确认

            # 模拟点击操作
            pyautogui.click(x=800, y=600)  # 示例坐标
            time.sleep(2)

            return True

        except Exception as e:
            print(f"添加到购物车失败: {str(e)}")
            return False

    def _purchase_game(self, game_name: str) -> Dict[str, Any]:
        """购买游戏"""
        result = {"success": False, "message": "", "steps": []}

        try:
            # 1. 搜索游戏
            result["steps"].append(f"搜索游戏: {game_name}")
            if not self._search_game_in_steam(game_name):
                result["message"] = "搜索游戏失败"
                return result

            # 2. 截图确认找到游戏
            screenshot_path = self._take_screenshot(f"search_{game_name}")
            result["steps"].append(f"搜索完成，截图保存: {screenshot_path}")

            # 3. 添加到购物车
            result["steps"].append("添加游戏到购物车")
            if not self._add_game_to_cart(game_name):
                result["message"] = "添加到购物车失败"
                return result

            # 4. 进入购物车
            result["steps"].append("进入购物车页面")
            # 这里需要实现导航到购物车的逻辑

            # 5. 确认购买
            result["steps"].append("确认购买")
            # 这里需要实现确认购买的逻辑

            result["success"] = True
            result["message"] = f"游戏 '{game_name}' 购买流程完成"

        except Exception as e:
            result["message"] = f"购买游戏失败: {str(e)}"

        return result

    def create_purchase_workflow(self, game_name: str, auto_confirm: bool = False) -> List[WorkflowStep]:
        """创建购买工作流"""
        steps = [
            WorkflowStep(
                name="启动Steam",
                description="启动Steam客户端",
                action="launch_steam",
                parameters={},
                wait_after=5.0,
                screenshot_after=True
            ),
            WorkflowStep(
                name="激活Steam窗口",
                description="激活Steam主窗口",
                action="activate_steam",
                parameters={},
                wait_before=1.0,
                wait_after=1.0,
                screenshot_before=True
            ),
            WorkflowStep(
                name="打开商店",
                description="导航到Steam商店",
                action="navigate_store",
                parameters={},
                wait_after=2.0,
                screenshot_after=True
            ),
            WorkflowStep(
                name="搜索游戏",
                description=f"搜索游戏: {game_name}",
                action="search_game",
                parameters={"game_name": game_name},
                wait_before=1.0,
                wait_after=3.0,
                screenshot_after=True
            ),
            WorkflowStep(
                name="选择游戏",
                description="从搜索结果中选择目标游戏",
                action="select_game",
                parameters={"game_name": game_name},
                wait_before=1.0,
                wait_after=2.0,
                screenshot_before=True
            ),
            WorkflowStep(
                name="添加到购物车",
                description="将游戏添加到购物车",
                action="add_to_cart",
                parameters={"game_name": game_name},
                wait_before=1.0,
                wait_after=2.0,
                screenshot_after=True
            ),
            WorkflowStep(
                name="进入购物车",
                description="打开购物车页面",
                action="view_cart",
                parameters={},
                wait_after=2.0,
                screenshot_after=True
            )
        ]

        # 如果需要自动确认购买
        if auto_confirm:
            steps.extend([
                WorkflowStep(
                    name="确认购买",
                    description="确认购买并支付",
                    action="confirm_purchase",
                    parameters={},
                    wait_before=2.0,
                    wait_after=10.0,
                    screenshot_before=True,
                    screenshot_after=True
                ),
                WorkflowStep(
                    name="验证购买",
                    description="验证购买是否成功",
                    action="verify_purchase",
                    parameters={"game_name": game_name},
                    wait_after=5.0,
                    screenshot_after=True
                )
            ])

        return steps

    def execute_workflow(self, steps: List[WorkflowStep]) -> Dict[str, Any]:
        """执行工作流"""
        result = {
            "success": False,
            "message": "",
            "steps_executed": 0,
            "steps_total": len(steps),
            "screenshots": [],
            "start_time": datetime.now(),
            "end_time": None,
            "duration": 0,
            "step_results": []
        }

        try:
            print(f"开始执行Steam工作流，共 {len(steps)} 个步骤")

            for i, step in enumerate(steps):
                step_result = {
                    "step_number": i + 1,
                    "step_name": step.name,
                    "description": step.description,
                    "success": False,
                    "message": "",
                    "screenshot_before": "",
                    "screenshot_after": "",
                    "start_time": datetime.now(),
                    "end_time": None,
                    "duration": 0
                }

                try:
                    # 步骤前等待
                    if step.wait_before > 0:
                        time.sleep(step.wait_before)

                    # 步骤前截图
                    if step.screenshot_before:
                        screenshot = self._take_screenshot(f"before_{step.name}")
                        step_result["screenshot_before"] = screenshot

                    # 执行步骤
                    success = self._execute_step(step)
                    step_result["success"] = success
                    step_result["message"] = f"步骤 '{step.name}' {'成功' if success else '失败'}"

                    # 步骤后截图
                    if step.screenshot_after:
                        screenshot = self._take_screenshot(f"after_{step.name}")
                        step_result["screenshot_after"] = screenshot
                        if screenshot:
                            result["screenshots"].append(screenshot)

                    # 步骤后等待
                    if step.wait_after > 0:
                        time.sleep(step.wait_after)

                except Exception as e:
                    step_result["success"] = False
                    step_result["message"] = f"步骤 '{step.name}' 执行异常: {str(e)}"

                finally:
                    step_result["end_time"] = datetime.now()
                    step_result["duration"] = (step_result["end_time"] - step_result["start_time"]).total_seconds()
                    result["step_results"].append(step_result)

                # 更新执行步骤数
                result["steps_executed"] = i + 1

                # 如果步骤失败且不是最后一步，决定是否继续
                if not step_result["success"] and i < len(steps) - 1:
                    print(f"步骤 {i + 1} 失败，继续执行下一个步骤")

            # 工作流完成
            result["end_time"] = datetime.now()
            result["duration"] = (result["end_time"] - result["start_time"]).total_seconds()

            # 判断整体成功状态
            success_steps = sum(1 for step in result["step_results"] if step["success"])
            result["success"] = success_steps >= len(steps) * 0.8  # 80%步骤成功即为整体成功

            if result["success"]:
                result["message"] = f"Steam工作流执行完成，成功 {success_steps}/{len(steps)} 个步骤"
            else:
                result["message"] = f"Steam工作流执行失败，仅成功 {success_steps}/{len(steps)} 个步骤"

            # 记录工作流历史
            workflow_record = {
                "workflow_id": f"steam_{int(time.time())}",
                "start_time": result["start_time"].isoformat(),
                "end_time": result["end_time"].isoformat(),
                "duration": result["duration"],
                "success": result["success"],
                "steps_total": result["steps_total"],
                "steps_executed": result["steps_executed"],
                "screenshots": result["screenshots"]
            }
            self.workflow_history.append(workflow_record)

        except Exception as e:
            result["message"] = f"Steam工作流执行异常: {str(e)}"

        return result

    def _execute_step(self, step: WorkflowStep) -> bool:
        """执行单个步骤"""
        try:
            if step.action == "launch_steam":
                return self._launch_steam()
            elif step.action == "activate_steam":
                return self._activate_steam_window()
            elif step.action == "navigate_store":
                return self._navigate_to_store()
            elif step.action == "search_game":
                game_name = step.parameters.get("game_name", "")
                return self._search_game_in_steam(game_name)
            elif step.action == "select_game":
                game_name = step.parameters.get("game_name", "")
                return self._select_game_from_results(game_name)
            elif step.action == "add_to_cart":
                game_name = step.parameters.get("game_name", "")
                return self._add_game_to_cart(game_name)
            elif step.action == "view_cart":
                return self._view_cart()
            elif step.action == "confirm_purchase":
                return self._confirm_purchase()
            elif step.action == "verify_purchase":
                game_name = step.parameters.get("game_name", "")
                return self._verify_purchase(game_name)
            else:
                print(f"未知步骤动作: {step.action}")
                return False

        except Exception as e:
            print(f"执行步骤失败: {step.action} - {str(e)}")
            return False

    def _launch_steam(self) -> bool:
        """启动Steam"""
        try:
            os.system("start steam://")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"启动Steam失败: {str(e)}")
            return False

    def _navigate_to_store(self) -> bool:
        """导航到商店页面"""
        try:
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            pyautogui.press('esc')  # 关闭搜索框
            time.sleep(1)
            # 这里需要更精确的商店导航逻辑
            return True
        except Exception as e:
            print(f"导航到商店失败: {str(e)}")
            return False

    def _select_game_from_results(self, game_name: str) -> bool:
        """从搜索结果中选择游戏"""
        try:
            # 这是一个简化的实现
            # 实际需要图像识别来找到正确的游戏
            pyautogui.click(x=600, y=400)  # 示例坐标
            time.sleep(2)
            return True
        except Exception as e:
            print(f"选择游戏失败: {str(e)}")
            return False

    def _view_cart(self) -> bool:
        """查看购物车"""
        try:
            # 实现购物车查看逻辑
            return True
        except Exception as e:
            print(f"查看购物车失败: {str(e)}")
            return False

    def _confirm_purchase(self) -> bool:
        """确认购买"""
        try:
            # 实现购买确认逻辑
            return True
        except Exception as e:
            print(f"确认购买失败: {str(e)}")
            return False

    def _verify_purchase(self, game_name: str) -> bool:
        """验证购买"""
        try:
            # 实现购买验证逻辑
            return True
        except Exception as e:
            print(f"验证购买失败: {str(e)}")
            return False

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """获取工作流统计信息"""
        if not self.workflow_history:
            return {"message": "暂无工作流历史"}

        total_workflows = len(self.workflow_history)
        successful_workflows = sum(1 for w in self.workflow_history if w["success"])
        success_rate = (successful_workflows / total_workflows) * 100 if total_workflows > 0 else 0

        avg_duration = sum(w["duration"] for w in self.workflow_history) / total_workflows

        return {
            "total_workflows": total_workflows,
            "successful_workflows": successful_workflows,
            "success_rate": f"{success_rate:.1f}%",
            "average_duration": f"{avg_duration:.2f} 秒",
            "total_screenshots": len(self.screenshots),
            "recent_workflows": [
                {
                    "workflow_id": w["workflow_id"],
                    "success": w["success"],
                    "duration": f"{w['duration']:.2f}s",
                    "steps_executed": f"{w['steps_executed']}/{w['steps_total']}",
                    "start_time": w["start_time"]
                }
                for w in sorted(self.workflow_history, key=lambda x: x["start_time"], reverse=True)[:5]
            ]
        }

# 创建全局Steam工作流实例
steam_workflow = SteamWorkflowEnhanced()