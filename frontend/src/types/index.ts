export type AnalysisMethod = "META" | "STRUCT" | "SEMANTIC";
export type StructAlgorithm = "BY_TYPE" | "CLUSTER" | "CRITERIA";

export interface Session {
  id: string;
  directory: string;
  status: string;
  created_at: string;
  recursive?: boolean;
  files_total?: number;
  analysis_method?: AnalysisMethod;
  struct_algorithm?: StructAlgorithm;
  actions_total?: number;
}

export interface FileSystemEntry {
  name: string;
  type: 'file' | 'directory';
  path: string;
  size?: number;
  modified?: string;
}

export interface AnalysisSummary {
  files_analyzed: number;
  description_examples: string[];
}

export interface PlanSummary {
  actions_created: number;
  breakdown: Record<string, number>;
}

export interface PreviewTree {
  tree: Record<string, any>;
}

export interface ApplyResult {
  applied: number;
  failed: number;
  errors: string[];
}

export interface ProgressReport {
  percent: number;
  status: string;
}