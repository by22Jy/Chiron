import { defineStore } from 'pinia'
import { monitorApi } from '../api/monitor'

export const useMonitorStore = defineStore('monitor', {
  state: () => ({
    systemStatus: {
      backend: 'unknown',
      ai_service: 'unknown',
      database: 'unknown',
      agent: 'unknown'
    },
    performance: {
      cpu_usage: 0,
      memory_usage: 0,
      gpu_usage: 0,
      network_in: 0,
      network_out: 0
    },
    statistics: {
      gesture_count: 0,
      success_rate: 0,
      avg_response_time: 0,
      total_requests: 0,
      error_count: 0
    },
    gestureStatus: {
      current_gesture: null,
      confidence: 0,
      last_update: null,
      is_detecting: false
    },
    loading: false,
    error: null,
    realTimeData: null
  }),

  getters: {
    // 获取整体系统健康状态
    systemHealth: (state) => {
      const services = Object.values(state.systemStatus)
      const healthyServices = services.filter(status => status === 'healthy')
      return {
        overall: healthyServices.length === services.length ? 'healthy' : 'warning',
        healthyServices: healthyServices.length,
        totalServices: services.length
      }
    },

    // 获取性能等级
    performanceLevel: (state) => {
      const avgUsage = (state.performance.cpu_usage + state.performance.memory_usage) / 2
      if (avgUsage < 50) return 'good'
      if (avgUsage < 80) return 'warning'
      return 'critical'
    }
  },

  actions: {
    // 加载系统状态
    async loadSystemStatus() {
      try {
        const response = await monitorApi.getSystemStatus()
        this.systemStatus = { ...this.systemStatus, ...response }
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // 加载性能指标
    async loadPerformanceMetrics() {
      try {
        const response = await monitorApi.getPerformanceMetrics()
        this.performance = { ...this.performance, ...response }
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // 加载统计数据
    async loadStatistics() {
      try {
        const response = await monitorApi.getStatistics()
        this.statistics = { ...this.statistics, ...response }
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // 加载手势识别状态
    async loadGestureStatus() {
      try {
        const response = await monitorApi.getGestureStatus()
        this.gestureStatus = { ...this.gestureStatus, ...response }
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // 加载所有监控数据
    async loadAllMonitoringData() {
      this.loading = true
      try {
        await Promise.all([
          this.loadSystemStatus(),
          this.loadPerformanceMetrics(),
          this.loadStatistics(),
          this.loadGestureStatus()
        ])
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // 更新实时数据
    updateRealTimeData(data) {
      this.realTimeData = data
      if (data.performance) {
        this.performance = { ...this.performance, ...data.performance }
      }
      if (data.gesture) {
        this.gestureStatus = { ...this.gestureStatus, ...data.gesture }
      }
      if (data.statistics) {
        this.statistics = { ...this.statistics, ...data.statistics }
      }
    },

    // 重置错误状态
    clearError() {
      this.error = null
    }
  }
})