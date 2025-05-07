<template>
    <div class="method-selection">
      <div class="card">
        <h2>Оберіть метод аналізу файлів</h2>
        <p class="subtitle">Директорія: {{ session?.directory }}</p>
        
        <div v-if="loading" class="loader">
          Завантаження...
        </div>
        
        <div v-else class="methods-container">
          <div 
            v-for="method in methods" 
            :key="method.id"
            class="method-card"
            :class="{ selected: selectedMethod === method.id }"
            @click="selectedMethod = method.id"
          >
            <h3>{{ method.name }}</h3>
            <p>{{ method.description }}</p>
          </div>
        </div>
        
        <div class="actions">
          <button @click="goBack" class="btn-secondary">Назад</button>
          <button 
            @click="runAnalysis" 
            class="btn-primary" 
            :disabled="!selectedMethod || analyzeLoading"
          >
            Далі
          </button>
        </div>
        
        <div v-if="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>
      </div>
      
      <div v-if="analysisSummary" class="card">
        <h3>Результати аналізу</h3>
        <p>Проаналізовано файлів: {{ analysisSummary.files_analyzed }}</p>
        <div v-if="analysisSummary.description_examples.length > 0">
          <h4>Приклади описів:</h4>
          <ul>
            <li v-for="(example, index) in analysisSummary.description_examples" :key="index">
              {{ example }}
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
  import type { Session, AnalysisSummary as AnalysisSummaryType, AnalysisMethod } from '@/types';
  
  const props = defineProps({
    sessionId: {
      type: String as PropType<string>,
      required: true
    }
  });
  
  const router = useRouter();
  const session = ref<Session | null>(null);
  const methods = ref<Array<{id: string, name: string, description: string}>>([]);
  const selectedMethod = ref<AnalysisMethod | null>(null);
  const loading = ref(true);
  const analyzeLoading = ref(false);
  const error = ref('');
  const analysisSummary = ref<AnalysisSummaryType | null>(null);
  
  onMounted(async () => {
    try {
      // Load session details
      const sessionResponse = await api.getSession(props.sessionId);
      session.value = sessionResponse.data;
      
      // Load available analysis methods
      const methodsResponse = await api.getAnalysisMethods();
      methods.value = methodsResponse.data;
      
      // Pre-select method if already set in session
      if (session.value.analysis_method) {
        selectedMethod.value = session.value.analysis_method;
      }
    } catch (err: any) {
      console.error(err);
      error.value = err.response?.data || 'Помилка при завантаженні даних';
    } finally {
      loading.value = false;
    }
  });
  
  const runAnalysis = async () => {
    if (!selectedMethod.value) return;
    
    analyzeLoading.value = true;
    error.value = '';
    
    try {
      const response = await api.runAnalysis(props.sessionId, selectedMethod.value);
      analysisSummary.value = response.data;
      
      // Wait a moment to show the summary before proceeding
      setTimeout(() => {
        router.push({ name: 'algorithm', params: { sessionId: props.sessionId } });
      }, 2000);
    } catch (err: any) {
      console.error(err);
      error.value = err.response?.data || 'Помилка при запуску аналізу';
    } finally {
      analyzeLoading.value = false;
    }
  };
  
  const goBack = () => {
    router.push({ name: 'home' });
  };
  </script>
  
  <style scoped>
  .subtitle {
    color: #868e96;
    margin-bottom: 1.5rem;
  }
  
  .methods-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  
  .method-card {
    padding: 1rem;
    border: 2px solid #dee2e6;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .method-card:hover {
    border-color: #4c6ef5;
    transform: translateY(-2px);
  }
  
  .method-card.selected {
    border-color: #4c6ef5;
    background-color: #edf2ff;
  }
  
  .method-card h3 {
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