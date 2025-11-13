# 停止 YOLO-LLM 服务指南

当您需要停止正在运行的 YOLO-LLM 服务时，有几种方法可以选择：

## 🛑 停止方法

### 方法1: 标准停止脚本 (推荐)
```powershell
.\stop-all.ps1
```

**特点:**
- 安全地停止所有YOLO-LLM相关进程
- 先尝试优雅关闭，失败时强制停止
- 智能识别Agent窗口并正确关闭
- 检查端口占用状态

### 方法2: 强制停止脚本 (紧急情况)
```powershell
.\force-stop.ps1
```

**特点:**
- 强制终止所有相关进程
- 适用于标准脚本无法停止的情况
- 会要求确认，防止误操作
- 可能关闭无关进程，请谨慎使用

### 方法3: 手动停止个别服务

#### 停止 Agent (手势控制)
```powershell
# 方法A: 在Agent窗口中按 Ctrl+C
# 方法B: 在Agent窗口中按 'q' 键
# 方法C: 直接关闭Agent窗口
```

#### 停止其他服务
- **Backend**: 在Spring Boot窗口按 `Ctrl+C`
- **AI Service**: 在FastAPI窗口按 `Ctrl+C`
- **Frontend**: 在npm窗口按 `Ctrl+C`

### 方法4: 任务管理器
1. 按 `Ctrl+Shift+Esc` 打开任务管理器
2. 查找以下进程并结束：
   - `python` (多个实例 - Agent和AI服务)
   - `java` (Backend)
   - `node` (Frontend)
   - `powershell` (如果服务窗口还在)

## 🔍 服务识别

### 进程特征
- **Agent**: Python进程，命令行包含 `agent.*main\.py`
- **AI Service**: Python进程，命令行包含 `uvicorn.*main:app`
- **Backend**: Java进程，命令行包含 `spring-boot`
- **Frontend**: Node.js进程，命令行包含 `vite` 或 `npm.*dev`

### 端口占用
- **8000**: AI Service
- **8080**: Backend API
- **5173**: Frontend Web界面

## ⚠️ 注意事项

1. **Agent窗口特殊性**: Agent使用实时摄像头，可能需要额外时间来正确释放摄像头资源
2. **优雅关闭**: 建议优先使用 `Ctrl+C` 而不是直接关闭窗口
3. **端口占用**: 如果服务重启时遇到端口占用，等待30秒或使用强制停止脚本
4. **摄像头权限**: 如果Agent下次启动时无法访问摄像头，重启电脑通常能解决

## 🚀 重新启动服务

停止服务后，可以使用以下命令重新启动：
```powershell
# 标准启动
.\start-all.ps1

# 或简化启动
.\start-simple.ps1
```

## 🐛 故障排除

### 问题1: Agent窗口无法关闭
**解决方案:**
```powershell
# 使用强制停止脚本
.\force-stop.ps1
```

### 问题2: 端口仍被占用
**解决方案:**
1. 等待30秒让进程完全终止
2. 使用强制停止脚本
3. 重启电脑
4. 手动修改端口配置

### 问题3: 摄像头被占用
**解决方案:**
1. 确保Agent进程已完全停止
2. 重启电脑
3. 检查其他应用是否在使用摄像头

## 📞 获取帮助

如果遇到无法解决的问题：
1. 检查各个服务窗口的错误信息
2. 确认所有依赖软件已正确安装
3. 尝试重启电脑作为最后手段