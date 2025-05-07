<template>
  <div>
    <p class="text-gray-600 dark:text-gray-300 mb-6">
      Select a directory you want to organize. This will be the starting point for scanning 
      files and creating a better structure.
    </p>
    
    <FileExplorer @select="selectDirectory" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'
import FileExplorer from '../components/FileExplorer.vue'

const router = useRouter()
const sessionStore = useSessionStore()

async function selectDirectory(directory: string, recursive: boolean) {
  try {
    const sessionId = await sessionStore.createNewSession(directory, recursive)
    
    // Save session ID to localStorage
    if (sessionId) {
      localStorage.setItem('sessionId', sessionId)
    }
    
    // Move to next step
    router.push('/method')
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}
</script>