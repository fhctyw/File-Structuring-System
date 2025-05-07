<template>
    <div class="algorithm-selection">
      <div class="card">
        <h2>Оберіть алгоритм структурування</h2>
        <p class="subtitle">Директорія: {{ session?.directory }}</p>
        <p class="info">Метод аналізу: {{ getMethodName(session?.analysis_method) }}</p>
        
        <div v-if="loading" class="loader">
          Завантаження...
        </div>
        
        <div v-else class="algorithms-container">
          <div 
            v-for="algorithm in algorithms" 
            :key="algorithm.id"
            class="algorithm-card"
            :class="{ selected: selectedAlgorithm === algorithm.id }"
            @click="selectedAlgorithm = algorithm.id"
          >
            <h3>{{ algorithm.name }}</h3>
            <p>{{ algorithm.description }}</p>
          </div>
        </div>
        
        <div class="actions">
          <button @click="goBack" class="btn-secondary">Назад</button>
          <button 
            @click="generatePlan" 
            class="btn-primary" 
            :disabled="!selectedAlgorithm || planLoading"
          >
            Далі
          </button>
        </div>
        
        <div v-if="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>
      </div>
      
      <div v-if="planSummary" class="card">
        <h3>Результати планування</h3>
        <p>Створено дій: {{ planSummary.actions_created }}</p>
        <div v-if="Object.keys(planSummary.breakdown).length > 0">
          <h4>Розподіл дій:</h4>
          <ul>
            <li v-for="(count, action) in planSummary.breakdown" :key="action">
              {{ action }}: {{ count }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import type { PropType } from 'vue';
  import api from '@/services/api';
  import type { Session, PlanSummary as PlanSummaryType, StructAlgorithm } from '@/types';
  
  const props = defineProps({
    sessionId: {
      type: String as PropType<string>,
      required: true
    }
  });
  
  const router = useRouter();
  const session = ref<Session | null>(null);
  const algorithms = ref<Array<{id: string, name: string, description: string}>>([]);
  const selectedAlgorithm = ref<StructAlgorithm | null>(null);
  const loading = ref(true);
  const planLoading = ref(false);
  const error = ref('');
  const planSummary = ref<PlanSummaryType | null>(null);
  
  // Method names map
  const methodNames: Record<string, string> = {
    'META': 'Аналіз метаданих',
    'STRUCT': 'Структурний аналіз',
    'SEMANTIC': 'Семантичний аналіз'
  };
  
  const getMethodName = (methodId?: string): string => {
    if (!methodId) return 'Не обрано';
    return methodNames[methodId] || methodId;
  };
  
  onMounted(async () => {
    try {
      // Load session details
      const sessionResponse = await api.getSession(props.sessionId);
      session.value = sessionResponse.data;
      
      // Load available structuring algorithms
      const algorithmsResponse = await api.getStructAlgorithms();
      algorithms.value = algorithmsResponse.data;
      
      // Pre-select algorithm if already set in session
      if (session.value.struct_algorithm) {
        selectedAlgorithm.value = session.value.struct_algorithm;
      }
    } catch (err: any) {
      console.error(err);
      error.value = err.response?.data || 'Помилка при завантаженні даних';
    } finally {
      loading.value = false;
    }
  });
  
  const generatePlan = async () => {
    if (!selectedAlgorithm.value) return;
    
    planLoading.value = true;
    error.value = '';
    
    try {
      const response = await api.generatePlan(props.sessionId, selectedAlgorithm.value);
      planSummary.value = response.data;
      
      // Wait a moment to show the summary before proceeding
      setTimeout(() => {
        router.push({ name: 'preview', params: { sessionId: props.sessionId } });
      }, 2000);
    } catch (err: any) {
      console.error(err);
      error.value = err.response?.data || 'Помилка при генерації плану';
    } finally {
      planLoading.value = false;
    }
  };
  
  const goBack = () => {
    router.push({ name: 'method', params: { sessionId: props.sessionId } });
  };
  </script>
  
  <style scoped>
  .subtitle, .info {
    color: #868e96;
    margin-bottom: 0.5rem;
  }
  
  .info {
    margin-bottom: 1.5rem;
  }
  
  .algorithms-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  
  .algorithm-card {
    padding: 1rem;
    border: 2px solid #dee2e6;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .algorithm-card:hover {
    border-color: #4c6ef5;
    transform: translateY(-2px);
  }
  
  .algorithm-card.selected {
    border-color: #4c6ef5;
    background-color: #edf2ff;
  }
  
  .algorithm-card h3 {
    margin-bottom: 0.5rem;
    color: #4c6ef5;
  }
  
  .actions {
    display: flex;
    justify-content: space-between;
    margin-top: 1.5rem;
  }
  
  .loader {
    text-align: center;
    padding: 2rem;
    color: #868e96;
  }
  
  .mt-3 {
    margin-top: 1rem;
  }
  </style>