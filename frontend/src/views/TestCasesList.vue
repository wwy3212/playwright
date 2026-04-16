<template>
  <div class="test-cases-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测试用例列表</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            新增用例
          </el-button>
        </div>
      </template>

      <!-- 用例筛选 -->
      <div class="filter-bar">
        <el-select v-model="selectedProject" placeholder="选择项目" clearable @change="loadTestCases">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <el-input
          v-model="searchText"
          placeholder="搜索功能 ID 或描述"
          clearable
          @input="loadTestCases"
          style="width: 300px"
        />
        <el-button type="primary" @click="loadTestCases">查询</el-button>
      </div>

      <!-- 用例列表 -->
      <el-table :data="testCases" style="width: 100%" border>
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <h4>测试步骤：</h4>
              <el-input
                v-model="row.steps"
                type="textarea"
                :rows="8"
                placeholder="测试步骤..."
              />
              <h4 style="margin-top: 15px">预期结果：</h4>
              <el-input
                v-model="row.expected"
                type="textarea"
                :rows="4"
                placeholder="预期结果..."
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="function_id" label="功能 ID" width="150" />
        <el-table-column prop="scenario" label="测试场景" width="250" show-overflow-tooltip />
        <el-table-column prop="precondition" label="前置条件" width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editCase(row)">编辑</el-button>
            <el-button size="small" type="primary" @click="generateCode(row)">生成代码</el-button>
            <el-button size="small" type="danger" @click="deleteCase(row)">删除</el-button>
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
          @size-change="loadTestCases"
          @current-change="loadTestCases"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑测试用例' : '新增测试用例'"
      width="700px"
    >
      <el-form
        ref="formRef"
        :model="form"
        label-width="100px"
      >
        <el-form-item label="所属项目" required>
          <el-select
            v-model="form.project_id"
            placeholder="选择项目"
            style="width: 100%"
            :disabled="isEdit"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="功能 ID" required>
          <el-input
            v-model="form.function_id"
            placeholder="例如：login, search"
          />
        </el-form-item>

        <el-form-item label="测试场景" required>
          <el-input
            v-model="form.scenario"
            placeholder="例如：正常登录流程"
          />
        </el-form-item>

        <el-form-item label="前置条件">
          <el-input
            v-model="form.precondition"
            type="textarea"
            :rows="2"
            placeholder="执行测试前需要满足的条件"
          />
        </el-form-item>

        <el-form-item label="测试步骤" required>
          <el-input
            v-model="form.steps"
            type="textarea"
            :rows="6"
            placeholder="1. 打开登录页面&#10;2. 输入用户名和密码&#10;3. 点击登录按钮"
          />
        </el-form-item>

        <el-form-item label="预期结果" required>
          <el-input
            v-model="form.expected"
            type="textarea"
            :rows="4"
            placeholder="登录成功，跳转到首页"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="草稿" value="draft" />
            <el-option label="待执行" value="pending" />
            <el-option label="已通过" value="passed" />
            <el-option label="已失败" value="failed" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const projects = ref([])
const testCases = ref([])
const selectedProject = ref(null)
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  project_id: null,
  function_id: '',
  scenario: '',
  precondition: '',
  steps: '',
  expected: '',
  status: 'draft'
})

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await axios.get('/api/projects')
    if (response.data.success) {
      projects.value = response.data.projects
    }
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

// 加载测试用例列表
const loadTestCases = async () => {
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    if (searchText.value) {
      params.search = searchText.value
    }

    const response = await axios.get('/api/test-cases/list', { params })
    if (response.data.success) {
      testCases.value = response.data.cases.map(item => ({
        ...item,
        steps: item.steps || '',
        expected: item.expected || ''
      }))
      total.value = response.data.pagination.total
      currentPage.value = response.data.pagination.page
      pageSize.value = response.data.pagination.per_page
    }
  } catch (error) {
    ElMessage.error('加载测试用例失败')
  }
}

// 显示新增对话框
const showAddDialog = () => {
  form.id = null
  form.project_id = null
  form.function_id = ''
  form.scenario = ''
  form.precondition = ''
  form.steps = ''
  form.expected = ''
  form.status = 'draft'
  isEdit.value = false
  dialogVisible.value = true
}

// 编辑用例
const editCase = (row) => {
  form.id = row.id
  form.project_id = row.project_id
  form.function_id = row.function_id
  form.scenario = row.scenario
  form.precondition = row.precondition || ''
  form.steps = row.steps || ''
  form.expected = row.expected || ''
  form.status = row.status
  isEdit.value = true
  dialogVisible.value = true
}

// 保存用例
const handleSave = async () => {
  if (!form.project_id) {
    ElMessage.warning('请选择项目')
    return
  }
  if (!form.function_id) {
    ElMessage.warning('请输入功能 ID')
    return
  }
  if (!form.scenario) {
    ElMessage.warning('请输入测试场景')
    return
  }
  if (!form.steps) {
    ElMessage.warning('请输入测试步骤')
    return
  }
  if (!form.expected) {
    ElMessage.warning('请输入预期结果')
    return
  }

  try {
    let response
    if (isEdit.value) {
      response = await axios.put(`/api/test-cases/list/${form.id}`, form)
    } else {
      response = await axios.post('/api/test-cases/list', form)
    }

    if (response.data.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadTestCases()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

// 删除用例
const deleteCase = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除测试用例 "${row.scenario}" 吗？`, '确认删除', {
      type: 'warning'
    })

    const response = await axios.delete(`/api/test-cases/list/${row.id}`)
    if (response.data.success) {
      ElMessage.success('删除成功')
      loadTestCases()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 生成代码
const generateCode = (row) => {
  // 将当前用例转换为自然语言格式并跳转到代码生成页面
  const nlContent = `## 测试场景：${row.scenario}
- 前置条件：${row.precondition || '无'}
- 测试步骤：
${row.steps}
- 预期结果：${row.expected}`

  // 存储到 sessionStorage 并跳转
  sessionStorage.setItem('temp_nl_content', nlContent)
  sessionStorage.setItem('temp_function_id', row.function_id)
  router.push(`/generate-code?from_case=${row.id}`)
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    draft: 'info',
    pending: 'warning',
    passed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    pending: '待执行',
    passed: '已通过',
    failed: '已失败'
  }
  return texts[status] || status
}

onMounted(() => {
  loadProjects()
  loadTestCases()
})
</script>

<style scoped>
.test-cases-container {
  max-width: 1600px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: center;
}

.expand-content {
  padding: 15px;
  background-color: #f5f7fa;
}

.expand-content h4 {
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
