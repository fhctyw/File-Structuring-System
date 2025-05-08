<template>
  <div class="file-explorer">
    <header class="explorer-header">
      <h2>Оберіть директорію для структурування</h2>
      <div class="path-controls">
        <input
          v-model="currentPath"
          type="text"
          class="path-input"
          placeholder="C:\шлях\до\директорії"
          @keyup.enter="loadPath"
        />
        <button @click="loadPath" class="btn-secondary">Обрати</button>
      </div>
      <small class="path-tip">Використовуйте формат: C:\\Users\\username\\path</small>
    </header>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Завантаження...</p>
    </div>

    <main class="explorer-body">
      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div v-if="!error && currentEntries.length > 0" class="file-list">
        <div 
          v-if="hasParentDirectory" 
          class="file-item is-folder" 
          @click="navigateToParent"
        >
          <span class="icon back-icon"></span>
          <span>..</span>
        </div>

        <div 
          v-for="(entry, index) in currentEntries" 
          :key="index" 
          class="file-item" 
          :class="{ 'is-folder': isFolder(entry) }" 
          @click="handleItemClick(entry)"
        >
          <span :class="['icon', isFolder(entry) ? 'folder-icon' : 'file-icon']"></span>
          <span>{{ entry.name || 'Без імені' }}</span>
        </div>
      </div>

      <div v-if="!loading && !error && currentEntries.length === 0" class="empty-state">
        <p>Порожня директорія або шлях не існує</p>
      </div>
    </main>

    <footer class="explorer-footer">
      <label>
        <input type="checkbox" v-model="recursive" />
        Включати піддиректорії
      </label>
      <button 
        @click="createSession" 
        class="btn-primary" 
        :disabled="!currentPath || loading"
      >
        Продовжити
      </button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';

const router = useRouter();
const currentPath = ref('');
const currentEntries = ref([]);
const loading = ref(false);
const error = ref('');
const recursive = ref(true);

const hasParentDirectory = computed(() => {
  const parts = currentPath.value.split(/[/\\]/);
  return parts.length > 1;
});

const navigateToParent = () => {
  const parts = currentPath.value.split(/[/\\]/);
  parts.pop();
  currentPath.value = parts.join('\\');
  loadPath();
};

const loadPath = async () => {
  if (!currentPath.value) return;
  loading.value = true;
  error.value = '';

  try {
    console.log('Запит до API з шляхом:', currentPath.value);
    const response = await api.getFileSystemEntries(currentPath.value);
    console.log('Відповідь API:', response.data);
    currentEntries.value = response.data.entries || [];
  } catch (err) {
    console.error('Помилка завантаження:', err);
    error.value = err.response?.data?.error || 'Помилка завантаження директорії';
  } finally {
    loading.value = false;
    console.log('Завантаження завершено');
  }
};

const isFolder = (entry) => entry.type === 'directory';

const handleItemClick = (entry) => {
  if (isFolder(entry)) {
    currentPath.value = entry.path;
    loadPath();
  }
};

const createSession = async () => {
  if (!currentPath.value) return;
  loading.value = true;
  error.value = '';

  try {
    const response = await api.createSession(currentPath.value, recursive.value);
    router.push({ name: 'method', params: { sessionId: response.data.id } });
  } catch (err) {
    error.value = err.response?.data?.error || 'Помилка створення сесії';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.file-explorer {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.explorer-header {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.path-controls {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.path-input {
  flex-grow: 1;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.path-tip {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #6c757d;
}

.loading-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.explorer-body {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
}

.file-list {
  display: flex;
  flex-direction: column;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 4px;
}

.file-item:hover {
  background-color: #f8f9fa;
}

.file-item.is-folder:hover {
  background-color: #e7f1ff;
}

.icon {
  width: 20px;
  height: 20px;
  margin-right: 0.5rem;
}

.folder-icon {
  background: url('folder-icon.svg') no-repeat center;
}

.file-icon {
  background: url('file-icon.svg') no-repeat center;
}

.back-icon {
  background: url('back-icon.svg') no-repeat center;
}

.empty-state {
  text-align: center;
  color: #6c757d;
}

.explorer-footer {
  padding: 1rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>