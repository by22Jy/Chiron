import apiClient from './index'

// 配置管理API
export const configApi = {
  // 获取手势映射配置
  getGestureMappings(params = {}) {
    return apiClient.get('/config', { params })
  },

  // 更新手势映射
  updateGestureMapping(gestureId, mappingData) {
    return apiClient.post(`/config/mappings/${gestureId}`, mappingData)
  },

  // 获取检测参数
  getDetectionParams() {
    return apiClient.get('/config/detection')
  },

  // 更新检测参数
  updateDetectionParams(params) {
    return apiClient.post('/config/detection', params)
  },

  // 获取用户设置
  getUserSettings() {
    return apiClient.get('/config/user')
  },

  // 更新用户设置
  updateUserSettings(settings) {
    return apiClient.post('/config/user', settings)
  }
}