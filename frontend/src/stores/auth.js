import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  const isAuthenticated = computed(() => !!user.value)

  // 配置 axios 默认头
  const setupAxios = () => {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  // 登录
  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/auth/login', { username, password })
      if (response.data.success) {
        user.value = response.data.user
        token.value = response.data.token || 'default-token'
        localStorage.setItem('token', token.value)
        setupAxios()
        return { success: true }
      }
      return { success: false, message: response.data.message }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || '登录失败'
      }
    }
  }

  // 登出
  const logout = async () => {
    try {
      await axios.post('/api/auth/logout')
    } catch (e) {
      // 忽略错误
    }
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  // 获取当前用户
  const getCurrentUser = async () => {
    try {
      const response = await axios.get('/api/auth/me')
      if (response.data.success) {
        user.value = response.data.user
        return user.value
      }
    } catch (error) {
      user.value = null
    }
    return null
  }

  // 初始化检查
  const initAuth = async () => {
    if (token.value) {
      setupAxios()
      await getCurrentUser()
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    getCurrentUser,
    initAuth
  }
})
