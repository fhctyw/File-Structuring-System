<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FileManager from '../components/FileManager.vue'
import { useSessionStore } from '../stores/useSessionStore'

const router = useRouter()
const sessionStore = useSessionStore()

// Create a new session when a directory is selected
const handleDirectorySelect = async (directory: string) => {
  try {
    await sessionStore.createSession(directory)
    router.push('/method')
  } catch (err) {
    console.error('Failed to create session:', err)
  }
}
</script>

<template>
  <div class="file-manager-view">
    <h2 class="view-subtitle">Select a directory to begin structuring files</h2>
    
    <div class="manager-container">
      <FileManager @select="handleDirectorySelect" />
    </div>
  </div>
</template>

<style scoped>
.file-manager-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.view-subtitle {
  margin-bottom: var(--space-6);
  color: var(--color-text-light);
  font-weight: 500;
}

.manager-container {
  flex: 1;
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}
</style>