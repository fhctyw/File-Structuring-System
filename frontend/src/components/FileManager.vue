<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useFsStore } from '../stores/useFsStore'
import { type FileEntry } from '../services/api'

const fsStore = useFsStore()
const selectedDirectory = ref<string>('')
const selectedEntry = ref<FileEntry | null>(null)

// Fetch entries when the component is mounted
onMounted(async () => {
  await fsStore.fetchEntries()
})

const navigateToDirectory = async (directory: string) => {
  selectedEntry.value = null
  await fsStore.fetchEntries(directory)
}

const handleEntryClick = (entry: FileEntry) => {
  if (entry.type === 'directory') {
    selectedEntry.value = entry
    selectedDirectory.value = entry.path
  }
}

const handleBreadcrumbClick = (path: string) => {
  navigateToDirectory(path)
}

const emit = defineEmits(['select'])

const selectDirectory = () => {
  if (selectedDirectory.value) {
    emit('select', selectedDirectory.value)
  }
}
</script>

<template>
  <div class="file-manager">
    <div class="breadcrumbs">
      <div 
        v-for="(crumb, index) in fsStore.breadcrumbs" 
        :key="index" 
        class="breadcrumb-item"
        @click="handleBreadcrumbClick(crumb.path)"
      >
        {{ crumb.name }}
        <span v-if="index < fsStore.breadcrumbs.length - 1" class="separator">/</span>
      </div>
    </div>
    
    <div class="directory-path">
      <span>Current directory: </span>
      <span class="path">{{ fsStore.currentDirectory || '/' }}</span>
    </div>
    
    <div v-if="fsStore.loading" class="loading">
      Loading entries...
    </div>
    
    <div v-else-if="fsStore.error" class="error">
      {{ fsStore.error }}
    </div>
    
    <div v-else class="entries">
      <div 
        v-for="entry in fsStore.entries" 
        :key="entry.path"
        class="entry"
        :class="{ 
          'is-directory': entry.type === 'directory',
          'selected': selectedEntry && entry.path === selectedEntry.path
        }"
        @click="handleEntryClick(entry)"
        @dblclick="entry.type === 'directory' && navigateToDirectory(entry.path)"
      >
        <div class="entry-icon">
          <span v-if="entry.type === 'directory'">📁</span>
          <span v-else>📄</span>
        </div>
        <div class="entry-name">{{ entry.name }}</div>
        <div class="entry-info">
          <span v-if="entry.size">{{ (entry.size / 1024).toFixed(1) }} KB</span>
          <span v-if="entry.modified">{{ new Date(entry.modified).toLocaleDateString() }}</span>
        </div>
      </div>
    </div>
    
    <div class="actions">
      <button 
        :disabled="!selectedDirectory"
        @click="selectDirectory"
      >
        Select Directory
      </button>
    </div>
  </div>
</template>

<style scoped>
.file-manager {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.breadcrumbs {
  display: flex;
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-background);
  border-bottom: 1px solid #e2e8f0;
  flex-wrap: wrap;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  color: var(--color-primary);
  font-weight: 500;
  cursor: pointer;
}

.breadcrumb-item:hover {
  text-decoration: underline;
}

.separator {
  margin: 0 var(--space-2);
  color: var(--color-text-light);
}

.directory-path {
  padding: var(--space-3) var(--space-4);
  font-size: 0.875rem;
  color: var(--color-text-light);
  border-bottom: 1px solid #e2e8f0;
}

.path {
  font-weight: 500;
  color: var(--color-text);
}

.loading, .error {
  padding: var(--space-6);
  text-align: center;
  color: var(--color-text-light);
}

.error {
  color: var(--color-error);
}

.entries {
  flex: 1;
  padding: var(--space-4);
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--space-4);
}

.entry {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.entry:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.entry.selected {
  background-color: rgba(37, 99, 235, 0.1);
}

.entry-icon {
  font-size: 2rem;
  margin-bottom: var(--space-2);
}

.entry-name {
  font-size: 0.875rem;
  text-align: center;
  word-break: break-word;
}

.entry-info {
  font-size: 0.75rem;
  color: var(--color-text-light);
  margin-top: var(--space-2);
}

.is-directory .entry-icon {
  color: var(--color-primary);
}

.actions {
  padding: var(--space-4);
  background-color: var(--color-background);
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}
</style>