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
        meta: { title: 'File Manager', step: 1 }
      },
      {
        path: '/method',
        name: 'method',
        component: () => import('../views/MethodSelectView.vue'),
        meta: { title: 'Select Analysis Method', step: 2 }
      },
      {
        path: '/algorithm',
        name: 'algorithm',
        component: () => import('../views/AlgorithmSelectView.vue'),
        meta: { title: 'Select Structuring Algorithm', step: 3 }
      },
      {
        path: '/preview',
        name: 'preview',
        component: () => import('../views/PreviewView.vue'),
        meta: { title: 'Preview Changes', step: 4 }
      },
      {
        path: '/result',
        name: 'result',
        component: () => import('../views/ResultView.vue'),
        meta: { title: 'Processing Result', step: 5 }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router