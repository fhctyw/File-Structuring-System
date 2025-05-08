import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sessionsApi, type Session } from '../services/api'

export const useSessionStore = defineStore('session', () => {
  const session = ref<Session | null>(null)
  const sessionId = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const progress = ref<{ percentage: number, status: string, message?: string } | null>(null)
  
  const hasSession = computed(() => !!sessionId.value)
  
  const createSession = async (directory: string) => {
    loading.value = true
    error.value = null
    try {
      const newSession = await sessionsApi.createSession(directory)
      session.value = newSession
      sessionId.value = newSession.id
      return newSession
    } catch (err: any) {
      error.value = err.message || 'Failed to create session'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const getSession = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const existingSession = await sessionsApi.getSession(id)
      session.value = existingSession
      sessionId.value = id
      return existingSession
    } catch (err: any) {
      error.value = err.message || 'Failed to get session'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const processSession = async (method: string, algorithm: string) => {
    if (!sessionId.value) {
      error.value = 'No active session'
      throw new Error('No active session')
    }
    
    loading.value = true
    error.value = null
    try {
      console.log('Processing session with:', { method, algorithm });
      
      // Передаємо тільки method і algorithm, без params
      await sessionsApi.processSession(sessionId.value, { 
        method, 
        algorithm 
        // params - не передаємо, оскільки серверна модель його не очікує
      });
    } catch (err: any) {
      console.error('Process session error:', err);
      error.value = err.message || 'Failed to process session'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const getSessionProgress = async () => {
    if (!sessionId.value) {
      error.value = 'No active session'
      throw new Error('No active session')
    }
    
    try {
      const progressData = await sessionsApi.getProgress(sessionId.value)
      progress.value = progressData
      return progressData
    } catch (err: any) {
      error.value = err.message || 'Failed to get progress'
      throw err
    }
  }
  
  const applyChanges = async (dryRun = false) => {
    if (!sessionId.value) {
      error.value = 'No active session'
      throw new Error('No active session')
    }
    
    loading.value = true
    error.value = null
    try {
      await sessionsApi.applyChanges(sessionId.value, dryRun)
    } catch (err: any) {
      error.value = err.message || 'Failed to apply changes'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const resetSession = () => {
    session.value = null
    sessionId.value = null
    error.value = null
    progress.value = null
  }
  
  return {
    session,
    sessionId,
    loading,
    error,
    progress,
    hasSession,
    createSession,
    getSession,
    processSession,
    getSessionProgress,
    applyChanges,
    resetSession
  }
})