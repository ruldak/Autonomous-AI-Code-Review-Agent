import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useReviewLogs, useReviewStats } from '@/hooks/useApi';
import { StatCard } from '@/components/StatCard';
import { ReviewCharts } from '@/components/ReviewCharts';
import { ReviewDetail } from '@/components/ReviewDetail';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  FileSearch,
  CheckCircle2,
  XCircle,
  Bug,
  TrendingUp,
  GitPullRequest,
  ArrowRight,
  Activity,
  Shield,
  Clock,
} from 'lucide-react';
import { format } from 'date-fns';
import type { ReviewLog } from '@/types/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: stats, loading: statsLoading } = useReviewStats();
  const { data: logsData, loading: logsLoading } = useReviewLogs({ page: 1, per_page: 5 });
  const [selectedLog, setSelectedLog] = useState<ReviewLog | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);

  const recentLogs = logsData?.data || [];

  const handleRowClick = (log: ReviewLog) => {
    setSelectedLog(log);
    setDetailOpen(true);
  };

  const statusBadge = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <Badge variant="success" className="text-[10px]">Success</Badge>;
      case 'FAILED':
        return <Badge variant="destructive" className="text-[10px]">Failed</Badge>;
      default:
        return <Badge variant="warning" className="text-[10px]">Pending</Badge>;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Overview of your AI code review activity and system health.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statsLoading ? (
          <>
            <Skeleton className="h-[120px]" />
            <Skeleton className="h-[120px]" />
            <Skeleton className="h-[120px]" />
            <Skeleton className="h-[120px]" />
          </>
        ) : stats ? (
          <>
            <StatCard
              title="Total Reviews"
              value={stats.total_reviews}
              icon={FileSearch}
              trend="up"
              trendValue="12%"
              description="All-time code reviews"
            />
            <StatCard
              title="Success Rate"
              value={`${stats.success_rate_percent.toFixed(1)}%`}
              icon={CheckCircle2}
              trend="up"
              trendValue="2.3%"
              description={`${stats.successful_reviews} successful`}
            />
            <StatCard
              title="Bugs Detected"
              value={stats.total_bugs_detected}
              icon={Bug}
              trend="up"
              trendValue="8"
              description="Total findings across all reviews"
            />
            <StatCard
              title="Failed Reviews"
              value={stats.failed_reviews}
              icon={XCircle}
              trend="down"
              trendValue="1"
              description="Requires attention"
            />
          </>
        ) : null}
      </div>

      {/* Charts */}
      <ReviewCharts logs={recentLogs} loading={logsLoading} />

      {/* Recent Reviews Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle className="text-base font-semibold">Recent Reviews</CardTitle>
            <p className="text-sm text-muted-foreground">Latest code review results</p>
          </div>
          <Button variant="ghost" size="sm" onClick={() => navigate('/logs')} className="gap-1">
            View All <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </CardHeader>
        <CardContent>
          {logsLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
            </div>
          ) : recentLogs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileSearch className="h-10 w-10 text-muted-foreground/50 mb-3" />
              <p className="text-sm font-medium text-muted-foreground">No reviews yet</p>
              <p className="text-xs text-muted-foreground mt-1">Reviews will appear here once your GitHub webhook is configured.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Repository</TableHead>
                    <TableHead>PR</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Findings</TableHead>
                    <TableHead>Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentLogs.map((log) => (
                    <TableRow
                      key={log.id}
                      className="cursor-pointer hover:bg-muted/60"
                      onClick={() => handleRowClick(log)}
                    >
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          <GitPullRequest className="h-3.5 w-3.5 text-muted-foreground" />
                          <span className="truncate max-w-[180px]">{log.repo_full_name}</span>
                        </div>
                      </TableCell>
                      <TableCell>#{log.pr_number}</TableCell>
                      <TableCell>{statusBadge(log.status)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1.5">
                          <Shield className="h-3.5 w-3.5 text-muted-foreground" />
                          {log.findings_count}
                        </div>
                      </TableCell>
                      <TableCell className="text-muted-foreground text-xs">
                        <div className="flex items-center gap-1.5">
                          <Clock className="h-3 w-3" />
                          {format(new Date(log.created_at), 'MMM d, HH:mm')}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <ReviewDetail log={selectedLog} open={detailOpen} onOpenChange={setDetailOpen} />
    </div>
  );
}
