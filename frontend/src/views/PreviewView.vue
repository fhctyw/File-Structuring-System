<template>
  <div>
    <p class="text-gray-600 dark:text-gray-300 mb-6">
      Preview how your files will be organized. Review the new structure before applying changes.
    </p>
    
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else-if="error" class="mt-4 p-3 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded-md">
      {{ error }}
    </div>
    
    <div v-else-if="previewData?.tree" class="preview-container">
      <div class="bg-gray-50 dark:bg-gray-800 rounded-md p-4 overflow-auto max-h-96">
        <h3 class="text-lg font-semibold mb-2">New Structure</h3>
        <TreeView :tree="previewData.tree" />
      </div>
      
      <div v-if="planSummary" class="mt-6 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-md">
        <h3 class="text-lg font-semibold mb-2">Summary</h3>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div class="bg-white dark:bg-gray-800 p-3 rounded-md shadow-sm">
            <div class="text-sm text-gray-500 dark:text-gray-400">Total Actions</div>
            <div class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ planSummary.actions_created }}
            </div>
          </div>
          
          <div 
            v-for="(count, action) in planSummary.breakdown" 
            :key="action"
            class="bg-white dark:bg-gray-800 p-3 rounded-md shadow-sm"
          >
            <div class="text-sm text-gray-500 dark:text-gray-400">{{ formatAction(action) }}</div>
            <div class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ count }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="text-center py-10 text-gray-500">
      No preview available. Please generate a plan first.
    </div>
    
    <div class="mt-8 flex justify-between">
      <button @click="goBack" class="btn btn-secondary">
        Back
      </button>
      <button 
        @click="applyChanges" 
        class="btn btn-accent"
        :disabled="!previewData || loading"
      >
        Apply Changes
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'
import TreeView from '../components/TreeView.vue'
import type { PreviewTree, PlanSummary } from '../types'

const router = useRouter()
const sessionStore = useSessionStore()

const previewData = ref<PreviewTree | null>(null)
const planSummary = ref<PlanSummary | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

async function loadPreview() {
  loading.value = true
  error.value = null
  
  try {
    previewData.value = await sessionStore.getPreview()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load preview'
  } finally {
    loading.value = false
  }
}

function formatAction(action: string): string {
  const formatted = action
    .replace(/([A-Z])/g, ' $1')
    .toLowerCase()
    .trim();
  
  return formatted.charAt(0).toUpperCase() + formatted.slice(1);
}

function goBack() {
  router.push('/algorithm')
}

async function applyChanges() {
  loading.value = true
  
  try {
    await sessionStore.applyPlan(false)
    router.push('/progress')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to start applying changes'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Redirect if no session exists or if no algorithm has been selected
  if (!sessionStore.currentSession || 
      !sessionStore.currentSession.analysisMethod || 
      !sessionStore.currentSession.structAlgorithm) {
    router.push('/')
    return
  }
  
  loadPreview()
  
  // Using fake plan summary for now, this would ideally come from the API
  planSummary.value = {
    actions_created: 25,
    breakdown: {
      "MOVE": 15,
      "RENAME": 7,
      "CREATE_FOLDER": 3
    }
  }
})
</script>