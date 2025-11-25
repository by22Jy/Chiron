<template>
  <div class="modern-dashboard">
    <!-- 英雄区域 -->
    <div class="hero-section animate-slide-in-top">
      <div class="hero-content">
        <div class="hero-text">
          <div class="title-container">
            <div class="title-content">
              <h1 class="hero-title">
                Chrion
                <span class="hero-accent">手势控制平台</span>
              </h1>
              <p class="hero-subtitle">基于人工智能的下一代手势交互体验</p>
            </div>
          </div>
        </div>
        <div class="hero-visual">
          <div class="floating-cards">
            <div class="gesture-demo animate-float-delay-1">
              <div class="hand-icon">✋</div>
              <span class="gesture-label">手势识别</span>
            </div>
            <div class="ai-demo animate-float-delay-2">
              <div class="ai-icon">🤖</div>
              <span class="ai-label">AI驱动</span>
            </div>
            <div class="control-demo animate-float-delay-3">
              <div class="control-icon">🎯</div>
              <span class="control-label">精准控制</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时数据统计 -->
    <div class="stats-section">
      <h2 class="section-title animate-slide-in-left">
        <span class="title-icon">📊</span>
        实时性能监控
      </h2>
      <div class="modern-grid">
        <div class="data-card animate-slide-in-left" style="animation-delay: 0.1s">
          <div class="card-header">
            <div class="card-icon blue">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M3 3v18h18" stroke="currentColor" stroke-width="2"/>
                <path d="M7 12l4 4 8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="status-indicator online"></div>
          </div>
          <div class="data-value">{{ statistics.gesture_count?.toLocaleString() || '1,234' }}</div>
          <div class="data-label">手势识别次数</div>
          <div class="data-trend positive">
            <span class="trend-icon">📈</span>
            +12.5%
          </div>
          <!-- 迷你趋势图 -->
          <div class="mini-chart">
            <svg viewBox="0 0 100 40" class="trend-svg">
              <!-- 背景区域填充 -->
              <defs>
                <linearGradient id="areaGradient1" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.3" />
                  <stop offset="100%" style="stop-color:#667eea;stop-opacity:0.05" />
                </linearGradient>
                <linearGradient id="lineGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                </linearGradient>
              </defs>
              <!-- 面积图 -->
              <path d="M 5,35 L 15,30 L 25,32 L 35,25 L 45,20 L 55,15 L 65,18 L 75,12 L 85,8 L 95,10 L 95,35 Z"
                    fill="url(#areaGradient1)" />
              <!-- 趋势线 -->
              <path d="M 5,35 L 15,30 L 25,32 L 35,25 L 45,20 L 55,15 L 65,18 L 75,12 L 85,8 L 95,10"
                    fill="none"
                    stroke="url(#lineGradient1)"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"/>
              <!-- 数据点 -->
              <circle cx="95" cy="10" r="2" fill="#667eea" opacity="0.8"/>
            </svg>
          </div>
        </div>

        <div class="data-card animate-slide-in-left" style="animation-delay: 0.2s">
          <div class="card-header">
            <div class="card-icon green">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M8 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="status-indicator online"></div>
          </div>
          <div class="data-value">{{ (statistics.success_rate || 98.7).toFixed(1) }}%</div>
          <div class="data-label">识别成功率</div>
          <div class="data-trend positive">
            <span class="trend-icon">📈</span>
            +2.3%
          </div>
          <!-- 成功率环形图 -->
          <div class="progress-ring">
            <svg viewBox="0 0 80 40" class="progress-svg">
              <!-- 背景环 -->
              <circle cx="40" cy="20" r="16" fill="none" stroke="#f0f0f0" stroke-width="4"/>
              <!-- 进度环 -->
              <circle cx="40" cy="20" r="16" fill="none" stroke="url(#successGradient)" stroke-width="4"
                      stroke-linecap="round"
                      stroke-dasharray="100"
                      :stroke-dashoffset="100 - (100 * (statistics.success_rate || 98.7) / 100)"
                      transform="rotate(-90 40 20)"/>
              <!-- 中心文字 -->
              <text x="40" y="24" text-anchor="middle" fill="#1a1a1a" font-size="10" font-weight="600">{{ (statistics.success_rate || 98.7).toFixed(1) }}%</text>
              <!-- 渐变定义 -->
              <defs>
                <linearGradient id="successGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#34c759;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#30d158;stop-opacity:1" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>

        <div class="data-card animate-slide-in-left" style="animation-delay: 0.3s">
          <div class="card-header">
            <div class="card-icon orange">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="data-value">{{ statistics.avg_response_time || 42 }}ms</div>
          <div class="data-label">平均响应时间</div>
          <div class="data-trend negative">
            <span class="trend-icon">📊</span>
            +5ms
          </div>
          <!-- 响应时间图表 -->
          <div class="response-bars">
            <div class="bar" v-for="(height, index) in responseTimeData" :key="index" :style="{ height: height + '%', backgroundColor: getBarColor(height) }"></div>
          </div>
        </div>

        <div class="data-card animate-slide-in-left" style="animation-delay: 0.4s">
          <div class="card-header">
            <div class="card-icon purple">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M9 9h6v6H9z" fill="currentColor"/>
              </svg>
            </div>
          </div>
          <div class="data-value">{{ statistics.error_count || 3 }}</div>
          <div class="data-label">错误次数</div>
          <div class="data-trend positive">
            <span class="trend-icon">📉</span>
            -2
          </div>
          <!-- 错误状态指示器 -->
          <div class="error-indicators">
            <svg viewBox="0 0 100 40" class="error-svg">
              <!-- 定义渐变 -->
              <defs>
                <linearGradient id="errorGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#ff3b30;stop-opacity:0.8" />
                  <stop offset="100%" style="stop-color:#ff6b35;stop-opacity:0.8" />
                </linearGradient>
              </defs>
              <!-- 错误柱状图 -->
              <rect x="10" y="25" width="8" height="10" rx="2" :fill="(statistics.error_count || 3) >= 1 ? 'url(#errorGradient)' : '#f0f0f0'"/>
              <rect x="25" y="20" width="8" height="15" rx="2" :fill="(statistics.error_count || 3) >= 2 ? 'url(#errorGradient)' : '#f0f0f0'"/>
              <rect x="40" y="15" width="8" height="20" rx="2" :fill="(statistics.error_count || 3) >= 3 ? 'url(#errorGradient)' : '#f0f0f0'"/>
              <rect x="55" y="28" width="8" height="7" rx="2" fill="#f0f0f0"/>
              <rect x="70" y="22" width="8" height="13" rx="2" fill="#f0f0f0"/>
              <!-- 基线 -->
              <line x1="5" y1="35" x2="95" y2="35" stroke="#e0e0e0" stroke-width="1"/>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- 简化的数据展示区域 -->
    <div class="data-visualization-section">
      <h2 class="section-title animate-slide-in-left">
        <span class="title-icon">📈</span>
        数据分析概览
      </h2>
      <div class="data-grid">
        <!-- 手势使用排行 -->
        <div class="data-showcase animate-slide-in-left" style="animation-delay: 0.1s">
          <div class="showcase-header">
            <h3>🏆 手势使用排行</h3>
            <span class="showcase-subtitle">最受欢迎的手势</span>
          </div>
          <div class="gesture-ranking">
            <div class="rank-item" v-for="(gesture, index) in gestureRanking" :key="index">
              <span class="rank-number">{{ index + 1 }}</span>
              <span class="rank-emoji">{{ gesture.emoji }}</span>
              <span class="rank-name">{{ gesture.name }}</span>
              <span class="rank-count">{{ gesture.count }}</span>
              <div class="rank-bar">
                <div class="rank-fill" :style="{ width: gesture.percentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 实时性能指标 -->
        <div class="data-showcase animate-slide-in-left" style="animation-delay: 0.2s">
          <div class="showcase-header">
            <h3>⚡ 实时性能指标</h3>
            <span class="showcase-subtitle">系统运行状态</span>
          </div>
          <div class="performance-metrics">
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-name">CPU使用率</span>
                <span class="metric-value">45%</span>
              </div>
              <div class="metric-bar">
                <div class="metric-fill" style="width: 45%; background: linear-gradient(90deg, #34c759, #30d158);"></div>
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-name">内存占用</span>
                <span class="metric-value">2.1GB</span>
              </div>
              <div class="metric-bar">
                <div class="metric-fill" style="width: 62%; background: linear-gradient(90deg, #ff9500, #ff6b35);"></div>
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-name">网络延迟</span>
                <span class="metric-value">12ms</span>
              </div>
              <div class="metric-bar">
                <div class="metric-fill" style="width: 15%; background: linear-gradient(90deg, #667eea, #764ba2);"></div>
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-name">识别准确率</span>
                <span class="metric-value">98.7%</span>
              </div>
              <div class="metric-bar">
                <div class="metric-fill" style="width: 98.7%; background: linear-gradient(90deg, #34c759, #30d158);"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 手势控制状态面板 -->
    <div class="gesture-control-section">
      <h2 class="section-title animate-slide-in-left">
        <span class="title-icon">🎛️</span>
        手势控制
      </h2>
      <div class="gesture-control-card animate-slide-in-left" style="animation-delay: 0.1s">
        <div class="gesture-control-header">
          <div class="gesture-control-info">
            <h3>控制状态</h3>
            <p>使用 ✌️ VICTORY 手势切换控制状态</p>
          </div>
          <div class="gesture-control-status" :class="{ 'enabled': gestureStatus?.gesture_control_enabled, 'disabled': !gestureStatus?.gesture_control_enabled }">
            <div class="status-indicator"></div>
            <span class="status-text">{{ gestureStatus?.gesture_control_enabled ? '已启用' : '已禁用' }}</span>
          </div>
        </div>
        <div class="gesture-control-actions">
          <button
            class="toggle-btn"
            @click="toggleGestureControl"
            :disabled="loading"
            :class="{ 'enabled': gestureStatus?.gesture_control_enabled }"
          >
            <span class="btn-icon">{{ gestureStatus?.gesture_control_enabled ? '🛑' : '▶️' }}</span>
            <span class="btn-text">{{ gestureStatus?.gesture_control_enabled ? '禁用控制' : '启用控制' }}</span>
          </button>
          <button
            class="sync-btn"
            @click="syncGestureStatus"
            :disabled="loading"
          >
            <span class="btn-icon">🔄</span>
            <span class="btn-text">同步状态</span>
          </button>
        </div>
        <div class="gesture-control-footer">
          <div class="control-tip">
            <span class="tip-icon">💡</span>
            <span class="tip-text">当前控制手势：{{ gestureStatus?.control_toggle_gesture?.toUpperCase() || 'VICTORY' }}</span>
          </div>
          <div class="last-sync">
            上次同步：{{ formatTime(gestureStatus?.last_update) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 系统状态面板 -->
    <div class="system-section">
      <div class="section-header">
        <h2 class="section-title animate-slide-in-left">
          <span class="title-icon">⚡</span>
          系统状态
        </h2>
        <button class="refresh-btn animate-slide-in-right" @click="refreshSystemStatus" :disabled="loading">
          <div v-if="!loading" class="refresh-icon">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M1.5 8a6.5 6.5 0 0 1 10.5-5.1L12 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M14.5 8a6.5 6.5 0 0 1-10.5 5.1L4 11.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 4.5h3v3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 11.5H4v-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div v-else class="loading-spinner small"></div>
          <span>{{ loading ? '刷新中...' : '刷新' }}</span>
        </button>
      </div>

      <div class="system-grid">
        <div class="glass-card system-card animate-slide-in-left" v-for="(status, key) in systemStatus" :key="key">
          <div class="system-card-header">
            <div class="system-icon" :class="getSystemIconClass(key)">
              <span class="system-emoji">{{ getSystemEmoji(key) }}</span>
            </div>
            <div class="system-status">
              <div class="status-indicator" :class="status === 'healthy' ? 'online' : 'offline'"></div>
              <span class="status-text">{{ status === 'healthy' ? '运行中' : '离线' }}</span>
            </div>
          </div>
          <div class="system-info">
            <h3>{{ getStatusName(key) }}</h3>
            <p class="system-desc">{{ getStatusText(status) }}</p>
            <!-- 状态进度条 -->
            <div class="status-progress">
              <div class="progress-bar" :class="status" :style="{ width: getStatusProgress(status) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="actions-section">
      <h2 class="section-title animate-slide-in-left">
        <span class="title-icon">🚀</span>
        快速开始
      </h2>
      <div class="action-grid">
        <div class="action-card animate-slide-in-left" style="animation-delay: 0.1s" @click="goToConfig">
          <div class="action-icon gradient-primary">
            <span class="action-emoji">⚙️</span>
          </div>
          <h3>配置管理</h3>
          <p>自定义手势映射和系统参数</p>
          <div class="action-arrow">
            <span>→</span>
          </div>
        </div>

        <div class="action-card animate-slide-in-left" style="animation-delay: 0.2s" @click="goToMonitor">
          <div class="action-icon gradient-success">
            <span class="action-emoji">📊</span>
          </div>
          <h3>实时监控</h3>
          <p>查看系统性能和识别状态</p>
          <div class="action-arrow">
            <span>→</span>
          </div>
        </div>

        <div class="action-card animate-slide-in-left" style="animation-delay: 0.3s" @click="goToTraining">
          <div class="action-icon gradient-warning">
            <span class="action-emoji">🤚</span>
          </div>
          <h3>手势训练</h3>
          <p>训练和优化手势识别模型</p>
          <div class="action-arrow">
            <span>→</span>
          </div>
        </div>

        <div class="action-card animate-slide-in-left" style="animation-delay: 0.4s" @click="goToLogs">
          <div class="action-icon gradient-info">
            <span class="action-emoji">📋</span>
          </div>
          <h3>系统日志</h3>
          <p>查看详细的操作记录和错误信息</p>
          <div class="action-arrow">
            <span>→</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMonitorStore } from '@/stores/monitor'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'

const router = useRouter()
const monitorStore = useMonitorStore()

// 响应式数据
const loading = ref(false)

// 计算属性
const systemStatus = computed(() => monitorStore.systemStatus)
const performance = computed(() => monitorStore.performance)
const statistics = computed(() => monitorStore.statistics)
const gestureStatus = computed(() => monitorStore.gestureStatus)

// 响应时间数据
const responseTimeData = ref([30, 45, 35, 50, 40, 25, 35, 45, 30, 40, 35, 50])

// 手势排行榜数据
const gestureRanking = ref([
  { emoji: '👆', name: 'POINT_UP', count: 335, percentage: 100 },
  { emoji: '👍', name: 'THUMBS_UP', count: 310, percentage: 92 },
  { emoji: '✋', name: 'PALM', count: 265, percentage: 79 },
  { emoji: '✌️', name: 'VICTORY', count: 234, percentage: 70 },
  { emoji: '🤘', name: 'ROCK_SIGN', count: 148, percentage: 44 },
  { emoji: '👌', name: 'OK_SIGN', count: 135, percentage: 40 },
  { emoji: '🤙', name: 'CALL_ME', count: 114, percentage: 34 },
  { emoji: '✊', name: 'FIST', count: 98, percentage: 29 }
])

// 方法
const refreshSystemStatus = async () => {
  loading.value = true
  try {
    await monitorStore.loadAllMonitoringData()
    // ElMessage.success('系统状态已刷新')
  } catch (error) {
    // ElMessage.error('刷新系统状态失败')
    console.error('刷新失败:', error)
  } finally {
    loading.value = false
  }
}

const getStatusName = (key) => {
  const names = {
    backend: '后端服务',
    ai_service: 'AI服务',
    database: '数据库',
    agent: 'Agent代理'
  }
  return names[key] || key
}

const getStatusText = (status) => {
  const texts = {
    healthy: '运行正常',
    warning: '性能警告',
    error: '连接错误',
    unknown: '状态未知'
  }
  return texts[status] || '未知'
}

const getSystemIcon = (key) => {
  const icons = {
    backend: 'Server',
    ai_service: 'Cpu',
    database: 'Database',
    agent: 'User'
  }
  return icons[key] || 'Circle'
}


// 辅助方法
const getBarColor = (height) => {
  if (height < 30) return '#34c759'
  if (height < 50) return '#ff9500'
  return '#ff3b30'
}

const getSystemEmoji = (key) => {
  const emojis = {
    backend: '🖥️',
    ai_service: '🤖',
    database: '🗄️',
    agent: '👤'
  }
  return emojis[key] || '⚪'
}

const getSystemIconClass = (key) => {
  const classes = {
    backend: 'icon-backend',
    ai_service: 'icon-ai',
    database: 'icon-database',
    agent: 'icon-agent'
  }
  return classes[key] || 'icon-default'
}

const getStatusProgress = (status) => {
  return status === 'healthy' ? 100 : 30
}

// 手势控制方法
const toggleGestureControl = async () => {
  try {
    loading.value = true
    const response = await fetch('/api/monitor/gesture/control', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      const data = await response.json()
      ElMessage.success(data.message)
      // 刷新状态
      await monitorStore.fetchGestureStatus()
    } else {
      ElMessage.error('切换手势控制失败')
    }
  } catch (error) {
    console.error('切换手势控制失败:', error)
    ElMessage.error('切换手势控制失败')
  } finally {
    loading.value = false
  }
}

const syncGestureStatus = async () => {
  try {
    loading.value = true
    await monitorStore.fetchGestureStatus()
    ElMessage.success('状态同步成功')
  } catch (error) {
    console.error('同步状态失败:', error)
    ElMessage.error('同步状态失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return '未知'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 快捷操作方法
const goToConfig = () => router.push('/config')
const goToMonitor = () => router.push('/monitor')
const goToTraining = () => router.push('/training')
const goToLogs = () => router.push('/logs')

// 生命周期
onMounted(async () => {
  await refreshSystemStatus()
  await monitorStore.fetchGestureStatus()
})
</script>

<style scoped>
@import '@/styles/modern.css';

.modern-dashboard {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* 英雄区域 */
.hero-section {
  padding: 120px 20px 80px 20px;
  background: radial-gradient(ellipse at top center, rgba(102, 126, 234, 0.05) 0%, transparent 50%),
              linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border-bottom: 1px solid var(--border-primary);
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 60px;
  position: relative;
  z-index: 1;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 30px;
}

.title-content {
  flex: 1;
}

/* 品牌头部 */
.brand-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: flex;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 50%, rgba(255, 255, 255, 0.8) 100%);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  pointer-events: none;
}

.brand-logo {
  position: relative;
  display: inline-block;
  pointer-events: auto;
  cursor: pointer;
}

.brand-logo-image {
  width: 120px;
  height: 120px;
  object-fit: contain;
  filter: drop-shadow(0 8px 32px rgba(102, 126, 234, 0.4));
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.brand-logo:hover .brand-logo-image {
  transform: scale(1.1) rotate(5deg);
  filter: drop-shadow(0 12px 48px rgba(102, 126, 234, 0.6));
}

.brand-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.4s ease;
  animation: pulse-glow 3s ease-in-out infinite;
}

.brand-logo:hover .brand-glow {
  opacity: 1;
}

@keyframes pulse-glow {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.1; }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fade-in-up 1s ease-out;
}

.hero-text h1 {
  font-size: 4rem;
  font-weight: 700;
  margin: 0 0 20px 0;
  color: var(--text-primary);
  line-height: 1.1;
  letter-spacing: -0.02em;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.hero-accent {
  display: block;
  font-size: 2rem;
  font-weight: 400;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-top: 10px;
  letter-spacing: 0.01em;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
  letter-spacing: 0.005em;
  line-height: 1.4;
}

.hero-visual {
  flex-shrink: 0;
}

.floating-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.floating-cards > div {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 24px;
  box-shadow: var(--glass-shadow);
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.floating-cards > div::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-primary);
}

.floating-cards > div:hover {
  transform: translateY(-5px);
  box-shadow: var(--glass-shadow-hover);
}

.hand-icon, .ai-icon, .control-icon {
  font-size: 2rem;
  margin-bottom: 8px;
  display: block;
}

.gesture-label, .ai-label, .control-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.animate-float-delay-1 { animation: float 3s ease-in-out infinite; animation-delay: 0s; }
.animate-float-delay-2 { animation: float 3s ease-in-out infinite; animation-delay: 0.5s; }
.animate-float-delay-3 { animation: float 3s ease-in-out infinite; animation-delay: 1s; }

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 统计区域 */
.stats-section {
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 40px;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  line-height: 1.2;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 2rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.modern-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 60px;
}

.data-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 32px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s var(--transition-smooth);
  box-shadow: var(--glass-shadow);
  color: var(--text-primary);
}

.data-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-primary);
}

