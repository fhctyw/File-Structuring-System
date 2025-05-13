<script setup lang="ts">
import { computed } from 'vue'
import { type FileEntry } from '../services/api'
import TreeNode from './TreeNode.vue' // Імпортуємо компонент з окремого файлу

const props = defineProps<{
  before: FileEntry[]
  after: FileEntry[]
}>()

// Helper function to build a tree structure from flat entries
const buildTree = (entries: FileEntry[] = []) => {
  // Перевірка, що entries існує і є масивом
  if (!entries || !Array.isArray(entries)) {
    console.warn('Invalid entries provided to buildTree:', entries)
    return {
      name: 'Корінь',
      path: '',
      type: 'directory',
      children: []
    }
  }
  
  const root: any = {
    name: 'Корінь',
    path: '',
    type: 'directory',
    children: []
  }
  
  const nodesMap = new Map()
  nodesMap.set('', root)
  
  // First create all nodes
  for (const entry of entries) {
    const node = {
      ...entry,
      children: entry.type === 'directory' ? [] : undefined
    }
    nodesMap.set(entry.path, node)
  }
  
  // Then connect them in the tree
  for (const entry of entries) {
    if (entry.path === '') continue // Skip root
    
    const node = nodesMap.get(entry.path)
    
    // Обробка шляху незалежно від слешів (Windows або Unix)
    const pathSeparator = entry.path.includes('\\') ? '\\' : '/'
    const pathParts = entry.path.split(pathSeparator)
    pathParts.pop() // Remove entry name to get parent path
    const parentPath = pathParts.join(pathSeparator)
    
    const parent = nodesMap.get(parentPath) || root
    if (parent.children) {
      parent.children.push(node)
    }
  }
  
  return root
}

const beforeTree = computed(() => buildTree(props.before))
const afterTree = computed(() => buildTree(props.after))

// Додамо логування для діагностики
console.log('Before tree:', beforeTree.value)
console.log('After tree:', afterTree.value)
console.log('Raw before data:', props.before)
console.log('Raw after data:', props.after)
</script>

<template>
  <div class="preview-tree">
    <div class="tree-container">
      <h3 class="tree-title">До</h3>
      <div v-if="props.before && props.before.length > 0" class="tree-view">
        <TreeNode :node="beforeTree" :depth="0" />
      </div>
      <div v-else class="empty-tree">
        Дані відсутні
      </div>
    </div>
    
    <div class="tree-separator">
      <div class="separator-line"></div>
      <div class="separator-icon">→</div>
      <div class="separator-line"></div>
    </div>
    
    <div class="tree-container">
      <h3 class="tree-title">Після</h3>
      <div v-if="props.after && props.after.length > 0" class="tree-view">
        <TreeNode :node="afterTree" :depth="0" />
      </div>
      <div v-else class="empty-tree">
        Дані відсутні
      </div>
    </div>
  </div>
</template>

<style scoped>
.preview-tree {
  display: flex;
  width: 100%;
  overflow: hidden;
}

.tree-container {
  flex: 1;
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  overflow: auto;
  max-height: 600px;
}

.tree-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: var(--space-4);
  text-align: center;
  color: var(--color-text);
}

.tree-view {
  font-size: 0.875rem;
}

.empty-tree {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-light);
  font-style: italic;
}

.tree-separator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 80px;
  padding: 0 var(--space-4);
}

.separator-line {
  flex: 1;
  width: 2px;
  background-color: #e2e8f0;
}

.separator-icon {
  font-size: 1.5rem;
  color: var(--color-primary);
  margin: var(--space-4) 0;
}

/* CSS для дочірніх компонентів - тепер з зовнішнім селектором */
:deep(.tree-node) {
  margin-bottom: var(--space-2);
}

:deep(.node-content) {
  display: flex;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  transition: background-color 0.2s ease;
}

:deep(.node-content:hover) {
  background-color: rgba(0, 0, 0, 0.05);
}

:deep(.node-icon) {
  margin-right: var(--space-2);
}

:deep(.node-name) {
  font-weight: 500;
}

:deep(.node-children) {
  margin-top: var(--space-2);
}
</style>