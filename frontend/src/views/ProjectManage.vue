<template>
  <div class="project-manage-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>项目管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建项目
          </el-button>
        </div>
      </template>

      <el-table :data="projects" style="width: 100%">
        <el-table-column prop="name" label="项目名称" width="200" />
        <el-table-column prop="source_type" label="源码类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.source_type === 'git' ? 'success' : ''">
              {{ row.source_type === 'git' ? 'Git 仓库' : '本地路径' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_path" label="源码路径" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewFiles(row)">
              查看文件
            </el-button>
            <el-button size="small" type="danger" @click="deleteProject(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建项目"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        label-width="100px"
      >
        <el-form-item label="项目名称" required>
          <el-input
            v-model="form.name"
            placeholder="例如：电商系统、OA 办公系统"
          />
        </el-form-item>

        <el-form-item label="源码类型" required>
          <el-radio-group v-model="form.source_type">
            <el-radio label="local">本地路径</el-radio>
            <el-radio label="git">Git 仓库</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="form.source_type === 'local'"
          label="本地路径"
          required
        >
          <el-input
            v-model="form.source_path"
            placeholder="例如：D:\projects\my-app"
          >
            <template #append>
              <el-button @click="selectLocalPath">选择</el-button>
            </template>
          </el-input>
          <div class="form-tip">选择包含源代码的文件夹</div>
        </el-form-item>

        <el-form-item
          v-if="form.source_type === 'git'"
          label="Git 仓库 URL"
          required
        >
          <el-input
            v-model="form.git_url"
            placeholder="例如：https://github.com/user/repo.git"
          />
          <div class="form-tip">平台将自动克隆仓库到本地</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看文件对话框 -->
    <el-dialog
      v-model="filesDialogVisible"
      :title="currentProject?.name || '项目文件'"
      width="700px"
    >
      <div v-if="projectFiles.length > 0" class="file-list">
        <el-checkbox-group v-model="selectedFiles">
          <div
            v-for="file in projectFiles"
            :key="file"
            class="file-item"
          >
            <el-checkbox :label="file">{{ file }}</el-checkbox>
          </div>
        </el-checkbox-group>
      </div>
      <el-empty v-else description="暂无文件" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const projects = ref([])
const dialogVisible = ref(false)
const filesDialogVisible = ref(false)
const creating = ref(false)
const currentProject = ref(null)
const projectFiles = ref([])
const selectedFiles = ref([])

const form = reactive({
  name: '',
  source_type: 'local',
  source_path: '',
  git_url: ''
})

const formRef = ref(null)

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

// 显示创建对话框
const showCreateDialog = () => {
  form.name = ''
  form.source_type = 'local'
  form.source_path = ''
  form.git_url = ''
  dialogVisible.value = true
}

// 选择本地路径（简化版，用户手动输入）
const selectLocalPath = () => {
  ElMessage.info('请手动输入本地项目源码路径，例如：D:\\projects\\my-app')
}

// 创建项目
const handleCreate = async () => {
  if (!form.name) {
    ElMessage.warning('请输入项目名称')
    return
  }

  if (form.source_type === 'local' && !form.source_path) {
    ElMessage.warning('请输入本地源码路径')
    return
  }

  if (form.source_type === 'git' && !form.git_url) {
    ElMessage.warning('请输入 Git 仓库地址')
    return
  }

  creating.value = true

  try {
    const payload = {
      name: form.name,
      source_type: form.source_type
    }

    if (form.source_type === 'local') {
      payload.source_path = form.source_path
    } else {
      payload.git_url = form.git_url
    }

    const response = await axios.post('/api/projects', payload)

    if (response.data.success) {
      ElMessage.success('项目创建成功')
      dialogVisible.value = false
      loadProjects()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '创建失败')
  } finally {
    creating.value = false
  }
}

// 查看文件
const viewFiles = async (project) => {
  currentProject.value = project
  projectFiles.value = []
  selectedFiles.value = []

  try {
    const response = await axios.get(`/api/projects/${project.id}/files`)
    if (response.data.success) {
      projectFiles.value = response.data.files
      filesDialogVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载文件列表失败：' + (error.response?.data?.message || '未知错误'))
  }
}

// 删除项目
const deleteProject = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此项目吗？', '确认删除', {
      type: 'warning'
    })

    const response = await axios.delete(`/api/projects/${id}`)
    if (response.data.success) {
      ElMessage.success('项目已删除')
      loadProjects()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.project-manage-container {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.file-list {
  max-height: 400px;
  overflow-y: auto;
}

.file-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.file-item:last-child {
  border-bottom: none;
}
</style>
