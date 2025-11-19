<template>
  <el-container class="app-layout">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>YOLO-LLM</h2>
        <p>手势控制平台</p>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        class="nav-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>

        <el-menu-item index="/config">
          <el-icon><Setting /></el-icon>
          <span>配置管理</span>
        </el-menu-item>

        <el-menu-item index="/monitor">
          <el-icon><View /></el-icon>
          <span>实时监控</span>
        </el-menu-item>

        <el-menu-item index="/training">
          <el-icon><Monitor /></el-icon>
          <span>手势训练</span>
        </el-menu-item>

        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <span>系统日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>YOLO-LLM</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 系统状态指示器 -->
          <div class="status-indicators">
            <el-tooltip content="后端服务状态">
              <el-icon :color="systemStatus.backend === 'healthy' ? '#67C23A' : '#F56C6C'">
                <Connection />
              </el-icon>
            </el-tooltip>

            <el-tooltip content="AI服务状态">
              <el-icon :color="systemStatus.ai_service === 'healthy' ? '#67C23A' : '#F56C6C'">
                <VideoPlay />
              </el-icon>
            </el-tooltip>
          </div>

          <!-- 用户菜单 -->
          <el-dropdown @command="handleUserMenuCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>管理员</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMonitorStore } from '@/stores/monitor'
import {
  Monitor,
  Setting,
  View,
  Document,
  Connection,
  VideoPlay,
  User,
  ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const monitorStore = useMonitorStore()

// 计算属性
const currentPageTitle = computed(() => {
  return route.meta?.title || '仪表盘'
})

const systemStatus = computed(() => monitorStore.systemStatus)

// 方法
const handleUserMenuCommand = (command) => {
  switch (command) {
    case 'profile':
      // 跳转到个人信息页面
      break
    case 'settings':
      router.push('/config')
      break
    case 'logout':
      // 退出登录逻辑
      break
  }
}

// 定时刷新系统状态
let statusTimer = null

const startStatusPolling = () => {
  statusTimer = setInterval(() => {
    monitorStore.loadSystemStatus().catch(console.error)
  }, 5000) // 每5秒刷新一次
}

const stopStatusPolling = () => {
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
}

// 生命周期
onMounted(async () => {
  // 初始加载系统状态
  await monitorStore.loadSystemStatus().catch(console.error)
  startStatusPolling()
})

onUnmounted(() => {
  stopStatusPolling()
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  color: #bfcbd9;
  overflow: hidden;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #3a4560;
}

.logo h2 {
  margin: 0;
  color: #409EFF;
  font-size: 18px;
}

.logo p {
  margin: 5px 0 0;
  font-size: 12px;
  color: #909399;
}

.nav-menu {
  border: none;
}

.main-container {
  background-color: #f0f2f5;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.status-indicators {
  display: flex;
  gap: 15px;
}

.status-indicators .el-icon {
  font-size: 16px;
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.main-content {
  padding: 20px;
  background-color: #f0f2f5;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 64px !important;
  }

  .logo h2,
  .logo p,
  .nav-menu span {
    display: none;
  }

  .nav-menu .el-icon {
    margin-right: 0;
  }
}
</style>