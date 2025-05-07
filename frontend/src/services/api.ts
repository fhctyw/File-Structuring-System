// src/services/api.ts
import axios from 'axios';
import type { 
  AnalysisMethod, 
  StructAlgorithm, 
  Session, 
  FileSystemEntry, 
  AnalysisSummary, 
  PlanSummary,
  PreviewTree,
  ApplyResult,
  ProgressReport
} from '@/types';

const api = axios.create({
  baseURL: '/api',
  // Add a timeout so we don't wait forever
  timeout: 10000
});

// Add request interceptor for debugging
api.interceptors.request.use(
  config => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data);
    return config;
  },
  error => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
api.interceptors.response.use(
  response => {
    console.log(`API Response: ${response.status}`, response.data);
    return response;
  },
  error => {
    console.error('API Response Error:', error);
    return Promise.reject(error);
  }
);

export default {
  // Get available analysis methods
  getAnalysisMethods() {
    return api.get<Array<{id: string, name: string, description: string}>>('/analysis-methods');
  },

  // Get available structuring algorithms
  getStructAlgorithms() {
    return api.get<Array<{id: string, name: string, description: string}>>('/struct-algorithms');
  },

  // Get file system entries for a directory
  getFileSystemEntries(directory: string) {
    // Make sure to encode the directory path properly for URL
    return api.get<{directory: string, entries: FileSystemEntry[]}>('/fs/entries', {
      params: { dir: directory }
    });
  },

  // Create a new session
  createSession(directory: string, recursive: boolean = true) {
    return api.post<Session>('/sessions/', { directory, recursive });
  },

  // List all sessions
  listSessions(skip: number = 0, limit: number = 50) {
    return api.get<Session[]>('/sessions/', {
      params: { skip, limit }
    });
  },

  // Get a specific session
  getSession(sessionId: string) {
    return api.get<Session>(`/sessions/${sessionId}`);
  },

  // Run analysis on files
  runAnalysis(sessionId: string, method: AnalysisMethod) {
    return api.post<AnalysisSummary>(`/sessions/${sessionId}/analyze`, { method });
  },

  // Generate a structuring plan
  generatePlan(sessionId: string, algorithm: StructAlgorithm) {
    return api.post<PlanSummary>(`/sessions/${sessionId}/plan`, { algorithm });
  },

  // Get preview of the resulting structure
  getPreview(sessionId: string) {
    return api.get<PreviewTree>(`/sessions/${sessionId}/preview`);
  },

  // Apply the plan
  applyPlan(sessionId: string, dryRun: boolean = false) {
    return api.post<ApplyResult>(`/sessions/${sessionId}/apply`, { dry_run: dryRun });
  },

  // Get progress of the operation
  getProgress(sessionId: string) {
    return api.get<ProgressReport>(`/sessions/${sessionId}/progress`);
  }
};