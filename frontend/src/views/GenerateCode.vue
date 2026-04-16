<template>
  <div class="generate-code-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>生成 Python 测试代码</span>
        </div>
      </template>

      <el-form label-width="120px">
        <el-form-item label="选择自然语言用例">
          <el-select
            v-model="selectedNlId"
            placeholder="请选择自然语言测试用例"
            style="width: 100%"
            @change="loadNlDetail"
          >
            <el-option
              v-for="item in nlList"
              :key="item.id"
              :label="`${item.function_id} - ${item.description}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 自然语言内容 -->
    <el-card v-if="nlDetail" class="nl-card">
      <template #header>
        <span>自然语言测试用例</span>
      </template>
      <el-input
        v-model="nlDetail.nl_content"
        type="textarea"
        :rows="10"
        readonly
      />
    </el-card>

    <!-- 生成按钮 -->
    <el-card class="action-card">
      <el-button type="primary" :loading="generating" @click="handleGenerate">
        <el-icon><Code /></el-icon>
        生成 Python 代码
      </el-button>
    </el-card>

    <!-- 生成的代码 -->
    <el-card v-if="generatedCode" class="code-card">
      <template #header>
        <div class="card-header">
          <span>生成的 Python 测试代码</span>
          <div>
            <el-button size="small" @click="copyCode">复制</el-button>
            <el-button size="small" type="success" @click="handleSave">保存</el-button>
          </div>
        </div>
      </template>

      <pre class="code-block"><code>{{ generatedCode.py_content }}</code></pre>

      <el-input
        v-model="generatedCode.py_content"
        type="textarea"
        :rows="25"
        class="code-editor"
        style="margin-top: 10px"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const selectedNlId = ref(route.query.nl_id ? parseInt(route.query.nl_id) : null)
const nlList = ref([])
const nlDetail = ref(null)
const generatedCode = ref(null)
const generating = ref(false)

// 加载自然语言用例列表
const loadNlList = async () => {
  try {
    const response = await axios.get('/api/test-cases/nl')
    if (response.data.success) {
      nlList.value = response.data.test_cases
    }
  } catch (error) {
    console.error('加载用例列表失败:', error)
  }
}

// 加载自然语言用例详情
const loadNlDetail = async () => {
  if (!selectedNlId.value) return

  try {
    const response = await axios.get(`/api/test-cases/nl/${selectedNlId.value}`)
    if (response.data.success) {
      nlDetail.value = response.data.test_case
    }
  } catch (error) {
    ElMessage.error('加载用例详情失败')
  }
}

// 生成 Python 代码
const handleGenerate = async () => {
  if (!selectedNlId.value) {
    ElMessage.warning('请先选择自然语言测试用例')
    return
  }

  generating.value = true

  try {
    const response = await axios.post('/api/test-cases/py/generate', {
      nl_id: selectedNlId.value
    })

    if (response.data.success) {
      generatedCode.value = response.data.test_case
      ElMessage.success('代码生成成功')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '生成失败')
  } finally {
    generating.value = false
  }
}

// 保存代码
const handleSave = async () => {
  if (!generatedCode.value) return

  try {
    const response = await axios.put(
      `/api/test-cases/py/${generatedCode.value.id}`,
      {
        py_content: generatedCode.value.py_content,
        file_path: generatedCode.value.file_path
      }
    )

    if (response.data.success) {
      ElMessage.success('保存成功')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 复制代码
const copyCode = () => {
  if (!generatedCode.value) return

  navigator.clipboard.writeText(generatedCode.value.py_content)
  ElMessage.success('代码已复制到剪贴板')
}

onMounted(() => {
  loadNlList()
  if (selectedNlId.value) {
    loadNlDetail()
  }
})
</script>

<style scoped>
.generate-code-container {
  max-width: 1200px;
  margin: 0 auto;
}

.nl-card,
.action-card,
.code-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.code-block {
  background-color: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
}

.code-block code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #24292e;
}

.code-editor {
  font-family: 'Consolas', 'Monaco', monospace;
}
</style>
