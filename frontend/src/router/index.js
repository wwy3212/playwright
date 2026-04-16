import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    redirect: '/generate-nl',
    children: [
      {
        path: 'projects',
        name: 'ProjectManage',
        component: () => import('@/views/ProjectManage.vue'),
        meta: { title: '项目管理', icon: 'Folder' }
      },
      {
        path: 'requirements',
        name: 'RequirementManage',
        component: () => import('@/views/RequirementManage.vue'),
        meta: { title: '需求文件管理', icon: 'Document' }
      },
      {
        path: 'generate-nl',
        name: 'GenerateNL',
        component: () => import('@/views/GenerateNL.vue'),
        meta: { title: '生成自然语言测试用例', icon: 'List' }
      },
      {
        path: 'generate-code',
        name: 'GenerateCode',
        component: () => import('@/views/GenerateCode.vue'),
        meta: { title: '生成 Python 测试代码', icon: 'Code' }
      },
      {
        path: 'execute',
        name: 'ExecuteTest',
        component: () => import('@/views/ExecuteTest.vue'),
        meta: { title: '执行测试', icon: 'VideoPlay' }
      },
      {
        path: 'reports',
        name: 'ViewReport',
        component: () => import('@/views/ViewReport.vue'),
        meta: { title: '测试报告', icon: 'DataAnalysis' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.path !== '/login' && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
