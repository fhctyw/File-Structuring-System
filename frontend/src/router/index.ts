import { createRouter, createWebHistory } from 'vue-router'
import FileExplorer from '@/components/FileExplorer.vue'
import MethodSelection from '@/components/MethodSelection.vue'
import AlgorithmSelection from '@/components/AlgorithmSelection.vue'
import PreviewView from '@/components/PreviewView.vue'
import ProgressView from '@/components/ProgressView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: FileExplorer
    },
    {
      path: '/method/:sessionId',
      name: 'method',
      component: MethodSelection,
      props: true
    },
    {
      path: '/algorithm/:sessionId',
      name: 'algorithm',
      component: AlgorithmSelection,
      props: true
    },
    {
      path: '/preview/:sessionId',
      name: 'preview',
      component: PreviewView,
      props: true
    },
    {
      path: '/progress/:sessionId',
      name: 'progress',
      component: ProgressView,
      props: true
    }
  ]
})

export default router