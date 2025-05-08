<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PreviewTree from '../components/PreviewTree.vue'
import { useSessionStore } from '../stores/useSessionStore'
import { useFsStore } from '../stores/useFsStore'

const router = useRouter()
const sessionStore = useSessionStore()
const fsStore = useFsStore()

// Redirect if no session exists
onMounted(async () => {
  if (!sessionStore.hasSession) {
    router.push('/')
    return
  }
  
  await fetchPreview()
})

// Fetch preview of file structure changes
const fetchPreview = async () => {
  try {
    await fsStore.fetchPreview(sessionStore.sessionId!)
  } catch (err) {
    console.error('Failed to fetch preview:', err)
  }
}

// Go back to algorithm selection
const goBack = () => {
  router.push('/algorithm')
}

// Apply changes and proceed to result view
const applyChanges = async () => {
  try {
    await sessionStore.applyChanges(false)
    router.push('/result')
  } catch (err) {
    console.error('Failed to apply changes:', err)
  }
}
</script>

<template>
  <div class="preview-view">
    <h2 class="view-subtitle">Preview the structural changes</h2>
    
    <div v-if="fsStore.loading" class="loading">
      Loading preview...
    </div>
    
    <div v-else-if="fsStore.error" class="error">
      {{ fsStore.error }}
    </div>
    
    <div v-else class="preview-container">
      <PreviewTree
        :before="fsStore.previewBefore"
        :after="fsStore.previewAfter"
      />
      
      <div class="actions">
        <button class="secondary" @click="goBack">Edit Selection</button>
        <button @click="applyChanges">Start Structuring</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.preview-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.view-subtitle {
  margin-bottom: var(--space-6);
  color: var(--color-text-light);
  font-weight: 500;
}

.loading, .error {
  padding: var(--space-8);
  text-align: center;
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.error {
  color: var(--color-error);
}

.preview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  padding: var(--space-6);
}

.actions {
  margin-top: var(--space-6);
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #e2e8f0;
  padding-top: var(--space-6);
}
</style>