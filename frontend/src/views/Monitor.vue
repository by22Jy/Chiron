<template>
  <div class="monitor-page">
    <!-- 系统状态概览 -->
    <el-row :gutter="20" class="status-overview">
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="status-card" :class="getSystemHealthClass()">
          <div class="status-icon">
            <el-icon size="32"><Monitor /></el-icon>
          </div>
          <div class="status-content">
            <div class="status-title">系统健康</div>
            <div class="status-value">{{ systemHealth.overall === 'healthy' ? '正常' : '警告' }}</div>
            <div class="status-detail">{{ systemHealth.healthyServices }}/{{ systemHealth.totalServices }}</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="status-card">
          <div class="status-icon">
            <el-icon size="32" color="#67C23A"><TrendCharts /></el-icon>
          </div>
          <div class="status-content">
            <div class="status-title">性能等级</div>
            <div class="status-value">{{ getPerformanceLevelText() }}</div>
            <div class="status-detail">CPU: {{ performance.cpu_usage }}%</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="status-card">
          <div class="status-icon">
            <el-icon size="32" color="#E6A23C"><Timer /></el-icon>
          </div>
          <div class="status-content">
            <div class="status-title">响应时间</div>
            <div class="status-value">{{ statistics.avg_response_time }}ms</div>
            <div class="status-detail">成功率: {{ (statistics.success_rate * 100).toFixed(1) }}%</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="status-card">
          <div class="status-icon">
            <el-icon size="32" color="#409EFF"><DataLine /></el-icon>
          </div>
          <div class="status-content">
            <div class="status-title">请求统计</div>
            <div class="status-value">{{ statistics.total_requests }}</div>
            <div class="status-detail">错误: {{ statistics.error_count }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细监控区域 -->
    <el-row :gutter="20" class="monitor-details">
      <!-- 系统服务状态 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="monitor-card" header="系统服务状态">
          <div class="service-status">
            <div v-for="(status, key) in systemStatus" :key="key" class="service-item">
              <div class="service-info">
                <div class="service-name">{{ getServiceName(key) }}</div>
                <div class="service-status-text">{{ getStatusText(status) }}</div>
              </div>
              <el-icon :class="`status-icon-${status}`">
                <CircleCheck v-if="status === 'healthy'" />
                <Warning v-else-if="status === 'warning'" />
                <CircleClose v-else />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 性能监控 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="monitor-card" header="性能监控">
          <div class="performance-metrics">
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-label">CPU使用率</span>
                <span class="metric-value">{{ performance.cpu_usage }}%</span>
              </div>
              <el-progress
                :percentage="performance.cpu_usage"
                :color="getProgressColor(performance.cpu_usage)"
                :show-text="false"
              />
            </div>

            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-label">内存使用率</span>
                <span class="metric-value">{{ performance.memory_usage }}%</span>
              </div>
              <el-progress
                :percentage="performance.memory_usage"
                :color="getProgressColor(performance.memory_usage)"
                :show-text="false"
              />
            </div>

            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-label">GPU使用率</span>
                <span class="metric-value">{{ performance.gpu_usage }}%</span>
              </div>
              <el-progress
                :percentage="performance.gpu_usage"
                :color="getProgressColor(performance.gpu_usage)"
                :show-text="false"
              />
            </div>

            <div class="network-metrics">
              <div class="network-item">
                <el-icon><Upload /></el-icon>
                <span>上传: {{ formatBytes(performance.network_in) }}/s</span>
              </div>
              <div class="network-item">
                <el-icon><Download /></el-icon>
                <span>下载: {{ formatBytes(performance.network_out) }}/s</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 手势识别状态 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="monitor-card" header="手势识别状态">
          <div class="gesture-status">
            <div class="gesture-current">
              <div class="gesture-label">当前手势</div>
              <div class="gesture-value">
                <el-tag v-if="gestureStatus.current_gesture" type="success" size="large">
                  {{ gestureStatus.current_gesture }}
                </el-tag>
                <el-tag v-else type="info" size="large">无</el-tag>
              </div>
            </div>

            <div class="gesture-confidence">
              <div class="gesture-label">置信度</div>
              <el-progress
                :percentage="Math.round(gestureStatus.confidence * 100)"
                color="#409EFF"
                :show-text="true"
              />
            </div>

            <div class="gesture-info">
              <div class="info-item">
                <span class="info-label">检测状态:</span>
                <el-tag :type="gestureStatus.is_detecting ? 'success' : 'info'">
                  {{ gestureStatus.is_detecting ? '识别中' : '等待中' }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="info-label">最后更新:</span>
                <span>{{ formatTime(gestureStatus.last_update) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 统计信息 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="monitor-card" header="统计信息">
          <div class="statistics-info">
            <div class="stat-item">
              <div class="stat-number">{{ statistics.gesture_count }}</div>
              <div class="stat-label">手势识别次数</div>
            </div>

            <div class="stat-item">
              <div class="stat-number">{{ statistics.total_requests }}</div>
              <div class="stat-label">总请求数</div>
            </div>

            <div class="stat-item">
              <div class="stat-number">{{ statistics.error_count }}</div>
              <div class="stat-label">错误次数</div>
            </div>

            <div class="stat-item">
              <div class="stat-number">{{ (statistics.success_rate * 100).toFixed(1) }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>

          <div class="refresh-actions">
            <el-button @click="refreshAll" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
            <el-button type="primary" @click="startAutoRefresh" v-if="!autoRefresh">
              <el-icon><VideoPlay /></el-icon>
              自动刷新
            </el-button>
            <el-button type="warning" @click="stopAutoRefresh" v-else>
              <el-icon><VideoPause /></el-icon>
              停止刷新
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMonitorStore } from '@/stores/monitor'
import { ElMessage } from 'element-plus'
import {
  Monitor,
  TrendCharts,
  Timer,
  DataLine,
  CircleCheck,
  Warning,
  CircleClose,
  Upload,
  Download,
  Refresh,
  VideoPlay,
  VideoPause
} from '@element-plus/icons-vue'

const monitorStore = useMonitorStore()

// 响应式数据
const loading = ref(false)
const autoRefresh = ref(false)
let refreshTimer = null

// 计算属性
const systemStatus = computed(() => monitorStore.systemStatus)
const performance = computed(() => monitorStore.performance)
const statistics = computed(() => monitorStore.statistics)
const gestureStatus = computed(() => monitorStore.gestureStatus)
const systemHealth = computed(() => monitorStore.systemHealth)

// 方法
const getSystemHealthClass = () => {
  const health = systemHealth.value.overall
  return health === 'healthy' ? 'status-healthy' : health === 'warning' ? 'status-warning' : 'status-error'
}

const getPerformanceLevelText = () => {
  const level = monitorStore.performanceLevel
  const texts = {
    good: '良好',
    warning: '警告',
    critical: '严重'
  }
  return texts[level] || '未知'
}

const getProgressColor = (percentage) => {
  if (percentage < 50) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

const getServiceName = (key) => {
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

const refreshAll = async () => {
  loading.value = true
  try {
    await monitorStore.loadAllMonitoringData()
    ElMessage.success('监控数据已刷新')
  } catch (error) {
    ElMessage.error('刷新监控数据失败')
  } finally {
    loading.value = false
  }
}

const startAutoRefresh = () => {
  autoRefresh.value = true
  refreshTimer = setInterval(() => {
    monitorStore.loadAllMonitoringData().catch(console.error)
  }, 5000)
  ElMessage.info('已开启自动刷新')
}

const stopAutoRefresh = () => {
  autoRefresh.value = false
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  ElMessage.info('已停止自动刷新')
}

// 生命周期
onMounted(async () => {
  await refreshAll()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.monitor-page {
  padding: 0;
}

.status-overview {
  margin-bottom: 20px;
}

.status-card {
  height: 120px;
  display: flex;
  align-items: center;
  transition: transform 0.2s;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-icon {
  margin-right: 15px;
}

.status-content {
  flex: 1;
}

.status-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.status-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.status-detail {
  font-size: 12px;
  color: #C0C4CC;
}

.status-healthy {
  border-left: 4px solid #67C23A;
}

.status-warning {
  border-left: 4px solid #E6A23C;
}

.status-error {
  border-left: 4px solid #F56C6C;
}

.monitor-details {
  margin-bottom: 20px;
}

.service-status {
  max-height: 300px;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #F0F0F0;
}

.service-item:last-child {
  border-bottom: none;
}

.service-info {
  flex: 1;
}

.service-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.service-status-text {
  font-size: 14px;
  color: #909399;
}

.status-icon-healthy {
  color: #67C23A;
  font-size: 20px;
}

.status-icon-warning {
  color: #E6A23C;
  font-size: 20px;
}

.status-icon-error {
  color: #F56C6C;
  font-size: 20px;
}

.performance-metrics {
  max-height: 300px;
}

.metric-item {
  margin-bottom: 20px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
}

.metric-value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.network-metrics {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.network-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.gesture-status {
  max-height: 300px;
}

.gesture-current {
  margin-bottom: 20px;
}

.gesture-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.gesture-value {
  margin-bottom: 20px;
}

.gesture-confidence {
  margin-bottom: 20px;
}

.gesture-info {
  space-y: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.info-label {
  color: #606266;
}

.statistics-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.refresh-actions {
  text-align: center;
}

.refresh-actions .el-button {
  margin: 0 5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .status-overview .el-col {
    margin-bottom: 15px;
  }

  .monitor-details .el-col {
    margin-bottom: 15px;
  }

  .statistics-info {
    grid-template-columns: 1fr 1fr;
  }

  .network-metrics {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .status-card {
    height: 100px;
  }

  .status-value {
    font-size: 18px;
  }

  .stat-number {
    font-size: 20px;
  }
}
</style>