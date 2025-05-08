import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fileSystemApi, type FileEntry, sessionsApi } from '../services/api'

export const useFsStore = defineStore('fs', () => {
  const entries = ref<FileEntry[]>([])
  const currentDirectory = ref<string>('C:\\')
  const loading = ref(false)
  const error = ref<string | null>(null)
  const previewBefore = ref<FileEntry[]>([])
  const previewAfter = ref<FileEntry[]>([])
  
  const breadcrumbs = computed(() => {
    if (!currentDirectory.value) return [{ name: 'Root', path: 'C:\\' }]
    
    const parts = currentDirectory.value.split('\\')
    const result = [{ name: 'Root', path: 'C:\\' }]
    
    let currentPath = parts[0] + '\\'
    for (let i = 1; i < parts.length; i++) {
      const part = parts[i]
      if (!part) continue
      currentPath += part + '\\'
      result.push({
        name: part,
        path: currentPath
      })
    }
    
    return result
  })
  
  const fetchEntries = async (directory = 'C:\\') => {
    loading.value = true
    error.value = null
    try {
      const response = await fileSystemApi.getEntries(directory)
      entries.value = response.entries.entries
      currentDirectory.value = directory
      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch directory entries'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const fetchPreview = async (sessionId: string) => {
    loading.value = true
    error.value = null
    try {
      console.log('Fetching preview for session:', sessionId)
      const response = await sessionsApi.getPreview(sessionId)
      console.log('Preview response:', response)
      
      if (!response || !response.tree) {
        console.error('No valid tree structure in response')
        previewBefore.value = []
        previewAfter.value = []
        return null
      }
      
      // Трансформація даних з вкладеної структури в плоский список FileEntry
      const beforeEntries: FileEntry[] = []
      const afterEntries: FileEntry[] = []
      
      // Рекурсивна функція для трансформації дерева в плоский список
      const processTree = (obj: any, parentPath: string = '', entries: FileEntry[]) => {
        for (const key in obj) {
          if (typeof obj[key] === 'object') {
            // Це директорія
            const path = parentPath ? `${parentPath}\\${key}` : key
            entries.push({
              name: key,
              path: path,
              type: 'directory'
            })
            
            // Рекурсивно обробляємо вміст директорії
            processTree(obj[key], path, entries)
          } else {
            // Це файл або інформація про переміщення
            const path = parentPath ? `${parentPath}\\${key}` : key
            entries.push({
              name: key,
              path: path,
              type: 'file'
            })
            
            // Якщо є інформація про переміщення, додаємо цей файл в afterEntries
            if (typeof obj[key] === 'string' && obj[key].startsWith('MOVE->')) {
              const newPath = obj[key].replace('MOVE->', '')
              afterEntries.push({
                name: key,
                path: newPath + key,
                type: 'file'
              })
            }
          }
        }
      }
      
      // Отримуємо поточну структуру (before)
      const rootDirectory = Object.keys(response.tree).length > 0 ? '' : 'C:\\'
      processTree(response.tree, rootDirectory, beforeEntries)
      
      // Якщо afterEntries порожній, генеруємо його на основі інформації про переміщення
      if (afterEntries.length === 0) {
        // Створюємо структуру директорій для afterEntries на основі шляхів переміщення
        const directorySet = new Set<string>()
        
        // Пройдемося по всім beforeEntries і подивимося на інформацію про переміщення
        for (const entry of beforeEntries) {
          if (entry.type === 'file') {
            // Шукаємо інформацію про переміщення в response.tree
            // Це спрощена логіка, можливо потрібно буде адаптувати під вашу точну структуру даних
            const movePath = findMovePath(response.tree, entry.name)
            if (movePath) {
              // Додаємо всі батьківські директорії в Set
              const pathParts = movePath.split('\\')
              let currentPath = ''
              for (let i = 0; i < pathParts.length - 1; i++) {
                if (pathParts[i]) {
                  currentPath += (currentPath ? '\\' : '') + pathParts[i]
                  directorySet.add(currentPath)
                }
              }
              
              // Додаємо сам файл у afterEntries
              afterEntries.push({
                name: entry.name,
                path: movePath,
                type: 'file'
              })
            } else {
              // Якщо немає інформації про переміщення, залишаємо файл на місці
              afterEntries.push({ ...entry })
            }
          }
        }
        
        // Додаємо всі директорії в afterEntries
        for (const dirPath of directorySet) {
          const dirName = dirPath.split('\\').pop() || ''
          afterEntries.push({
            name: dirName,
            path: dirPath,
            type: 'directory'
          })
        }
      }
      
      // Функція для пошуку шляху переміщення для файлу
      function findMovePath(tree: any, fileName: string): string | null {
        for (const key in tree) {
          if (typeof tree[key] === 'object') {
            // Якщо це директорія, шукаємо рекурсивно
            const result = findMovePath(tree[key], fileName)
            if (result) return result
          } else if (key === fileName && typeof tree[key] === 'string' && tree[key].startsWith('MOVE->')) {
            // Знайшли інформацію про переміщення
            return tree[key].replace('MOVE->', '')
          }
        }
        return null
      }
      
      previewBefore.value = afterEntries
      previewAfter.value = beforeEntries
      
      console.log('Transformed preview data:', {
        before: previewBefore.value,
        after: previewAfter.value
      })
      
      return response
    } catch (err: any) {
      console.error('Preview fetch error:', err)
      error.value = err.message || 'Failed to fetch preview'
      previewBefore.value = []
      previewAfter.value = []
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    entries,
    currentDirectory,
    loading,
    error,
    breadcrumbs,
    previewBefore,
    previewAfter,
    fetchEntries,
    fetchPreview
  }
})