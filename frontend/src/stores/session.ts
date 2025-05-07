import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Session, AnalysisMethod, StructAlgorithm, PreviewTree } from '../types'
import api from '../services/api'

export const useSessionStore = defineStore('session', () => {
  const currentSession = ref<Session | null>(null)
  const previewData = ref<PreviewTree | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  async function createNewSession(directory: string, recursive: boolean = true) {
    loading.value = true
    error.value = null
    
    try {
      const session = await api.createSession(directory, recursive)
      currentSession.value = {
        id: session.id,
        directory: session.directory,
        recursive: session.recursive,
        status: session.status,
        filesTotal: session.files_total,
        actionsTotal: session.actions_total,
        analysisMethod: session.analysis_method || undefined,
        structAlgorithm: session.struct_algorithm || undefined
      }
      return session.id
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create session'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function loadSession(sessionId: string) {
    loading.value = true
    error.value = null
    
    try {
      const session = await api.getSession(sessionId)
      currentSession.value = {
        id: session.id,
        directory: session.directory,
        recursive: session.recursive,
        status: session.status,
        filesTotal: session.files_total,
        actionsTotal: session.actions_total,
        analysisMethod: session.analysis_method || undefined,
        structAlgorithm: session.struct_algorithm || undefined
      }
      return currentSession.value
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load session'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function runAnalysis(method: AnalysisMethod) {
    if (!currentSession.value?.id) {
      error.value = 'No active session'
      throw error.value
    }
    
    loading.value = true
    error.value = null
    
    try {
      const result = await api.runAnalysis(currentSession.value.id, method)
      currentSession.value.analysisMethod = method
      return result
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Analysis failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function generatePlan(algorithm: StructAlgorithm) {
    if (!currentSession.value?.id) {
      error.value = 'No active session'
      throw error.value
    }
    
    loading.value = true
    error.value = null
    
    try {
      const result = await api.generatePlan(currentSession.value.id, algorithm)
      currentSession.value.structAlgorithm = algorithm
      return result
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Plan generation failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function getPreview() {
    if (!currentSession.value?.id) {
      error.value = 'No active session'
      throw error.value
    }
    
    loading.value = true
    error.value = null
    
    try {
      const result = await api.getPreview(currentSession.value.id)
      previewData.value = result
      return result
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to retrieve preview'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function applyPlan(dryRun: boolean = false) {
    if (!currentSession.value?.id) {
      error.value = 'No active session'
      throw error.value
    }
    
    loading.value = true
    error.value = null
    
    try {
      return await api.applyPlan(currentSession.value.id, dryRun)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to apply plan'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function getProgress() {
    if (!currentSession.value?.id) {
      error.value = 'No active session'
      throw error.value
    }
    
    try {
      return await api.getProgress(currentSession.value.id)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to get progress'
      throw error.value
    }
  }

  function reset() {
    currentSession.value = null
    previewData.value = null
    error.value = null
  }

  return {
    currentSession,
    previewData,
    loading,
    error,
    createNewSession,
    loadSession,
    runAnalysis,
    generatePlan,
    getPreview,
    applyPlan,
    getProgress,
    reset
  }
})