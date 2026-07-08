import type { ReviewLogListResponse, ReviewStats, HealthStatus, GetLogsParams } from '@/types/api';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

async function fetchWithError<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  getLogs: (params: GetLogsParams = {}): Promise<ReviewLogListResponse> => {
    const query = new URLSearchParams();
    if (params.page) query.set('page', String(params.page));
    if (params.per_page) query.set('per_page', String(params.per_page));
    if (params.repo_full_name) query.set('repo_full_name', params.repo_full_name);
    if (params.status) query.set('status', params.status);
    return fetchWithError(`${BASE_URL}/reviews/logs?${query.toString()}`);
  },

  getStats: (repo_full_name?: string): Promise<ReviewStats> => {
    const query = repo_full_name ? `?repo_full_name=${encodeURIComponent(repo_full_name)}` : '';
    return fetchWithError(`${BASE_URL}/reviews/stats${query}`);
  },

  getHealth: (): Promise<HealthStatus> => {
    return fetchWithError(`${BASE_URL}/health`);
  },
};
