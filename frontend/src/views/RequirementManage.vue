<template>
  <div class="requirement-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>需求文件管理</span>
          <div class="header-actions">
            <el-select
              v-model="selectedProjectId"
              placeholder="选择项目"
              style="width: 200px; margin-right: 10px"
              @change="loadRequirements"
            >
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
            <el-button
              type="primary"
              @click="showUploadDialog = true"
              :disabled="!selectedProjectId"
            >
              <el-icon><Upload /></el-icon>
              上传需求文件
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="requirements" style="width: 100%" v-loading="loading">
        <el-table-column prop="filename" label="文件名" min-width="200" />
        <el-table-column prop="file_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.file_type?.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="uploader" label="上传人" width="100" />
        <el-table-column prop="uploaded_at" label="上传时间" width="160" />
        <el-table-column prop="updated_at" label="更新时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="downloadFile(row)">
              下载
            </el-button>
            <el-button size="small" @click="showEditDialog(row)">
              修改
            </el-button>
            <el-button size="small" type="danger" @click="deleteFile(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && requirements.length === 0" description="暂无需求文件" />
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传需求文件"
      width="500px"
    >
      <el-form>
        <el-form-item label="选择项目">
          <el-select v-model="uploadForm.project_id" placeholder="选择项目" style="width: 100%">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择文件">
          <el-upload
            ref="uploadRef"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :file-list="fileList"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.md,.ppt,.pptx"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持格式：PDF、Word、Excel、PowerPoint、TXT、Markdown
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改对话框 -->
    <el-dialog
      v-model="showEditDialogVisible"
      title="修改需求文件"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="当前文件">
          <span>{{ currentFile?.filename }}</span>
        </el-form-item>
        <el-form-item label="所属项目">
          <el-select v-model="editForm.project_id" placeholder="选择项目" style="width: 100%">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="替换文件">
          <el-upload
            ref="editUploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleEditFileChange"
            :file-list="editFileList"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.md,.ppt,.pptx"
          >
            <el-button>选择新文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                选择新文件将替换原文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editing" @click="handleUpdate">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, UploadFilled } from '@element-plus/icons-vue'

const requirements = ref([])
const projects = ref([])
const selectedProjectId = ref(null)
const loading = ref(false)
const uploading = ref(false)
const editing = ref(false)

// 上传相关
const showUploadDialog = ref(false)
const uploadRef = ref(null)
const uploadForm = reactive({
  project_id: null,
  file: null
})
const fileList = ref([])

// 修改相关
const showEditDialogVisible = ref(false)
const editUploadRef = ref(null)
const currentFile = ref(null)
const editForm = reactive({
  project_id: null,
  file: null
})
const editFileList = ref([])

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await axios.get('/api/projects')
    if (response.data.success) {
      projects.value = response.data.projects
      // 如果有项目，默认选择第一个
      if (projects.value.length > 0 && !selectedProjectId.value) {
        selectedProjectId.value = projects.value[0].id
        loadRequirements()
      }
    }
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

// 加载需求文件列表
const loadRequirements = async () => {
  if (!selectedProjectId.value) {
    requirements.value = []
    return
  }

  loading.value = true
  try {
    const response = await axios.get('/api/requirements', {
      params: { project_id: selectedProjectId.value }
    })
    if (response.data.success) {
      requirements.value = response.data.requirements
    }
  } catch (error) {
    ElMessage.error('加载需求文件失败')
  } finally {
    loading.value = false
  }
}

// 文件变化处理
const handleFileChange = (file) => {
  uploadForm.file = file.raw
}

// 修改文件变化处理
const handleEditFileChange = (file) => {
  editForm.file = file.raw
}

// 上传文件
const handleUpload = async () => {
  if (!uploadForm.project_id) {
    ElMessage.warning('请选择项目')
    return
  }

  if (!uploadForm.file) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('project_id', uploadForm.project_id)
    formData.append('file', uploadForm.file)

    const response = await axios.post('/api/requirements/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (response.data.success) {
      ElMessage.success('文件上传成功')
      showUploadDialog.value = false
      fileList.value = []
      uploadForm.file = null
      loadRequirements()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 显示修改对话框
const showEditDialog = (file) => {
  currentFile.value = file
  editForm.project_id = file.project_id
  editForm.file = null
  editFileList.value = []
  showEditDialogVisible.value = true
}

// 更新文件
const handleUpdate = async () => {
  if (!currentFile.value) return

  editing.value = true

  try {
    const formData = new FormData()
    formData.append('project_id', editForm.project_id)
    if (editForm.file) {
      formData.append('file', editForm.file)
    }

    const response = await axios.put(
      `/api/requirements/${currentFile.value.id}`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    )

    if (response.data.success) {
      ElMessage.success('文件更新成功')
      showEditDialogVisible.value = false
      loadRequirements()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '更新失败')
  } finally {
    editing.value = false
  }
}

// 下载文件
const downloadFile = async (file) => {
  try {
    const response = await axios.get(`/api/requirements/${file.id}/download`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', file.filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 删除文件
const deleteFile = async (file) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${file.filename}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )

    const response = await axios.delete(`/api/requirements/${file.id}`)

    if (response.data.success) {
      ElMessage.success('文件已删除')
      loadRequirements()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.requirement-container {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.el-icon--upload {
  font-size: 67px;
  color: var(--el-text-color-placeholder);
  margin-bottom: 16px;
}

.el-upload__tip {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-top: 7px;
}
</style>
