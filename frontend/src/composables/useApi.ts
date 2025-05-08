import { ref } from 'vue'

export function useApi<T, P extends any[]>(
  apiFn: (...args: P) => Promise<T>
) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const execute = async (...args: P): Promise<T> => {
    loading.value = true
    error.value = null
    
    try {
      const result = await apiFn(...args)
      data.value = result
      return result
    } catch (err) {
      error.value = err as Error
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    error,
    execute
  }
}