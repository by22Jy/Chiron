<template>
  <div class="config-page">
    <!-- 手势映射配置 -->
    <el-card class="config-card" header="手势映射配置">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 静态手势 -->
        <el-tab-pane label="静态手势" name="static">
          <el-table :data="staticGestures" style="width: 100%">
            <el-table-column prop="gesture_code" label="手势代码" width="150">
              <template #default="scope">
                <el-tag>{{ scope.row.gesture_code }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="gesture_name" label="手势名称" width="150" />
            <el-table-column label="动作类型" width="120">
              <template #default="scope">
                <el-tag :type="getActionTypeColor(scope.row.action?.type)">
                  {{ scope.row.action?.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="action.value" label="动作值" width="200" />
            <el-table-column prop="action.description" label="描述" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="testMapping(scope.row)">测试</el-button>
                <el-button size="small" type="primary" @click="editMapping(scope.row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 动态手势 -->
        <el-tab-pane label="动态手势" name="dynamic">
          <el-table :data="dynamicGestures" style="width: 100%">
            <el-table-column prop="gesture_code" label="手势代码" width="150">
              <template #default="scope">
                <el-tag type="warning">{{ scope.row.gesture_code }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="gesture_name" label="手势名称" width="150" />
            <el-table-column label="动作类型" width="120">
              <template #default="scope">
                <el-tag :type="getActionTypeColor(scope.row.action?.type)">
                  {{ scope.row.action?.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="action.value" label="动作值" width="200" />
            <el-table-column prop="action.description" label="描述" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="testMapping(scope.row)">测试</el-button>
                <el-button size="small" type="primary" @click="editMapping(scope.row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <div class="config-actions">
        <el-button type="success" @click="refreshMappings">
          <el-icon><Refresh /></el-icon>
          刷新配置
        </el-button>
        <el-button type="primary" @click="addNewMapping">
          <el-icon><Plus /></el-icon>
          添加映射
        </el-button>
      </div>
    </el-card>

    <!-- 检测参数配置 -->
    <el-card class="config-card" header="检测参数配置">
      <el-form :model="detectionParams" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="置信度阈值">
              <el-slider
                v-model="detectionParams.confidence_threshold"
                :min="0"
                :max="1"
                :step="0.05"
                :format-tooltip="formatConfidence"
              />
              <span>{{ (detectionParams.confidence_threshold * 100).toFixed(0) }}%</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="检测间隔">
              <el-input-number
                v-model="detectionParams.detection_interval"
                :min="0.05"
                :max="1"
                :step="0.05"
                :precision="2"
              />
              <span style="margin-left: 10px;">秒</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="摄像头ID">
              <el-input-number
                v-model="detectionParams.camera_id"
                :min="0"
                :max="10"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item>
              <el-button type="primary" @click="saveDetectionParams">保存参数</el-button>
              <el-button @click="resetDetectionParams">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 用户设置 -->
    <el-card class="config-card" header="用户设置">
      <el-form :model="userSettings" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="界面主题">
              <el-select v-model="userSettings.theme">
                <el-option label="浅色主题" value="light" />
                <el-option label="深色主题" value="dark" />
                <el-option label="自动" value="auto" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="语言">
              <el-select v-model="userSettings.language">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="通知">
              <el-switch v-model="userSettings.notifications" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="saveUserSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 编辑映射对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑手势映射" width="600px">
      <el-form :model="editingMapping" label-width="120px">
        <el-form-item label="手势代码">
          <el-input v-model="editingMapping.gesture_code" disabled />
        </el-form-item>
        <el-form-item label="手势名称">
          <el-input v-model="editingMapping.gesture_name" />
        </el-form-item>
        <el-form-item label="动作类型">
          <el-select v-model="editingMapping.action_type">
            <el-option label="热键" value="hotkey" />
            <el-option label="鼠标点击" value="click" />
            <el-option label="滚动" value="scroll" />
            <el-option label="文本输入" value="text" />
          </el-select>
        </el-form-item>
        <el-form-item label="动作值">
          <el-input v-model="editingMapping.action_value" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editingMapping.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMapping">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useConfigStore } from '@/stores/config'
import { ElMessage } from 'element-plus'
import { Refresh, Plus } from '@element-plus/icons-vue'

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

// 计算属性
const staticGestures = computed(() => configStore.staticGestures)
const dynamicGestures = computed(() => configStore.dynamicGestures)
const detectionParams = computed(() => configStore.detectionParams)
const userSettings = computed(() => configStore.userSettings)

// 方法
const getActionTypeColor = (type) => {
  const colors = {
    hotkey: 'primary',
    click: 'success',
    scroll: 'warning',
    text: 'info',
    mouse: 'danger'
  }
  return colors[type] || 'info'
}

const formatConfidence = (value) => {
  return `${(value * 100).toFixed(0)}%`
}

const refreshMappings = async () => {
  try {
    await configStore.loadGestureMappings()
    ElMessage.success('配置已刷新')
  } catch (error) {
    ElMessage.error('刷新配置失败')
  }
}

const testMapping = (mapping) => {
  ElMessage.info(`测试手势: ${mapping.gesture_code}`)
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
    await configStore.updateGestureMapping(editingMapping.value.gesture_code, {
      gesture_name: editingMapping.value.gesture_name,
      action: {
        type: editingMapping.value.action_type,
        value: editingMapping.value.action_value,
        description: editingMapping.value.description
      }
    })
    editDialogVisible.value = false
    ElMessage.success('映射已保存')
  } catch (error) {
    ElMessage.error('保存映射失败')
  }
}

const addNewMapping = () => {
  ElMessage.info('添加新映射功能开发中...')
}

const saveDetectionParams = async () => {
  try {
    await configStore.updateDetectionParams(detectionParams.value)
    ElMessage.success('检测参数已保存')
  } catch (error) {
    ElMessage.error('保存检测参数失败')
  }
}

const resetDetectionParams = () => {
  configStore.detectionParams = {
    confidence_threshold: 0.5,
    detection_interval: 0.1,
    camera_id: 0
  }
}

const saveUserSettings = async () => {
  try {
    await configStore.updateUserSettings(userSettings.value)
    ElMessage.success('用户设置已保存')
  } catch (error) {
    ElMessage.error('保存用户设置失败')
  }
}

// 生命周期
onMounted(async () => {
  await configStore.loadGestureMappings()
})
</script>

<style scoped>
.config-page {
  padding: 0;
}

.config-card {
  margin-bottom: 20px;
}

.config-actions {
  margin-top: 20px;
  text-align: right;
}

.config-actions .el-button {
  margin-left: 10px;
}

:deep(.el-tabs__content) {
  padding: 20px 0;
}

:deep(.el-table) {
  margin-bottom: 20px;
}
</style>