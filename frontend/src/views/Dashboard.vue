<template>
  <div class="modern-dashboard">
    <!-- 英雄区域 -->
    <div class="hero-section animate-slide-in-top">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            YOLO-LLM
            <span class="hero-accent">手势控制平台</span>
          </h1>
          <p class="hero-subtitle">基于人工智能的下一代手势交互体验</p>
        </div>
        <div class="hero-visual">
          <div class="floating-card animate-float">
            <div class="card-icon">
              <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <circle cx="32" cy="32" r="30" stroke="url(#gradient1)" stroke-width="2"/>
                <path d="M20 32 L28 40 L44 24" stroke="url(#gradient1)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                <defs>
                  <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#667eea"/>
                    <stop offset="100%" style="stop-color:#764ba2"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div class="status-pulse"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时数据统计 -->
    <div class="stats-section">
      <h2 class="section-title animate-slide-in-left">实时性能监控</h2>
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
          <div class="data-value">{{ statistics.gesture_count || 1,234 }}</div>
          <div class="data-label">手势识别次数</div>
          <div class="data-trend positive">+12.5%</div>
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
          <div class="data-value">{{ (statistics.success_rate).toFixed(1) || 98.7 }}%</div>
          <div class="data-label">识别成功率</div>
          <div class="data-trend positive">+2.3%</div>
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
          <div class="data-trend negative">+5ms</div>
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
          <div class="data-trend positive">-2</div>
        </div>
      </div>
    </div>

    <!-- 系统状态面板 -->
    <div class="system-section">
      <div class="section-header">
        <h2 class="section-title animate-slide-in-left">系统状态</h2>
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
            <div class="system-icon">
              <component :is="getSystemIcon(key)" />
            </div>
            <div class="system-status">
              <div class="status-indicator" :class="status === 'healthy' ? 'online' : 'offline'"></div>
            </div>
          </div>
          <div class="system-info">
            <h3>{{ getStatusName(key) }}</h3>
            <p class="system-desc">{{ getStatusText(status) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="actions-section">
      <h2 class="section-title animate-slide-in-left">快速开始</h2>
      <div class="action-grid">
        <div class="action-card animate-slide-in-left" style="animation-delay: 0.1s" @click="goToConfig">
          <div class="action-icon gradient-primary">
            <Setting />
          </div>
          <h3>配置管理</h3>
          <p>自定义手势映射和系统参数</p>
          <div class="action-arrow">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <div class="action-card animate-slide-in-left" style="animation-delay: 0.2s" @click="goToMonitor">
          <div class="action-icon gradient-success">
            <View />
          </div>
          <h3>实时监控</h3>
          <p>查看系统性能和识别状态</p>
          <div class="action-arrow">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <div class="action-card animate-slide-in-left" style="animation-delay: 0.3s" @click="goToTraining">
          <div class="action-icon gradient-warning">
            <Star />
          </div>
          <h3>手势训练</h3>
          <p>训练和优化手势识别模型</p>
          <div class="action-arrow">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <div class="action-card animate-slide-in-left" style="animation-delay: 0.4s" @click="goToLogs">
          <div class="action-icon gradient-info">
            <Document />
          </div>
          <h3>系统日志</h3>
          <p>查看详细的操作记录和错误信息</p>
          <div class="action-arrow">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
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
import {
  TrendCharts,
  SuccessFilled,
  Timer,
  Warning,
  CircleCheck,
  CircleClose,
  Setting,
  View,
  Document,
  Connection,
  Star
} from '@element-plus/icons-vue'

const router = useRouter()
const monitorStore = useMonitorStore()

// 响应式数据
const loading = ref(false)

// 计算属性
const systemStatus = computed(() => monitorStore.systemStatus)
const performance = computed(() => monitorStore.performance)
const statistics = computed(() => monitorStore.statistics)
const gestureStatus = computed(() => monitorStore.gestureStatus)

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

// 快捷操作方法
const goToConfig = () => router.push('/config')
const goToMonitor = () => router.push('/monitor')
const goToTraining = () => router.push('/training')
const goToLogs = () => router.push('/logs')

// 生命周期
onMounted(async () => {
  await refreshSystemStatus()
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
  padding: 80px 20px;
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

.floating-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 40px;
  box-shadow: var(--glass-shadow);
  position: relative;
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-pulse {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 16px;
  height: 16px;
  background: var(--accent-green);
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(52, 199, 89, 0.6);
  animation: pulse 2s ease-in-out infinite;
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

.data-trend.positive {
  background: rgba(52, 199, 89, 0.2);
  color: var(--accent-green);
}

.data-trend.negative {
  background: rgba(255, 59, 48, 0.2);
  color: var(--accent-red);
}

/* 系统状态 */
.system-section {
  padding: 80px 20px;
  background: var(--bg-secondary);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
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
  width: 40px;
  height: 40px;
  background: var(--gradient-primary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.system-info h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.system-desc {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0;
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
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 20px;
  font-size: 24px;
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

  .hero-text h1 {
    font-size: 3rem;
  }

  .hero-accent {
    font-size: 1.5rem;
  }

  .section-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }

  .modern-grid,
  .system-grid,
  .action-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .data-card,
  .system-card,
  .action-card {
    padding: 24px;
  }

  .floating-card {
    width: 160px;
    height: 160px;
    padding: 30px;
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