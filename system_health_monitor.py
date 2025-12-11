#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO-LLM System Health Monitor and Auto-Recovery Service
企业级系统健康监控和自动恢复服务
"""

import asyncio
import aiohttp
import logging
import json
import time
import subprocess
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import psutil
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceHealth:
    """Service health status data class"""
    name: str
    url: str
    port: int
    status: str = "unknown"  # healthy, unhealthy, unknown
    response_time: float = 0.0
    last_check: datetime = None
    failure_count: int = 0
    max_failures: int = 3
    process_name: Optional[str] = None
    startup_command: Optional[str] = None
    startup_dir: Optional[str] = None

class SystemHealthMonitor:
    """System health monitor and auto-recovery service"""

    def __init__(self):
        self.services = self._initialize_services()
        self.session = None
        self.running = False
        self.check_interval = 30  # seconds
        self.recovery_cooldown = 300  # 5 minutes
        self.last_recovery_attempts = {}

    def _initialize_services(self) -> Dict[str, ServiceHealth]:
        """Initialize service definitions"""
        return {
            "mcp_server": ServiceHealth(
                name="MCP Server",
                url="http://localhost:8083/health",
                port=8083,
                process_name="enhanced_mcp_server.py",
                startup_command="python enhanced_mcp_server.py",
                startup_dir="mcp"
            ),
            "backend": ServiceHealth(
                name="Backend Service",
                url="http://localhost:8080/actuator/health",
                port=8080,
                process_name="java",
                startup_command="mvn spring-boot:run",
                startup_dir="backend"
            ),
            "ai_service": ServiceHealth(
                name="AI Service",
                url="http://localhost:8000/health",
                port=8000,
                process_name="uvicorn",
                startup_command="uvicorn main:app --host 127.0.0.1 --port 8000 --reload",
                startup_dir="ai"
            ),
            "frontend": ServiceHealth(
                name="Frontend Service",
                url="http://localhost:5173",
                port=5173,
                process_name="npm",
                startup_command="npm run dev",
                startup_dir="frontend"
            )
        }

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def check_service_health(self, service: ServiceHealth) -> bool:
        """Check individual service health"""
        try:
            start_time = time.time()

            # Try HTTP health check first
            async with self.session.get(service.url) as response:
                response_time = time.time() - start_time
                service.response_time = response_time
                service.last_check = datetime.now()

                if response.status == 200:
                    service.status = "healthy"
                    service.failure_count = 0
                    logger.info(f"✅ {service.name}: Healthy ({response_time:.2f}s)")
                    return True
                else:
                    logger.warning(f" {service.name}: HTTP {response.status}")
                    return False

        except Exception as e:
            logger.error(f"❌ {service.name}: Health check failed - {str(e)}")

            # Fallback to port check
            if await self._check_port_open(service.port):
                service.status = "healthy"
                service.failure_count = 0
                logger.info(f"✅ {service.name}: Port check passed")
                return True
            else:
                service.status = "unhealthy"
                service.failure_count += 1
                logger.error(f"❌ {service.name}: Port {service.port} closed")
                return False

    async def _check_port_open(self, port: int) -> bool:
        """Check if port is open"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def is_process_running(self, process_name: str) -> bool:
        """Check if process is running by name"""
        try:
            for proc in psutil.process_iter(['name']):
                if process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"Process check failed: {str(e)}")
            return False

    async def restart_service(self, service: ServiceHealth) -> bool:
        """Attempt to restart a service"""
        service_key = service.name.lower().replace(" ", "_")
        now = datetime.now()

        # Check cooldown
        if service_key in self.last_recovery_attempts:
            time_since_last = now - self.last_recovery_attempts[service_key]
            if time_since_last.total_seconds() < self.recovery_cooldown:
                logger.warning(f"⏰ {service.name}: Recovery cooldown active ({self.recovery_cooldown - time_since_last.total_seconds():.0f}s remaining)")
                return False

        try:
            logger.info(f"🔄 Attempting to restart {service.name}...")

            # Kill existing process if running
            if self.is_process_running(service.process_name):
                await self._kill_process(service.process_name)
                await asyncio.sleep(3)

            # Start new process
            success = await self._start_service_process(service)

            if success:
                self.last_recovery_attempts[service_key] = now
                service.failure_count = 0
                logger.info(f"✅ {service.name}: Restart initiated successfully")
                return True
            else:
                logger.error(f"❌ {service.name}: Failed to restart")
                return False

        except Exception as e:
            logger.error(f"❌ {service.name}: Restart failed - {str(e)}")
            return False

    async def _kill_process(self, process_name: str):
        """Kill process by name"""
        try:
            system_name = platform.system().lower()
            if system_name == "windows":
                subprocess.run(f'taskkill /f /im "{process_name}"', shell=True, check=False)
            else:
                subprocess.run(f'pkill -f "{process_name}"', shell=True, check=False)
        except Exception as e:
            logger.error(f"Failed to kill process {process_name}: {str(e)}")

    async def _start_service_process(self, service: ServiceHealth) -> bool:
        """Start service process"""
        try:
            if not service.startup_dir or not service.startup_command:
                logger.error(f"❌ {service.name}: Missing startup configuration")
                return False

            startup_dir = Path(service.startup_dir)
            if not startup_dir.exists():
                logger.error(f"❌ {service.name}: Startup directory not found: {startup_dir}")
                return False

            system_name = platform.system().lower()

            if system_name == "windows":
                # Windows PowerShell startup
                if service.process_name == "python":
                    cmd = f'powershell -Command "cd {startup_dir.absolute()}; {service.startup_command}"'
                else:
                    cmd = f'powershell -Command "cd {startup_dir.absolute()}; {service.startup_command}"'
            else:
                # Linux/Mac startup
                cmd = f'cd {startup_dir.absolute()} && {service.startup_command}'

            # Start process detached
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            logger.info(f"🚀 {service.name}: Startup command executed")
            return True

        except Exception as e:
            logger.error(f"❌ {service.name}: Failed to start process - {str(e)}")
            return False

    async def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "platform": platform.system(),
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "services": {}
        }

        for key, service in self.services.items():
            report["services"][key] = {
                "name": service.name,
                "status": service.status,
                "url": service.url,
                "port": service.port,
                "response_time": service.response_time,
                "failure_count": service.failure_count,
                "last_check": service.last_check.isoformat() if service.last_check else None
            }

        return report

    async def save_health_report(self, report: Dict):
        """Save health report to file"""
        try:
            os.makedirs('logs', exist_ok=True)
            with open('logs/health_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save health report: {str(e)}")

    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🔍 Starting system health monitor...")

        while self.running:
            try:
                unhealthy_services = []

                # Check all services
                for key, service in self.services.items():
                    is_healthy = await self.check_service_health(service)

                    if not is_healthy and service.failure_count >= service.max_failures:
                        unhealthy_services.append(service)

                # Attempt recovery for unhealthy services
                for service in unhealthy_services:
                    await self.restart_service(service)

                # Generate and save health report
                report = await self.generate_health_report()
                await self.save_health_report(report)

                # Log summary
                healthy_count = sum(1 for s in self.services.values() if s.status == "healthy")
                total_count = len(self.services)

                logger.info(f"📊 Health check complete: {healthy_count}/{total_count} services healthy")

                # Wait for next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Monitor loop error: {str(e)}")
                await asyncio.sleep(10)

    async def start(self):
        """Start the health monitor"""
        self.running = True
        await self.monitor_loop()

    def stop(self):
        """Stop the health monitor"""
        self.running = False
        logger.info("Health monitor stopped")

class HealthDashboard:
    """Health dashboard server for real-time monitoring"""

    def __init__(self, monitor: SystemHealthMonitor):
        self.monitor = monitor
        self.app = None
        self.setup_routes()

    def setup_routes(self):
        """Setup FastAPI routes for dashboard"""
        try:
            from fastapi import FastAPI
            from fastapi.responses import HTMLResponse, JSONResponse
            from fastapi.staticfiles import StaticFiles

            self.app = FastAPI(title="YOLO-LLM Health Dashboard", version="1.0.0")

            @self.app.get("/", response_class=HTMLResponse)
            async def dashboard():
                return self._generate_dashboard_html()

            @self.app.get("/health")
            async def health():
                report = await self.monitor.generate_health_report()
                return JSONResponse(report)

            @self.app.get("/services")
            async def services():
                return JSONResponse({
                    key: {
                        "name": service.name,
                        "status": service.status,
                        "port": service.port,
                        "response_time": service.response_time,
                        "failure_count": service.failure_count
                    }
                    for key, service in self.monitor.services.items()
                })

            logger.info("Health dashboard routes configured")

        except ImportError:
            logger.warning("FastAPI not available, dashboard disabled")

    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>YOLO-LLM Health Dashboard</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #333; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .service-card { background: white; margin: 10px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .healthy { border-left: 4px solid #4CAF50; }
        .unhealthy { border-left: 4px solid #f44336; }
        .unknown { border-left: 4px solid #FF9800; }
        .status { font-weight: bold; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric { background: white; padding: 15px; border-radius: 8px; text-align: center; }
        .refresh { position: fixed; bottom: 20px; right: 20px; background: #2196F3; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 YOLO-LLM System Health Dashboard</h1>
            <p>Real-time system monitoring and health status</p>
        </div>

        <div class="metrics">
            <div class="metric">
                <h3 id="total-services">4</h3>
                <p>Total Services</p>
            </div>
            <div class="metric">
                <h3 id="healthy-services">0</h3>
                <p>Healthy Services</p>
            </div>
            <div class="metric">
                <h3 id="unhealthy-services">0</h3>
                <p>Unhealthy Services</p>
            </div>
            <div class="metric">
                <h3 id="last-update">Never</h3>
                <p>Last Update</p>
            </div>
        </div>

        <div id="services-container">
            <div class="service-card">
                <p>Loading services...</p>
            </div>
        </div>

        <button class="refresh" onclick="loadServices()">🔄 Refresh</button>
    </div>

    <script>
        async function loadServices() {
            try {
                const response = await fetch('/services');
                const services = await response.json();

                const container = document.getElementById('services-container');
                container.innerHTML = '';

                let healthy = 0, unhealthy = 0;

                for (const [key, service] of Object.entries(services)) {
                    const card = document.createElement('div');
                    card.className = `service-card ${service.status}`;

                    const statusColor = service.status === 'healthy' ? '#4CAF50' :
                                       service.status === 'unhealthy' ? '#f44336' : '#FF9800';

                    card.innerHTML = `
                        <h3>${service.name}</h3>
                        <p><span class="status" style="color: ${statusColor}">${service.status.toUpperCase()}</span></p>
                        <p>Port: ${service.port}</p>
                        <p>Response Time: ${service.response_time.toFixed(2)}s</p>
                        <p>Failures: ${service.failure_count}</p>
                        <p>URL: <a href="${service.url}" target="_blank">${service.url}</a></p>
                    `;

                    container.appendChild(card);

                    if (service.status === 'healthy') healthy++;
                    else if (service.status === 'unhealthy') unhealthy++;
                }

                document.getElementById('total-services').textContent = Object.keys(services).length;
                document.getElementById('healthy-services').textContent = healthy;
                document.getElementById('unhealthy-services').textContent = unhealthy;
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();

            } catch (error) {
                console.error('Failed to load services:', error);
            }
        }

        // Auto-refresh every 30 seconds
        setInterval(loadServices, 30000);

        // Initial load
        loadServices();
    </script>
</body>
</html>
        """

async def main():
    """Main function"""
    logger.info("🚀 Starting YOLO-LLM System Health Monitor")

    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)

    monitor = SystemHealthMonitor()

    try:
        async with monitor:
            # Start health monitor
            monitor_task = asyncio.create_task(monitor.start())

            # Setup dashboard if FastAPI is available
            dashboard = HealthDashboard(monitor)
            if dashboard.app:
                import uvicorn
                logger.info("🌐 Starting health dashboard on http://localhost:9999")
                dashboard_task = asyncio.create_task(
                    uvicorn.run(dashboard.app, host="127.0.0.1", port=9999, log_level="warning")
                )

            # Keep running
            try:
                await monitor_task
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                monitor.stop()

    except Exception as e:
        logger.error(f"Health monitor failed: {str(e)}")
        monitor.stop()

if __name__ == "__main__":
    asyncio.run(main())