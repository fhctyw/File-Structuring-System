<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import DynamicForm from '../components/DynamicForm.vue'
import { useSessionStore } from '../stores/useSessionStore'
import { methodsApi, type AnalysisMethod } from '../services/api'
import { useApi } from '../composables/useApi'

const router = useRouter()
const sessionStore = useSessionStore()

// Підготовка реактивних станів
const methodsApi$ = useApi(methodsApi.getAnalysisMethods)
const selectedLayer = ref<string>('META')
const selectedMethod = ref<string>('')
const methodParams = reactive<Record<string, any>>({})

// Обчислювані властивості для спрощення доступу в шаблоні
const isLoading = computed(() => methodsApi$.loading.value)
const hasError = computed(() => !!methodsApi$.error.value)
const hasData = computed(() => !!methodsApi$.data.value)
const errorMessage = computed(() => methodsApi$.error.value?.message || 'Невідома помилка')

// Отримання методів для вибраного шару
const methodsInSelectedLayer = computed(() => {
  if (!hasData.value || !methodsApi$.data.value || !methodsApi$.data.value[selectedLayer.value]) {
    return []
  }
  return methodsApi$.data.value[selectedLayer.value]
})

// Отримання вибраного методу
const selectedMethodObject = computed(() => {
  if (!selectedMethod.value || methodsInSelectedLayer.value.length === 0) return null
  return methodsInSelectedLayer.value.find(m => m.id === selectedMethod.value)
})

// Створення схеми для параметрів методу
const methodParamsSchema = computed(() => {
  return {
    type: 'object',
    properties: {
      // Проста схема-приклад - у реальному додатку це було б згенеровано на основі вимог методу
      options: {
        type: 'object',
        properties: {}
      }
    }
  }
})

// Доступні шари методів
const layers = [
  { id: 'META', name: 'Мета-інформація' },
  { id: 'STRUCT', name: 'Аналіз структури' },
  { id: 'CONTENT', name: 'Аналіз вмісту' }
]

// Функція для отримання методів з API
const fetchMethods = async () => {
  try {
    console.log('Fetching methods...')
    const result = await methodsApi$.execute()
    console.log('Raw API result:', result)
    console.log('Methods fetched:', methodsApi$.data.value)
    
    // Перевірка наявності даних
    if (!methodsApi$.data.value) {
      console.warn('No data returned from API')
    }
    
    // Переконаємось, що DOM оновиться
    await nextTick()
    console.log('After nextTick - Loading:', methodsApi$.loading.value)
    console.log('After nextTick - Has data:', !!methodsApi$.data.value)
  } catch (err) {
    console.error('Failed to fetch methods:', err)
  }
}

// Функція вибору методу
const handleMethodSelect = (methodId: string) => {
  selectedMethod.value = methodId
}

// Перехід до наступного кроку (вибір алгоритму)
const continueToAlgorithm = () => {
  if (!selectedMethod.value) return
  
  // Збереження вибраного методу в локальному сховищі
  localStorage.setItem('selectedMethod', selectedMethod.value)
  localStorage.setItem('methodParams', JSON.stringify(methodParams))
  
  router.push('/algorithm')
}

// Спостереження за змінами
watch(() => selectedLayer.value, (newValue) => {
  console.log('Selected layer changed:', newValue)
})

watch(() => methodsApi$.data.value, (newValue) => {
  console.log('methodsApi$.data updated:', newValue)
})

// Отримання даних при монтуванні компонента
onMounted(async () => {
  if (!sessionStore.hasSession) {
    router.push('/')
    return
  }
  
  await fetchMethods()
})
</script>

