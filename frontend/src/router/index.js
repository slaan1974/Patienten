import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/patienten',
    name: 'Patienten',
    component: () => import('../views/PatientListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/patienten/:id',
    name: 'PatientDetail',
    component: () => import('../views/PatientDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/patienten/:id/dsm5',
    name: 'Dsm5Form',
    component: () => import('../views/Dsm5FormView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dsm5',
    name: 'Dsm5Overview',
    component: () => import('../views/Dsm5OverviewView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/kindcheck',
    name: 'KindcheckOverview',
    component: () => import('../views/KindcheckOverviewView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/patienten/:id/kindcheck',
    name: 'KindcheckForm',
    component: () => import('../views/KindcheckFormView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/audit',
    name: 'Audit',
    component: () => import('../views/AuditLogView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/audit/:id',
    name: 'AuditDetail',
    component: () => import('../views/AuditDetailView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