.data-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--glass-shadow-hover);
  border-color: var(--border-accent);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.card-icon.blue { background: var(--gradient-info); }
.card-icon.green { background: var(--gradient-success); }
.card-icon.orange { background: var(--gradient-warning); }
.card-icon.purple { background: var(--gradient-primary); }

.data-value {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 16px 0;
  line-height: 1;
  letter-spacing: -0.01em;
}

.data-label {
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.data-trend {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
  display: inline-block;
}

.data-trend {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.data-trend.positive {
  background: rgba(52, 199, 89, 0.2);
  color: var(--accent-green);
}

.data-trend.negative {
  background: rgba(255, 59, 48, 0.2);
  color: var(--accent-red);
}

.trend-icon {
  font-size: 0.75rem;
}

/* 迷你图表样式 */
.mini-chart, .progress-ring, .response-bars, .error-indicators {
  margin-top: 16px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trend-svg, .progress-svg, .error-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.response-bars {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.bar {
  flex: 1;
  min-height: 4px;
  border-radius: 2px;
  transition: all 0.3s ease;
}


/* 数据可视化区域 */
.data-visualization-section {
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 32px;
}

.data-showcase {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 32px;
  transition: all 0.3s ease;
  box-shadow: var(--glass-shadow);
}

.data-showcase:hover {
  transform: translateY(-5px);
  box-shadow: var(--glass-shadow-hover);
}

.showcase-header {
  margin-bottom: 24px;
}

.showcase-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.showcase-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 手势排行榜 */
.gesture-ranking {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.rank-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateX(4px);
}

.rank-number {
  width: 24px;
  height: 24px;
  background: var(--gradient-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
}

.rank-emoji {
  font-size: 1.25rem;
}

.rank-name {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.rank-count {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-right: 12px;
}

.rank-bar {
  width: 80px;
  height: 6px;
  background: var(--border-secondary);
  border-radius: 3px;
  overflow: hidden;
}

.rank-fill {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* 性能指标 */
.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.metric-value {
  font-size: 0.875rem;
  font-weight: bold;
  color: var(--accent-blue);
}

.metric-bar {
  height: 8px;
  background: var(--border-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 系统状态 */
.system-section {
  padding: 80px 20px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-primary);
}

.section-header {
  max-width: 1200px;
  margin: 0 auto 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.refresh-btn {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 12px 20px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.system-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.system-card {
  padding: 24px;
  transition: all 0.3s ease;
}

.system-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
}

.system-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.system-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  transition: all 0.3s ease;
}

.system-emoji {
  font-size: 1.5rem;
  filter: grayscale(0%);
}

.icon-backend { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.icon-ai { background: linear-gradient(135deg, #34c759 0%, #30d158 100%); }
.icon-database { background: linear-gradient(135deg, #ff9500 0%, #ff6b35 100%); }
.icon-agent { background: linear-gradient(135deg, #5ac8fa 0%, #007aff 100%); }

.system-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.system-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.system-desc {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.status-progress {
  height: 4px;
  background: var(--border-secondary);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-bar {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.progress-bar.healthy {
  background: var(--accent-green);
  width: 100%;
}

.progress-bar.warning {
  background: var(--accent-orange);
  width: 60%;
}

.progress-bar.error {
  background: var(--accent-red);
  width: 30%;
}

/* 手势控制状态 */
.gesture-control-section {
  padding: 60px 20px;
  max-width: 800px;
  margin: 0 auto;
}

.gesture-control-card {
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-primary);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 8px 32px var(--shadow-light);
  transition: all 0.3s ease;
}

.gesture-control-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 48px var(--shadow-medium);
}

.gesture-control-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.gesture-control-info h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.gesture-control-info p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0;
  line-height: 1.4;
}

.gesture-control-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.gesture-control-status.enabled {
  background: var(--accent-green-light);
  color: var(--accent-green);
}

.gesture-control-status.disabled {
  background: var(--accent-red-light);
  color: var(--accent-red);
}

.gesture-control-status .status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

.gesture-control-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.toggle-btn,
.sync-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.toggle-btn:hover,
.sync-btn:hover {
  background: var(--bg-hover);
  transform: translateY(-1px);
}

.toggle-btn:disabled,
.sync-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.toggle-btn.enabled {
  background: var(--accent-red-light);
  color: var(--accent-red);
  border-color: var(--accent-red-light);
}

.toggle-btn.enabled:hover {
  background: var(--accent-red);
  color: white;
}

.sync-btn {
  background: var(--accent-blue-light);
  color: var(--accent-blue);
  border-color: var(--accent-blue-light);
}

.sync-btn:hover {
  background: var(--accent-blue);
  color: white;
}

.btn-icon {
  font-size: 1rem;
}

.gesture-control-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-primary);
}

.control-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.813rem;
}

.tip-icon {
  font-size: 1rem;
}

.last-sync {
  color: var(--text-tertiary);
  font-size: 0.75rem;
}

/* 快捷操作 */
.actions-section {
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.action-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 32px;
  cursor: pointer;
  transition: all 0.3s var(--transition-smooth);
  position: relative;
  overflow: hidden;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.3);
}

.action-card:hover::before {
  opacity: 1;
}

.action-icon {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 20px;
  font-size: 1.8rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.action-emoji {
  font-size: 2rem;
  filter: grayscale(0%);
}

.gradient-primary { background: var(--gradient-primary); }
.gradient-success { background: var(--gradient-success); }
.gradient-warning { background: var(--gradient-warning); }
.gradient-info { background: var(--gradient-info); }

.action-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.action-card p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.action-arrow {
  color: var(--text-secondary);
  transition: all 0.3s ease;
  display: inline-block;
}

.action-card:hover .action-arrow {
  color: var(--accent-blue);
  transform: translateX(4px);
}

/* 小型加载动画 */
.loading-spinner.small {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-content {
    flex-direction: column;
    text-align: center;
    gap: 40px;
  }

  .title-container {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .brand-header {
    padding: 15px;
  }

  .brand-logo-image {
    width: 80px;
    height: 80px;
  }

  .brand-glow {
    width: 100px;
    height: 100px;
  }

  .hero-section {
    padding: 100px 16px 60px 16px;
  }

  .hero-text h1 {
    font-size: 3rem;
  }

  .hero-accent {
    font-size: 1.5rem;
  }

  .floating-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .section-title {
    font-size: 2rem;
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }

  .section-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }

  .modern-grid,
  .system-grid,
  .action-grid,
  .charts-grid,
  .data-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .data-card,
  .system-card,
  .action-card,
  .chart-card,
  .data-showcase {
    padding: 24px;
  }

  .data-grid,
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 60px 16px;
  }

  .stats-section,
  .system-section,
  .actions-section {
    padding: 60px 16px;
  }

  .hero-text h1 {
    font-size: 2.5rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .data-value {
    font-size: 2.5rem;
  }
}
</style>