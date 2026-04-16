<template>
  <router-view />
</template>

<script setup>
// AI 智能测试平台 - 主应用组件
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100%;
  height: 100vh;
}

/* 代码编辑器样式 */
.code-editor {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
}

/* Markdown 渲染样式 */
.markdown-body {
  padding: 20px;
  line-height: 1.6;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #303133;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 20px;
}

.markdown-body li {
  margin: 5px 0;
}

/* 测试结果状态颜色 */
.status-passed {
  color: #67c23a;
}

.status-failed {
  color: #f56c6c;
}

.status-error {
  color: #e6a23c;
}

.status-skipped {
  color: #909399;
}
</style>
