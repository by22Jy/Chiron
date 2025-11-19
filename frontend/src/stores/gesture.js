/**
 * 手势识别状态管理
 * YOLO-LLM Platform
 *
 * 管理实时手势识别数据、状态和历史记录
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import wsService from '@/services/websocket'

export const useGestureStore = defineStore('gesture', () => {
  // 响应式状态
  const isConnected = ref(false)
  const isAnalyzing = ref(false)
  const currentGesture = ref(null)
  const gestureHistory = ref([])
  const realTimeData = ref(null)
  const statistics = ref({
    totalDetections: 0,
    correctDetections: 0,
    falsePositives: 0,
    avgConfidence: 0,
    sessionDuration: 0
  })
  const config = ref({
    fps: 10,
    confidenceThreshold: 0.7,
    gestureTypes: ['hand', 'pose', 'emotion'],
    enableTracking: true,
    enableAudioFeedback: false,
    enableVisualFeedback: true
  })
  const error = ref(null)

  // 内部状态
  const sessionStartTime = ref(null)
  const gestureCounts = ref({})
  const confidenceScores = ref([])

  // 计算属性
  const accuracy = computed(() => {
    const total = statistics.value.totalDetections
    if (total === 0) return 0
    return ((statistics.value.correctDetections / total) * 100).toFixed(1)
  })

  const avgConfidence = computed(() => {
    const scores = confidenceScores.value
    if (scores.length === 0) return 0
    const sum = scores.reduce((a, b) => a + b, 0)
    return (sum / scores.length).toFixed(2)
  })

  const sessionDuration = computed(() => {
    if (!sessionStartTime.value) return 0
    return Math.floor((Date.now() - sessionStartTime.value) / 1000)
  })

  const gestureStats = computed(() => {
    const stats = {}
    Object.entries(gestureCounts.value).forEach(([gesture, count]) => {
      const gestureHistory = getGestureHistory(gesture)
      const totalConfidence = gestureHistory.reduce((sum, item) => sum + item.confidence, 0)
      const avgGestureConfidence = gestureHistory.length > 0 ? totalConfidence / gestureHistory.length : 0

      stats[gesture] = {
        count,
        confidence: avgGestureConfidence.toFixed(2),
        trend: getGestureTrend(gesture),
        lastDetected: getLastDetectedTime(gesture)
      }
    })
    return stats
  })

  // 方法
  const connect = async () => {
    try {
      error.value = null
      await wsService.connect()

      // 注册消息处理器
      wsService.onMessage('gesture_result', handleGestureResult)
      wsService.onMessage('analysis_status', handleAnalysisStatus)
      wsService.onConnection(handleConnectionChange)
      wsService.onError(handleError)

      isConnected.value = true
    } catch (err) {
      error.value = err.message
      isConnected.value = false
      throw err
    }
  }

  const disconnect = () => {
    stopAnalysis()
    wsService.disconnect()
    isConnected.value = false
  }

  const startAnalysis = async (analysisConfig = null) => {
    if (!isConnected.value) {
      await connect()
    }

    try {
      const configToUse = analysisConfig || config.value
      await wsService.startRealtimeAnalysis(configToUse)

      isAnalyzing.value = true
      sessionStartTime.value = Date.now()
      resetSessionData()

      console.log('🎯 开始实时手势分析')
    } catch (err) {
      error.value = err.message
      isAnalyzing.value = false
      throw err
    }
  }

  const stopAnalysis = () => {
    if (isAnalyzing.value) {
      wsService.stopRealtimeAnalysis()
      isAnalyzing.value = false
      updateSessionStatistics()
      console.log('⏹️ 停止实时手势分析')
    }
  }

  const updateConfig = (newConfig) => {
    config.value = { ...config.value, ...newConfig }

    // 如果正在分析，重新启动以应用新配置
    if (isAnalyzing.value) {
      stopAnalysis()
      setTimeout(() => {
        startAnalysis()
      }, 1000)
    }
  }

  const clearHistory = () => {
    gestureHistory.value = []
    statistics.value = {
      totalDetections: 0,
      correctDetections: 0,
      falsePositives: 0,
      avgConfidence: 0,
      sessionDuration: 0
    }
    gestureCounts.value = {}
    confidenceScores.value = []
    console.log('🗑️ 清空历史记录')
  }

  // 消息处理器
  const handleGestureResult = (data) => {
    try {
      currentGesture.value = data
      realTimeData.value = data

      // 添加到历史记录
      const historyItem = {
        id: Date.now(),
        timestamp: data.timestamp || Date.now(),
        gesture: data.gesture,
        confidence: data.confidence,
        bbox: data.bbox,
        landmarks: data.landmarks,
        image: data.image,
        duration: data.duration || 0
      }

      gestureHistory.value.unshift(historyItem)

      // 限制历史记录长度
      if (gestureHistory.value.length > 1000) {
        gestureHistory.value = gestureHistory.value.slice(0, 1000)
      }

      // 更新统计信息
      updateStatistics(data)

      // 更新手势计数
      const gestureName = data.gesture
      gestureCounts.value[gestureName] = (gestureCounts.value[gestureName] || 0) + 1

      // 添加置信度分数
      confidenceScores.value.push(data.confidence)
      if (confidenceScores.value.length > 100) {
        confidenceScores.value = confidenceScores.value.slice(-100)
      }

      console.log(`👋 检测到手势: ${gestureName} (置信度: ${(data.confidence * 100).toFixed(1)}%)`)
    } catch (err) {
      console.error('❌ 处理手势结果错误:', err)
    }
  }

  const handleAnalysisStatus = (data) => {
    console.log('📊 分析状态更新:', data)

    if (data.status === 'started') {
      isAnalyzing.value = true
      sessionStartTime.value = Date.now()
    } else if (data.status === 'stopped') {
      isAnalyzing.value = false
      updateSessionStatistics()
    }
  }

  const handleConnectionChange = (status) => {
    isConnected.value = status === 'connected'

    if (status === 'disconnected') {
      isAnalyzing.value = false
      currentGesture.value = null
      realTimeData.value = null
    }
  }

  const handleError = (error) => {
    console.error('❌ WebSocket错误:', error)
    this.error = error.message
    isAnalyzing.value = false
  }

  // 辅助方法
  const updateStatistics = (data) => {
    statistics.value.totalDetections++

    if (data.confidence >= config.value.confidenceThreshold) {
      statistics.value.correctDetections++
    } else {
      statistics.value.falsePositives++
    }

    // 更新平均置信度
    const totalConfidence = confidenceScores.value.reduce((sum, score) => sum + score, 0)
    statistics.value.avgConfidence = totalConfidence / confidenceScores.value.length
  }

  const updateSessionStatistics = () => {
    if (sessionStartTime.value) {
      statistics.value.sessionDuration = sessionDuration.value
    }
  }

  const resetSessionData = () => {
    sessionStartTime.value = Date.now()
    gestureCounts.value = {}
    confidenceScores.value = []
    currentGesture.value = null
  }

  const getGestureHistory = (gestureName) => {
    return gestureHistory.value.filter(item => item.gesture === gestureName)
  }

  const getGestureTrend = (gestureName) => {
    const recent = getGestureHistory(gestureName).slice(0, 10)
    if (recent.length < 2) return 'stable'

    const firstHalf = recent.slice(0, Math.floor(recent.length / 2))
    const secondHalf = recent.slice(Math.floor(recent.length / 2))

    const firstCount = firstHalf.length
    const secondCount = secondHalf.length

    if (secondCount > firstCount) return 'increasing'
    if (secondCount < firstCount) return 'decreasing'
    return 'stable'
  }

  const getLastDetectedTime = (gestureName) => {
    const history = getGestureHistory(gestureName)
    return history.length > 0 ? history[0].timestamp : null
  }

  const getRecentGestures = (limit = 10) => {
    return gestureHistory.value.slice(0, limit)
  }

  const getMostCommonGesture = () => {
    const counts = {}
    gestureHistory.value.forEach(item => {
      counts[item.gesture] = (counts[item.gesture] || 0) + 1
    })

    return Object.entries(counts)
      .sort(([,a], [,b]) => b - a)
      .map(([gesture, count]) => ({ gesture, count }))[0]?.gesture || null
  }

  return {
    // 状态
    isConnected,
    isAnalyzing,
    currentGesture,
    gestureHistory,
    realTimeData,
    statistics,
    config,
    error,

    // 计算属性
    accuracy,
    avgConfidence,
    sessionDuration,
    gestureStats,

    // 方法
    connect,
    disconnect,
    startAnalysis,
    stopAnalysis,
    updateConfig,
    clearHistory,
    getRecentGestures,
    getMostCommonGesture
  }
})