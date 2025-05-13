<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import DynamicForm from '../components/DynamicForm.vue'
import { useSessionStore } from '../stores/useSessionStore'
import { algorithmsApi } from '../services/api'
import { useApi } from '../composables/useApi'

const router = useRouter()
const sessionStore = useSessionStore()

// Підготовка реактивних станів
const algorithmsApi$ = useApi(algorithmsApi.getStructAlgorithms)
const selectedMethod = ref<string>('')
const selectedAlgorithm = ref<string>('')
const algorithmParams = reactive<Record<string, any>>({})

// Обчислювані властивості для спрощення доступу в шаблоні
const isLoading = computed(() => algorithmsApi$.loading.value)
const hasError = computed(() => !!algorithmsApi$.error.value)
const hasData = computed(() => !!algorithmsApi$.data.value)
const errorMessage = computed(() => algorithmsApi$.error.value?.message || 'Невідома помилка')

// Отримання вибраного алгоритму
const selectedAlgorithmObject = computed(() => {
  if (!selectedAlgorithm.value || !algorithmsApi$.data.value) return null
  return algorithmsApi$.data.value.find(a => a.id === selectedAlgorithm.value)
})

// Створення схеми параметрів на основі схеми вибраного алгоритму
const algorithmParamsSchema = computed(() => {
  if (!selectedAlgorithmObject.value) {
    return {
      type: 'object',
      properties: {}
    }
  }
  
  return selectedAlgorithmObject.value.params_schema
})

// Fetch structuring algorithms from API
const fetchAlgorithms = async () => {
  try {
    console.log('Fetching algorithms...')
    const result = await algorithmsApi$.execute()
    console.log('Raw API result:', result)
    console.log('Algorithms fetched:', algorithmsApi$.data.value)
    
    // Перевірка наявності даних
    if (!algorithmsApi$.data.value) {
      console.warn('No data returned from API')
    }
    
    // Переконаємось, що DOM оновиться
    await nextTick()
    console.log('After nextTick - Loading:', algorithmsApi$.loading.value)
    console.log('After nextTick - Has data:', !!algorithmsApi$.data.value)
  } catch (err) {
    console.error('Failed to fetch algorithms:', err)
  }
}

// Handle algorithm selection
const handleAlgorithmSelect = (algorithmId: string) => {
  selectedAlgorithm.value = algorithmId
}

// Process the session and continue to preview
const continueToPreview = async () => {
  if (!selectedAlgorithm.value) return
  
  try {
    await sessionStore.processSession(
      selectedMethod.value,
      selectedAlgorithm.value,
      algorithmParams
    )
    
    router.push('/preview')
  } catch (err) {
    console.error('Failed to process session:', err)
  }
}

// Спостереження за змінами
watch(() => algorithmsApi$.data.value, (newValue) => {
  console.log('algorithmsApi$.data updated:', newValue)
})

// Отримання даних при монтуванні компонента
onMounted(async () => {
  if (!sessionStore.hasSession) {
    router.push('/')
    return
  }
  
  // Get selected method from previous step
  const method = localStorage.getItem('selectedMethod')
  if (!method) {
    router.push('/method')
    return
  }
  
  selectedMethod.value = method
  
  await fetchAlgorithms()
})
</script>

