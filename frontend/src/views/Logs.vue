<template>
  <div class="logs-page">
    <!-- 日志搜索和过滤 -->
    <el-card class="logs-card" header="日志搜索和过滤">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="输入搜索关键词"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="日志级别">
          <el-select v-model="searchForm.level" placeholder="选择级别" clearable>
            <el-option label="全部" value="" />
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
        </el-form-item>

        <el-form-item label="组件">
          <el-select v-model="searchForm.component" placeholder="选择组件" clearable>
            <el-option label="全部" value="" />
            <el-option label="Agent" value="agent" />
            <el-option label="Video" value="video" />
            <el-option label="Detector" value="detector" />
            <el-option label="Standalone" value="standalone" />
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="searching">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="success" @click="refreshLogs" :loading="refreshing">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 快捷过滤 -->
      <div class="quick-filters">
        <span class="filter-label">快捷过滤:</span>
        <el-button size="small" @click="filterByLevel('ERROR')">
          <el-tag type="danger">仅错误</el-tag>
        </el-button>
        <el-button size="small" @click="filterByLevel('WARNING')">
          <el-tag type="warning">仅警告</el-tag>
        </el-button>
        <el-button size="small" @click="showRecentLogs">
          <el-tag type="info">最近1小时</el-tag>
        </el-button>
        <el-button size="small" @click="showTodayLogs">
          <el-tag>今天</el-tag>
        </el-button>
      </div>
    </el-card>

    <!-- 日志列表 -->
    <el-card class="logs-card" header="日志列表">
      <template #header>
        <div class="card-header">
          <span>日志列表 ({{ filteredLogs.length }} 条)</span>
          <div class="header-actions">
            <el-button size="small" @click="exportLogs">
              <el-icon><Download /></el-icon>
              导出日志
            </el-button>
            <el-button size="small" type="danger" @click="clearLogs">
              <el-icon><Delete /></el-icon>
              清理日志
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="paginatedLogs"
        style="width: 100%"
        :height="tableHeight"
        v-loading="loading"
        @row-click="viewLogDetail"
      >
        <el-table-column prop="timestamp" label="时间" width="180" fixed="left">
          <template #default="scope">
            {{ formatDateTime(scope.row.timestamp) }}
          </template>
        </el-table-column>

        <el-table-column prop="level" label="级别" width="100">
          <template #default="scope">
            <el-tag :type="getLogLevelType(scope.row.level)" size="small">
              {{ scope.row.level }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="component" label="组件" width="120">
          <template #default="scope">
            <el-tag :type="getComponentType(scope.row.component)" size="small">
              {{ scope.row.component }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="message" label="消息内容" min-width="300">
          <template #default="scope">
            <div class="log-message">
              <span v-if="scope.row.highlight" v-html="scope.row.highlightedMessage"></span>
              <span v-else>{{ scope.row.message }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="thread" label="线程" width="100" />

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" @click.stop="viewLogDetail(scope.row)">
              详情
            </el-button>
            <el-button size="small" type="danger" @click.stop="copyLog(scope.row)">
              复制
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100, 200]"
          :total="filteredLogs.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 日志详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="日志详情" width="800px">
      <div v-if="selectedLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="时间">
            {{ formatDateTime(selectedLog.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="getLogLevelType(selectedLog.level)">
              {{ selectedLog.level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="组件">
            <el-tag :type="getComponentType(selectedLog.component)">
              {{ selectedLog.component }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="线程">
            {{ selectedLog.thread }}
          </el-descriptions-item>
          <el-descriptions-item label="消息内容" :span="2">
            <div class="detail-message">{{ selectedLog.message }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 相关上下文 -->
        <div v-if="logContext.length > 0" class="log-context">
          <h4>相关上下文</h4>
          <div class="context-lines">
            <div
              v-for="(line, index) in logContext"
              :key="index"
              class="context-line"
              :class="{ 'target-line': line.timestamp === selectedLog.timestamp }"
            >
              <span class="line-time">{{ formatDateTime(line.timestamp) }}</span>
              <span class="line-level">{{ line.level }}</span>
              <span class="line-message">{{ line.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Download, Delete } from '@element-plus/icons-vue'

// 响应式数据
const searchForm = ref({
  keyword: '',
  level: '',
  component: '',
  dateRange: []
})

const logs = ref([])
const loading = ref(false)
const searching = ref(false)
const refreshing = ref(false)
const detailDialogVisible = ref(false)
const selectedLog = ref(null)
const logContext = ref([])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(50)

// 模拟日志数据
const mockLogs = ref([
  {
    timestamp: new Date('2024-01-20T10:30:15'),
    level: 'INFO',
    component: 'agent',
    message: '[AGENT] 手势检测: SWIPE_LEFT (confidence: 0.92)',
    thread: 'main'
  },
  {
    timestamp: new Date('2024-01-20T10:30:14'),
    level: 'DEBUG',
    component: 'detector',
    message: '[DETECTOR] Recognized SWIPE_LEFT (dx=-0.234 < 0)',
    thread: 'detector-thread'
  },
  {
    timestamp: new Date('2024-01-20T10:30:13'),
    level: 'ERROR',
    component: 'video',
    message: '[VIDEO] Failed to capture frame: Camera busy',
    thread: 'capture-thread'
  },
  {
    timestamp: new Date('2024-01-20T10:30:12'),
    level: 'WARNING',
    component: 'detector',
    message: '[DETECTOR] Distance too small: 0.15 < 0.20',
    thread: 'detector-thread'
  }
])

// 计算属性
const filteredLogs = computed(() => {
  let filtered = logs.value

  if (searchForm.keyword) {
    const keyword = searchForm.keyword.toLowerCase()
    filtered = filtered.filter(log =>
      log.message.toLowerCase().includes(keyword) ||
      log.component.toLowerCase().includes(keyword)
    )
  }

  if (searchForm.level) {
    filtered = filtered.filter(log => log.level === searchForm.level)
  }

  if (searchForm.component) {
    filtered = filtered.filter(log => log.component === searchForm.component)
  }

  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    const [start, end] = searchForm.dateRange
    filtered = filtered.filter(log => {
      const logTime = new Date(log.timestamp)
      return logTime >= new Date(start) && logTime <= new Date(end)
    })
  }

  return filtered
})

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLogs.value.slice(start, end)
})

const tableHeight = computed(() => {
  return window.innerHeight - 400
})

// 方法
const formatDateTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

const getLogLevelType = (level) => {
  const types = {
    DEBUG: 'info',
    INFO: 'success',
    WARNING: 'warning',
    ERROR: 'danger'
  }
  return types[level] || 'info'
}

const getComponentType = (component) => {
  const types = {
    agent: 'primary',
    video: 'success',
    detector: 'warning',
    standalone: 'info'
  }
  return types[component] || 'info'
}

const handleSearch = async () => {
  searching.value = true
  try {
    // 这里可以调用API搜索日志
    await new Promise(resolve => setTimeout(resolve, 500))

    // 高亮搜索结果
    if (searchForm.keyword) {
      const keyword = searchForm.keyword
      filteredLogs.value.forEach(log => {
        if (log.message.includes(keyword)) {
          log.highlight = true
          log.highlightedMessage = log.message.replace(
            new RegExp(keyword, 'gi'),
            match => `<mark>${match}</mark>`
          )
        }
      })
    }

    ElMessage.success(`找到 ${filteredLogs.value.length} 条日志`)
  } catch (error) {
    ElMessage.error('搜索日志失败')
  } finally {
    searching.value = false
  }
}

const resetSearch = () => {
  searchForm.value = {
    keyword: '',
    level: '',
    component: '',
    dateRange: []
  }
  currentPage.value = 1
}

const refreshLogs = async () => {
  refreshing.value = true
  try {
    await loadLogs()
    ElMessage.success('日志已刷新')
  } catch (error) {
    ElMessage.error('刷新日志失败')
  } finally {
    refreshing.value = false
  }
}

const filterByLevel = (level) => {
  searchForm.value.level = searchForm.value.level === level ? '' : level
  handleSearch()
}

const showRecentLogs = () => {
  const now = new Date()
  const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)
  searchForm.value.dateRange = [
    oneHourAgo.toISOString().slice(0, 19).replace('T', ' '),
    now.toISOString().slice(0, 19).replace('T', ' ')
  ]
  handleSearch()
}

const showTodayLogs = () => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  searchForm.value.dateRange = [
    today.toISOString().slice(0, 19).replace('T', ' '),
    now.toISOString().slice(0, 19).replace('T', ' ')
  ]
  handleSearch()
}

const exportLogs = () => {
  ElMessage.info('导出日志功能开发中...')
}

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清理日志吗？此操作不可恢复。',
      '确认清理',
      {
        type: 'warning'
      }
    )

    // 这里可以调用API清理日志
    ElMessage.success('日志清理成功')
  } catch (error) {
    // 用户取消
  }
}

const viewLogDetail = (log) => {
  selectedLog.value = log
  detailDialogVisible.value = true

  // 模拟获取上下文日志
  const logIndex = filteredLogs.value.findIndex(l => l.timestamp === log.timestamp)
  const start = Math.max(0, logIndex - 5)
  const end = Math.min(filteredLogs.value.length, logIndex + 5)
  logContext.value = filteredLogs.value.slice(start, end)
}

const copyLog = async (log) => {
  try {
    await navigator.clipboard.writeText(
      `${formatDateTime(log.timestamp)} [${log.level}] [${log.component}] ${log.message}`
    )
    ElMessage.success('日志已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const loadLogs = async () => {
  loading.value = true
  try {
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 500))

    // 使用模拟数据
    logs.value = [...mockLogs.value]

    // 生成更多模拟数据
    for (let i = 0; i < 50; i++) {
      const timestamp = new Date(Date.now() - Math.random() * 3600000)
      const levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
      const components = ['agent', 'video', 'detector', 'standalone']

      logs.value.push({
        timestamp,
        level: levels[Math.floor(Math.random() * levels.length)],
        component: components[Math.floor(Math.random() * components.length)],
        message: `模拟日志消息 ${i + 1}`,
        thread: `thread-${Math.floor(Math.random() * 3)}`
      })
    }

    // 按时间倒序排列
    logs.value.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  } catch (error) {
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.logs-page {
  padding: 0;
}

.logs-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.quick-filters {
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
}

.log-message {
  word-break: break-all;
  line-height: 1.4;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.log-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-message {
  background: #F5F7FA;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  line-height: 1.4;
}

.log-context {
  margin-top: 20px;
  border-top: 1px solid #E4E7ED;
  padding-top: 20px;
}

.log-context h4 {
  margin-bottom: 15px;
  color: #303133;
}

.context-lines {
  max-height: 200px;
  overflow-y: auto;
  background: #F8F9FA;
  padding: 10px;
  border-radius: 4px;
}

.context-line {
  display: flex;
  gap: 10px;
  padding: 5px 0;
  border-bottom: 1px solid #E4E7ED;
  font-family: monospace;
  font-size: 12px;
}

.context-line:last-child {
  border-bottom: none;
}

.target-line {
  background: #FFF7E6;
}

.line-time {
  color: #909399;
  min-width: 140px;
}

.line-level {
  color: #606266;
  min-width: 60px;
}

.line-message {
  color: #303133;
  flex: 1;
}

:deep(.mark) {
  background: #FFE6B3;
  padding: 1px 2px;
  border-radius: 2px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .quick-filters {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 5px;
  }

  .pagination {
    text-align: center;
  }
}
</style>