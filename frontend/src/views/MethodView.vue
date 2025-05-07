<template>
  <div>
    <p class="text-gray-600 dark:text-gray-300 mb-6">
      Choose an analysis method to identify patterns in your files. This will determine how 
      your files are evaluated before being reorganized.
    </p>
    
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else class="grid md:grid-cols-3 gap-4">
      <OptionCard
        v-for="method in methods"
        :key="method.id"
        :title="method.name"
        :description="method.description"
        :icon="method.icon"
        :selected="selectedMethod === method.id"
        @select="selectMethod(method.id)"
      />
    </div>
    
    <div v-if="error" class="mt-4 p-3 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded-md">
      {{ error }}
    </div>
    
    <div class="mt-8 flex justify-between">
      <button @click="goBack" class="btn btn-secondary">
        Back
      </button>
      <button 
        @click="confirmMethod" 
        class="btn btn-primary"
        :disabled="!selectedMethod || loading"
      >
        Continue
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'
import OptionCard from '../components/OptionCard.vue'
import api from '../services/api'
import type { AnalysisMethod, AnalysisMethodInfo } from '../types'

const router = useRouter()
const sessionStore = useSessionStore()

const methods = ref<AnalysisMethodInfo[]>([])
const selectedMethod = ref<AnalysisMethod | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

async function loadMethods() {
  loading.value = true
  error.value = null
  
  try {
    methods.value = await api.getAnalysisMethods()
    
    // Set default icons if not provided by API
    methods.value.forEach(method => {
      if (!method.icon) {
        switch (method.id) {
          case 'META':
            method.icon = '📊'
            break
          case 'STRUCT':
            method.icon = '📁'
            break
          case 'SEMANTIC':
            method.icon = '🧠'
            break
        }
      }
    })
    
    // Set selected method if we have one from a previous session
    if (sessionStore.currentSession?.analysisMethod) {
      selectedMethod.value = sessionStore.currentSession.analysisMethod
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load analysis methods'
  } finally {
    loading.value = false
  }
}

function selectMethod(method: AnalysisMethod) {
  selectedMethod.value = method
}

async function confirmMethod() {
  if (!selectedMethod.value) return
  
  loading.value = true
  error.value = null
  
  try {
    await sessionStore.runAnalysis(selectedMethod.value)
    router.push('/algorithm')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Analysis failed'
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/')
}

onMounted(() => {
  // Redirect if no session exists
  if (!sessionStore.currentSession) {
    router.push('/')
    return
  }
  
  loadMethods()
})
</script>