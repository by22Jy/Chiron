<template>
  <div class="modern-layout">
    <!-- 浮动导航栏 -->
    <nav class="floating-nav glass-card">
      <div class="nav-brand">
        <div class="brand-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" stroke="url(#brandGradient)" stroke-width="2"/>
            <path d="M10 16l4 4 8-8" stroke="url(#brandGradient)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="brandGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea"/>
                <stop offset="100%" style="stop-color:#764ba2"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <span class="brand-text">Chrion</span>
      </div>

      <div class="nav-menu">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <component :is="item.icon" class="nav-icon" />
          <span class="nav-label">{{ item.label }}</span>
          <div class="nav-indicator"></div>
        </router-link>
      </div>

      <div class="nav-actions">
        <div class="status-indicators">
          <div class="status-dot" :class="{ online: systemStatus.backend === 'healthy' }" :title="getStatusText('backend')"></div>
          <div class="status-dot" :class="{ online: systemStatus.ai_service === 'healthy' }" :title="getStatusText('ai_service')"></div>
        </div>

        <div class="user-menu" @click="showUserMenu = !showUserMenu">
          <div class="user-avatar">
            <User />
          </div>
          <span class="user-name">管理员</span>
          <ArrowDown class="dropdown-arrow" :class="{ active: showUserMenu }" />
        </div>

        <!-- 用户下拉菜单 -->
        <div v-if="showUserMenu" class="user-dropdown glass-card">
          <div class="dropdown-item" @click="handleUserMenuCommand('profile')">
            <User />
            <span>个人信息</span>
          </div>
          <div class="dropdown-item" @click="handleUserMenuCommand('settings')">
            <Setting />
            <span>设置</span>
          </div>
          <div class="dropdown-divider"></div>
          <div class="dropdown-item" @click="handleUserMenuCommand('logout')">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 3h8a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M3 8h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M6.5 5.5L3 8l3.5 2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>退出登录</span>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 面包屑导航 -->
        <div class="breadcrumb-nav" v-if="$route.path !== '/' && $route.path !== '/dashboard'">
          <div class="breadcrumb-item">
            <router-link to="/dashboard" class="breadcrumb-link">首页</router-link>
          </div>
          <div class="breadcrumb-separator">/</div>
          <div class="breadcrumb-item current">{{ currentPageTitle }}</div>
        </div>

        <!-- 路由内容 -->
        <div class="route-content">
          <router-view v-slot="{ Component }">
            <transition name="page-transition" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </div>
    </main>

    <!-- 点击外部关闭用户菜单 -->
    <div v-if="showUserMenu" class="menu-overlay" @click="showUserMenu = false"></div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMonitorStore } from '@/stores/monitor'
