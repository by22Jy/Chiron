import apiClient from './index'

// 监控API
export const monitorApi = {
  // 获取系统状态
  getSystemStatus() {
    return apiClient.get('/monitor/status')
  },

  // 获取性能指标
  getPerformanceMetrics() {
    return apiClient.get('/monitor/performance')
  },

  // 获取统计数据
  getStatistics() {
    return apiClient.get('/monitor/statistics')
  },

  // 获取手势识别状态
  getGestureStatus() {
    return apiClient.get('/monitor/gesture')
  }
}