<template>
    <div class="tree-item" :class="{ 'is-folder': isFolder }">
      <div 
        class="item-content" 
        @click="handleClick"
        :class="{ 'is-folder': isFolder }"
      >
        <div class="column column-name">
          <span :class="['icon', isFolder ? 'folder-icon' : 'file-icon']"></span>
          <span class="name">{{ entry.name }}</span>
        </div>
        <div class="column column-type">{{ isFolder ? 'Папка' : getFileType(entry.name) }}</div>
        <div class="column column-size">{{ isFolder ? '' : formatSize(entry.size || 0) }}</div>
        <div class="column column-modified">{{ formatDate(entry.modified) }}</div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { computed } from 'vue';
  import type { PropType } from 'vue';
  import type { FileSystemEntry } from '@/types';
  
  const props = defineProps({
    entry: {
      type: Object as PropType<FileSystemEntry>,
      required: true
    },
    currentPath: {
      type: String,
      required: true
    }
  });
  
  const emit = defineEmits(['folder-click']);
  
  const isFolder = computed(() => props.entry.type === 'directory');
  
  const handleClick = () => {
    if (isFolder.value) {
      // Construct the full path for the clicked folder
      const path = props.entry.path || `${props.currentPath}\\${props.entry.name}`;
      emit('folder-click', path);
    }
  };
  
  const getFileType = (fileName: string): string => {
    const extension = fileName.split('.').pop()?.toLowerCase() || '';
    
    const typeMap: Record<string, string> = {
      'txt': 'Текстовий документ',
      'pdf': 'PDF документ',
      'doc': 'Word документ',
      'docx': 'Word документ',
      'xls': 'Excel документ',
      'xlsx': 'Excel документ',
      'ppt': 'PowerPoint документ',
      'pptx': 'PowerPoint документ',
      'jpg': 'Зображення',
      'jpeg': 'Зображення',
      'png': 'Зображення',
      'gif': 'Зображення',
      'mp3': 'Аудіо',
      'wav': 'Аудіо',
      'mp4': 'Відео',
      'avi': 'Відео',
      'mov': 'Відео',
      'zip': 'Архів',
      'rar': 'Архів',
      'exe': 'Програма',
      'js': 'JavaScript файл',
      'ts': 'TypeScript файл',
      'py': 'Python файл',
      'html': 'HTML файл',
      'css': 'CSS файл'
    };
    
    return typeMap[extension] || `Файл ${extension ? '.' + extension : ''}`;
  };
  
  const formatSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
  };
  
  const formatDate = (dateString?: string): string => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleString('uk-UA', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  };
  </script>
  
  <style scoped>
  .tree-item {
    margin-bottom: 0.25rem;
  }
  
  .item-content {
    display: flex;
    padding: 0.5rem;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .item-content:hover {
    background-color: #f1f3f9;
  }
  
  .item-content.is-folder:hover {
    background-color: #e7f1ff;
  }
  
  .column {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .column-name {
    display: flex;
    align-items: center;
    flex: 3;
  }
  
  .column-type {
    flex: 1;
  }
  
  .column-size {
    flex: 1;
    text-align: right;
  }
  
  .column-modified {
    flex: 2;
    text-align: right;
  }
  
  .icon {
    display: inline-block;
    width: 20px;
    height: 20px;
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
  
  .name {
    overflow: hidden;
    text-overflow: ellipsis;
  }
  </style>