import {
  Monitor,
  Setting,
  View,
  Document,
  User,
  ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const monitorStore = useMonitorStore()

// 响应式数据
const showUserMenu = ref(false)

// 导航配置
const navItems = [
  {
    path: '/dashboard',
    label: '仪表盘',
    icon: Monitor
  },
  {
    path: '/config',
    label: '配置管理',
    icon: Setting
  },
  {
    path: '/monitor',
    label: '实时监控',
    icon: View
  },
  {
    path: '/training',
    label: '手势训练',
    icon: Monitor
  },
  {
    path: '/logs',
    label: '系统日志',
    icon: Document
  }
]

// 计算属性
const currentPageTitle = computed(() => {
  const routeMap = {
    '/dashboard': '仪表盘',
    '/config': '配置管理',
    '/monitor': '实时监控',
    '/training': '手势训练',
    '/logs': '系统日志'
  }
  return routeMap[route.path] || '仪表盘'
})

const systemStatus = computed(() => monitorStore.systemStatus)

// 方法
const handleUserMenuCommand = (command) => {
  showUserMenu.value = false
  switch (command) {
    case 'profile':
      // 跳转到个人信息页面
      console.log('个人信息')
      break
    case 'settings':
      router.push('/config')
      break
    case 'logout':
      // 退出登录逻辑
      console.log('退出登录')
      break
  }
}

const getStatusText = (key) => {
  const texts = {
    backend: '后端服务',
    ai_service: 'AI服务',
    database: '数据库',
    agent: 'Agent代理'
  }
  const status = systemStatus.value[key]
  return `${texts[key] || key}: ${status === 'healthy' ? '正常' : '异常'}`
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
@import '@/styles/modern.css';

.modern-layout {
  min-height: 100vh;
  background: var(--bg-primary);
  position: relative;
}

/* 浮动导航栏 */
.floating-nav {
  position: fixed;
  top: 20px;
  left: 20px;
  right: 20px;
  height: 72px;
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 1000;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.floating-nav:hover {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
  border-color: rgba(102, 126, 234, 0.3);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.brand-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 导航菜单 */
.nav-menu {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
  max-width: 600px;
  margin: 0 40px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  font-weight: 500;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--gradient-primary);
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 12px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  transform: translateY(-2px);
}

.nav-item.active {
  color: white;
  background: var(--gradient-primary);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-item.active .nav-indicator {
  opacity: 1;
}

.nav-icon {
  width: 18px;
  height: 18px;
  z-index: 1;
}

.nav-label {
  font-size: 0.875rem;
  z-index: 1;
  white-space: nowrap;
}

.nav-indicator {
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

/* 导航右侧操作 */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}

.status-indicators {
  display: flex;
  gap: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.status-dot.online {
  background: var(--accent-green);
  box-shadow: 0 0 12px rgba(52, 199, 89, 0.6);
}

.status-dot::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: inherit;
  opacity: 0.3;
  animation: pulse 2s ease-in-out infinite;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
  position: relative;
}

.user-menu:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--gradient-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
  transition: transform 0.3s ease;
}

.dropdown-arrow.active {
  transform: rotate(180deg);
}

/* 用户下拉菜单 */
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  min-width: 180px;
  padding: 8px;
  border-radius: 16px;
  z-index: 1001;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.dropdown-item svg {
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 4px 0;
  border-radius: 1px;
}

/* 主内容区域 */
.main-content {
  margin-top: 112px;
  min-height: calc(100vh - 112px);
  padding: 0 20px 40px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

/* 面包屑导航 */
.breadcrumb-nav {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding: 16px 24px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
}

.breadcrumb-item {
  font-size: 0.875rem;
  font-weight: 500;
}

.breadcrumb-link {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.3s ease;
}

.breadcrumb-link:hover {
  color: var(--accent-blue);
}

.breadcrumb-item.current {
  color: var(--text-primary);
}

.breadcrumb-separator {
  color: var(--text-secondary);
  font-weight: 400;
}

/* 路由内容 */
.route-content {
  min-height: 600px;
}

/* 页面切换动画 */
.page-transition-enter-active,
.page-transition-leave-active {
  transition: all 0.4s var(--transition-smooth);
}

.page-transition-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-transition-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 菜单遮罩 */
.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  background: transparent;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .floating-nav {
    left: 16px;
    right: 16px;
    padding: 0 20px;
  }

  .nav-menu {
    margin: 0 24px;
  }

  .nav-label {
    display: none;
  }

  .nav-item {
    padding: 12px;
  }
}

@media (max-width: 768px) {
  .floating-nav {
    height: auto;
    min-height: 64px;
    flex-direction: column;
    gap: 16px;
    padding: 16px;
    top: 16px;
    left: 16px;
    right: 16px;
  }

  .nav-brand {
    width: 100%;
    justify-content: center;
  }

  .nav-menu {
    width: 100%;
    justify-content: space-around;
    margin: 0;
  }

  .nav-actions {
    width: 100%;
    justify-content: space-between;
  }

  .main-content {
    margin-top: 140px;
    padding: 0 16px 32px;
  }

  .breadcrumb-nav {
    padding: 12px 16px;
    margin-bottom: 20px;
  }
}

@media (max-width: 480px) {
  .floating-nav {
    top: 12px;
    left: 12px;
    right: 12px;
    padding: 12px;
    border-radius: 16px;
  }

  .main-content {
    margin-top: 120px;
    padding: 0 12px 24px;
  }

  .brand-text {
    font-size: 1.125rem;
  }

  .nav-item {
    padding: 10px;
  }

  .user-name {
    display: none;
  }
}
</style>