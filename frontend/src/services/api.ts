import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface FileEntry {
  name: string
  path: string
  type: 'file' | 'directory'
  size?: number
  extension?: string | null
  mime_type?: string
  file_type?: string
}

export interface DirectoryResponse {
  directory: string
  parent_directory: string | null
  entries: FileEntry[]
  has_access: boolean
}

export interface DirectoryEntriesResponse {
  directory: string
  entries: {
    directory: string
    parent_directory: string | null
    entries: FileEntry[]
    has_access: boolean
  }
}

export interface Session {
  id: string
  directory: string
  status: 'created' | 'analyzing' | 'processing' | 'completed' | 'failed'
  created_at: string
}

export interface AnalysisMethod {
  id: string
  layer: string
  domain: string
  action: string
  description: string
  returns: Array<{ name: string, type: string, unit: string }>
  impl_class: string
  enabled: boolean
}

export interface StructAlgorithm {
  id: string
  description: string
  params_schema: {
    type: string
    properties: Record<string, any>
    required?: string[]
    additionalProperties?: boolean
  }
  scope: string
  impl_class: string
  enabled: boolean
}

export interface FileSystemApi {
  getEntries: (directory?: string) => Promise<DirectoryEntriesResponse>
}

export interface PreviewResponse {
  tree: {
    [key: string]: any;
  };
}

export interface SessionsApi {
  createSession: (directory: string) => Promise<Session>
  getSession: (id: string) => Promise<Session>
  processSession: (id: string, data: {
    method: string,
    algorithm: string
  }) => Promise<void>
  getPreview: (id: string) => Promise<PreviewResponse>
  applyChanges: (id: string, dryRun?: boolean) => Promise<void>
  getProgress: (id: string) => Promise<{
    percentage: number,
    status: string,
    message?: string
  }>
}

export interface MethodsApi {
  getAnalysisMethods: () => Promise<Record<string, AnalysisMethod[]>>
}

export interface AlgorithmsApi {
  getStructAlgorithms: () => Promise<StructAlgorithm[]>
}

export const fileSystemApi: FileSystemApi = {
  getEntries: async (directory = 'C:\\') => {
    const response = await api.get('/fs/entries', {
      params: { dir: directory }
    })
    return response.data
  }
}

export const sessionsApi: SessionsApi = {
  createSession: async (directory) => {
    const response = await api.post('/sessions/', { directory })
    return response.data
  },
  
  getSession: async (id) => {
    const response = await api.get(`/sessions/${id}`)
    return response.data
  },
  
  processSession: async (id, data) => {
    // Передаємо тільки method і algorithm, без params
    const response = await api.post(`/sessions/${id}/process`, {
      method: data.method,
      algorithm: data.algorithm
    })
    return response.data
  },
  
  getPreview: async (id) => {
    const response = await api.get(`/sessions/${id}/preview`)
    return response.data
  },
  
  applyChanges: async (id, dryRun = false) => {
    const response = await api.post(`/sessions/${id}/apply`, { dry_run: dryRun })
    return response.data
  },
  
  getProgress: async (id) => {
    const response = await api.get(`/sessions/${id}/progress`)
    return response.data
  }
}

export const methodsApi: MethodsApi = {
  getAnalysisMethods: async () => {
    const response = await api.get('/analysis-methods')
    return response.data
  }
}

export const algorithmsApi: AlgorithmsApi = {
  getStructAlgorithms: async () => {
    const response = await api.get('/struct-algorithms')
    return response.data
  }
}

export default {
  fileSystem: fileSystemApi,
  sessions: sessionsApi,
  methods: methodsApi,
  algorithms: algorithmsApi
}