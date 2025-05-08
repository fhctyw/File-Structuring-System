<script setup lang="ts">
const props = defineProps<{
  percentage: number
  status: string
  message?: string
}>()
</script>

<template>
  <div class="progress-overlay">
    <div class="progress-card">
      <h3 class="progress-title">Processing Files</h3>
      
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: `${percentage}%` }"></div>
      </div>
      
      <div class="progress-info">
        <div class="progress-percentage">{{ percentage }}%</div>
        <div class="progress-status">{{ status }}</div>
      </div>
      
      <div v-if="message" class="progress-message">{{ message }}</div>
    </div>
  </div>
</template>

<style scoped>
.progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 100;
  backdrop-filter: blur(4px);
}

.progress-card {
  background-color: var(--color-background);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  width: 100%;
  max-width: 500px;
  box-shadow: var(--shadow-lg);
  animation: fadeIn 0.3s ease;
}

.progress-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: var(--space-6);
  text-align: center;
  color: var(--color-text);
}

.progress-bar-container {
  height: 12px;
  background-color: #e2e8f0;
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--space-4);
}

.progress-bar {
  height: 100%;
  background-color: var(--color-primary);
  transition: width 0.5s ease;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.progress-percentage {
  font-weight: 600;
  color: var(--color-primary);
}

.progress-status {
  color: var(--color-text-light);
}

.progress-message {
  padding: var(--space-4);
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  font-style: italic;
  color: var(--color-text-light);
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