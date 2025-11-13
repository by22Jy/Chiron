#!/bin/bash

echo "==================================="
echo "   YOLO-LLM 项目启动脚本 (Linux/Mac)"
echo "==================================="

# 设置环境变量 - 请根据实际情况修改
export DB_URL="jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC"
export DB_USER="root"
export DB_PASS="Wangjiayi1"
# 请设置你的 LLM API Key
export KIMI_API_KEY="your_kimi_api_key_here"
# 或者使用 Qwen
# export QWEN_API_KEY="your_qwen_api_key_here"

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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装或不在PATH中"
        return 1
    fi
    return 0
}

# 检查MySQL连接
echo
log_info "检查MySQL连接..."
if ! mysql -u $DB_USER -p$DB_PASS -e "USE yolo_platform;" 2>/dev/null; then
    log_error "无法连接到MySQL数据库，请确保："
    echo "1. MySQL服务已启动"
    echo "2. 数据库 yolo_platform 已创建"
    echo "3. 用户名密码正确"
    exit 1
fi
log_info "MySQL连接正常"

# 检查必要的命令
echo
log_info "检查必要的环境..."
for cmd in python3 java mvn npm; do
    if ! check_command $cmd; then
        log_error "请先安装 $cmd"
        exit 1
    fi
done

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 启动后端服务
echo
log_info "启动后端服务 (端口: 8080)..."
cd "$SCRIPT_DIR/backend"
nohup mvn spring-boot:run > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 10

# 启动AI服务
echo
log_info "启动AI服务 (端口: 8000)..."
cd "$SCRIPT_DIR/ai"
if [ ! -d ".venv" ]; then
    log_info "创建Python虚拟环境..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt -q
nohup uvicorn main:app --reload --host 127.0.0.1 --port 8000 > ai.log 2>&1 &
AI_PID=$!
echo "AI Service PID: $AI_PID"
sleep 5

# 启动前端服务
echo
log_info "启动前端服务 (端口: 5173)..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    log_info "安装前端依赖..."
    npm install
fi
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
sleep 5

echo
echo "==================================="
echo "       所有服务启动完成"
echo "==================================="
echo "后端API: http://localhost:8080"
echo "AI服务:  http://localhost:8000"
echo "前端界面: http://localhost:5173"
echo
echo "进程PID："
echo "Backend:  $BACKEND_PID"
echo "AI Service: $AI_PID"
echo "Frontend:  $FRONTEND_PID"
echo
echo "Agent手动启动命令："
echo "  cd agent"
echo "  pip install -r requirements.txt"
echo "  python main.py --realtime"
echo
echo "停止所有服务："
echo "  kill $BACKEND_PID $AI_PID $FRONTEND_PID"
echo

# 保存PID到文件
echo "$BACKEND_PID" > .backend.pid
echo "$AI_PID" > .ai.pid
echo "$FRONTEND_PID" > .frontend.pid

log_info "服务已后台运行，PID已保存到 .*.pid 文件"