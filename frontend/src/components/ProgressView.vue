<template>
    <div class="progress-view">
      <div class="card">
        <h2>Застосування змін</h2>
        <p class="subtitle">Директорія: {{ session?.directory }}</p>
        
        <div class="progress-info">
          <h3>{{ progressReport?.status || 'Ініціалізація...' }}</h3>
          
          <div class="progress-container">
            <div 
              class="progress-bar" 
              :style="{ width: `${progressReport?.percent || 0}%` }"
            ></div>
          </div>
          
          <p class="progress-percent">{{ progressReport?.percent || 0 }}% завершено</p>
        </div>
        
        <div v-if="result" class="result-info">
          <h3>Результат</h3>
          <p>Успішно застосовано дій: {{ result.applied }}</p>
          <p>Невдалих дій: {{ result.failed }}</p>
          
          <div v-if="result.errors.length > 0" class="errors">
            <h4>Помилки:</h4>
            <ul>
              <li v-for="(error, index) in result.errors" :key="index">
                {{ error }}
              </li>
            </ul>
          </div>
        </div>
        
        <div class="actions">
          <button 
            @click="goToHome" 
            class="btn-primary"
            :disabled="!completed"
          >
            Завершити
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, onUnmounted } from 'vue';
  import { useRouter } from 'vue-router';
  import type { PropType } from 'vue';
  import api from '@/services/api';
  import type { Session, ProgressReport, ApplyResult } from '@/types';
  
  const props = defineProps({
    sessionId: {
      type: String as PropType<string>,
      required: true
    }
  });
  
  const router = useRouter();
  const session = ref<Session | null>(null);
  const progressReport = ref<ProgressReport | null>(null);
  const result = ref<ApplyResult | null>(null);
  const completed = ref(false);
  const intervalId = ref<number | null>(null);
  
  onMounted(async () => {
    try {
      // Load session details
      const sessionResponse = await api.getSession(props.sessionId);
      session.value = sessionResponse.data;
      
      // Start polling for progress
      startProgressPolling();
    } catch (err) {
      console.error(err);
    }
  });
  
  onUnmounted(() => {
    if (intervalId.value !== null) {
      clearInterval(intervalId.value);
    }
  });
  
  const startProgressPolling = () => {
    // Check progress immediately
    checkProgress();
    
    // Then check every second
    intervalId.value = window.setInterval(() => {
      checkProgress();
    }, 1000);
  };
  
  const checkProgress = async () => {
    try {
      const response = await api.getProgress(props.sessionId);
      progressReport.value = response.data;
      
      // If completed (100%)
      if (progressReport.value.percent === 100) {
        completed.value = true;
        
        // Stop polling
        if (intervalId.value !== null) {
          clearInterval(intervalId.value);
          intervalId.value = null;
        }
        
        // Get final result
        const resultResponse = await api.applyPlan(props.sessionId, true); // Get result with dry_run=true
        result.value = resultResponse.data;
      }
    } catch (err) {
      console.error(err);
      
      // In case of error, stop polling
      if (intervalId.value !== null) {
        clearInterval(intervalId.value);
        intervalId.value = null;
      }
    }
  };
  
  const goToHome = () => {
    router.push({ name: 'home' });
  };
  </script>
  
  <style scoped>
  .subtitle {
    color: #868e96;
    margin-bottom: 1.5rem;
  }
  
  .progress-info {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .progress-info h3 {
    margin-bottom: 1rem;
  }
  
  .progress-container {
    width: 100%;
    height: 20px;
    background-color: #e9ecef;
    border-radius: 10px;
    overflow: hidden;
  }
  
  .progress-bar {
    height: 100%;
    background-color: #40c057;
    width: 0;
    transition: width 0.5s ease;
  }
  
  .progress-percent {
    margin-top: 0.5rem;
    font-weight: 500;
  }
  
  .result-info {
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #dee2e6;
  }
  
  .errors {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #fff5f5;
    border-radius: 4px;
  }
  
  .errors h4 {
    color: #fa5252;
    margin-bottom: 0.5rem;
  }
  
  .errors ul {
    padding-left: 1.5rem;
    color: #fa5252;
  }
  
  .actions {
    display: flex;
    justify-content: center;
    margin-top: 2rem;
  }
  </style>