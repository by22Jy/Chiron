<template>
  <div class="modern-config">
    <!-- 页面标题区域 -->
    <div class="config-hero animate-slide-in-top">
      <div class="hero-content">
        <h1 class="hero-title">配置管理中心</h1>
        <p class="hero-subtitle">自定义手势映射和系统参数，打造专属的交互体验</p>
      </div>
      <div class="hero-visual">
        <div class="floating-icon animate-float">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="30" stroke="url(#gradient1)" stroke-width="2"/>
            <path d="M20 24h24v4H20zM20 32h24v4H20zM20 40h16v4H20z" stroke="url(#gradient1)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M40 40l6 6M40 48l6-6" stroke="url(#gradient1)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea"/>
                <stop offset="100%" style="stop-color:#764ba2"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
    </div>

    <!-- 配置内容区域 -->
    <div class="config-content">
      <!-- 手势映射配置 -->
      <div class="config-section animate-slide-in-left">
        <div class="section-header">
          <h2 class="section-title">手势映射配置</h2>
          <div class="section-actions">
            <button class="modern-btn secondary" @click="refreshMappings">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M1.5 8a6.5 6.5 0 0 1 10.5-5.1L12 4.5M14.5 8a6.5 6.5 0 0 1-10.5 5.1L4 11.5M9 4.5h3v3M7 11.5H4v-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              刷新
            </button>
            <button class="modern-btn primary" @click="addNewMapping">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 4v8M4 8h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              新建映射
            </button>
          </div>
        </div>

        <div class="tabs-container glass-card">
          <div class="modern-tabs">
            <div
              v-for="tab in gestureTabs"
              :key="tab.name"
              class="tab-item"
              :class="{ active: activeTab === tab.name }"
              @click="activeTab = tab.name"
            >
              <div class="tab-icon">{{ tab.icon }}</div>
              <span class="tab-label">{{ tab.label }}</span>
              <div class="tab-indicator"></div>
            </div>
          </div>

          <div class="tab-content">
            <!-- 静态手势 -->
            <div v-if="activeTab === 'static'" class="gesture-grid">
              <div
                v-for="gesture in staticGestures"
                :key="gesture.gesture_code"
                class="gesture-card glass-card animate-slide-in-up"
                :style="{ animationDelay: `${staticGestures.indexOf(gesture) * 0.1}s` }"
              >
                <div class="gesture-header">
                  <div class="gesture-icon">
                    <span class="gesture-emoji">{{ getGestureEmoji(gesture.gesture_code) }}</span>
                  </div>
                  <div class="gesture-actions">
                    <button class="icon-btn" @click="testMapping(gesture)" title="测试">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 1l2.5 5H13l-4 4 1 5-5-2.5L0 15l4-4-2.5-5h2.5z" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                    <button class="icon-btn" @click="editMapping(gesture)" title="编辑">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M12 2l2 2M4 10l8-8-2-2-8 8-2 4z" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                  </div>
                </div>

                <div class="gesture-info">
                  <h3 class="gesture-name">{{ gesture.gesture_name || gesture.gesture_code }}</h3>
                  <div class="gesture-code">
                    <span class="code-tag">{{ gesture.gesture_code }}</span>
                  </div>
                </div>

                <div class="gesture-action">
                  <div class="action-type">
                    <span class="action-icon">{{ getActionIcon(gesture.action?.type) }}</span>
                    <span class="action-label">{{ getActionLabel(gesture.action?.type) }}</span>
                  </div>
                  <div class="action-value">
                    {{ gesture.action?.value || '未配置' }}
                  </div>
                </div>

                <div class="gesture-status">
                  <div class="status-indicator" :class="{ active: gesture.action }"></div>
                  <span>{{ gesture.action ? '已启用' : '未配置' }}</span>
                </div>
              </div>
            </div>

            <!-- 动态手势 -->
            <div v-if="activeTab === 'dynamic'" class="gesture-grid">
              <div
                v-for="gesture in dynamicGestures"
                :key="gesture.gesture_code"
                class="gesture-card glass-card animate-slide-in-up"
                :style="{ animationDelay: `${dynamicGestures.indexOf(gesture) * 0.1}s` }"
              >
                <div class="gesture-header">
                  <div class="gesture-icon dynamic">
                    <span class="gesture-emoji">👋</span>
                    <div class="dynamic-badge">动态</div>
                  </div>
                  <div class="gesture-actions">
                    <button class="icon-btn" @click="testMapping(gesture)" title="测试">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 1l2.5 5H13l-4 4 1 5-5-2.5L0 15l4-4-2.5-5h2.5z" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                    <button class="icon-btn" @click="editMapping(gesture)" title="编辑">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M12 2l2 2M4 10l8-8-2-2-8 8-2 4z" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                  </div>
                </div>

                <div class="gesture-info">
                  <h3 class="gesture-name">{{ gesture.gesture_name || gesture.gesture_code }}</h3>
                  <div class="gesture-code">
                    <span class="code-tag dynamic">{{ gesture.gesture_code }}</span>
                  </div>
                </div>

                <div class="gesture-action">
                  <div class="action-type">
                    <span class="action-icon">{{ getActionIcon(gesture.action?.type) }}</span>
                    <span class="action-label">{{ getActionLabel(gesture.action?.type) }}</span>
                  </div>
                  <div class="action-value">
                    {{ gesture.action?.value || '未配置' }}
                  </div>
                </div>

                <div class="gesture-status">
                  <div class="status-indicator" :class="{ active: gesture.action }"></div>
                  <span>{{ gesture.action ? '已启用' : '未配置' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 检测参数配置 -->
      <div class="config-section animate-slide-in-left" style="animation-delay: 0.2s">
        <div class="section-header">
          <h2 class="section-title">检测参数配置</h2>
          <div class="section-badge">
            <div class="status-dot online"></div>
            <span>实时同步</span>
          </div>
        </div>

        <div class="params-grid">
          <div class="param-card glass-card">
            <div class="param-header">
              <div class="param-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" stroke="url(#gradient2)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <defs>
                    <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#4FACFE"/>
                      <stop offset="100%" style="stop-color:#00F2FE"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <h3>置信度阈值</h3>
            </div>
            <div class="param-control">
              <div class="slider-container">
                <input
                  type="range"
                  v-model="detectionParams.confidence_threshold"
                  min="0"
                  max="1"
                  step="0.05"
                  class="modern-slider"
                />
                <div class="slider-value">{{ Math.round(detectionParams.confidence_threshold * 100) }}%</div>
              </div>
              <p class="param-desc">调整手势识别的敏感度，越高越准确但可能漏检</p>
            </div>
          </div>

          <div class="param-card glass-card">
            <div class="param-header">
              <div class="param-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="url(#gradient3)" stroke-width="2"/>
                  <path d="M12 6v6l4 2" stroke="url(#gradient3)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <defs>
                    <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#FA8231"/>
                      <stop offset="100%" style="stop-color:#FED330"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <h3>检测间隔</h3>
            </div>
            <div class="param-control">
              <div class="number-input">
                <button class="input-btn" @click="detectionParams.detection_interval = Math.max(0.05, detectionParams.detection_interval - 0.05)">-</button>
                <input
                  type="number"
                  v-model="detectionParams.detection_interval"
                  min="0.05"
                  max="1"
                  step="0.05"
                  class="modern-input"
                />
                <button class="input-btn" @click="detectionParams.detection_interval = Math.min(1, detectionParams.detection_interval + 0.05)">+</button>
              </div>
              <p class="param-desc">设置检测频率，单位为秒，建议0.05-0.2秒</p>
            </div>
          </div>

          <div class="param-card glass-card">
            <div class="param-header">
              <div class="param-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <rect x="2" y="4" width="20" height="16" rx="2" stroke="url(#gradient4)" stroke-width="2"/>
                  <circle cx="8" cy="10" r="2" fill="url(#gradient4)"/>
                  <path d="M14 10h6M14 14h6" stroke="url(#gradient4)" stroke-width="2" stroke-linecap="round"/>
                  <defs>
                    <linearGradient id="gradient4" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#13B497"/>
                      <stop offset="100%" style="stop-color:#59D4A4"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <h3>摄像头ID</h3>
            </div>
            <div class="param-control">
              <div class="camera-selector">
                <select v-model="detectionParams.camera_id" class="modern-select">
                  <option v-for="i in 5" :key="i-1" :value="i-1">摄像头 {{ i-1 }}</option>
                </select>
              </div>
              <p class="param-desc">选择要使用的摄像头设备，通常0为默认摄像头</p>
            </div>
          </div>
        </div>

        <div class="param-actions">
          <button class="modern-btn success large" @click="saveDetectionParams">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M5 10l3 3 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            保存参数
          </button>
          <button class="modern-btn secondary" @click="resetDetectionParams">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10h12M10 4v12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            重置默认
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑映射对话框 -->
    <div v-if="editDialogVisible" class="modal-overlay" @click="editDialogVisible = false">
      <div class="modal-dialog glass-card animate-scale-in" @click.stop>
        <div class="modal-header">
          <h3>编辑手势映射</h3>
          <button class="close-btn" @click="editDialogVisible = false">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label>手势代码</label>
            <input v-model="editingMapping.gesture_code" class="modern-input" disabled />
          </div>

          <div class="form-group">
            <label>手势名称</label>
            <input v-model="editingMapping.gesture_name" class="modern-input" placeholder="输入手势名称" />
          </div>

          <div class="form-group">
            <label>动作类型</label>
            <select v-model="editingMapping.action_type" class="modern-select">
              <option value="">选择动作类型</option>
              <option value="hotkey">热键</option>
              <option value="click">鼠标点击</option>
              <option value="scroll">滚动</option>
              <option value="text">文本输入</option>
            </select>
          </div>

          <div class="form-group">
            <label>动作值</label>
            <input v-model="editingMapping.action_value" class="modern-input" placeholder="输入快捷键或动作参数" />
          </div>

          <div class="form-group">
            <label>描述</label>
            <textarea v-model="editingMapping.description" class="modern-textarea" placeholder="描述这个手势的用途"></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="modern-btn secondary" @click="editDialogVisible = false">取消</button>
          <button class="modern-btn primary" @click="saveMapping">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()

// 响应式数据
const activeTab = ref('static')
const editDialogVisible = ref(false)
const editingMapping = ref({
  gesture_code: '',
  gesture_name: '',
  action_type: '',
  action_value: '',
  description: ''
})

// 手势标签页配置
const gestureTabs = [
  { name: 'static', label: '静态手势', icon: '✋' },
  { name: 'dynamic', label: '动态手势', icon: '👋' }
]

// 计算属性
const staticGestures = computed(() => configStore.staticGestures || [
  { gesture_code: 'POINT_UP', gesture_name: '指向上方', action: { type: 'hotkey', value: 'space' } },
  { gesture_code: 'THUMBS_UP', gesture_name: '点赞', action: { type: 'click', value: 'left' } },
  { gesture_code: 'VICTORY', gesture_name: '胜利手势', action: { type: 'hotkey', value: 'ctrl+v' } },
  { gesture_code: 'OK_SIGN', gesture_name: 'OK手势', action: { type: 'hotkey', value: 'enter' } },
  { gesture_code: 'PEACE_SIGN', gesture_name: '和平手势', action: null },
  { gesture_code: 'ROCK_SIGN', gesture_name: '摇滚手势', action: null },
  { gesture_code: 'CALL_ME', gesture_name: '打电话', action: null },
  { gesture_code: 'FIST', gesture_name: '拳头', action: null }
])

const dynamicGestures = computed(() => configStore.dynamicGestures || [
  { gesture_code: 'swipe_left', gesture_name: '左滑', action: { type: 'scroll', value: 'left' } },
  { gesture_code: 'swipe_right', gesture_name: '右滑', action: { type: 'scroll', value: 'right' } },
  { gesture_code: 'swipe_up', gesture_name: '上滑', action: { type: 'hotkey', value: 'up' } },
  { gesture_code: 'swipe_down', gesture_name: '下滑', action: { type: 'hotkey', value: 'down' } }
])

const detectionParams = computed(() => configStore.detectionParams || {
  confidence_threshold: 0.5,
  detection_interval: 0.1,
  camera_id: 0
})

// 方法
const getGestureEmoji = (code) => {
  const emojiMap = {
    'POINT_UP': '☝️',
    'THUMBS_UP': '👍',
    'VICTORY': '✌️',
    'OK_SIGN': '👌',
    'PEACE_SIGN': '✌️',
    'ROCK_SIGN': '🤘',
    'CALL_ME': '🤙',
    'FIST': '✊',
    'swipe_left': '👈',
    'swipe_right': '👉',
    'swipe_up': '👆',
    'swipe_down': '👇'
  }
  return emojiMap[code] || '🤚'
}

const getActionIcon = (type) => {
  const iconMap = {
    'hotkey': '⌨️',
    'click': '🖱️',
    'scroll': '📜',
    'text': '📝',
    'mouse': '🖱️'
  }
  return iconMap[type] || '❓'
}

const getActionLabel = (type) => {
  const labelMap = {
    'hotkey': '热键',
    'click': '鼠标点击',
    'scroll': '滚动',
    'text': '文本输入',
    'mouse': '鼠标移动'
  }
  return labelMap[type] || '未配置'
}

const refreshMappings = async () => {
  try {
    await configStore.loadGestureMappings?.({
      username: 'admin',
      application: 'chrome.exe',
      os: 'windows'
    })
    console.log('配置已刷新')
  } catch (error) {
    console.error('刷新配置失败:', error)
  }
}

const testMapping = (mapping) => {
  console.log(`测试手势: ${mapping.gesture_code}`)
  // 这里可以调用后端API测试手势映射
}

const editMapping = (mapping) => {
  editingMapping.value = {
    gesture_code: mapping.gesture_code,
    gesture_name: mapping.gesture_name || '',
    action_type: mapping.action?.type || '',
    action_value: mapping.action?.value || '',
    description: mapping.action?.description || ''
  }
  editDialogVisible.value = true
}

const saveMapping = async () => {
  try {
    await configStore.updateGestureMapping?.(editingMapping.value.gesture_code, {
      gesture_name: editingMapping.value.gesture_name,
      action: {
        type: editingMapping.value.action_type,
        value: editingMapping.value.action_value,
        description: editingMapping.value.description
      }
    })
    editDialogVisible.value = false
    console.log('映射已保存')
  } catch (error) {
    console.error('保存映射失败:', error)
  }
}

const addNewMapping = () => {
  console.log('添加新映射功能开发中...')
}

const saveDetectionParams = async () => {
  try {
    await configStore.updateDetectionParams?.(detectionParams.value)
    console.log('检测参数已保存')
  } catch (error) {
    console.error('保存检测参数失败:', error)
  }
}

const resetDetectionParams = () => {
  if (configStore.detectionParams) {
    configStore.detectionParams = {
      confidence_threshold: 0.5,
      detection_interval: 0.1,
      camera_id: 0
    }
  }
}

// 生命周期
onMounted(async () => {
  await configStore.loadGestureMappings?.({
    username: 'admin',
    application: 'chrome.exe',
    os: 'windows'
  })
})
</script>

<style scoped>
@import '@/styles/modern.css';

.modern-config {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* 配置英雄区域 */
.config-hero {
  padding: 80px 20px 60px;
  background: radial-gradient(ellipse at bottom, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
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

.floating-icon {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 配置内容区域 */
.config-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
}

.config-section {
  margin-bottom: 60px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-actions {
  display: flex;
  gap: 12px;
}

.section-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
}

/* 现代化按钮 */
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

.modern-btn.large {
  padding: 12px 24px;
  font-size: 1rem;
}

.modern-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* 标签页容器 */
.tabs-container {
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
}

.modern-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px 12px 0 0;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  font-weight: 500;
  color: var(--text-secondary);
}

.tab-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.tab-item.active {
  background: var(--gradient-primary);
  color: white;
}

.tab-icon {
  font-size: 1.2rem;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.tab-item.active .tab-indicator {
  opacity: 1;
}

/* 手势网格 */
.gesture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  min-height: 400px;
}

.gesture-card {
  padding: 24px;
  border-radius: 20px;
  position: relative;
  transition: all 0.3s ease;
  cursor: pointer;
}

.gesture-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.gesture-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.gesture-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.gesture-icon.dynamic {
  background: var(--gradient-warning);
}

.gesture-emoji {
  font-size: 1.5rem;
}

.dynamic-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--accent-orange);
  color: white;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 0.625rem;
  font-weight: 600;
}

.gesture-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  transform: scale(1.1);
}

.gesture-info {
  margin-bottom: 16px;
}

.gesture-name {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.gesture-code {
  display: flex;
  gap: 8px;
}

.code-tag {
  padding: 4px 8px;
  background: var(--gradient-info);
  color: white;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.code-tag.dynamic {
  background: var(--gradient-warning);
}

.gesture-action {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.action-type {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.action-icon {
  font-size: 1rem;
}

.action-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.action-value {
  font-size: 0.875rem;
  color: var(--text-primary);
  font-family: 'Monaco', 'Menlo', monospace;
}

.gesture-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-secondary);
  transition: all 0.3s ease;
}

.status-indicator.active {
  background: var(--accent-green);
  box-shadow: 0 0 10px rgba(52, 199, 89, 0.6);
}

/* 参数网格 */
.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.param-card {
  padding: 24px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.param-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.12);
}

.param-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.param-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.param-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.param-control {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.modern-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--glass-bg);
  outline: none;
  -webkit-appearance: none;
}

.modern-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--gradient-primary);
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.slider-value {
  min-width: 48px;
  text-align: center;
  font-weight: 600;
  color: var(--accent-blue);
  font-size: 1.125rem;
}

.number-input {
  display: flex;
  align-items: center;
  gap: 0;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
}

.modern-input {
  flex: 1;
  background: var(--glass-bg);
  border: none;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
}

.modern-input:focus {
  background: rgba(255, 255, 255, 0.08);
}

.modern-select {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
  width: 100%;
}

.input-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: var(--glass-bg);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.input-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.input-btn:first-child {
  border-radius: 0;
}

.input-btn:last-child {
  border-radius: 0;
}

.param-desc {
  color: var(--text-secondary);
  font-size: 0.8125rem;
  line-height: 1.5;
  margin: 0;
}

.param-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 24px 0;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-dialog {
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 20px;
  padding: 0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 20px;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: var(--glass-bg);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.modern-textarea {
  width: 100%;
  min-height: 80px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
  resize: vertical;
  font-family: inherit;
}

.modern-textarea:focus {
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px 24px 24px;
  border-top: 1px solid var(--glass-border);
}

/* 动画 */
@keyframes slide-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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

.animate-slide-in-up {
  animation: slide-in-up 0.6s ease-out forwards;
  opacity: 0;
}

.animate-scale-in {
  animation: scale-in 0.3s ease-out;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .config-hero {
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

  .config-content {
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

  .gesture-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .params-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .modal-dialog {
    margin: 20px;
    max-width: calc(100% - 40px);
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }

  .tab-item {
    padding: 10px 16px;
  }

  .tab-label {
    display: none;
  }

  .section-title {
    font-size: 1.5rem;
  }
}
</style>