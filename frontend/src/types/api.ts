// ==========================================
// ENUMS (Berdasarkan review_models.py)
// ==========================================
export enum Severity {
  INFO = "info",
  WARNING = "warning",
  CRITICAL = "critical",
  BLOCKER = "blocker"
}

export enum Category {
  LOGIC_BUG = "Logic Bug",
  SECURITY = "Security",
  ERROR_HANDLING = "Error Handling",
  TYPE_SAFETY = "Type Safety",
  RESOURCE_LEAK = "Resource Leak",
  CONCURRENCY = "Concurrency",
  API_CONTRACT = "API Contract",
  PERFORMANCE = "Performance",
  DATA_INTEGRITY = "Data Integrity",
  CONFIGURATION = "Configuration"
}

// ==========================================
// DATA MODELS
// ==========================================
export interface Finding {
  severity: Severity;
  line: number | null;
  category: Category;
  message: string;
  explanation: string;
}

export interface AIMetadata {
  summary: string;
  findings: Finding[];
}

export interface ReviewLog {
  id: number;
  tenant_id: number;
  repo_full_name: string;
  pr_number: number;
  status: "PENDING" | "SUCCESS" | "FAILED";
  findings_count: number;
  ai_metadata: AIMetadata | null;
  created_at: string; // ISO Date String
}

export interface ReviewLogListResponse {
  total: number;
  page: number;
  per_page: number;
  data: ReviewLog[];
}

export interface ReviewStats {
  total_reviews: number;
  successful_reviews: number;
  failed_reviews: number;
  success_rate_percent: number;
  total_bugs_detected: number;
}

export interface HealthStatus {
  status: string;
  database: string;
  redis: string;
}

// ==========================================
// API QUERY PARAMS
// ==========================================
export interface GetLogsParams {
  page?: number;
  per_page?: number;
  repo_full_name?: string;
  status?: "SUCCESS" | "FAILED" | "PENDING";
}

export interface GetStatsParams {
  repo_full_name?: string;
}
