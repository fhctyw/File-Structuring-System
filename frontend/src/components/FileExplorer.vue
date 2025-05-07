<template>
  <div class="file-explorer">
    <div class="card">
      <h2>Оберіть директорію для структурування</h2>
      <div class="form-group">
        <label for="directory">Шлях до директорії:</label>
        <div class="directory-input">
          <input
            id="directory"
            v-model="directory"
            type="text"
            class="form-control"
            placeholder="/абсолютний/шлях/до/директорії"
          />
          <button @click="browseDirectory" class="btn-secondary">Обрати</button>
        </div>
        <small class="path-tip">Використовуйте формат: C:\\Users\\username\\path (подвійний слеш)</small>
      </div>
      
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="recursive" />
          Включати піддиректорії
        </label>
      </div>
      
      <button 
        @click="createSession" 
        class="btn-primary" 
        :disabled="!directory || loading"
      >
        Далі
      </button>
      
      <div v-if="error" class="alert alert-danger mt-3">
        {{ formattedError }}
      </div>

      <div v-if="backendStatus === 'error'" class="alert alert-warning mt-3">
        Схоже, що бекенд не запущено або не відповідає. Переконайтеся, що Python-сервер запущено.
      </div>
    </div>
    
    <div v-if="entries.length > 0" class="card">
      <h3>Вміст директорії</h3>
      <div class="file-list">
        <div v-for="entry in entries" :key="entry.path || entry.name" class="file-item">
          <span :class="['icon', entry.type === 'directory' ? 'folder' : 'file']"></span>
          <span class="file-name">{{ entry.name }}</span>
          <span class="size" v-if="entry.size">{{ formatSize(entry.size) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import type { FileSystemEntry } from '@/types';

const router = useRouter();
const directory = ref('');
const recursive = ref(true);
const entries = ref<FileSystemEntry[]>([]);
const loading = ref(false);
const error = ref('');
const backendStatus = ref('unknown'); // 'unknown', 'ok', 'error'

// Format path for windows (replace single backslashes with double)
const formatPath = (path: string): string => {
  // Replace single backslashes with double backslashes for the API
  return path.replace(/\\/g, '\\\\');
};

// Format error message to be more user-friendly
const formattedError = computed(() => {
  if (error.value.includes('Not Found')) {
    return `Директорія "${directory.value}" не знайдена або не може бути прочитана. Перевірте шлях та права доступу.`;
  }
  if (error.value.includes('Network Error')) {
    backendStatus.value = 'error';
    return "Помилка з'єднання з сервером. Переконайтеся, що Python-сервер запущено.";
  }
  return error.value;
});

const browseDirectory = async () => {
  // In a real application, this would open a native file dialog
  // For this demo, we'll just set a sample directory
  directory.value = 'C:\\Users\\arsen\\Desktop';
  await loadDirectoryContents();
};

const loadDirectoryContents = async () => {
  if (!directory.value) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    const formattedDir = formatPath(directory.value);
    console.log(`Requesting directory: ${formattedDir}`);
    
    const response = await api.getFileSystemEntries(formattedDir);
    entries.value = response.data.entries;
    backendStatus.value = 'ok';
  } catch (err: any) {
    console.error('Error loading directory:', err);
    if (err.response) {
      error.value = `${err.response.status}: ${JSON.stringify(err.response.data)}`;
    } else if (err.request) {
      error.value = 'Network Error: Не вдалося з\'єднатися з сервером';
      backendStatus.value = 'error';
    } else {
      error.value = err.message || 'Невідома помилка';
    }
    entries.value = [];
  } finally {
    loading.value = false;
  }
};

const createSession = async () => {
  if (!directory.value) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    const formattedDir = formatPath(directory.value);
    console.log(`Creating session for directory: ${formattedDir}`);
    
    const response = await api.createSession(formattedDir, recursive.value);
    const sessionId = response.data.id;
    router.push({ name: 'method', params: { sessionId } });
  } catch (err: any) {
    console.error('Error creating session:', err);
    if (err.response) {
      error.value = `${err.response.status}: ${JSON.stringify(err.response.data)}`;
    } else if (err.request) {
      error.value = 'Network Error: Не вдалося з\'єднатися з сервером';
      backendStatus.value = 'error';
    } else {
      error.value = err.message || 'Невідома помилка';
    }
  } finally {
    loading.value = false;
  }
};

const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

onMounted(() => {
  // Check if backend is available
  api.getAnalysisMethods()
    .then(() => {
      backendStatus.value = 'ok';
    })
    .catch(() => {
      backendStatus.value = 'error';
    });
    
  // Load last used directory from localStorage if available
  const lastDirectory = localStorage.getItem('lastDirectory');
  if (lastDirectory) {
    directory.value = lastDirectory;
    loadDirectoryContents();
  }
});
</script>

<style scoped>
.directory-input {
  display: flex;
  gap: 0.5rem;
}

.directory-input input {
  flex-grow: 1;
}

.path-tip {
  display: block;
  margin-top: 5px;
  color: #6c757d;
  font-size: 0.85rem;
}

.file-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-top: 1rem;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid #f1f3f5;
}

.file-item:last-child {
  border-bottom: none;
}

.icon {
  width: 20px;
  height: 20px;
  margin-right: 0.5rem;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon.folder {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%234c6ef5' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
}

.icon.file {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23868e96' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.size {
  margin-left: auto;
  color: #868e96;
  font-size: 0.85rem;
}

.mt-3 {
  margin-top: 1rem;
}

.alert-warning {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
}

.file-name {
  flex-grow: 1;
  margin-right: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>