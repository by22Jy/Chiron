#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置同步管理器 - AC5: 配置同步机制实现
负责配置热更新、验证和通知机制
"""

import yaml
import time
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class ConfigSyncManager:
    """配置同步管理器"""

    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self.config_data = {}
        self.last_modified = 0
        self.sync_enabled = True
        self.poll_interval = 60  # 秒
        self.validate_format = True
        self.hot_reload = True

        # 回调函数
        self.on_config_changed: Optional[Callable[[Dict[str, Any]], None]] = None

        # 监控线程
        self._monitor_thread = None
        self._stop_event = threading.Event()

        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not self.config_file.exists():
                logger.warning(f"配置文件不存在: {self.config_file}")
                return {}

            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}

            self.last_modified = self.config_file.stat().st_mtime

            # 提取同步配置
            sync_config = self.config_data.get('backend', {}).get('sync', {})
            self.sync_enabled = sync_config.get('enabled', True)
            self.poll_interval = sync_config.get('poll_interval', 60)
            self.validate_format = sync_config.get('validate_format', True)
            self.hot_reload = sync_config.get('hot_reload', True)

            logger.info(f"配置加载成功: {self.config_file}")
            return self.config_data

        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            return {}

    def validate_config(self) -> bool:
        """验证配置格式 - AC4: API契约验证"""
        if not self.validate_format:
            return True

        try:
            # 检查必需的枚举定义
            enumerations = self.config_data.get('enumerations', {})

            required_enums = ['status_values', 'action_types', 'gesture_names']
            for enum_name in required_enums:
                if enum_name not in enumerations:
                    logger.error(f"缺少必需的枚举定义: {enum_name}")
                    return False

                enum_values = enumerations[enum_name]
                if not isinstance(enum_values, list) or len(enum_values) == 0:
                    logger.error(f"枚举值格式错误: {enum_name}")
                    return False

            # 检查数据格式定义
            data_format = self.config_data.get('data_format', {})
            if 'timestamp_format' not in data_format:
                logger.error("缺少时间戳格式定义")
                return False

            if data_format['timestamp_format'] != "ISO_8601":
                logger.error("时间戳格式必须为ISO_8601")
                return False

            # 检查响应结构定义
            response_structure = data_format.get('response_structure', {})
            required_fields = ['status', 'data', 'message', 'timestamp']
            for field in required_fields:
                if field not in response_structure:
                    logger.error(f"响应结构缺少必需字段: {field}")
                    return False

            logger.info("配置验证通过")
            return True

        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False

    def get_enum_values(self, enum_type: str) -> list:
        """获取枚举值"""
        enumerations = self.config_data.get('enumerations', {})
        return enumerations.get(enum_type, [])

    def get_data_format_config(self) -> Dict[str, Any]:
        """获取数据格式配置"""
        return self.config_data.get('data_format', {})

    def check_config_changes(self) -> bool:
        """检查配置文件是否有变更"""
        try:
            if not self.config_file.exists():
                return False

            current_modified = self.config_file.stat().st_mtime
            return current_modified > self.last_modified
        except Exception:
            return False

    def reload_config(self) -> bool:
        """重新加载配置"""
        try:
            old_config = self.config_data.copy()

            if self.load_config():
                if self.validate_config():
                    logger.info("配置重新加载成功")

                    # 触发配置变更回调
                    if self.on_config_changed and self.config_data != old_config:
                        self.on_config_changed(self.config_data)

                    return True
                else:
                    logger.error("配置验证失败，回滚到之前版本")
                    self.config_data = old_config
                    return False
            else:
                logger.error("配置重新加载失败")
                return False

        except Exception as e:
            logger.error(f"配置重新加载异常: {e}")
            return False

    def start_monitoring(self):
        """启动配置文件监控"""
        if not self.hot_reload or not self.sync_enabled:
            logger.info("配置热更新未启用")
            return

        if self._monitor_thread and self._monitor_thread.is_alive():
            logger.warning("配置监控已在运行")
            return

        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_config_changes,
            name="ConfigMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        logger.info(f"配置监控已启动，检查间隔: {self.poll_interval}秒")

    def stop_monitoring(self):
        """停止配置文件监控"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_event.set()
            self._monitor_thread.join(timeout=5)
            logger.info("配置监控已停止")

    def _monitor_config_changes(self):
        """配置文件变更监控循环"""
        while not self._stop_event.is_set():
            try:
                if self.check_config_changes():
                    logger.info("检测到配置文件变更，重新加载...")
                    self.reload_config()

                # 等待下次检查
                self._stop_event.wait(self.poll_interval)

            except Exception as e:
                logger.error(f"配置监控异常: {e}")
                self._stop_event.wait(5)  # 异常时短暂等待后重试

    def get_config_value(self, key_path: str, default=None):
        """
        获取配置值，支持点号分隔的路径
        例: "backend.base_url" 或 "enumerations.status_values"
        """
        try:
            keys = key_path.split('.')
            value = self.config_data

            for key in keys:
                value = value.get(key, {})
                if value == {} and key != keys[-1]:
                    return default

            return value if value != {} else default

        except Exception:
            return default

    def validate_enum_value(self, enum_type: str, value: str) -> bool:
        """验证枚举值是否符合标准"""
        valid_values = self.get_enum_values(enum_type)
        return value in valid_values

    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态信息"""
        return {
            "sync_enabled": self.sync_enabled,
            "hot_reload": self.hot_reload,
            "validate_format": self.validate_format,
            "poll_interval": self.poll_interval,
            "last_modified": datetime.fromtimestamp(self.last_modified).isoformat(),
            "monitoring_active": self._monitor_thread and self._monitor_thread.is_alive()
        }


# 全局配置同步管理器实例
_config_sync_manager: Optional[ConfigSyncManager] = None


def get_config_sync_manager(config_file: str = "config.yaml") -> ConfigSyncManager:
    """获取全局配置同步管理器实例"""
    global _config_sync_manager
    if _config_sync_manager is None:
        _config_sync_manager = ConfigSyncManager(config_file)
    return _config_sync_manager


def start_config_sync(config_file: str = "config.yaml") -> ConfigSyncManager:
    """启动配置同步管理"""
    manager = get_config_sync_manager(config_file)
    manager.start_monitoring()
    return manager


def stop_config_sync():
    """停止配置同步管理"""
    global _config_sync_manager
    if _config_sync_manager:
        _config_sync_manager.stop_monitoring()