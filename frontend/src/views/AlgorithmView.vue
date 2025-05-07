<template>
  <div>
    <p class="text-gray-600 dark:text-gray-300 mb-6">
      Choose a structuring algorithm to determine how your files will be organized. 
      Each algorithm uses different criteria to create a more logical file structure.
    </p>
    
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else class="grid md:grid-cols-3 gap-4">
      <OptionCard
        v-for="algorithm in algorithms"
        :key="algorithm.id"
        :title="algorithm.name"
        :description="algorithm.description"
        :icon="algorithm.icon"
        :selected="selectedAlgorithm === algorithm.id"
        @select="selectAlgorithm(algorithm.id)"
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
        @click="confirmAlgorithm" 
        class="btn btn-primary"
        :disabled="!selectedAlgorithm || loading"
      >
        Generate Plan
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
import type { StructAlgorithm, StructAlgorithmInfo } from '../types'

const router = useRouter()
const sessionStore = useSessionStore()

const algorithms = ref<StructAlgorithmInfo[]>([])
const selectedAlgorithm = ref<StructAlgorithm | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

async function loadAlgorithms() {
  loading.value = true
  error.value = null
  
  try {
    algorithms.value = await api.getStructAlgorithms()
    
    // Set default icons if not provided by API
    algorithms.value.forEach(algorithm => {
      if (!algorithm.icon) {
        switch (algorithm.id) {
          case 'BY_TYPE':
            algorithm.icon = '🗂️'
            break
          case 'CLUSTER':
            algorithm.icon = '🧩'
            break
          case 'CRITERIA':
            algorithm.icon = '📏'
            break
        }
      }
    })
    
    // Set selected algorithm if we have one from a previous session
    if (sessionStore.currentSession?.structAlgorithm) {
      selectedAlgorithm.value = sessionStore.currentSession.structAlgorithm
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load structuring algorithms'
  } finally {
    loading.value = false
  }
}

function selectAlgorithm(algorithm: StructAlgorithm) {
  selectedAlgorithm.value = algorithm
}

async function confirmAlgorithm() {
  if (!selectedAlgorithm.value) return
  
  loading.value = true
  error.value = null
  
  try {
    await sessionStore.generatePlan(selectedAlgorithm.value)
    router.push('/preview')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Plan generation failed'
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/method')
}

onMounted(() => {
  // Redirect if no session exists or if no analysis method has been selected
  if (!sessionStore.currentSession || !sessionStore.currentSession.analysisMethod) {
    router.push('/')
    return
  }
  
  loadAlgorithms()
})
</script>