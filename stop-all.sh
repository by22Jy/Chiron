#!/bin/bash

echo "==================================="
echo "   YOLO-LLM 项目停止脚本 (Linux/Mac)"
echo "==================================="

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[信息]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

log_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 停止服务函数
stop_service() {
    local service_name=$1
    local pid_file=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            log_info "停止 $service_name (PID: $pid)..."
            kill $pid
            sleep 2
            if kill -0 $pid 2>/dev/null; then
                log_warn "$service_name 未停止，强制杀死..."
                kill -9 $pid
            fi
            log_info "$service_name 已停止"
        else
            log_warn "$service_name 进程不存在 (PID: $pid)"
        fi
        rm -f "$pid_file"
    else
        log_warn "$service_name PID文件不存在"
    fi
}

# 停止所有服务
stop_service "Backend" ".backend.pid"
stop_service "AI Service" ".ai.pid"
stop_service "Frontend" ".frontend.pid"

# 额外检查并停止可能遗留的进程
echo
log_info "检查遗留进程..."

# 查找并停止可能的Spring Boot进程
pkill -f "spring-boot:run" 2>/dev/null && log_info "停止遗留的Spring Boot进程"

# 查找并停止可能的uvicorn进程
pkill -f "uvicorn main:app" 2>/dev/null && log_info "停止遗留的uvicorn进程"

# 查找并停止可能的npm dev进程
pkill -f "vite.*dev" 2>/dev/null && log_info "停止遗留的Vite开发服务器"

echo
log_info "所有YOLO-LLM服务已停止"