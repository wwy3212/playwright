<template>
  <div class="generate-nl-container">
    <!-- 顶部操作区 -->
    <el-card class="action-card">
      <div class="action-bar">
        <div class="left-actions">
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            新增用例
          </el-button>
        </div>
        <div class="right-actions">
          <el-select v-model="filterProject" placeholder="筛选项目" clearable @change="loadTestCases" style="width: 150px; margin-right: 10px">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
          <el-input
            v-model="searchText"
            placeholder="搜索功能ID或场景"
            clearable
            @input="loadTestCases"
            style="width: 200px"
          />
        </div>
      </div>
    </el-card>

    <!-- 测试用例列表 -->
    <el-card class="list-card">
      <el-table :data="testCases" style="width: 100%" border @row-click="handleRowClick">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <el-form label-width="100px" label-position="left">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="功能ID">
                      <el-input v-model="row.function_id" placeholder="功能ID" @change="updateCase(row)" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="测试场景">
                      <el-input v-model="row.scenario" placeholder="测试场景" @change="updateCase(row)" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="前置条件">
                  <el-input v-model="row.precondition" type="textarea" :rows="2" placeholder="前置条件" @change="updateCase(row)" />
                </el-form-item>
                <el-form-item label="测试步骤">
                  <el-input v-model="row.steps" type="textarea" :rows="8" placeholder="测试步骤" @change="updateCase(row)" />
                </el-form-item>
                <el-form-item label="预期结果">
                  <el-input v-model="row.expected" type="textarea" :rows="4" placeholder="预期结果" @change="updateCase(row)" />
                </el-form-item>
                <el-form-item label="状态">
                  <el-select v-model="row.status" @change="updateCase(row)">
                    <el-option label="草稿" value="draft" />
                    <el-option label="待执行" value="pending" />
                    <el-option label="已通过" value="passed" />
                    <el-option label="已失败" value="failed" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="saveEdit(row)">保存</el-button>
                  <el-button type="success" @click="generateCode(row)">生成代码</el-button>
                  <el-button type="danger" @click="deleteCase(row)">删除</el-button>
                </el-form-item>
              </el-form>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="function_id" label="功能ID" width="120" />
        <el-table-column prop="scenario" label="测试场景" min-width="180" show-overflow-tooltip />
        <el-table-column prop="precondition" label="前置条件" min-width="150" show-overflow-tooltip />
        <el-table-column prop="steps" label="测试步骤" min-width="200" show-overflow-tooltip />
        <el-table-column prop="expected" label="预期结果" min-width="150" show-overflow-tooltip />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
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

    <!-- 新增用例对话框 -->
    <el-dialog v-model="dialogVisible" title="新增测试用例" width="700px">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="所属项目" required>
          <el-select v-model="form.project_id" placeholder="选择项目" style="width: 100%">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="功能ID" required>
          <el-input v-model="form.function_id" placeholder="例如：login" />
        </el-form-item>
        <el-form-item label="测试场景" required>
          <el-input v-model="form.scenario" placeholder="例如：正常登录流程" />
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input v-model="form.precondition" type="textarea" :rows="2" placeholder="执行测试前需要满足的条件" />
        </el-form-item>
        <el-form-item label="测试步骤" required>
          <el-input v-model="form.steps" type="textarea" :rows="6" placeholder="1. 打开登录页面&#10;2. 输入用户名和密码&#10;3. 点击登录按钮" />
        </el-form-item>
        <el-form-item label="预期结果" required>
          <el-input v-model="form.expected" type="textarea" :rows="4" placeholder="登录成功，跳转到首页" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">创建</el-button>
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
const filterProject = ref(null)
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const formRef = ref(null)

const form = reactive({
  project_id: null,
  function_id: '',
  scenario: '',
  precondition: '',
  steps: '',
  expected: ''
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
    if (filterProject.value) {
      params.project_id = filterProject.value
    }
    if (searchText.value) {
      params.search = searchText.value
    }

    const response = await axios.get('/api/test-cases/list', { params })
    if (response.data.success) {
      testCases.value = response.data.cases
      total.value = response.data.pagination.total
    }
  } catch (error) {
    ElMessage.error('加载测试用例失败')
  }
}

// 显示新增对话框
const showAddDialog = () => {
  form.project_id = null
  form.function_id = ''
  form.scenario = ''
  form.precondition = ''
  form.steps = ''
  form.expected = ''
  dialogVisible.value = true
}

// 新增用例
const handleAdd = async () => {
  if (!form.project_id) {
    ElMessage.warning('请选择项目')
    return
  }
  if (!form.function_id || !form.scenario || !form.steps || !form.expected) {
    ElMessage.warning('请填写必填字段')
    return
  }

  try {
    const response = await axios.post('/api/test-cases/list', form)
    if (response.data.success) {
      ElMessage.success('创建成功')
      dialogVisible.value = false
      loadTestCases()
    }
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

// 行点击展开编辑
const handleRowClick = (row) => {
  // 点击行时自动展开（可选）
}

// 保存编辑
const updateCase = (row) => {
  // 实时保存更新（可选）
}

// 保存并关闭
const saveEdit = async (row) => {
  try {
    await axios.put(`/api/test-cases/list/${row.id}`, {
      function_id: row.function_id,
      scenario: row.scenario,
      precondition: row.precondition,
      steps: row.steps,
      expected: row.expected,
      status: row.status
    })
    ElMessage.success('保存成功')
    loadTestCases()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 删除用例
const deleteCase = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除测试用例 "${row.scenario}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await axios.delete(`/api/test-cases/list/${row.id}`)
    ElMessage.success('删除成功')
    loadTestCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 生成代码
const generateCode = (row) => {
  const nlContent = `## 测试场景：${row.scenario}
- 前置条件：${row.precondition || '无'}
- 测试步骤：
${row.steps}
- 预期结果：${row.expected}`

  sessionStorage.setItem('temp_nl_content', nlContent)
  sessionStorage.setItem('temp_function_id', row.function_id)
  router.push(`/generate-code?from_case=${row.id}`)
}

// 获取状态类型
const getStatusType = (status) => {
  const types = { draft: 'info', pending: 'warning', passed: 'success', failed: 'danger' }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = { draft: '草稿', pending: '待执行', passed: '已通过', failed: '已失败' }
  return texts[status] || status
}

onMounted(() => {
  loadProjects()
  loadTestCases()
})
</script>

<style scoped>
.generate-nl-container {
  max-width: 100%;
  margin: 0 auto;
}

.action-card {
  margin-bottom: 15px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-card {
  margin-bottom: 15px;
}

.expand-content {
  padding: 20px;
  background-color: #f5f7fa;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
