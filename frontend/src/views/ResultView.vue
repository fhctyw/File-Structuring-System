<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import ProgressOverlay from '../components/ProgressOverlay.vue'
import { useSessionStore } from '../stores/useSessionStore'
import { useFsStore } from '../stores/useFsStore'
import { usePolling } from '../composables/usePolling'

const router = useRouter()
const sessionStore = useSessionStore()
const fsStore = useFsStore()

const isComplete = ref(false)

// Redirect if no session exists
onMounted(() => {
  if (!sessionStore.hasSession) {
    router.push('/')
    return
  }
  
  startPolling()
})

// Set up polling for progress
const polling = usePolling(
  () => sessionStore.getSessionProgress(),
  {
    interval: 3000,
    stopCondition: (data) => data.percentage >= 100,
    onComplete: () => {
      isComplete.value = true
    }
  }
)

const startPolling = async () => {
  await polling.start()
}

// Watch for completion to refresh the file list
watch(isComplete, async (newValue) => {
  if (newValue) {
    try {
      // Refresh the file structure after processing is complete
      await fsStore.fetchEntries()
    } catch (err) {
      console.error('Failed to refresh file list:', err)
    }
  }
})

// Start a new structuring process
const startNew = () => {
  sessionStore.resetSession()
  router.push('/')
}
</script>

<template>
  <div class="result-view">
    <div v-if="!isComplete">
      <ProgressOverlay
        :percentage="sessionStore.progress?.percentage || 0"
        :status="sessionStore.progress?.status || 'Обробка...'"
        :message="sessionStore.progress?.message"
      />
    </div>
    
    <div v-else class="completion-container">
      <div class="completion-card">
        <div class="success-icon">✓</div>
        <h2 class="completion-title">Структуризація завершена!</h2>
        <p class="completion-message">
          Ваші файли були успішно реструктуровані відповідно до обраного методу та алгоритму.
        </p>
        
        <div class="actions">
          <button @click="startNew">Почати нову структуризацію</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.result-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.completion-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: var(--space-6);
}

.completion-card {
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--space-8);
  text-align: center;
  max-width: 500px;
  animation: fadeIn 0.5s ease;
}

.success-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--color-success);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin: 0 auto var(--space-6);
}

.completion-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: var(--space-4);
  color: var(--color-text);
}

.completion-message {
  color: var(--color-text-light);
  margin-bottom: var(--space-6);
}

.actions {
  margin-top: var(--space-6);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>