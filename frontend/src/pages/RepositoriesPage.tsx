import { useMemo, useState } from 'react';
import { useReviewLogs } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { GitBranch, Search, ExternalLink, Star, GitFork, FileSearch, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface RepoSummary {
  name: string;
  total_reviews: number;
  success_count: number;
  failed_count: number;
  pending_count: number;
  total_findings: number;
  last_review: string;
}

export default function RepositoriesPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const { data, loading } = useReviewLogs({ per_page: 100 });

  const repos = useMemo(() => {
    if (!data?.data) return [];
    const map = new Map<string, RepoSummary>();
    data.data.forEach((log) => {
      const existing = map.get(log.repo_full_name);
      if (existing) {
        existing.total_reviews++;
        if (log.status === 'SUCCESS') existing.success_count++;
        else if (log.status === 'FAILED') existing.failed_count++;
        else existing.pending_count++;
        existing.total_findings += log.findings_count;
        if (new Date(log.created_at) > new Date(existing.last_review)) {
          existing.last_review = log.created_at;
        }
      } else {
        map.set(log.repo_full_name, {
          name: log.repo_full_name,
          total_reviews: 1,
          success_count: log.status === 'SUCCESS' ? 1 : 0,
          failed_count: log.status === 'FAILED' ? 1 : 0,
          pending_count: log.status === 'PENDING' ? 1 : 0,
          total_findings: log.findings_count,
          last_review: log.created_at,
        });
      }
    });
    return Array.from(map.values()).sort((a, b) => b.total_reviews - a.total_reviews);
  }, [data]);

  const filteredRepos = repos.filter((r) =>
    r.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Repositories</h1>
        <p className="text-muted-foreground">All connected repositories and their review metrics.</p>
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search repositories..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-[180px]" />
          ))}
        </div>
      ) : filteredRepos.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <GitBranch className="h-10 w-10 text-muted-foreground/50 mb-3" />
          <p className="text-sm font-medium text-muted-foreground">No repositories found</p>
          <p className="text-xs text-muted-foreground mt-1">Connect your GitHub App to start tracking repositories.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredRepos.map((repo) => (
            <Card key={repo.name} className="group cursor-pointer hover:border-primary/30 transition-all">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                      <GitBranch className="h-4 w-4 text-primary" />
                    </div>
                    <div className="min-w-0">
                      <CardTitle className="text-sm font-semibold truncate">{repo.name}</CardTitle>
                      <p className="text-xs text-muted-foreground">{repo.total_reviews} reviews</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/logs?repo=${encodeURIComponent(repo.name)}`);
                    }}
                  >
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex gap-2">
                  <Badge variant="success" className="text-[10px]">{repo.success_count} success</Badge>
                  {repo.failed_count > 0 && (
                    <Badge variant="destructive" className="text-[10px]">{repo.failed_count} failed</Badge>
                  )}
                  {repo.pending_count > 0 && (
                    <Badge variant="warning" className="text-[10px]">{repo.pending_count} pending</Badge>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-1.5 text-muted-foreground">
                    <FileSearch className="h-3 w-3" />
                    {repo.total_findings} findings
                  </div>
                  <div className="flex items-center gap-1.5 text-muted-foreground">
                    <Star className="h-3 w-3" />
                    {((repo.success_count / repo.total_reviews) * 100).toFixed(0)}% success
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