<template>
  <div class="method-select-view">
    <h2 class="view-subtitle">Оберіть метод аналізу для ваших файлів</h2>
    
    <!-- Debug info для розробки -->
    <!-- <div class="debug-info" style="margin-bottom: 10px; padding: 10px; border: 1px solid #ccc;">
      <strong>Debug Info:</strong>
      <ul>
        <li>isLoading: {{ isLoading }}</li>
        <li>hasError: {{ hasError }}</li>
        <li>hasData: {{ hasData }}</li>
        <li v-if="hasData">Available Layers: {{ Object.keys(methodsApi$.data.value ?? {}).join(', ') }}</li>
      </ul>
    </div> -->
    
    <!-- Екран завантаження -->
    <div v-if="isLoading" class="loading">
      Завантаження доступних методів...
    </div>
    
    <!-- Повідомлення про помилку -->
    <div v-else-if="hasError" class="error">
      Помилка: {{ errorMessage }}
    </div>
    
    <!-- Немає даних після завантаження -->
    <div v-else-if="!hasData" class="info">
      Дані відсутні. Спробуйте оновити сторінку.
    </div>
    
    <!-- Основний вміст - методи та вибір -->
    <div v-else class="method-selection">
      <div class="layer-tabs">
        <button
          v-for="layer in layers"
          :key="layer.id"
          class="layer-tab"
          :class="{ 'active': selectedLayer === layer.id }"
          @click="selectedLayer = layer.id"
        >
          {{ layer.name }}
        </button>
      </div>
      
      <!-- Повідомлення, якщо немає методів у вибраному шарі -->
      <div v-if="methodsInSelectedLayer.length === 0" class="no-methods">
        Методи для вибраного шару відсутні.
      </div>
      
      <!-- Сітка методів -->
      <div v-else class="methods-grid">
        <div
          v-for="method in methodsInSelectedLayer"
          :key="method.id"
          class="method-card"
          :class="{ 'selected': selectedMethod === method.id }"
          @click="handleMethodSelect(method.id)"
        >
          <div v-if="selectedMethod === method.id" class="selected-indicator">✓ Вибрано</div>

          <div class="method-header">
            <h3 class="method-name">{{ method.action }}</h3>
            <span class="method-domain">Область: {{ method.domain }}</span>
          </div>
          
          <p class="method-description">{{ method.description }}</p>
          
          <div class="method-returns">
            <h4>Повертає:</h4>
            <ul>
              <li v-for="ret in method.returns" :key="ret.name">
                {{ ret.name }}: <span class="return-type">{{ ret.type }}</span>
                <span v-if="ret.unit" class="return-unit">({{ ret.unit }})</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- Кнопки дій -->
      <div class="actions">
        <button class="secondary" @click="router.push('/')">Назад</button>
        <button
          :disabled="!selectedMethod"
          @click="continueToAlgorithm"
        >
          Продовжити
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.method-select-view {
  display: flex;
  flex-direction: column;
}

.view-subtitle {
  margin-bottom: var(--space-6);
  color: var(--color-text-light);
  font-weight: 500;
}

.loading, .error, .info, .no-methods {
  padding: var(--space-8);
  text-align: center;
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.error {
  color: var(--color-error);
}

.method-selection {
  background-color: white;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.layer-tabs {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  background-color: var(--color-surface);
}

.layer-tab {
  padding: var(--space-4) var(--space-6);
  background: none;
  border: none;
  font-weight: 500;
  color: var(--color-text-light);
  cursor: pointer;
  transition: color 0.2s ease, box-shadow 0.2s ease;
  border-bottom: 2px solid transparent;
}

.layer-tab:hover {
  color: var(--color-primary);
  background-color: rgba(0, 0, 0, 0.02);
}

.layer-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.methods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-4);
  padding: var(--space-4);
}

.method-card {
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  cursor: pointer;
  transition: all 0.2s ease;
}

.method-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.method-card.selected {
  border-color: var(--color-primary);
  background-color: rgba(37, 99, 235, 0.05);
}

.method-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.method-name {
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.method-domain {
  font-size: 0.75rem;
  color: var(--color-text-light);
  background-color: #f1f5f9;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
}

.method-description {
  margin-bottom: var(--space-3);
  font-size: 0.875rem;
  color: var(--color-text);
}

.method-returns {
  font-size: 0.875rem;
}

.method-returns h4 {
  margin-bottom: var(--space-2);
  font-weight: 500;
}

.method-returns ul {
  list-style: none;
  padding: 0;
}

.method-returns li {
  margin-bottom: var(--space-1);
}

.return-type {
  color: var(--color-primary);
  font-weight: 500;
}

.return-unit {
  color: var(--color-text-light);
  font-size: 0.75rem;
}

.method-params {
  padding: var(--space-6);
  border-top: 1px solid #e2e8f0;
}

.method-params h3 {
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

.method-card {
  position: relative;
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
</style>