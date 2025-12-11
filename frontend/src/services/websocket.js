/**
 * WebSocket 服务 - 实时手势识别连接
 * YOLO-LLM Platform
 *
 * 提供与AI服务的实时WebSocket连接，支持手势识别流式处理
 */

import { ElMessage, ElNotification } from 'element-plus'

export class WebSocketService {
  constructor() {
    this.ws = null
    this.isConnected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
    this.heartbeatInterval = null
    this.messageHandlers = new Map()
    this.connectionHandlers = []
    this.errorHandlers = []
    this.url = this.getWebSocketUrl()
  }

  /**
   * 获取WebSocket连接URL
   */
  getWebSocketUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const port = window.location.port === '5173' ? '8000' : window.location.port
    return `${protocol}//${host}:${port}/ws/analyze`
  }

  /**
   * 建立WebSocket连接
   */
  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket已连接')
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('✅ WebSocket连接成功')
          this.isConnected = true
          this.reconnectAttempts = 0
          this.startHeartbeat()

          ElNotification({
            title: '连接成功',
            message: '实时手势识别服务已连接',
            type: 'success',
            duration: 3000,
            showClose: false
          })

          this.connectionHandlers.forEach(handler => handler('connected'))
          resolve()
        }

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data)
        }

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket错误:', error)
          this.isConnected = false

          ElNotification({
            title: '连接错误',
            message: '实时手势识别服务连接失败',
            type: 'error',
            duration: 5000
          })

          this.errorHandlers.forEach(handler => handler(error))
          reject(error)
        }

        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket连接关闭:', event.code, event.reason)
          this.isConnected = false
          this.stopHeartbeat()

          this.connectionHandlers.forEach(handler => handler('disconnected'))

          // 非正常关闭时自动重连
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect()
          }
        }
      } catch (error) {
        console.error('❌ WebSocket连接失败:', error)
        reject(error)
      }
    })
  }

  /**
   * 处理接收到的消息
   */
  handleMessage(data) {
    try {
      const message = JSON.parse(data)

      // 处理心跳响应
      if (message.type === 'pong') {
        return
      }

      // 处理手势识别结果
      if (message.type === 'gesture_result') {
        const handler = this.messageHandlers.get('gesture_result')
        if (handler) {
          handler(message.data)
        }
        return
      }

      // 处理分析状态
      if (message.type === 'analysis_status') {
        const handler = this.messageHandlers.get('analysis_status')
        if (handler) {
          handler(message.data)
        }
        return
      }

      // 处理错误消息
      if (message.type === 'error') {
        console.error('❌ 服务器错误:', message.message)
        ElMessage.error(`服务器错误: ${message.message}`)
        return
      }

      console.log('📨 收到消息:', message)
    } catch (error) {
      console.error('❌ 消息解析错误:', error)
    }
  }

  /**
   * 发送消息
   */
  send(message) {
    if (!this.isConnected || !this.ws) {
      console.warn(' WebSocket未连接，无法发送消息')
      return false
    }

    try {
      const data = typeof message === 'string' ? message : JSON.stringify(message)
      this.ws.send(data)
      console.log('📤 发送消息:', message)
      return true
    } catch (error) {
      console.error('❌ 发送消息失败:', error)
      return false
    }
  }

  /**
   * 开始实时手势分析
   */
  startRealtimeAnalysis(config = {}) {
    const message = {
      type: 'start_realtime',
      data: {
        fps: config.fps || 10,
        confidence_threshold: config.confidenceThreshold || 0.7,
        gesture_types: config.gestureTypes || ['hand', 'pose', 'emotion'],
        enable_tracking: config.enableTracking || true,
        ...config
      }
    }
    return this.send(message)
  }

  /**
   * 停止实时手势分析
   */
  stopRealtimeAnalysis() {
    const message = {
      type: 'stop_realtime'
    }
    return this.send(message)
  }

  /**
   * 发送图片进行分析
   */
  sendImage(imageData, config = {}) {
    const message = {
      type: 'analyze_image',
      data: {
        image: imageData,
        timestamp: Date.now(),
        ...config
      }
    }
    return this.send(message)
  }

  /**
   * 注册消息处理器
   */
  onMessage(type, handler) {
    this.messageHandlers.set(type, handler)
  }

  /**
   * 注册连接状态处理器
   */
  onConnection(handler) {
    this.connectionHandlers.push(handler)
  }

  /**
   * 注册错误处理器
   */
  onError(handler) {
    this.errorHandlers.push(handler)
  }

  /**
   * 移除消息处理器
   */
  offMessage(type) {
    this.messageHandlers.delete(type)
  }

  /**
   * 开始心跳
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.send({ type: 'ping' })
    }, 30000) // 30秒心跳
  }

  /**
   * 停止心跳
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 计划重连
   */
  scheduleReconnect() {
    this.reconnectAttempts++
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1)

    console.log(`🔄 ${delay/1000}秒后尝试第${this.reconnectAttempts}次重连...`)

    ElNotification({
      title: '连接断开',
      message: `${delay/1000}秒后尝试第${this.reconnectAttempts}次重连`,
      type: 'warning',
      duration: 3000,
      showClose: false
    })

    setTimeout(() => {
      this.connect().catch(() => {
        // 重连失败会在connect方法中处理
      })
    }, delay)
  }

  /**
   * 手动重连
   */
  reconnect() {
    this.disconnect()
    this.reconnectAttempts = 0
    return this.connect()
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect')
      this.ws = null
    }
    this.isConnected = false
    this.stopHeartbeat()
  }

  /**
   * 获取连接状态
   */
  getConnectionStatus() {
    if (!this.ws) return 'disconnected'

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return 'connected'
      case WebSocket.CLOSING: return 'closing'
      case WebSocket.CLOSED: return 'disconnected'
      default: return 'unknown'
    }
  }

  /**
   * 检查是否连接
   */
  isConnectionActive() {
    return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// 创建全局WebSocket实例
export const wsService = new WebSocketService()

// 导出默认实例
export default wsService