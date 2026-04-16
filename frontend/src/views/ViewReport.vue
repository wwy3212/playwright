<template>
  <div class="view-report-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测试报告</span>
          <div>
            <el-button size="small" @click="loadReports">刷新</el-button>
            <el-button size="small" type="danger" @click="clearResults">清空记录</el-button>
          </div>
        </div>
      </template>

      <!-- 统计概览 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-statistic title="总执行次数" :value="stats.total" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="通过" :value="stats.passed">
            <template #suffix>
              <span class="stat-suffix passed">次</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="失败" :value="stats.failed">
            <template #suffix>
              <span class="stat-suffix failed">次</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="通过率" :value="passRate" suffix="%" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 结果列表 -->
    <el-card class="result-card">
      <template #header>
        <div class="card-header">
          <span>执行记录</span>
          <el-select
            v-model="filterStatus"
            placeholder="筛选状态"
            clearable
            style="width: 150px"
            @change="loadReports"
          >
            <el-option label="通过" value="passed" />
            <el-option label="失败" value="failed" />
            <el-option label="错误" value="error" />
            <el-option label="跳过" value="skipped" />
          </el-select>
        </div>
      </template>

      <el-table :data="reports" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="test_case_id" label="用例 ID" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="执行时间 (s)" width="120" />
        <el-table-column prop="executed_at" label="执行时间" width="180" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row.id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadReports"
          @current-change="loadReports"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="执行详情"
      width="900px"
    >
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="执行 ID">{{ currentDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="测试用例 ID">{{ currentDetail.test_case_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentDetail.status)">
              {{ getStatusText(currentDetail.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">{{ currentDetail.duration }}s</el-descriptions-item>
          <el-descriptions-item label="执行于" :span="2">
            {{ currentDetail.executed_at }}
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px">输出日志：</h4>
        <pre class="log-output">{{ currentDetail.output_log || '无日志输出' }}</pre>

        <h4 style="margin-top: 20px">错误信息：</h4>
        <pre class="error-output">{{ currentDetail.error_message || '无错误信息' }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const reports = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterStatus = ref('')
const detailVisible = ref(false)
const currentDetail = ref(null)

const stats = reactive({
  total: 0,
  passed: 0,
  failed: 0
})

const passRate = computed(() => {
  if (stats.total === 0) return 0
  return ((stats.passed / stats.total) * 100).toFixed(1)
})

// 加载测试报告
const loadReports = async () => {
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }

    const response = await axios.get('/api/execution/results', { params })

    if (response.data.success) {
      reports.value = response.data.results
      total.value = response.data.pagination.total
      currentPage.value = response.data.pagination.page
      pageSize.value = response.data.pagination.per_page

      // 加载统计数据
      loadStats()
    }
  } catch (error) {
    ElMessage.error('加载报告失败')
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await axios.get('/api/execution/results', {
      params: { per_page: 1000 }
    })

    if (response.data.success) {
      const results = response.data.results
      stats.total = results.length
      stats.passed = results.filter(r => r.status === 'passed').length
      stats.failed = results.filter(r => r.status === 'failed').length
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 清空结果
const clearResults = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有测试结果记录吗？此操作不可恢复。', '确认清空', {
      type: 'warning'
    })

    const response = await axios.delete('/api/execution/results')
    if (response.data.success) {
      ElMessage.success('已清空所有记录')
      loadReports()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败')
    }
  }
}

// 查看详情
const viewDetail = async (resultId) => {
  try {
    const response = await axios.get(`/api/execution/results/${resultId}`)
    if (response.data.success) {
      currentDetail.value = response.data.result
      detailVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    passed: 'success',
    failed: 'danger',
    error: 'warning',
    skipped: 'info'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    passed: '通过',
    failed: '失败',
    error: '错误',
    skipped: '跳过'
  }
  return texts[status] || status
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.view-report-container {
  max-width: 1400px;
  margin: 0 auto;
}

.stats-row {
  margin-top: 20px;
  padding: 10px;
}

.stat-suffix.passed {
  color: #67c23a;
}

.stat-suffix.failed {
  color: #f56c6c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.detail-content {
  max-height: 600px;
  overflow-y: auto;
}

.log-output,
.error-output {
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

.error-output {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>
