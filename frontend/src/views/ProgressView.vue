<template>
  <div>
    <p class="text-gray-600 dark:text-gray-300 mb-6">
      Your files are being reorganized based on the plan. Please wait while the changes are applied.
    </p>
    
    <div v-if="error" class="mb-6 p-3 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded-md">
      {{ error }}
    </div>
    
    <ProgressBar 
      :percent="progress.percent" 
      :status="progress.status" 
    />
    
    <div v-if="resultData" class="mt-8">
      <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-md">
        <h3 class="text-lg font-semibold text-green-800 dark:text-green-300 mb-2">
          Changes Applied
        </h3>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-white dark:bg-gray-800 p-3 rounded-md shadow-sm">
            <div class="text-sm text-gray-500 dark:text-gray-400">Successfully Applied</div>
            <div class="text-2xl font-bold text-accent-600 dark:text-accent-400">
              {{ resultData.applied }}
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 p-3 rounded-md shadow-sm">
            <div class="text-sm text-gray-500 dark:text-gray-400">Failed Operations</div>
            <div class="text-2xl font-bold" :class="resultData.failed > 0 ? 'text-red-600' : 'text-gray-600'">
              {{ resultData.failed }}
            </div>
          </div>
        </div>
        
        <div v-if="resultData.errors && resultData.errors.length > 0" class="mt-4">
          <h4 class="text-md font-semibold text-red-800 dark:text-red-300 mb-2">Errors</h4>
          <ul class="bg-red-50 dark:bg-red-900/20 rounded-md p-3 text-sm text-red-700 dark:text-red-300">
            <li v-for="(err, i) in resultData.errors" :key="i" class="mb-1">
              {{ err }}
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="mt-8 flex justify-between">
      <button 
        @click="startNewSession" 
        class="btn btn-secondary"
      >
        Start New Session
      </button>
      
      <button 
        v-if="progress.percent === 100"
        @click="goToDirectory" 
        class="btn btn-primary"
      >
        View Directory
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'
import ProgressBar from '../components/ProgressBar.vue'
import api from '../services/api'
import type { ProgressReport, ApplyResult } from '../types'

const router = useRouter()
const sessionStore = useSessionStore()

const progress = ref<ProgressReport>({ percent: 0, status: 'Starting...' })
const resultData = ref<ApplyResult | null>(null)
const error = ref<string | null>(null)
const pollingInterval = ref<number | null>(null)

async function checkProgress() {
  try {
    const result = await sessionStore.getProgress()
    progress.value = result
    
    // If completed, fetch the final result
    if (result.percent === 100) {
      stopPolling()
      fetchResult()
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to get progress'
    stopPolling()
  }
}

async function fetchResult() {
  if (!sessionStore.currentSession?.id) return
  
  try {
    // This would be an API call to get the final results
    // For now, using mock data similar to what the API would return
    resultData.value = {
      applied: 22,
      failed: 3,
      errors: [
        "Could not move file.txt: Permission denied",
        "Destination folder already exists",
        "Source file missing"
      ]
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to get result'
  }
}

function startPolling() {
  stopPolling()
  pollingInterval.value = setInterval(checkProgress, 1000) as unknown as number
}

function stopPolling() {
  if (pollingInterval.value !== null) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

function startNewSession() {
  sessionStore.reset()
  localStorage.removeItem('sessionId')
  router.push('/')
}

function goToDirectory() {
  // This is a placeholder for opening the file explorer view to the organized directory
  // In a real application, we might redirect to a file browser or open the system's file explorer
  router.push('/')
}

onMounted(() => {
  // Redirect if no session exists
  if (!sessionStore.currentSession) {
    router.push('/')
    return
  }
  
  // Start checking progress
  checkProgress()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>