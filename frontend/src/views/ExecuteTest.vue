<template>
  <div class="execute-test-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>执行测试用例</span>
          <el-button type="success" :loading="executingAll" @click="runAllTests">
            <el-icon><VideoPlay /></el-icon>
            执行所有测试
          </el-button>
        </div>
      </template>

      <el-table :data="testCases" style="width: 100%">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <h4>Python 代码：</h4>
              <pre class="code-preview">{{ row.py_content.substring(0, 500) }}...</pre>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="file_path" label="文件名" width="200" />
        <el-table-column label="最近执行状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.last_status)" size="small">
              {{ row.last_status || '未执行' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_executed_at" label="最近执行时间" width="180" />
        <el-table-column label="操作" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :loading="executingId === row.id"
              @click="runTest(row.id)"
            >
              执行
            </el-button>
            <el-button size="small" @click="viewResult(row.id)">
              查看结果
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 执行日志 -->
    <el-dialog
      v-model="logDialogVisible"
      title="执行日志"
      width="800px"
    >
      <div v-if="currentLog" class="log-container">
        <div class="log-header">
          <el-tag :type="getStatusType(currentLog.status)">
            {{ currentLog.status }}
          </el-tag>
          <span>执行时间：{{ currentLog.duration }}s</span>
        </div>
        <pre class="log-content">{{ currentLog.stdout }}</pre>
        <pre v-if="currentLog.stderr" class="log-error">{{ currentLog.stderr }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const testCases = ref([])
const executingId = ref(null)
const executingAll = ref(false)
const logDialogVisible = ref(false)
const currentLog = ref(null)

// 加载测试用例列表
const loadTestCases = async () => {
  try {
    const response = await axios.get('/api/test-cases/nl')
    if (response.data.success) {
      // 获取每个自然语言用例关联的 Python 测试代码
      for (const nlCase of response.data.test_cases) {
        const detailResponse = await axios.get(`/api/test-cases/nl/${nlCase.id}`)
        if (detailResponse.data.success) {
          const pyCases = detailResponse.data.test_case.py_test_cases || []
          for (const pyCase of pyCases) {
            const pyDetailResponse = await axios.get(`/api/test-cases/py/${pyCase.id}`)
            if (pyDetailResponse.data.success) {
              const pyData = pyDetailResponse.data.test_case
              // 获取最近执行结果
              const resultResponse = await axios.get(
                `/api/execution/results?test_case_id=${pyCase.id}&per_page=1`
              )
              let lastStatus = null
              let lastExecutedAt = null
              if (resultResponse.data.success && resultResponse.data.results.length > 0) {
                lastStatus = resultResponse.data.results[0].status
                lastExecutedAt = resultResponse.data.results[0].executed_at
              }
              testCases.value.push({
                ...pyData,
                nl_case_id: pyData.nl_case_id,
                last_status: lastStatus,
                last_executed_at: lastExecutedAt
              })
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('加载测试用例失败:', error)
  }
}

// 执行单个测试
const runTest = async (testCaseId) => {
  executingId.value = testCaseId

  try {
    const response = await axios.post(`/api/execution/run/${testCaseId}`)

    if (response.data.success) {
      ElMessage.success(`测试执行完成：${response.data.result.status}`)
      currentLog.value = response.data.result
      logDialogVisible.value = true
      loadTestCases() // 刷新列表
    } else {
      ElMessage.error(response.data.message || '执行失败')
      currentLog.value = response.data.result
      logDialogVisible.value = true
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '执行失败')
    if (error.response?.data?.result) {
      currentLog.value = error.response.data.result
      logDialogVisible.value = true
    }
  } finally {
    executingId.value = null
  }
}

// 执行所有测试
const runAllTests = async () => {
  executingAll.value = true

  try {
    const response = await axios.post('/api/execution/run-all')

    if (response.data.success) {
      ElMessage.success(response.data.message)
      currentLog.value = {
        stdout: JSON.stringify(response.data.results, null, 2),
        status: 'completed',
        duration: 0
      }
      logDialogVisible.value = true
      loadTestCases()
    }
  } catch (error) {
    ElMessage.error('批量执行失败')
  } finally {
    executingAll.value = false
  }
}

// 查看结果
const viewResult = async (testCaseId) => {
  try {
    const response = await axios.get(`/api/execution/results?test_case_id=${testCaseId}&per_page=1`)
    if (response.data.success && response.data.results.length > 0) {
      currentLog.value = response.data.results[0]
      logDialogVisible.value = true
    } else {
      ElMessage.info('暂无执行记录')
    }
  } catch (error) {
    ElMessage.error('加载结果失败')
  }
}

// 获取状态标签类型
const getStatusType = (status) => {
  const types = {
    passed: 'success',
    failed: 'danger',
    error: 'warning',
    skipped: 'info'
  }
  return types[status] || 'info'
}

onMounted(() => {
  loadTestCases()
})
</script>

<style scoped>
.execute-test-container {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expand-content {
  padding: 10px;
}

.expand-content h4 {
  margin-bottom: 10px;
  color: #606266;
}

.code-preview {
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-container {
  max-height: 500px;
  overflow-y: auto;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e6e6e6;
}

.log-content {
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
}

.log-error {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
  margin-top: 10px;
}
</style>
