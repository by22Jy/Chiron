<template>
  <div class="dashboard">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <div class="stat-card">
          <div class="stat-icon">
            <el-icon color="#409EFF"><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.gesture_count }}</div>
            <div class="stat-label">手势识别次数</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <div class="stat-card">
          <div class="stat-icon">
            <el-icon color="#67C23A"><SuccessFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ (statistics.success_rate * 100).toFixed(1) }}%</div>
            <div class="stat-label">识别成功率</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <div class="stat-card">
          <div class="stat-icon">
            <el-icon color="#E6A23C"><Timer /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.avg_response_time }}ms</div>
            <div class="stat-label">平均响应时间</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <div class="stat-card">
          <div class="stat-icon">
            <el-icon color="#F56C6C"><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.error_count }}</div>
            <div class="stat-label">错误次数</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="main-content">
      <!-- 系统状态 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
        <el-card class="system-status-card">
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
              <el-button
                type="text"
                size="small"
                @click="refreshSystemStatus"
                :loading="loading"
              >
                刷新
              </el-button>
            </div>
          </template>

          <div class="status-list">
            <div class="status-item" v-for="(status, key) in systemStatus" :key="key">
              <div class="status-info">
                <span class="status-name">{{ getStatusName(key) }}</span>
                <el-tag
                  :type="status === 'healthy' ? 'success' : status === 'warning' ? 'warning' : 'danger'"
                  size="small"
                >
                  {{ getStatusText(status) }}
                </el-tag>
              </div>
              <el-icon :color="status === 'healthy' ? '#67C23A' : '#F56C6C'">
                <CircleCheck v-if="status === 'healthy'" />
                <Warning v-else-if="status === 'warning'" />
                <CircleClose v-else />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 性能监控 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
        <el-card class="performance-card">
          <template #header>
            <div class="card-header">
              <span>性能监控</span>
            </div>
          </template>

          <div class="performance-metrics">
            <div class="metric-item">
              <div class="metric-label">CPU使用率</div>
              <el-progress
                :percentage="performance.cpu_usage"
                :color="getProgressColor(performance.cpu_usage)"
                :show-text="true"
              />
            </div>

            <div class="metric-item">
              <div class="metric-label">内存使用率</div>
              <el-progress
                :percentage="performance.memory_usage"
                :color="getProgressColor(performance.memory_usage)"
                :show-text="true"
              />
            </div>

            <div class="metric-item">
              <div class="metric-label">网络上传</div>
              <div class="metric-value">{{ formatBytes(performance.network_in) }}/s</div>
            </div>

            <div class="metric-item">
              <div class="metric-label">网络下载</div>
              <div class="metric-value">{{ formatBytes(performance.network_out) }}/s</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 手势识别状态 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
        <el-card class="gesture-status-card">
          <template #header>
            <div class="card-header">
              <span>手势识别状态</span>
              <el-tag
                :type="gestureStatus.is_detecting ? 'success' : 'info'"
                size="small"
              >
                {{ gestureStatus.is_detecting ? '识别中' : '等待中' }}
              </el-tag>
            </div>
          </template>

          <div class="gesture-info">
            <div class="current-gesture">
              <div class="gesture-label">当前手势</div>
              <div class="gesture-value">
                {{ gestureStatus.current_gesture || '无' }}
              </div>
            </div>

            <div class="confidence">
              <div class="confidence-label">置信度</div>
              <el-progress
                :percentage="Math.round(gestureStatus.confidence * 100)"
                color="#409EFF"
                :show-text="true"
              />
            </div>

            <div class="last-update">
              <div class="update-label">最后更新</div>
              <div class="update-value">
                {{ formatTime(gestureStatus.last_update) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>

          <div class="action-buttons">
            <el-button type="primary" @click="goToConfig">
              <el-icon><Setting /></el-icon>
              配置管理
            </el-button>

            <el-button type="success" @click="goToMonitor">
              <el-icon><View /></el-icon>
              实时监控
            </el-button>

            <el-button type="warning" @click="goToTraining">
              <el-icon><Star /></el-icon>
              手势训练
            </el-button>

            <el-button type="info" @click="goToLogs">
              <el-icon><Document /></el-icon>
              系统日志
            </el-button>

            <el-button type="danger" @click="testConnection">
              <el-icon><Connection /></el-icon>
              连接测试
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
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
    ElMessage.success('系统状态已刷新')
  } catch (error) {
    ElMessage.error('刷新系统状态失败')
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
    healthy: '正常',
    warning: '警告',
    error: '错误',
    unknown: '未知'
  }
  return texts[status] || '未知'
}

const getProgressColor = (percentage) => {
  if (percentage < 50) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTime = (timestamp) => {
  if (!timestamp) return '无'
  return new Date(timestamp).toLocaleTimeString()
}

// 快捷操作方法
const goToConfig = () => router.push('/config')
const goToMonitor = () => router.push('/monitor')
const goToTraining = () => router.push('/training')
const goToLogs = () => router.push('/logs')

const testConnection = async () => {
  try {
    await monitorStore.loadAllMonitoringData()
    ElMessage.success('所有服务连接正常')
  } catch (error) {
    ElMessage.error('连接测试失败，请检查服务状态')
  }
}

// 生命周期
onMounted(async () => {
  await refreshSystemStatus()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 8px;
  margin-right: 15px;
}

.stat-icon .el-icon {
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.main-content {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-list {
  space-y: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.status-item:last-child {
  border-bottom: none;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-name {
  font-weight: 500;
  color: #303133;
}

.performance-metrics {
  space-y: 20px;
}

.metric-item {
  margin-bottom: 20px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.gesture-info {
  space-y: 20px;
}

.gesture-label,
.confidence-label,
.update-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.gesture-value,
.update-value {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-cards .el-col {
    margin-bottom: 15px;
  }

  .action-buttons {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .stat-card {
    padding: 15px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    margin-right: 10px;
  }

  .stat-icon .el-icon {
    font-size: 20px;
  }

  .stat-value {
    font-size: 20px;
  }
}
</style>