import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import type { ReviewLogListResponse, ReviewStats, HealthStatus, GetLogsParams } from '@/types/api';

export function useReviewLogs(params: GetLogsParams = {}) {
  const [data, setData] = useState<ReviewLogListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getLogs(params);
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch logs');
    } finally {
      setLoading(false);
    }
  }, [params.page, params.per_page, params.repo_full_name, params.status]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  return { data, loading, error, refetch: fetchLogs };
}

export function useReviewStats(repo_full_name?: string) {
  const [data, setData] = useState<ReviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    api.getStats(repo_full_name)
      .then((res) => { if (mounted) setData(res); })
      .catch((err) => { if (mounted) setError(err.message); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [repo_full_name]);

  return { data, loading, error };
}

export function useHealth() {
  const [data, setData] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getHealth()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading };
}
