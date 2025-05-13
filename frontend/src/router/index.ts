import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../views/FileManagerView.vue'),
        meta: { title: 'Менеджер файлів', step: 1 }
      },
      {
        path: '/method',
        name: 'method',
        component: () => import('../views/MethodSelectView.vue'),
        meta: { title: 'Вибір методу аналізу', step: 2 }
      },
      {
        path: '/algorithm',
        name: 'algorithm',
        component: () => import('../views/AlgorithmSelectView.vue'),
        meta: { title: 'Вибір алгоритму структуризації', step: 3 }
      },
      {
        path: '/preview',
        name: 'preview',
        component: () => import('../views/PreviewView.vue'),
        meta: { title: 'Попередній перегляд змін', step: 4 }
      },
      {
        path: '/result',
        name: 'result',
        component: () => import('../views/ResultView.vue'),
        meta: { title: 'Результат обробки', step: 5 }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router