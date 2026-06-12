import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../pages/DashboardPage.vue') },
    { path: '/intakes', component: () => import('../pages/IntakeListPage.vue') },
    { path: '/intakes/new', component: () => import('../pages/IntakeFormPage.vue') },
    { path: '/intakes/scan', component: () => import('../pages/ScanPage.vue') },
    { path: '/intakes/:id', component: () => import('../pages/IntakeDetailPage.vue') },
    { path: '/staff', component: () => import('../pages/StaffPage.vue') },
  ],
})

export default router
