<template>
    <div class="preview-view">
      <div class="card">
        <h2>Превью структуризації</h2>
        <p class="subtitle">Директорія: {{ session?.directory }}</p>
        <div class="info-row">
          <span>Метод аналізу: {{ getMethodName(session?.analysis_method) }}</span>
          <span>Алгоритм: {{ getAlgorithmName(session?.struct_algorithm) }}</span>
        </div>
        
        <div v-if="loading" class="loader">
          Завантаження превью...
        </div>
        
        <div v-else-if="preview" class="preview-container">
          <h3>Майбутня структура файлів:</h3>
          <div class="tree-view">
            <TreeNode :node="preview.tree" :root-path="session?.directory || ''" />
          </div>
        </div>
        
        <div class="actions">
          <button @click="goBack" class="btn-secondary">Назад</button>
          <button @click="applyPlan" class="btn-success" :disabled="applyLoading">
            Застосувати зміни
          </button>
        </div>
        
        <div v-if="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, defineComponent } from 'vue';
  import { useRouter } from 'vue-router';
  import type { PropType } from 'vue';
  import api from '@/services/api';
  import type { Session, PreviewTree as PreviewTreeType } from '@/types';
  
  // Define TreeNode component
  const TreeNode = defineComponent({
    name: 'TreeNode',
    props: {
      node: {
        type: Object as PropType<Record<string, any>>,
        required: true
      },
      rootPath: {
        type: String,
        required: true
      },
      level: {
        type: Number,
        default: 0
      }
    },
    setup(props) {
      const isFolder = (item: any): boolean => {
        return typeof item === 'object' && item !== null && !item.toString().startsWith('MOVE->');
      };
      
      return { isFolder };
    },
    template: `
      <div class="tree-node" :style="{ marginLeft: level * 20 + 'px' }">
        <div v-for="(value, key) in node" :key="key">
          <div v-if="isFolder(value)" class="folder">
            <span class="folder-icon"></span>
            <span class="folder-name">{{ key }}</span>
            <TreeNode :node="value" :root-path="rootPath + '/' + key" :level="level + 1" />
          </div>
          <div v-else class="file">
            <span class="file-icon"></span>
            <span class="file-name">{{ key }}</span>
            <span v-if="typeof value === 'string' && value.startsWith('MOVE->')" class="action">
              {{ value }}
            </span>
          </div>
        </div>
      </div>
    `
  });
  
  const props = defineProps({
    sessionId: {
      type: String as PropType<string>,
      required: true
    }
  });
  
  const router = useRouter();
  const session = ref<Session | null>(null);
  const preview = ref<PreviewTreeType | null>(null);
  const loading = ref(true);
  const applyLoading = ref(false);
  const error = ref('');
  
  // Method names map
  const methodNames: Record<string, string> = {
    'META': 'Аналіз метаданих',
    'STRUCT': 'Структурний аналіз',
    'SEMANTIC': 'Семантичний аналіз'
  };
  
  // Algorithm names map
  const algorithmNames: Record<string, string> = {
    'BY_TYPE': 'За типом файлів',
    'CLUSTER': 'Кластеризація',
    'CRITERIA': 'За критеріями'
  };
  
  const getMethodName = (methodId?: string): string => {
    if (!methodId) return 'Не обрано';
    return methodNames[methodId] || methodId;
  };
  
  const getAlgorithmName = (algorithmId?: string): string => {
    if (!algorithmId) return 'Не обрано';
    return algorithmNames[algorithmId] || algorithmId;
  };
  
  onMounted(async () => {
    try {
      // Load session details
      const sessionResponse = await api.getSession(props.sessionId);
      session.value = sessionResponse.data;
      
      // Load preview
      const previewResponse = await api.getPreview(props.sessionId);
      preview.value = previewResponse.data;
    } catch (err: any) {
      console.error(err);
      error.value = err.response?.data || 'Помилка при завантаженні превью';
    } finally {
      loading.value = false;
    }
  });
  
  const applyPlan = async () => {
    applyLoading.value = true;
    error.value = '';
    
    try {
      await api.applyPlan(props.sessionId, false);
      router.push({ name: 'progress', params: { sessionId: props.sessionId } });
    } catch (err: any) {
      console.error(err);
      error.value = err.response?.data || 'Помилка при застосуванні змін';
      applyLoading.value = false;
    }
  };
  
  const goBack = () => {
    router.push({ name: 'algorithm', params: { sessionId: props.sessionId } });
  };
  </script>
  
  <style scoped>
  .subtitle {
    color: #868e96;
    margin-bottom: 0.5rem;
  }
  
  .info-row {
    display: flex;
    gap: 2rem;
    color: #868e96;
    margin-bottom: 1.5rem;
  }
  
  .preview-container {
    margin: 1.5rem 0;
  }
  
  .tree-view {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 1rem;
    max-height: 500px;
    overflow-y: auto;
    background-color: #f8f9fa;
  }
  
  .tree-node {
    margin-bottom: 0.5rem;
  }
  
  .folder {
    margin-bottom: 0.5rem;
  }
  
  .folder-icon, .file-icon {
    display: inline-block;
    width: 16px;
    height: 16px;
    margin-right: 0.5rem;
    background-size: contain;
    background-repeat: no-repeat;
  }
  
  .folder-icon {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%234c6ef5' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
  }
  
  .file-icon {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23868e96' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
  }
  
  .folder-name {
    font-weight: 500;
    color: #4c6ef5;
  }
  
  .file-name {
    color: #495057;
  }
  
  .action {
    margin-left: 0.5rem;
    color: #fa5252;
    font-size: 0.85rem;
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