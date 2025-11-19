<template>
  <div class="modern-training">
    <!-- 页面英雄区域 -->
    <div class="training-hero animate-slide-in-top">
      <div class="hero-content">
        <h1 class="hero-title">手势训练中心</h1>
        <p class="hero-subtitle">智能学习您的手势，打造个性化的AI交互体验</p>
      </div>
      <div class="hero-visual">
        <div class="floating-cards">
          <div class="gesture-preview animate-float" style="animation-delay: 0s">
            <div class="gesture-icon">👍</div>
          </div>
          <div class="gesture-preview animate-float" style="animation-delay: 0.5s">
            <div class="gesture-icon">✌️</div>
          </div>
          <div class="gesture-preview animate-float" style="animation-delay: 1s">
            <div class="gesture-icon">👌</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 训练模式选择 -->
    <div class="training-content">
      <div class="mode-section animate-slide-in-left">
        <h2 class="section-title">选择训练模式</h2>
        <div class="mode-grid">
          <div
            class="mode-card glass-card"
            :class="{ active: selectedMode === 'realtime' }"
            @click="selectMode('realtime')"
          >
            <div class="mode-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" stroke="url(#gradient1)" stroke-width="2"/>
                <path d="M24 14v10l6 3" stroke="url(#gradient1)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <defs>
                  <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#667eea"/>
                    <stop offset="100%" style="stop-color:#764ba2"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <h3>实时识别</h3>
            <p>通过摄像头实时检测手势，即时反馈识别结果</p>
            <div class="mode-badge primary">
              <span>推荐</span>
            </div>
          </div>

          <div
            class="mode-card glass-card"
            :class="{ active: selectedMode === 'practice' }"
            @click="selectMode('practice')"
          >
            <div class="mode-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect x="8" y="12" width="32" height="24" rx="4" stroke="url(#gradient2)" stroke-width="2"/>
                <circle cx="24" cy="24" r="8" stroke="url(#gradient2)" stroke-width="2"/>
                <path d="M24 20v8M20 24h8" stroke="url(#gradient2)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <defs>
                  <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#13B497"/>
                    <stop offset="100%" style="stop-color:#59D4A4"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <h3>练习模式</h3>
            <p>跟随指导学习标准手势，逐步提升识别准确率</p>
            <div class="mode-badge success">
              <span>教学</span>
            </div>
          </div>

          <div
            class="mode-card glass-card"
            :class="{ active: selectedMode === 'game' }"
            @click="selectMode('game')"
          >
            <div class="mode-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <path d="M12 12l8 8m0 0l8 8m-8-8v16m0-16h16" stroke="url(#gradient3)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="24" cy="24" r="20" stroke="url(#gradient3)" stroke-width="2"/>
                <defs>
                  <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#FA8231"/>
                    <stop offset="100%" style="stop-color:#FED330"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <h3>手势游戏</h3>
            <p>通过有趣的游戏方式训练手势识别，寓教于乐</p>
            <div class="mode-badge warning">
              <span>娱乐</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 实时识别区域 -->
      <div v-if="selectedMode === 'realtime'" class="realtime-section animate-slide-in-left" style="animation-delay: 0.2s">
        <div class="section-header">
          <h2 class="section-title">实时手势识别</h2>
          <div class="section-actions">
            <button
              class="modern-btn"
              :class="cameraActive ? 'danger' : 'primary'"
              @click="toggleCamera"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M1 6h2l1-1h8l1 1h2v8H1z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="8" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/>
              </svg>
              {{ cameraActive ? '停止识别' : '开始识别' }}
            </button>
            <button class="modern-btn secondary" @click="switchCamera">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 6h12M8 2v12M4 3l8 10M12 3l-8 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              切换摄像头
            </button>
          </div>
        </div>

        <div class="realtime-grid">
          <!-- 摄像头预览 -->
          <div class="camera-container glass-card">
            <div class="camera-header">
              <h3>摄像头预览</h3>
              <div class="camera-status">
                <div class="status-dot" :class="{ online: cameraActive }"></div>
                <span>{{ cameraActive ? '识别中' : '未启动' }}</span>
                <div class="status-separator">|</div>
                <div class="connection-status" :style="{ color: connectionStatusColor }">
                  <div class="status-dot" :class="{
                    online: wsConnectionStatus === 'connected' || wsConnectionStatus === 'analyzing',
                    warning: wsConnectionStatus === 'connecting'
                  }"></div>
                  <span>{{ connectionStatusText }}</span>
                </div>
              </div>
            </div>
            <div class="camera-view">
              <video
                ref="videoRef"
                autoplay
                playsinline
                class="camera-feed"
                :class="{ active: cameraActive }"
              ></video>
              <div v-if="!cameraActive" class="camera-placeholder">
                <div class="placeholder-icon">
                  <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                    <rect x="16" y="20" width="32" height="24" rx="4" stroke="currentColor" stroke-width="2"/>
                    <circle cx="32" cy="32" r="4" fill="currentColor"/>
                  </svg>
                </div>
                <p>点击"开始识别"启动摄像头</p>
              </div>
            </div>
          </div>

          <!-- 识别结果 -->
          <div class="result-container glass-card">
            <div class="result-header">
              <h3>识别结果</h3>
              <div class="confidence-meter">
                <span>置信度</span>
                <div class="confidence-bar">
                  <div
                    class="confidence-fill"
                    :style="{ width: `${currentConfidence * 100}%` }"
                  ></div>
                </div>
                <span>{{ Math.round(currentConfidence * 100) }}%</span>
              </div>
            </div>

            <div class="result-display">
              <div v-if="currentGesture" class="detected-gesture animate-scale-in">
                <div class="gesture-display">
                  <div class="gesture-emoji large">{{ getGestureEmoji(currentGesture) }}</div>
                  <div class="gesture-name">{{ getGestureName(currentGesture) }}</div>
                  <div class="gesture-code">{{ currentGesture }}</div>
                </div>
              </div>
              <div v-else class="no-gesture">
                <div class="waiting-icon animate-pulse">
                  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                    <circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="2" stroke-dasharray="4 2"/>
                  </svg>
                </div>
                <p>等待手势检测...</p>
              </div>
            </div>

            <!-- 历史记录 -->
            <div class="gesture-history">
              <h4>识别历史</h4>
              <div class="history-list">
                <div
                  v-for="(gesture, index) in gestureHistory.slice(-5)"
                  :key="index"
                  class="history-item animate-slide-in-right"
                >
                  <span class="history-emoji">{{ getGestureEmoji(gesture.gesture) }}</span>
                  <span class="history-name">{{ getGestureName(gesture.gesture) }}</span>
                  <span class="history-confidence">{{ Math.round(gesture.confidence * 100) }}%</span>
                </div>
                <div v-if="gestureHistory.length === 0" class="history-empty">
                  <span>暂无识别记录</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 练习模式 -->
      <div v-if="selectedMode === 'practice'" class="practice-section animate-slide-in-left" style="animation-delay: 0.2s">
        <div class="section-header">
          <h2 class="section-title">手势练习</h2>
          <div class="progress-info">
            <span>学习进度</span>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${practiceProgress}%` }"></div>
            </div>
            <span>{{ practiceProgress }}%</span>
          </div>
        </div>

        <div class="practice-content">
          <div class="gesture-tutorial glass-card">
            <div class="tutorial-header">
              <h3>当前练习</h3>
              <div class="tutorial-step">第 {{ currentStep }} / {{ totalSteps }} 步</div>
            </div>

            <div class="tutorial-gesture">
              <div class="gesture-showcase">
                <div class="gesture-emoji extra-large">{{ getGestureEmoji(currentTutorialGesture) }}</div>
                <div class="gesture-instruction">
                  <h4>{{ getGestureName(currentTutorialGesture) }}</h4>
                  <p>{{ getGestureInstruction(currentTutorialGesture) }}</p>
                </div>
              </div>
            </div>

            <div class="tutorial-actions">
              <button class="modern-btn secondary" @click="previousStep">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                上一步
              </button>
              <button class="modern-btn primary" @click="practiceGesture">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M2 8h12M8 2v12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                开始练习
              </button>
              <button class="modern-btn secondary" @click="nextStep">
                下一步
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 手势图鉴 -->
          <div class="gesture-gallery glass-card">
            <h3>手势图鉴</h3>
            <div class="gallery-grid">
              <div
                v-for="gesture in tutorialGestures"
                :key="gesture.code"
                class="gallery-item"
                :class="{ completed: gesture.completed, current: gesture.code === currentTutorialGesture }"
                @click="selectGesture(gesture.code)"
              >
                <div class="gallery-emoji">{{ getGestureEmoji(gesture.code) }}</div>
                <div class="gallery-name">{{ gesture.name }}</div>
                <div class="gallery-status">
                  <div class="status-indicator" :class="{ active: gesture.completed }"></div>
                  <span>{{ gesture.completed ? '已掌握' : '学习中' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 游戏模式 -->
      <div v-if="selectedMode === 'game'" class="game-section animate-slide-in-left" style="animation-delay: 0.2s">
        <div class="section-header">
          <h2 class="section-title">手势挑战游戏</h2>
          <div class="game-stats">
            <div class="stat-item">
              <span class="stat-label">得分</span>
              <span class="stat-value">{{ gameScore }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">连击</span>
              <span class="stat-value">{{ gameCombo }}</span>
            </div>
          </div>
        </div>

        <div class="game-content">
          <div class="game-board glass-card">
            <div class="game-challenge">
              <div class="challenge-timer">
                <div class="timer-circle">
                  <svg class="timer-svg" viewBox="0 0 36 36">
                    <path
                      class="timer-bg"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      class="timer-progress"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      :stroke-dasharray="gameTimerProgress"
                    />
                  </svg>
                  <div class="timer-text">{{ gameTimer }}</div>
                </div>
              </div>

              <div class="challenge-target">
                <h3>做出这个手势</h3>
                <div class="target-gesture animate-bounce">
                  <div class="gesture-emoji massive">{{ getGestureEmoji(targetGesture) }}</div>
                  <div class="gesture-name">{{ getGestureName(targetGesture) }}</div>
                </div>
              </div>
            </div>

            <div class="game-feedback">
              <div v-if="gameResult" class="feedback-result animate-scale-in" :class="gameResult.type">
                <div class="feedback-icon">{{ gameResult.icon }}</div>
                <div class="feedback-text">{{ gameResult.message }}</div>
                <div class="feedback-points">+{{ gameResult.points }} 分</div>
              </div>
            </div>

            <div class="game-controls">
              <button
                class="modern-btn success large"
                @click="startGame"
                :disabled="gameActive"
              >
                {{ gameActive ? '游戏进行中...' : '开始游戏' }}
              </button>
            </div>
          </div>

          <!-- 排行榜 -->
          <div class="leaderboard glass-card">
            <h3>排行榜</h3>
            <div class="leaderboard-list">
              <div
                v-for="(player, index) in leaderboard"
                :key="index"
                class="leaderboard-item"
                :class="{ self: player.isSelf }"
              >
                <div class="rank">{{ index + 1 }}</div>
                <div class="player-info">
                  <div class="player-name">{{ player.name }}</div>
                  <div class="player-score">{{ player.score }} 分</div>
                </div>
                <div class="player-badge" v-if="index === 0">👑</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useGestureStore } from '@/stores/gesture'
import { mobileGestureService } from '@/services/mobile'
import { ElMessage, ElNotification } from 'element-plus'

// 手势识别Store
const gestureStore = useGestureStore()

// 响应式数据
const selectedMode = ref('realtime')
const cameraActive = ref(false)
const currentGesture = ref('')
const currentConfidence = ref(0)
const gestureHistory = ref([])
const videoRef = ref(null)

// 练习模式数据
const practiceProgress = ref(0)
const currentStep = ref(1)
const totalSteps = ref(8)
const currentTutorialGesture = ref('POINT_UP')

const tutorialGestures = ref([
  { code: 'POINT_UP', name: '指向上方', completed: true },
  { code: 'THUMBS_UP', name: '点赞', completed: true },
  { code: 'VICTORY', name: '胜利', completed: false },
  { code: 'OK_SIGN', name: 'OK', completed: false },
  { code: 'PEACE_SIGN', name: '和平', completed: false },
  { code: 'ROCK_SIGN', name: '摇滚', completed: false },
  { code: 'CALL_ME', name: '打电话', completed: false },
  { code: 'FIST', name: '拳头', completed: false }
])

// 游戏模式数据
const gameScore = ref(0)
const gameCombo = ref(0)
const gameTimer = ref(30)
const gameActive = ref(false)
const targetGesture = ref('')
const gameResult = ref(null)
const gameTimerProgress = ref('0 100')

const leaderboard = ref([
  { name: '手势大师', score: 2850, isSelf: false },
  { name: 'AI新手', score: 1920, isSelf: false },
  { name: '你', score: 0, isSelf: true },
  { name: '学习者', score: 850, isSelf: false },
  { name: '练习生', score: 420, isSelf: false }
])

// 手势映射
const gestureData = {
  'POINT_UP': { emoji: '☝️', name: '指向上方', instruction: '伸出食指，其他手指握紧' },
  'THUMBS_UP': { emoji: '👍', name: '点赞', instruction: '大拇指向上，其他手指握紧' },
  'VICTORY': { emoji: '✌️', name: '胜利', instruction: '伸出食指和中指呈V字形' },
  'OK_SIGN': { emoji: '👌', name: 'OK', instruction: '大拇指和食指形成圆圈' },
  'PEACE_SIGN': { emoji: '✌️', name: '和平', instruction: '伸出食指和中指' },
  'ROCK_SIGN': { emoji: '🤘', name: '摇滚', instruction: '伸出食指和小拇指' },
  'CALL_ME': { emoji: '🤙', name: '打电话', instruction: '大拇指和小拇指伸出' },
  'FIST': { emoji: '✊', name: '拳头', instruction: '所有手指握紧成拳' }
}

// 方法
const selectMode = (mode) => {
  selectedMode.value = mode
  if (mode === 'realtime') {
    initRealtimeMode()
  } else if (mode === 'practice') {
    initPracticeMode()
  } else if (mode === 'game') {
    initGameMode()
  }
}

const getGestureEmoji = (code) => {
  return gestureData[code]?.emoji || '🤚'
}

const getGestureName = (code) => {
  return gestureData[code]?.name || '未知手势'
}

const getGestureInstruction = (code) => {
  return gestureData[code]?.instruction || '暂无说明'
}

const toggleCamera = async () => {
  if (cameraActive.value) {
    stopCamera()
  } else {
    await startCamera()
  }
}

const startCamera = async () => {
  try {
    // 首先获取摄像头流
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'user'
      }
    })

    if (videoRef.value) {
      videoRef.value.srcObject = stream
      cameraActive.value = true

      // 连接WebSocket服务
      try {
        await gestureStore.connect()

        // 启动实时手势分析
        await gestureStore.startAnalysis({
          fps: 10,
          confidenceThreshold: 0.7,
          gestureTypes: ['hand', 'pose', 'emotion'],
          enableTracking: true
        })

        ElNotification({
          title: '实时识别已启动',
          message: '摄像头已连接，开始识别您的手势',
          type: 'success',
          duration: 3000,
          showClose: false
        })

        // 开始发送视频帧到后端
        startVideoFrameSending()

      } catch (wsError) {
        console.error('WebSocket连接失败:', wsError)
        ElMessage.error('无法连接到AI服务，请检查服务是否启动')

        // 如果WebSocket连接失败，回退到模拟模式
        simulateGestureRecognition()
      }
    }
  } catch (error) {
    console.error('无法访问摄像头:', error)
    ElMessage.error('无法访问摄像头，请检查权限设置')
  }
}

const stopCamera = () => {
  // 停止视频帧发送
  stopVideoFrameSending()

  // 停止手势分析
  gestureStore.stopAnalysis()

  // 停止摄像头流
  if (videoRef.value && videoRef.value.srcObject) {
    const stream = videoRef.value.srcObject
    const tracks = stream.getTracks()
    tracks.forEach(track => track.stop())
    videoRef.value.srcObject = null
    cameraActive.value = false
  }

  ElNotification({
    title: '实时识别已停止',
    message: '摄像头连接已断开',
    type: 'info',
    duration: 2000,
    showClose: false
  })
}

const switchCamera = () => {
  // 切换摄像头逻辑
  console.log('切换摄像头')
}

// WebSocket视频帧发送
let frameSendInterval = null

const startVideoFrameSending = () => {
  if (!videoRef.value || !gestureStore.isConnected) return

  frameSendInterval = setInterval(() => {
    if (videoRef.value && gestureStore.isAnalyzing && cameraActive.value) {
      captureAndSendFrame()
    }
  }, 1000 / 10) // 10 FPS
}

const stopVideoFrameSending = () => {
  if (frameSendInterval) {
    clearInterval(frameSendInterval)
    frameSendInterval = null
  }
}

const captureAndSendFrame = () => {
  try {
    const canvas = document.createElement('canvas')
    const context = canvas.getContext('2d')

    if (videoRef.value) {
      canvas.width = videoRef.value.videoWidth
      canvas.height = videoRef.value.videoHeight
      context.drawImage(videoRef.value, 0, 0, canvas.width, canvas.height)

      // 压缩图像数据
      const imageData = canvas.toDataURL('image/jpeg', 0.8)

      // 发送到WebSocket服务
      if (imageData.length < 100000) { // 限制图片大小
        gestureStore.wsService?.sendImage(imageData)
      }
    }
  } catch (error) {
    console.error('发送视频帧失败:', error)
  }
}

// 实时手势数据响应
const updateRealtimeGesture = () => {
  if (gestureStore.currentGesture) {
    const gesture = gestureStore.currentGesture

    // 更新当前显示的手势
    currentGesture.value = gesture.gesture || ''
    currentConfidence.value = gesture.confidence || 0

    // 更新手势历史
    if (gesture.gesture && gesture.confidence > 0.5) {
      const historyItem = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
        gesture: gesture.gesture,
        confidence: gesture.confidence,
        emoji: getGestureEmoji(gesture.gesture)
      }

      gestureHistory.value.unshift(historyItem)

      // 限制历史记录长度
      if (gestureHistory.value.length > 20) {
        gestureHistory.value = gestureHistory.value.slice(0, 20)
      }

      // 游戏模式检测
      if (selectedMode.value === 'game' && gameActive.value && targetGesture.value) {
        checkGameResult(gesture.gesture)
      }
    }
  }
}

// 计算属性
const wsConnectionStatus = computed(() => {
  if (!gestureStore.isConnected) return 'disconnected'
  if (gestureStore.isAnalyzing) return 'analyzing'
  return 'connected'
})

const connectionStatusText = computed(() => {
  switch (wsConnectionStatus.value) {
    case 'connected': return '已连接'
    case 'analyzing': return '分析中'
    case 'disconnected': return '未连接'
    default: return '未知'
  }
})

const connectionStatusColor = computed(() => {
  switch (wsConnectionStatus.value) {
    case 'connected': return 'var(--accent-green)'
    case 'analyzing': return 'var(--accent-blue)'
    case 'disconnected': return 'var(--accent-red)'
    default: return 'var(--text-secondary)'
  }
})

const simulateGestureRecognition = () => {
  // 模拟手势识别
  const gestures = Object.keys(gestureData)
  const simulate = () => {
    if (cameraActive.value) {
      const randomGesture = gestures[Math.floor(Math.random() * gestures.length)]
      const confidence = 0.7 + Math.random() * 0.3

      currentGesture.value = randomGesture
      currentConfidence.value = confidence

      if (confidence > 0.8) {
        gestureHistory.value.unshift({
          gesture: randomGesture,
          confidence: confidence,
          timestamp: Date.now()
        })

        if (gestureHistory.value.length > 10) {
          gestureHistory.value = gestureHistory.value.slice(0, 10)
        }
      }
    }
  }

  const interval = setInterval(() => {
    if (cameraActive.value) {
      simulate()
    } else {
      clearInterval(interval)
    }
  }, 2000)
}

// 练习模式方法
const initPracticeMode = () => {
  updatePracticeProgress()
}

const updatePracticeProgress = () => {
  const completed = tutorialGestures.value.filter(g => g.completed).length
  practiceProgress.value = Math.round((completed / tutorialGestures.value.length) * 100)
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
    const gestures = Object.keys(gestureData)
    currentTutorialGesture.value = gestures[currentStep.value - 1]
  }
}

const nextStep = () => {
  if (currentStep.value < totalSteps.value) {
    currentStep.value++
    const gestures = Object.keys(gestureData)
    currentTutorialGesture.value = gestures[currentStep.value - 1]
  }
}

const practiceGesture = () => {
  // 开始练习特定手势
  selectMode('realtime')
  targetGesture.value = currentTutorialGesture.value
}

const selectGesture = (code) => {
  currentTutorialGesture.value = code
  const index = Object.keys(gestureData).indexOf(code) + 1
  currentStep.value = index
}

// 游戏模式方法
const initGameMode = () => {
  resetGame()
}

const startGame = () => {
  gameActive.value = true
  gameScore.value = 0
  gameCombo.value = 0
  gameTimer.value = 30
  gameResult.value = null

  const gestures = Object.keys(gestureData)
  targetGesture.value = gestures[Math.floor(Math.random() * gestures.length)]

  startGameTimer()
}

const resetGame = () => {
  gameActive.value = false
  gameScore.value = 0
  gameCombo.value = 0
  gameTimer.value = 30
  gameResult.value = null
}

const startGameTimer = () => {
  const timer = setInterval(() => {
    if (gameTimer.value > 0 && gameActive.value) {
      gameTimer.value--
      const progress = (gameTimer.value / 30) * 100
      const circumference = 2 * Math.PI * 15.9155
      const offset = circumference - (progress / 100) * circumference
      gameTimerProgress.value = `${offset} ${circumference}`
    } else {
      clearInterval(timer)
      endGame()
    }
  }, 1000)
}

const endGame = () => {
  gameActive.value = false
  // 更新排行榜
  const playerIndex = leaderboard.value.findIndex(p => p.isSelf)
  if (playerIndex !== -1) {
    leaderboard.value[playerIndex].score = Math.max(leaderboard.value[playerIndex].score, gameScore.value)
    leaderboard.value.sort((a, b) => b.score - a.score)
  }
}

// 移动端手势处理
const initMobileGestures = () => {
  if (!mobileGestureService.isMobile) return

  // 初始化移动端优化
  mobileGestureService.setViewport()
  mobileGestureService.setMobileCSSVariables()
  mobileGestureService.optimizeMobileInputs()

  // 注册滑动手势 - 切换模式
  mobileGestureService.on('swipeleft', (gestureData) => {
    const modes = ['realtime', 'practice', 'game']
    const currentIndex = modes.indexOf(selectedMode.value)
    const nextIndex = (currentIndex + 1) % modes.length
    selectMode(modes[nextIndex])
    mobileGestureService.vibrate(20)
  })

  mobileGestureService.on('swiperight', (gestureData) => {
    const modes = ['realtime', 'practice', 'game']
    const currentIndex = modes.indexOf(selectedMode.value)
    const prevIndex = (currentIndex - 1 + modes.length) % modes.length
    selectMode(modes[prevIndex])
    mobileGestureService.vibrate(20)
  })

  // 注册长按手势 - 显示相机选项
  mobileGestureService.on('longpress', (gestureData, e) => {
    if (selectedMode.value === 'realtime') {
      showMobileCameraOptions()
      mobileGestureService.vibrate(50)
    }
  })

  // 初始化触摸手势监听
  const container = document.querySelector('.modern-training')
  if (container) {
    mobileGestureService.init(container)
  }
}

// 显示移动端摄像头选项
const showMobileCameraOptions = () => {
  ElNotification({
    title: '摄像头选项',
    message: '长按功能开发中...',
    type: 'info',
    duration: 2000,
    showClose: false
  })
}

// 生命周期
onMounted(async () => {
  initRealtimeMode()

  // 初始化移动端手势
  initMobileGestures()

  // 初始化手势识别监听
  const unwatchGesture = gestureStore.$subscribe((mutation, state) => {
    if (state.currentGesture) {
      updateRealtimeGesture()
    }
  })

  // 处理屏幕旋转
  const handleOrientationChange = () => {
    setTimeout(() => {
      // 重新计算布局
      window.dispatchEvent(new Event('resize'))
    }, 100)
  }

  mobileGestureService.handleOrientationChange(handleOrientationChange)

  // 页面卸载时清理
  onUnmounted(() => {
    unwatchGesture()
    stopCamera()
    gestureStore.disconnect()
    mobileGestureService.destroy()
  })

  // 尝试预连接WebSocket（不启动分析）
  try {
    await gestureStore.connect()
    console.log('✅ WebSocket预连接成功')
  } catch (error) {
    console.warn('⚠️ WebSocket预连接失败，将在使用时重试:', error)
  }
})

onUnmounted(() => {
  stopCamera()
  gestureStore.disconnect()
})
</script>

<style scoped>
@import '@/styles/modern.css';

.modern-training {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* 训练英雄区域 */
.training-hero {
  padding: 80px 20px 60px;
  background: radial-gradient(ellipse at bottom, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 60px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  margin: 0 0 20px 0;
  background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
  line-height: 1.6;
}

.floating-cards {
  display: flex;
  gap: 20px;
  flex-shrink: 0;
}

.gesture-preview {
  width: 80px;
  height: 80px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--glass-shadow);
}

.gesture-icon {
  font-size: 2rem;
}

/* 训练内容区域 */
.training-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 32px;
  background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 模式选择网格 */
.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 60px;
}

.mode-card {
  padding: 32px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.mode-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
}

.mode-card.active {
  border: 2px solid var(--accent-blue);
  box-shadow: 0 0 30px rgba(0, 122, 255, 0.3);
}

.mode-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mode-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: var(--text-primary);
}

.mode-card p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.mode-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.mode-badge.primary {
  background: var(--gradient-primary);
  color: white;
}

.mode-badge.success {
  background: var(--gradient-success);
  color: white;
}

.mode-badge.warning {
  background: var(--gradient-warning);
  color: white;
}

/* 区域通用样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.section-actions {
  display: flex;
  gap: 12px;
}

.modern-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 12px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
}

.modern-btn.primary {
  background: var(--gradient-primary);
  color: white;
}

.modern-btn.secondary {
  background: var(--glass-bg);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.modern-btn.success {
  background: var(--gradient-success);
  color: white;
}

.modern-btn.danger {
  background: var(--gradient-secondary);
  color: white;
}

.modern-btn.large {
  padding: 12px 24px;
  font-size: 1rem;
}

.modern-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* 实时识别区域 */
.realtime-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.camera-container,
.result-container {
  padding: 24px;
  border-radius: 20px;
}

.camera-header,
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.camera-header h3,
.result-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.camera-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.status-separator {
  color: var(--text-secondary);
  opacity: 0.5;
  margin: 0 4px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.connection-status .status-dot {
  width: 8px;
  height: 8px;
}

.connection-status .status-dot.online {
  background: var(--accent-green);
  box-shadow: 0 0 8px rgba(52, 199, 89, 0.4);
}

.connection-status .status-dot.warning {
  background: var(--accent-orange);
  box-shadow: 0 0 8px rgba(250, 130, 49, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

.confidence-meter {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.875rem;
}

.confidence-bar {
  width: 100px;
  height: 6px;
  background: var(--glass-bg);
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: var(--gradient-success);
  transition: width 0.3s ease;
}

.camera-view {
  position: relative;
  width: 100%;
  height: 300px;
  background: var(--bg-secondary);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 16px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.camera-feed.active {
  opacity: 1;
}

.camera-placeholder {
  text-align: center;
  color: var(--text-secondary);
}

.placeholder-icon {
  margin-bottom: 16px;
  opacity: 0.5;
}

.result-display {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detected-gesture {
  text-align: center;
}

.gesture-display {
  padding: 24px;
  background: var(--glass-bg);
  border-radius: 16px;
  border: 1px solid var(--glass-border);
}

.gesture-emoji.large {
  font-size: 4rem;
  margin-bottom: 12px;
  display: block;
}

.gesture-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.gesture-code {
  font-family: 'Monaco', 'Menlo', monospace;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
}

.no-gesture {
  text-align: center;
  color: var(--text-secondary);
}

.waiting-icon {
  margin-bottom: 16px;
  opacity: 0.5;
}

/* 历史记录 */
.gesture-history {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--glass-border);
}

.gesture-history h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: var(--text-primary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--glass-bg);
  border-radius: 8px;
  font-size: 0.875rem;
}

.history-emoji {
  font-size: 1.2rem;
}

.history-name {
  flex: 1;
  color: var(--text-primary);
}

.history-confidence {
  color: var(--accent-blue);
  font-weight: 600;
}

.history-empty {
  text-align: center;
  color: var(--text-secondary);
  padding: 20px;
  font-style: italic;
}

/* 练习模式 */
.practice-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.gesture-tutorial,
.gesture-gallery {
  padding: 32px;
  border-radius: 20px;
}

.tutorial-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.tutorial-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.tutorial-step {
  background: var(--gradient-info);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.progress-bar {
  width: 120px;
  height: 6px;
  background: var(--glass-bg);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--gradient-success);
  transition: width 0.3s ease;
}

.gesture-showcase {
  text-align: center;
  padding: 40px 20px;
}

.gesture-emoji.extra-large {
  font-size: 6rem;
  margin-bottom: 20px;
  display: block;
}

.gesture-instruction h4 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: var(--text-primary);
}

.gesture-instruction p {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin: 0;
}

.tutorial-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
}

.gallery-item {
  padding: 16px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  border: 2px solid transparent;
}

.gallery-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.12);
}

.gallery-item.current {
  border-color: var(--accent-blue);
  background: rgba(0, 122, 255, 0.1);
}

.gallery-item.completed {
  border-color: var(--accent-green);
  background: rgba(52, 199, 89, 0.1);
}

.gallery-emoji {
  font-size: 2rem;
  margin-bottom: 8px;
  display: block;
}

.gallery-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.gallery-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* 游戏模式 */
.game-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.game-board,
.leaderboard {
  padding: 32px;
  border-radius: 20px;
}

.game-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.game-challenge {
  text-align: center;
  margin-bottom: 32px;
}

.challenge-timer {
  margin-bottom: 32px;
}

.timer-circle {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 16px;
}

.timer-svg {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.timer-bg {
  fill: none;
  stroke: var(--glass-bg);
  stroke-width: 3;
}

.timer-progress {
  fill: none;
  stroke: var(--gradient-primary);
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dasharray 0.3s ease;
}

.timer-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.target-gesture {
  padding: 32px;
  background: var(--glass-bg);
  border-radius: 20px;
  border: 1px solid var(--glass-border);
}

.gesture-emoji.massive {
  font-size: 8rem;
  margin-bottom: 16px;
  display: block;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.game-feedback {
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
}

.feedback-result {
  text-align: center;
  padding: 24px;
  border-radius: 16px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
}

.feedback-result.success {
  border-color: var(--accent-green);
  background: rgba(52, 199, 89, 0.1);
}

.feedback-result.error {
  border-color: var(--accent-red);
  background: rgba(255, 59, 48, 0.1);
}

.feedback-icon {
  font-size: 3rem;
  margin-bottom: 8px;
}

.feedback-text {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.feedback-points {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.game-controls {
  text-align: center;
}

/* 排行榜 */
.leaderboard h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 24px 0;
  color: var(--text-primary);
}

.leaderboard-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--glass-bg);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.leaderboard-item.self {
  border: 2px solid var(--accent-blue);
  background: rgba(0, 122, 255, 0.1);
}

.rank {
  width: 32px;
  height: 32px;
  background: var(--gradient-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.player-info {
  flex: 1;
}

.player-name {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.player-score {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.player-badge {
  font-size: 1.5rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .realtime-grid {
    grid-template-columns: 1fr;
  }

  .game-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .training-hero {
    padding: 60px 16px 40px;
  }

  .hero-content {
    flex-direction: column;
    text-align: center;
    gap: 40px;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .floating-cards {
    justify-content: center;
  }

  .training-content {
    padding: 40px 16px;
  }

  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .section-actions {
    justify-content: stretch;
  }

  .modern-btn {
    flex: 1;
    justify-content: center;
  }

  .mode-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .game-stats {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  /* 移动端英雄区域优化 */
  .hero-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .hero-title {
    font-size: 2rem;
    line-height: 1.2;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .floating-cards {
    position: relative;
    width: 200px;
    height: 60px;
  }

  .gesture-preview {
    position: absolute;
    width: 40px;
    height: 40px;

    &:nth-child(1) { top: 0; left: 20px; }
    &:nth-child(2) { top: 10px; left: 80px; }
    &:nth-child(3) { top: 0; left: 140px; }
  }

  .section-title {
    font-size: 1.5rem;
  }

  /* 移动端模式选择优化 */
  .mode-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    margin-bottom: 32px;
  }

  .mode-card {
    padding: 20px;
    text-align: center;
  }

  .mode-icon {
    width: 48px;
    height: 48px;
    margin: 0 auto 16px;
  }

  .mode-card h3 {
    font-size: 1.25rem;
  }

  .mode-card p {
    font-size: 0.875rem;
    margin-bottom: 16px;
  }

  /* 移动端实时识别区域优化 */
  .realtime-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .camera-container,
  .gesture-panel {
    padding: 20px;
  }

  .camera-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .camera-status {
    justify-content: center;
    flex-wrap: wrap;
    gap: 12px;
  }

  .section-actions {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .modern-btn {
    padding: 12px 16px;
    font-size: 0.875rem;
    min-height: 44px; /* 触摸友好的最小高度 */

    svg {
      width: 14px;
      height: 14px;
    }
  }

  /* 移动端手势识别结果优化 */
  .current-gesture {
    padding: 16px;
  }

  .gesture-emoji.large {
    font-size: 3rem;
  }

  .gesture-emoji.extra-large {
    font-size: 4rem;
  }

  .gesture-emoji.massive {
    font-size: 4.5rem;
  }

  .confidence-bar {
    width: 80px;
  }

  /* 移动端手势历史优化 */
  .history-list {
    gap: 6px;
  }

  .history-item {
    padding: 10px 12px;
  }

  .history-emoji {
    font-size: 1rem;
  }

  /* 移动端练习模式优化 */
  .practice-content {
    gap: 16px;
  }

  .gesture-tutorial,
  .gesture-gallery {
    padding: 20px;
  }

  .tutorial-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }

  .progress-info {
    justify-content: center;
    font-size: 0.8rem;
  }

  .gesture-showcase {
    text-align: center;
  }

  .gesture-demo {
    padding: 20px;
    gap: 16px;
  }

  /* 移动端游戏模式优化 */
  .game-header {
    flex-direction: column;
    gap: 16px;
  }

  .game-stats {
    justify-content: space-around;
    width: 100%;
  }

  .game-stat {
    flex-direction: column;
    text-align: center;
    gap: 4px;
  }

  .game-board {
    padding: 20px;
  }

  .game-challenge {
    flex-direction: column;
    gap: 20px;
  }

  .target-gesture {
    padding: 20px;
  }

  .gesture-emoji.massive {
    font-size: 5rem;
  }

  .game-controls {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .modern-btn.large {
    padding: 16px 24px;
    min-height: 48px;
  }

  /* 移动端排行榜优化 */
  .leaderboard-list {
    gap: 8px;
  }

  .leaderboard-item {
    padding: 12px 16px;
  }

  .player-rank {
    width: 24px;
    height: 24px;
    font-size: 0.75rem;
  }

  .player-info {
    flex: 1;
  }

  .player-name {
    font-size: 0.875rem;
  }

  .player-score {
    font-size: 0.875rem;
  }

  /* 移动端触摸优化 */
  .mode-card,
  .glass-card,
  .modern-btn {
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    user-select: none;
  }

  .mode-card:active {
    transform: scale(0.98);
  }

  .modern-btn:active {
    transform: scale(0.95);
  }

  /* 移动端滚动优化 */
  .modern-training {
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }

  .gesture-gallery,
  .leaderboard-content {
    max-height: 300px;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  /* 移动端摄像头优化 */
  .camera-feed {
    border-radius: 16px;
  }

  .camera-placeholder {
    min-height: 200px;
  }
}

/* 移动端横屏适配 */
@media screen and (orientation: landscape) and (max-height: 500px) {
  .hero-section {
    padding: 40px 16px;
  }

  .hero-content {
    flex-direction: row;
  }

  .floating-cards {
    width: 150px;
    height: 50px;
  }

  .gesture-preview {
    width: 30px;
    height: 30px;
  }
}

/* 额外动画 */
@keyframes slide-in-right {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-slide-in-right {
  animation: slide-in-right 0.4s ease-out;
}

.animate-scale-in {
  animation: scale-in 0.3s ease-out;
}
</style>