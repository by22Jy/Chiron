import apiClient from './index'

// 日志管理API
export const logsApi = {
  // 获取日志列表
  getLogs(params = {}) {
    return apiClient.get('/logs', { params })
  },

  // 获取日志详情
  getLogDetail(logId) {
    return apiClient.get(`/logs/${logId}`)
  },

  // 下载日志文件
  downloadLog(logId) {
    return apiClient.get(`/logs/${logId}/download`, {
      responseType: 'blob'
    })
  },

  // 清理日志
  clearLogs(days = 7) {
    return apiClient.post('/logs/clear', { days })
  },

  // 搜索日志
  searchLogs(query, params = {}) {
    return apiClient.get('/logs/search', {
      params: { ...params, q: query }
    })
  }
}