<template>
  <div class="algorithm-select-view">
    <h2 class="view-subtitle">Оберіть алгоритм для структуризації ваших файлів</h2>
    
    <!-- Debug info для розробки -->
    <!-- <div class="debug-info" style="margin-bottom: 10px; padding: 10px; border: 1px solid #ccc;">
      <strong>Debug Info:</strong>
      <ul>
        <li>isLoading: {{ isLoading }}</li>
        <li>hasError: {{ hasError }}</li>
        <li>hasData: {{ hasData }}</li>
        <li v-if="hasData">Algorithms count: {{ algorithmsApi$.data.value?.length }}</li>
      </ul>
    </div> -->
    
    <!-- Екран завантаження -->
    <div v-if="isLoading" class="loading">
      Завантаження доступних алгоритмів...
    </div>
    
    <!-- Повідомлення про помилку -->
    <div v-else-if="hasError" class="error">
      Помилка: {{ errorMessage }}
    </div>
    
    <!-- Немає даних після завантаження -->
    <div v-else-if="!hasData" class="info">
      Алгоритми відсутні. Спробуйте оновити сторінку.
    </div>
    
    <!-- Основний вміст - алгоритми та вибір -->
    <div v-else class="algorithm-selection">
      <!-- Сітка алгоритмів -->
      <div v-if="algorithmsApi$.data.value.length === 0" class="no-algorithms">
        Алгоритми відсутні.
      </div>
      
      <div v-else class="algorithms-grid">
        <div
          v-for="algorithm in algorithmsApi$.data.value"
          :key="algorithm.id"
          class="algorithm-card"
          :class="{ 'selected': selectedAlgorithm === algorithm.id }"
          @click="handleAlgorithmSelect(algorithm.id)"
        >
          <div v-if="selectedAlgorithm === algorithm.id" class="selected-indicator">✓ Вибрано</div>
          
          <div class="algorithm-header">
            <h3 class="algorithm-name">{{ algorithm.id }}</h3>
            <span class="algorithm-scope">Область: {{ algorithm.scope }}</span>
          </div>
          
          <p class="algorithm-description">{{ algorithm.description }}</p>
        </div>
      </div>
      
      <!-- Параметри вибраного алгоритму -->
      <div v-if="selectedAlgorithm" class="algorithm-params">
        <h3>Параметри алгоритму</h3>
        <p class="params-info">
          Налаштуйте параметри для вибраного алгоритму:
          <strong>{{ selectedAlgorithmObject?.id }}</strong>
        </p>
        
        <DynamicForm
          v-if="selectedAlgorithmObject"
          :schema="algorithmParamsSchema"
          v-model="algorithmParams"
        />
      </div>
      
      <!-- Кнопки дій -->
      <div class="actions">
        <button class="secondary" @click="router.push('/method')">Назад</button>
        <button
          :disabled="!selectedAlgorithm"
          @click="continueToPreview"
        >
          Продовжити
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.algorithm-select-view {
  display: flex;
  flex-direction: column;
}

.view-subtitle {
  margin-bottom: var(--space-6);
  color: var(--color-text-light);
  font-weight: 500;
}

.loading, .error, .info, .no-algorithms {
  padding: var(--space-8);
  text-align: center;
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.error {
  color: var(--color-error);
}

.algorithm-selection {
  background-color: white;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.algorithms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-4);
  padding: var(--space-4);
}

.algorithm-card {
  position: relative;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  cursor: pointer;
  transition: all 0.2s ease;
}

.algorithm-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.algorithm-card.selected {
  border-color: var(--color-primary);
  background-color: rgba(37, 99, 235, 0.05);
}

.selected-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: var(--color-primary);
  color: white;
  padding: 2px 8px;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  font-weight: 500;
}

.algorithm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.algorithm-name {
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.algorithm-scope {
  font-size: 0.75rem;
  color: var(--color-text-light);
  background-color: #f1f5f9;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
}

.algorithm-description {
  margin-bottom: var(--space-3);
  font-size: 0.875rem;
  color: var(--color-text);
}

.algorithm-params {
  padding: var(--space-6);
  border-top: 1px solid #e2e8f0;
}

.algorithm-params h3 {
  margin-bottom: var(--space-3);
}

.params-info {
  margin-bottom: var(--space-4);
  color: var(--color-text-light);
}

.actions {
  padding: var(--space-4);
  background-color: var(--color-surface);
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #e2e8f0;
}

/* Додаткові стилі для відлагоджувальної інформації */
.debug-info {
  font-family: monospace;
  font-size: 12px;
  margin-bottom: 10px;
}

.debug-info ul {
  list-style: none;
  padding-left: 10px;
}
</style>