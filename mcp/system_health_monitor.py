#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统健康监控和自动恢复机制
提供实时系统监控、预警和自动恢复功能
"""

import os
import time
import asyncio
import threading
import psutil
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class AlertLevel(Enum):
    """告警级别枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class HealthMetric:
    """健康指标数据结构"""
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    status: HealthStatus
    timestamp: datetime
    description: str

@dataclass
class Alert:
    """告警数据结构"""
    id: str
    metric_name: str
    level: AlertLevel
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    actions_taken: List[str] = None

    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []

@dataclass
class RecoveryAction:
    """恢复动作数据结构"""
    name: str
    condition: str
    action: Callable
    description: str
    enabled: bool = True

class SystemHealthMonitor:
    """系统健康监控器"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.metrics: Dict[str, HealthMetric] = {}
        self.alerts: List[Alert] = []
        self.recovery_actions: List[RecoveryAction] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_check_time = datetime.now()

        # 初始化恢复动作
        self._init_recovery_actions()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "check_interval": 30,  # 检查间隔（秒）
            "alert_cooldown": 300,  # 告警冷却时间（秒）
            "auto_recovery_enabled": True,
            "email_alerts_enabled": False,
            "email_smtp_server": "smtp.gmail.com",
            "email_smtp_port": 587,
            "email_username": "",
            "email_password": "",
            "email_recipients": [],
            "log_retention_days": 7
        }

    def _init_recovery_actions(self):
        """初始化恢复动作"""
        self.recovery_actions = [
            RecoveryAction(
                name="清理临时文件",
                condition="disk_usage > 85",
                action=self._cleanup_temp_files,
                description="清理系统临时文件释放磁盘空间",
                enabled=True
            ),
            RecoveryAction(
                name="重启高内存进程",
                condition="memory_usage > 90",
                action=self._restart_high_memory_processes,
                description="重启占用内存过高的进程",
                enabled=False  # 默认禁用，可能影响业务
            ),
            RecoveryAction(
                name="结束高CPU进程",
                condition="cpu_usage > 95",
                action=self._terminate_high_cpu_processes,
                description="结束CPU占用过高的进程",
                enabled=False  # 默认禁用，可能影响业务
            ),
            RecoveryAction(
                name="重启网络服务",
                condition="network_issues",
                action=self._restart_network_services,
                description="重启网络相关服务",
                enabled=True
            ),
            RecoveryAction(
                name="清理系统缓存",
                condition="system_slow",
                action=self._clear_system_cache,
                description="清理系统缓存文件",
                enabled=True
            )
        ]

    def start_monitoring(self):
        """开始监控"""
        if self.monitoring_active:
            print("系统监控已在运行中")
            return

        print("启动系统健康监控...")
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止监控"""
        print("停止系统健康监控...")
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def _monitoring_loop(self):
        """监控主循环"""
        while self.monitoring_active:
            try:
                self._collect_metrics()
                self._analyze_health()
                self._check_recovery_conditions()
                self.last_check_time = datetime.now()
                time.sleep(self.config["check_interval"])

            except Exception as e:
                print(f"监控循环异常: {str(e)}")
                time.sleep(5)  # 短暂等待后重试

    def _collect_metrics(self):
        """收集系统指标"""
        try:
            # CPU指标
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics["cpu"] = HealthMetric(
                name="CPU使用率",
                value=cpu_percent,
                unit="%",
                threshold_warning=70.0,
                threshold_critical=90.0,
                status=self._evaluate_status(cpu_percent, 70.0, 90.0),
                timestamp=datetime.now(),
                description="中央处理器使用率"
            )

            # 内存指标
            memory = psutil.virtual_memory()
            self.metrics["memory"] = HealthMetric(
                name="内存使用率",
                value=memory.percent,
                unit="%",
                threshold_warning=80.0,
                threshold_critical=95.0,
                status=self._evaluate_status(memory.percent, 80.0, 95.0),
                timestamp=datetime.now(),
                description="系统内存使用率"
            )

            # 磁盘指标
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics["disk"] = HealthMetric(
                name="磁盘使用率",
                value=disk_percent,
                unit="%",
                threshold_warning=80.0,
                threshold_critical=95.0,
                status=self._evaluate_status(disk_percent, 80.0, 95.0),
                timestamp=datetime.now(),
                description="系统磁盘使用率"
            )

            # 网络指标
            network = psutil.net_io_counters()
            connections = len(psutil.net_connections())
            self.metrics["network_connections"] = HealthMetric(
                name="网络连接数",
                value=connections,
                unit="个",
                threshold_warning=1000.0,
                threshold_critical=2000.0,
                status=self._evaluate_status(connections, 1000.0, 2000.0),
                timestamp=datetime.now(),
                description="活动网络连接数"
            )

            # 进程指标
            processes = len(psutil.pids())
            self.metrics["processes"] = HealthMetric(
                name="运行进程数",
                value=processes,
                unit="个",
                threshold_warning=200.0,
                threshold_critical=300.0,
                status=self._evaluate_status(processes, 200.0, 300.0),
                timestamp=datetime.now(),
                description="系统运行进程总数"
            )

            # 系统负载（Windows可用）
            try:
                load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
                self.metrics["load"] = HealthMetric(
                    name="系统负载",
                    value=load_avg,
                    unit="",
                    threshold_warning=2.0,
                    threshold_critical=4.0,
                    status=self._evaluate_status(load_avg, 2.0, 4.0),
                    timestamp=datetime.now(),
                    description="系统平均负载"
                )
            except:
                pass  # Windows可能不支持

            # 启动时间
            boot_time = psutil.boot_time()
            uptime_hours = (time.time() - boot_time) / 3600
            self.metrics["uptime"] = HealthMetric(
                name="系统运行时间",
                value=uptime_hours,
                unit="小时",
                threshold_warning=720.0,  # 30天
                threshold_critical=1440.0,  # 60天
                status=HealthStatus.HEALTHY,  # 运行时间越长越好
                timestamp=datetime.now(),
                description="系统持续运行时间"
            )

        except Exception as e:
            print(f"收集系统指标失败: {str(e)}")

    def _evaluate_status(self, value: float, warning_threshold: float, critical_threshold: float) -> HealthStatus:
        """评估健康状态"""
        if value >= critical_threshold:
            return HealthStatus.CRITICAL
        elif value >= warning_threshold:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY

    def _analyze_health(self):
        """分析健康状态并生成告警"""
        for metric_name, metric in self.metrics.items():
            if metric.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
                alert_id = f"{metric_name}_{int(metric.timestamp.timestamp())}"

                # 检查是否已有相同告警
                existing_alert = next((a for a in self.alerts if a.metric_name == metric_name and not a.resolved), None)

                if existing_alert:
                    # 更新现有告警
                    if existing_alert.level.value != metric.status.value:
                        existing_alert.level = AlertLevel(metric.status.value)
                        existing_alert.message = f"{metric.name}状态变更: {metric.value}{metric.unit}"
                        existing_alert.timestamp = datetime.now()
                else:
                    # 创建新告警
                    alert = Alert(
                        id=alert_id,
                        metric_name=metric_name,
                        level=AlertLevel(metric.status.value),
                        message=f"{metric.name}异常: {metric.value}{metric.unit} (阈值: {metric.threshold_warning}{metric.unit})",
                        timestamp=datetime.now()
                    )
                    self.alerts.append(alert)
                    print(f"生成告警: {alert.message}")

                    # 发送邮件通知
                    if self.config["email_alerts_enabled"]:
                        self._send_email_alert(alert)

    def _check_recovery_conditions(self):
        """检查恢复条件并执行恢复动作"""
        if not self.config["auto_recovery_enabled"]:
            return

        for action in self.recovery_actions:
            if not action.enabled:
                continue

            try:
                if self._should_trigger_recovery(action.condition):
                    print(f"触发自动恢复: {action.name}")
                    result = action.action()
                    if result:
                        print(f"恢复动作执行成功: {action.name}")
                        # 记录恢复动作
                        self._log_recovery_action(action, "成功")
                    else:
                        print(f"恢复动作执行失败: {action.name}")
                        self._log_recovery_action(action, "失败")

            except Exception as e:
                print(f"执行恢复动作异常: {action.name} - {str(e)}")
                self._log_recovery_action(action, f"异常: {str(e)}")

    def _should_trigger_recovery(self, condition: str) -> bool:
        """判断是否应该触发恢复动作"""
        try:
            # 简单的条件解析
            if condition == "disk_usage > 85":
                return self.metrics.get("disk", HealthMetric("", 0, "", 0, 0, HealthStatus.HEALTHY, datetime.now(), "")).value > 85
            elif condition == "memory_usage > 90":
                return self.metrics.get("memory", HealthMetric("", 0, "", 0, 0, HealthStatus.HEALTHY, datetime.now(), "")).value > 90
            elif condition == "cpu_usage > 95":
                return self.metrics.get("cpu", HealthMetric("", 0, "", 0, 0, HealthStatus.HEALTHY, datetime.now(), "")).value > 95
            elif condition == "network_issues":
                # 简单的网络检查
                return self._check_network_connectivity() == False
            elif condition == "system_slow":
                # 系统响应缓慢判断
                return self._check_system_responsiveness() > 5.0  # 响应时间超过5秒
            else:
                return False

        except Exception as e:
            print(f"条件判断异常: {condition} - {str(e)}")
            return False

    def _cleanup_temp_files(self) -> bool:
        """清理临时文件"""
        try:
            import tempfile
            import shutil

            temp_dir = tempfile.gettempdir()
            cleaned_size = 0

            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                try:
                    if os.path.isfile(item_path):
                        file_age = time.time() - os.path.getctime(item_path)
                        if file_age > 86400:  # 清理超过1天的文件
                            file_size = os.path.getsize(item_path)
                            os.remove(item_path)
                            cleaned_size += file_size
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                except:
                    pass  # 忽略无法删除的文件

            print(f"清理临时文件完成，释放空间: {cleaned_size / 1024 / 1024:.2f} MB")
            return True

        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")
            return False

    def _restart_high_memory_processes(self) -> bool:
        """重启高内存进程"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 20:  # 内存使用超过20%
                        processes.append(proc.info)
                except:
                    continue

            if processes:
                print(f"发现高内存进程: {processes}")
                # 这里只记录，不实际重启（需要谨慎）
                return True
            return False

        except Exception as e:
            print(f"重启高内存进程失败: {str(e)}")
            return False

    def _terminate_high_cpu_processes(self) -> bool:
        """结束高CPU进程"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 80:  # CPU使用超过80%
                        processes.append(proc.info)
                except:
                    continue

            if processes:
                print(f"发现高CPU进程: {processes}")
                # 这里只记录，不实际结束（需要谨慎）
                return True
            return False

        except Exception as e:
            print(f"结束高CPU进程失败: {str(e)}")
            return False

    def _restart_network_services(self) -> bool:
        """重启网络服务"""
        try:
            # 简单的网络连通性测试
            if self._check_network_connectivity():
                print("网络连接正常，无需重启")
                return True

            # 在Windows上可以重启网络适配器
            if os.name == 'nt':
                os.system('ipconfig /release')
                time.sleep(2)
                os.system('ipconfig /renew')
                print("网络服务重启完成")
                return True

            return False

        except Exception as e:
            print(f"重启网络服务失败: {str(e)}")
            return False

    def _clear_system_cache(self) -> bool:
        """清理系统缓存"""
        try:
            if os.name == 'nt':
                # Windows系统清理
                os.system('del /q /f /s %TEMP%\\*')
                os.system('del /q /f /s C:\\Windows\\Temp\\*')
                print("系统缓存清理完成")
                return True
            else:
                # Linux系统清理
                os.system('sync && echo 3 > /proc/sys/vm/drop_caches')
                print("系统缓存清理完成")
                return True

        except Exception as e:
            print(f"清理系统缓存失败: {str(e)}")
            return False

    def _check_network_connectivity(self) -> bool:
        """检查网络连通性"""
        try:
            response = requests.get("https://www.baidu.com", timeout=5)
            return response.status_code == 200
        except:
            try:
                response = requests.get("https://8.8.8.8", timeout=5)
                return True
            except:
                return False

    def _check_system_responsiveness(self) -> float:
        """检查系统响应时间"""
        start_time = time.time()
        try:
            # 执行一个简单的系统调用
            os.listdir('/')
            return time.time() - start_time
        except:
            return float('inf')

    def _send_email_alert(self, alert: Alert):
        """发送邮件告警"""
        try:
            if not self.config.get("email_recipients"):
                return

            msg = MimeMultipart()
            msg['From'] = self.config["email_username"]
            msg['To'] = ', '.join(self.config["email_recipients"])
            msg['Subject'] = f"系统告警 - {alert.level.value.upper()}: {alert.metric_name}"

            body = f"""
系统健康监控告警

告警ID: {alert.id}
告警级别: {alert.level.value.upper()}
指标名称: {alert.metric_name}
告警消息: {alert.message}
告警时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

系统指标概览:
{json.dumps({k: asdict(v) for k, v in self.metrics.items()}, indent=2, ensure_ascii=False)}

请及时处理相关告警。
            """

            msg.attach(MimeText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(self.config["email_smtp_server"], self.config["email_smtp_port"])
            server.starttls()
            server.login(self.config["email_username"], self.config["email_password"])
            server.send_message(msg)
            server.quit()

            print(f"邮件告警发送成功: {alert.id}")

        except Exception as e:
            print(f"发送邮件告警失败: {str(e)}")

    def _log_recovery_action(self, action: RecoveryAction, result: str):
        """记录恢复动作"""
        for alert in self.alerts:
            if not alert.resolved and action.condition in alert.message:
                alert.actions_taken.append(f"{action.name}: {result}")
                break

    def get_health_summary(self) -> Dict[str, Any]:
        """获取健康状态摘要"""
        resolved_alerts = [a for a in self.alerts if a.resolved]
        active_alerts = [a for a in self.alerts if not a.resolved]

        # 计算整体健康状态
        if any(m.status == HealthStatus.CRITICAL for m in self.metrics.values()):
            overall_status = HealthStatus.CRITICAL
        elif any(m.status == HealthStatus.WARNING for m in self.metrics.values()):
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            "overall_status": overall_status.value,
            "monitoring_active": self.monitoring_active,
            "last_check_time": self.last_check_time.isoformat(),
            "metrics_count": len(self.metrics),
            "active_alerts_count": len(active_alerts),
            "resolved_alerts_count": len(resolved_alerts),
            "total_alerts_count": len(self.alerts),
            "metrics": {k: {
                "name": v.name,
                "value": v.value,
                "unit": v.unit,
                "status": v.status.value,
                "description": v.description
            } for k, v in self.metrics.items()},
            "active_alerts": [asdict(a) for a in active_alerts[-10:]],  # 最近10个活跃告警
            "recovery_actions_enabled": sum(1 for a in self.recovery_actions if a.enabled),
            "auto_recovery_enabled": self.config["auto_recovery_enabled"]
        }

    def get_detailed_metrics(self) -> List[Dict[str, Any]]:
        """获取详细指标数据"""
        return [asdict(metric) for metric in self.metrics.values()]

    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取告警历史"""
        return [asdict(alert) for alert in sorted(self.alerts, key=lambda x: x.timestamp, reverse=True)[:limit]]

    def resolve_alert(self, alert_id: str) -> bool:
        """手动解决告警"""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                print(f"告警已解决: {alert_id}")
                return True
        return False

# 创建全局健康监控实例
health_monitor = SystemHealthMonitor()