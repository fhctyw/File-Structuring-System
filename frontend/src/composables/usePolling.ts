import { ref, onUnmounted } from 'vue'

export function usePolling<T>(
  fetchFn: () => Promise<T>,
  options: {
    interval: number,
    stopCondition?: (data: T) => boolean,
    onComplete?: () => void,
    maxAttempts?: number,
    logProgress?: boolean
  }
) {
  const intervalId = ref<number | null>(null)
  const isPolling = ref(false)
  const lastData = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const attemptCount = ref(0)
  const maxAttempts = options.maxAttempts || Infinity
  const logProgress = options.logProgress !== undefined ? options.logProgress : true

  // Поліпшена функція, що визначає, чи треба зупинити опитування
  const shouldStop = (data: any): boolean => {
    if (!data) return false
    
    // Якщо користувач вказав власну умову зупинки, використовуємо її
    if (options.stopCondition && options.stopCondition(data)) {
      return true
    }
    
    // Стандартна перевірка на відсоток завершення (підтримує 'percent' і 'percentage')
    const percentValue = data.percent !== undefined ? data.percent : 
                         (data.percentage !== undefined ? data.percentage : 0)
    
    // Стандартна перевірка на статус (перевіряємо 'DONE', 'done', 'Completed', 'completed')
    const status = (data.status || '').toLowerCase()
    const isCompletedStatus = ['done', 'completed', 'finished', 'success'].includes(status)
    
    // Зупиняємо опитування, якщо відсоток >= 100 або статус вказує на завершення
    return percentValue >= 100 || isCompletedStatus
  }

  const start = async () => {
    if (isPolling.value) return

    isPolling.value = true
    error.value = null
    attemptCount.value = 0
    
    try {
      // Початкове отримання даних
      const initialData = await fetchFn()
      lastData.value = initialData
      
      if (logProgress) {
        console.log('Initial polling data:', initialData)
      }
      
      // Перевіряємо, чи потрібно відразу зупинитися
      if (shouldStop(initialData)) {
        if (logProgress) {
          console.log('Polling stopping immediately - condition met:', initialData)
        }
        stop()
        options.onComplete?.()
        return
      }

      // Встановлюємо регулярне опитування
      intervalId.value = window.setInterval(async () => {
        attemptCount.value++
        
        // Перевіряємо, чи не перевищено максимальну кількість спроб
        if (attemptCount.value > maxAttempts) {
          console.warn(`Polling stopped: reached max attempts (${maxAttempts})`)
          stop()
          return
        }
        
        try {
          const data = await fetchFn()
          lastData.value = data
          
          if (logProgress) {
            console.log(`Polling attempt ${attemptCount.value}:`, data)
          }
          
          if (shouldStop(data)) {
            if (logProgress) {
              console.log('Polling stopping - condition met:', data)
            }
            stop()
            options.onComplete?.()
          }
        } catch (err) {
          const errorObj = err instanceof Error ? err : new Error(String(err))
          console.error('Polling error:', errorObj)
          error.value = errorObj
        }
      }, options.interval)
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error(String(err))
      console.error('Initial polling fetch error:', errorObj)
      error.value = errorObj
      isPolling.value = false
    }
  }

  const stop = () => {
    if (intervalId.value) {
      clearInterval(intervalId.value)
      intervalId.value = null
    }
    isPolling.value = false
  }

  // Обов'язково зупиняємо опитування, коли компонент розмонтовується
  onUnmounted(() => {
    stop()
  })

  return {
    start,
    stop,
    isPolling,
    lastData,
    error,
    attemptCount
  }
}