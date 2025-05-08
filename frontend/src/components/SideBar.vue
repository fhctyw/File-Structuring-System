<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const steps = [
  { name: 'File Selection', path: '/', step: 1 },
  { name: 'Analysis Method', path: '/method', step: 2 },
  { name: 'Structuring Algorithm', path: '/algorithm', step: 3 },
  { name: 'Preview Changes', path: '/preview', step: 4 },
  { name: 'Results', path: '/result', step: 5 }
]

const currentStep = computed(() => {
  return route.meta.step as number || 1
})

const isStepAccessible = (step: number) => {
  return step <= currentStep.value
}

const navigateToStep = (path: string, step: number) => {
  if (isStepAccessible(step)) {
    router.push(path)
  }
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h1 class="app-title">File Structuring</h1>
    </div>
    <nav class="steps-nav">
      <div 
        v-for="(step, index) in steps" 
        :key="index"
        class="step-item" 
        :class="{ 
          'active': currentStep === step.step, 
          'completed': currentStep > step.step,
          'clickable': isStepAccessible(step.step)
        }"
        @click="navigateToStep(step.path, step.step)"
      >
        <div class="step-indicator">
          <span class="step-number">{{ step.step }}</span>
        </div>
        <div class="step-label">{{ step.name }}</div>
      </div>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 280px;
  background-color: #f8fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 24px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: #2563eb;
  margin: 0;
}

.steps-nav {
  padding: 24px 0;
}

.step-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  transition: background-color 0.2s ease;
}

.step-item.clickable {
  cursor: pointer;
}

.step-item.clickable:hover {
  background-color: #e2e8f0;
}

.step-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.step-number {
  font-weight: 600;
  color: #64748b;
}

.step-item.active .step-indicator {
  background-color: #2563eb;
}

.step-item.active .step-number {
  color: #ffffff;
}

.step-item.completed .step-indicator {
  background-color: #10b981;
}

.step-item.completed .step-number {
  color: #ffffff;
}

.step-label {
  font-size: 16px;
  font-weight: 500;
  color: #64748b;
}

.step-item.active .step-label {
  color: #1e293b;
  font-weight: 600;
}
</style>