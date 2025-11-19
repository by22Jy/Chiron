<template>
  <div class="training-page">
    <!-- 训练概览 -->
    <el-card class="training-card" header="手势训练概览">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
          <div class="overview-item">
            <el-icon size="32" color="#409EFF"><Trophy /></el-icon>
            <div class="overview-content">
              <div class="overview-value">{{ trainingStats.total_sessions }}</div>
              <div class="overview-label">训练会话</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
          <div class="overview-item">
            <el-icon size="32" color="#67C23A"><SuccessFilled /></el-icon>
            <div class="overview-content">
              <div class="overview-value">{{ trainingStats.avg_accuracy }}%</div>
              <div class="overview-label">平均准确率</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
          <div class="overview-item">
            <el-icon size="32" color="#E6A23C"><Clock /></el-icon>
            <div class="overview-content">
              <div class="overview-value">{{ trainingStats.total_time }}min</div>
              <div class="overview-label">总训练时间</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
          <div class="overview-item">
            <el-icon size="32" color="#F56C6C"><Medal /></el-icon>
            <div class="overview-content">
              <div class="overview-value">{{ trainingStats.completed_gestures }}</div>
              <div class="overview-label">已掌握手势</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 手势演示区域 -->
    <el-row :gutter="20">
      <!-- 手势选择和演示 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="training-card" header="手势选择和演示">
          <div class="gesture-selection">
            <el-tabs v-model="selectedGestureType" type="border-card">
              <!-- 静态手势 -->
              <el-tab-pane label="静态手势" name="static">
                <div class="gesture-grid">
                  <div
                    v-for="gesture in staticGestures"
                    :key="gesture.code"
                    class="gesture-item"
                    :class="{ active: selectedGesture === gesture.code }"
                    @click="selectGesture(gesture)"
                  >
                    <div class="gesture-icon">
                      <el-icon size="24"><Hand /></el-icon>
                    </div>
                    <div class="gesture-info">
                      <div class="gesture-name">{{ gesture.name }}</div>
                      <div class="gesture-code">{{ gesture.code }}</div>
                    </div>
                    <div class="gesture-status" v-if="gesture.mastered">
                      <el-tag type="success" size="small">已掌握</el-tag>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <!-- 动态手势 -->
              <el-tab-pane label="动态手势" name="dynamic">
                <div class="gesture-grid">
                  <div
                    v-for="gesture in dynamicGestures"
                    :key="gesture.code"
                    class="gesture-item"
                    :class="{ active: selectedGesture === gesture.code }"
                    @click="selectGesture(gesture)"
                  >
                    <div class="gesture-icon">
                      <el-icon size="24"><ArrowRight v-if="gesture.code.includes('right')" />
                      <el-icon size="24"><ArrowLeft v-else-if="gesture.code.includes('left')" />
                      <el-icon size="24"><ArrowUp v-else-if="gesture.code.includes('up')" />
                      <el-icon size="24"><ArrowDown v-else /></el-icon>
                    </div>
                    <div class="gesture-info">
                      <div class="gesture-name">{{ gesture.name }}</div>
                      <div class="gesture-code">{{ gesture.code }}</div>
                    </div>
                    <div class="gesture-status" v-if="gesture.mastered">
                      <el-tag type="success" size="small">已掌握</el-tag>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- 手势说明 -->
          <div class="gesture-instructions" v-if="selectedGesture">
            <h4>{{ getGestureName(selectedGesture) }} 操作说明</h4>
            <div class="instruction-content">
              <p>{{ getGestureDescription(selectedGesture) }}</p>
              <div class="instruction-steps">
                <div v-for="(step, index) in getGestureSteps(selectedGesture)" :key="index" class="instruction-step">
                  <span class="step-number">{{ index + 1 }}</span>
                  <span class="step-text">{{ step }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 实时练习区域 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="training-card" header="实时练习">
          <div class="practice-area">
            <!-- 视频预览 -->
            <div class="video-preview">
              <video ref="videoRef" autoplay playsinline class="practice-video"></video>
              <div class="video-overlay">
                <div v-if="!isTraining" class="start-prompt">
                  <el-icon size="48"><VideoPlay /></el-icon>
                  <p>点击开始练习</p>
                </div>
                <div v-else class="recognition-status">
                  <div v-if="currentDetected" class="detected-gesture">
                    <el-tag type="success" size="large">{{ currentDetected }}</el-tag>
                    <div class="confidence">
                      置信度: {{ (currentConfidence * 100).toFixed(1) }}%
                    </div>
                  </div>
                  <div v-else class="waiting">
                    <el-icon class="pulse"><Loading /></el-icon>
                    <p>等待手势...</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 练习控制 -->
            <div class="practice-controls">
              <el-button
                type="primary"
                size="large"
                @click="toggleTraining"
                :loading="loading"
              >
                <el-icon v-if="!isTraining"><VideoPlay /></el-icon>
                <el-icon v-else><VideoPause /></el-icon>
                {{ isTraining ? '停止练习' : '开始练习' }}
              </el-button>

              <el-button @click="resetProgress" :disabled="!isTraining">
                <el-icon><Refresh /></el-icon>
                重置进度
              </el-button>
            </div>

            <!-- 进度统计 -->
            <div class="practice-stats" v-if="isTraining">
              <div class="stats-row">
                <div class="stat-item">
                  <div class="stat-value">{{ sessionStats.attempts }}</div>
                  <div class="stat-label">尝试次数</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ sessionStats.success }}</div>
                  <div class="stat-label">成功次数</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ getSessionAccuracy() }}%</div>
                  <div class="stat-label">当前准确率</div>
                </div>
              </div>

              <!-- 进度条 -->
              <div class="progress-section">
                <div class="progress-label">训练进度</div>
                <el-progress
                  :percentage="sessionStats.progress"
                  color="#409EFF"
                  :show-text="true"
                />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 训练历史 -->
    <el-card class="training-card" header="训练历史">
      <el-table :data="trainingHistory" style="width: 100%">
        <el-table-column prop="date" label="训练日期" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.date) }}
          </template>
        </el-table-column>
        <el-table-column prop="gesture" label="训练手势" width="150" />
        <el-table-column prop="duration" label="训练时长" width="120">
          <template #default="scope">
            {{ scope.row.duration }}分钟
          </template>
        </el-table-column>
        <el-table-column prop="attempts" label="尝试次数" width="120" />
        <el-table-column prop="success_rate" label="成功率" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.success_rate >= 80 ? 'success' : 'warning'">
              {{ scope.row.success_rate }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'completed' ? 'success' : 'info'">
              {{ scope.row.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" @click="viewDetails(scope.row)">查看详情</el-button>
            <el-button size="small" type="primary" @click="repeatTraining(scope.row)">重复训练</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Trophy,
  SuccessFilled,
  Clock,
  Medal,
  Hand,
  ArrowRight,
  ArrowLeft,
  ArrowUp,
  ArrowDown,
  VideoPlay,
  VideoPause,
  Refresh,
  Loading
} from '@element-plus/icons-vue'

// 响应式数据
const selectedGestureType = ref('static')
const selectedGesture = ref('')
const isTraining = ref(false)
const loading = ref(false)
const currentDetected = ref('')
const currentConfidence = ref(0)
const sessionStats = ref({
  attempts: 0,
  success: 0,
  progress: 0
})

// 手势数据
const staticGestures = ref([
  { code: 'POINT_UP', name: '指点向上', mastered: true },
  { code: 'THUMBS_UP', name: '点赞', mastered: true },
  { code: 'VICTORY', name: '胜利手势', mastered: false },
  { code: 'CLOSED_FIST', name: '握拳', mastered: true },
  { code: 'OPEN_PALM', name: '张开手掌', mastered: false }
])

const dynamicGestures = ref([
  { code: 'SWIPE_LEFT', name: '左滑', mastered: true },
  { code: 'SWIPE_RIGHT', name: '右滑', mastered: true },
  { code: 'SWIPE_UP', name: '上滑', mastered: false },
  { code: 'SWIPE_DOWN', name: '下滑', mastered: false }
])

const trainingStats = ref({
  total_sessions: 12,
  avg_accuracy: 85,
  total_time: 45,
  completed_gestures: 6
})

const trainingHistory = ref([
  {
    date: new Date('2024-01-15'),
    gesture: 'SWIPE_LEFT',
    duration: 15,
    attempts: 45,
    success_rate: 87,
    status: 'completed'
  },
  {
    date: new Date('2024-01-14'),
    gesture: 'POINT_UP',
    duration: 10,
    attempts: 32,
    success_rate: 92,
    status: 'completed'
  }
])

// 计算属性
const getSessionAccuracy = () => {
  if (sessionStats.value.attempts === 0) return 0
  return Math.round((sessionStats.value.success / sessionStats.value.attempts) * 100)
}

// 方法
const selectGesture = (gesture) => {
  selectedGesture.value = gesture.code
  ElMessage.info(`已选择手势: ${gesture.name}`)
}

const getGestureName = (code) => {
  const allGestures = [...staticGestures.value, ...dynamicGestures.value]
  const gesture = allGestures.find(g => g.code === code)
  return gesture?.name || code
}

const getGestureDescription = (code) => {
  const descriptions = {
    'POINT_UP': '食指向上指，用于表示确认或选择操作。',
    'THUMBS_UP': '竖起大拇指，表示赞同或确认。',
    'VICTORY': '伸出食指和中指呈V字形，表示胜利或和平。',
    'CLOSED_FIST': '握紧拳头，表示停止或取消操作。',
    'OPEN_PALM': '张开手掌，表示暂停或显示桌面。',
    'SWIPE_LEFT': '从右向左滑动，用于向左导航或切换。',
    'SWIPE_RIGHT': '从左向右滑动，用于向右导航或切换。',
    'SWIPE_UP': '从下向上滑动，用于向上滚动或翻页。',
    'SWIPE_DOWN': '从上向下滑动，用于向下滚动或翻页。'
  }
  return descriptions[code] || '暂无说明'
}

const getGestureSteps = (code) => {
  const steps = {
    'POINT_UP': ['伸出右手', '食指伸直向上', '其他手指自然弯曲', '保持稳定姿势'],
    'THUMBS_UP': ['伸出右手', '大拇指向上竖起', '其他手指收拢', '保持稳定姿势'],
    'SWIPE_LEFT': ['从屏幕右侧开始', '向左侧快速滑动', '保持水平轨迹', '滑动距离适中'],
    'SWIPE_RIGHT': ['从屏幕左侧开始', '向右侧快速滑动', '保持水平轨迹', '滑动距离适中']
  }
  return steps[code] || ['按照标准手势执行']
}

const toggleTraining = async () => {
  if (!selectedGesture.value) {
    ElMessage.warning('请先选择要训练的手势')
    return
  }

  if (isTraining.value) {
    stopTraining()
  } else {
    await startTraining()
  }
}

const startTraining = async () => {
  loading.value = true
  try {
    // 这里可以调用后端API开始训练
    isTraining.value = true
    sessionStats.value = { attempts: 0, success: 0, progress: 0 }
    ElMessage.success('训练已开始')
  } catch (error) {
    ElMessage.error('启动训练失败')
  } finally {
    loading.value = false
  }
}

const stopTraining = () => {
  isTraining.value = false
  currentDetected.value = ''
  currentConfidence.value = 0
  ElMessage.info('训练已停止')
}

const resetProgress = () => {
  sessionStats.value = { attempts: 0, success: 0, progress: 0 }
  currentDetected.value = ''
  currentConfidence.value = 0
  ElMessage.info('进度已重置')
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const viewDetails = (record) => {
  ElMessage.info(`查看 ${record.gesture} 的训练详情`)
}

const repeatTraining = (record) => {
  selectedGesture.value = record.gesture
  ElMessage.info(`开始重复训练 ${record.gesture}`)
}

// 模拟手势检测
let detectionInterval = null

const startGestureDetection = () => {
  detectionInterval = setInterval(() => {
    // 模拟随机检测
    if (Math.random() > 0.7) {
      currentDetected.value = selectedGesture.value
      currentConfidence.value = 0.8 + Math.random() * 0.2
      sessionStats.value.attempts++

      if (currentConfidence.value > 0.85) {
        sessionStats.value.success++
        ElMessage.success('检测成功!')
      }

      sessionStats.value.progress = Math.min(100, sessionStats.value.progress + 10)
    } else {
      currentDetected.value = ''
      currentConfidence.value = 0
    }
  }, 2000)
}

const stopGestureDetection = () => {
  if (detectionInterval) {
    clearInterval(detectionInterval)
    detectionInterval = null
  }
}

// 生命周期
onMounted(() => {
  // 初始化默认选择
  if (staticGestures.value.length > 0) {
    selectGesture(staticGestures.value[0])
  }
})

onUnmounted(() => {
  stopTraining()
  stopGestureDetection()
})
</script>

<style scoped>
.training-page {
  padding: 0;
}

.training-card {
  margin-bottom: 20px;
}

.overview-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.overview-content {
  margin-left: 15px;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.overview-label {
  font-size: 14px;
  color: #909399;
}

.gesture-selection {
  margin-bottom: 20px;
}

.gesture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.gesture-item {
  padding: 15px;
  border: 2px solid #E4E7ED;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  position: relative;
}

.gesture-item:hover {
  border-color: #409EFF;
  transform: translateY(-2px);
}

.gesture-item.active {
  border-color: #409EFF;
  background: #ECF5FF;
}

.gesture-icon {
  margin-bottom: 10px;
}

.gesture-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.gesture-code {
  font-size: 12px;
  color: #909399;
}

.gesture-status {
  position: absolute;
  top: 10px;
  right: 10px;
}

.gesture-instructions {
  margin-top: 20px;
  padding: 20px;
  background: #F4F4F5;
  border-radius: 8px;
}

.gesture-instructions h4 {
  margin-bottom: 15px;
  color: #303133;
}

.instruction-content p {
  margin-bottom: 15px;
  color: #606266;
}

.instruction-steps {
  margin-left: 20px;
}

.instruction-step {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  margin-right: 10px;
}

.step-text {
  color: #606266;
}

.video-preview {
  position: relative;
  width: 100%;
  height: 240px;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.practice-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
}

.start-prompt {
  text-align: center;
  color: white;
}

.start-prompt .el-icon {
  margin-bottom: 10px;
}

.recognition-status {
  text-align: center;
  color: white;
}

.detected-gesture {
  margin-bottom: 10px;
}

.detected-gesture .confidence {
  margin-top: 5px;
  font-size: 14px;
}

.waiting {
  opacity: 0.8;
}

.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.practice-controls {
  text-align: center;
  margin-bottom: 20px;
}

.practice-controls .el-button {
  margin: 0 10px;
}

.practice-stats {
  padding: 20px;
  background: #F8F9FA;
  border-radius: 8px;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.progress-section {
  margin-top: 20px;
}

.progress-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-item {
    margin-bottom: 15px;
  }

  .gesture-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }

  .stats-row {
    flex-direction: column;
    gap: 15px;
  }
}
</style>