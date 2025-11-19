import { defineStore } from 'pinia'
import { configApi } from '../api/config'

export const useConfigStore = defineStore('config', {
  state: () => ({
    gestureMappings: [],
    detectionParams: {
      confidence_threshold: 0.5,
      detection_interval: 0.1,
      camera_id: 0
    },
    userSettings: {
      theme: 'light',
      language: 'zh-CN',
      notifications: true
    },
    loading: false,
    error: null
  }),

  getters: {
    // 获取特定手势的映射
    getMappingByGesture: (state) => (gesture) => {
      return state.gestureMappings.find(mapping => mapping.gesture_code === gesture)
    },

    // 获取所有静态手势
    staticGestures: (state) => {
      return state.gestureMappings.filter(mapping => mapping.gesture_type === 'static')
    },

    // 获取所有动态手势
    dynamicGestures: (state) => {
      return state.gestureMappings.filter(mapping => mapping.gesture_type === 'dynamic')
    }
  },

  actions: {
    // 加载手势映射配置
    async loadGestureMappings(params = {}) {
      this.loading = true
      try {
        const response = await configApi.getGestureMappings(params)
        this.gestureMappings = response.mappings || []
        this.error = null
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // 加载检测参数
    async loadDetectionParams() {
      try {
        const response = await configApi.getDetectionParams()
        this.detectionParams = { ...this.detectionParams, ...response }
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // 加载用户设置
    async loadUserSettings() {
      try {
        const response = await configApi.getUserSettings()
        this.userSettings = { ...this.userSettings, ...response }
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // 更新手势映射
    async updateGestureMapping(gestureId, mappingData) {
      try {
        await configApi.updateGestureMapping(gestureId, mappingData)
        // 重新加载映射数据
        await this.loadGestureMappings()
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // 更新检测参数
    async updateDetectionParams(params) {
      try {
        await configApi.updateDetectionParams(params)
        this.detectionParams = { ...this.detectionParams, ...params }
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // 更新用户设置
    async updateUserSettings(settings) {
      try {
        await configApi.updateUserSettings(settings)
        this.userSettings = { ...this.userSettings, ...settings }
      } catch (error) {
        this.error = error.message
        throw error
      }
    }
  }
})