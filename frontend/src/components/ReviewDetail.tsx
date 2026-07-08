import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';
import type { ReviewLog, Severity, Category } from '@/types/api';
import { GitPullRequest, Calendar, FileCode, AlertTriangle, Info, XCircle, ShieldAlert } from 'lucide-react';
import { format } from 'date-fns';

interface ReviewDetailProps {
  log: ReviewLog | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function parseFindings(log: ReviewLog): Array<{ severity: string; line: number | null; category: string; message: string; explanation: string }> {
  const meta = log.ai_metadata;
  if (!meta) return [];
  
  if (Array.isArray(meta.findings)) return meta.findings;
  
  if (typeof meta.findings === 'string') {
    const str = meta.findings as string;
    const regex = /Finding\(severity=<Severity\.(\w+):[^>]+>, line=(\d+), category=<Category\.(\w+):[^>]+>, message='([^']+)', explanation='([^']+)'\)/g;
    const results = [];
    let match;
    while ((match = regex.exec(str)) !== null) {
      results.push({
        severity: match[1].toLowerCase(),
        line: parseInt(match[2]),
        category: match[3],
        message: match[4],
        explanation: match[5],
      });
    }
    return results;
  }
  
  return [];
}

const severityConfig: Record<Severity, { color: string; icon: typeof AlertTriangle; label: string }> = {
  info: { color: 'bg-info/10 text-info border-info/20', icon: Info, label: 'Info' },
  warning: { color: 'bg-warning/10 text-warning border-warning/20', icon: AlertTriangle, label: 'Warning' },
  critical: { color: 'bg-destructive/10 text-destructive border-destructive/20', icon: XCircle, label: 'Critical' },
  blocker: { color: 'bg-destructive/20 text-destructive border-destructive/30', icon: ShieldAlert, label: 'Blocker' },
};

const statusConfig = {
  SUCCESS: { color: 'bg-success/10 text-success border-success/20', label: 'Success' },
  FAILED: { color: 'bg-destructive/10 text-destructive border-destructive/20', label: 'Failed' },
  PENDING: { color: 'bg-warning/10 text-warning border-warning/20', label: 'Pending' },
};


export function ReviewDetail({ log, open, onOpenChange }: ReviewDetailProps) {
  if (!log) return null;

  const findings = parseFindings(log);
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <FileCode className="h-5 w-5 text-primary" />
            </div>
            <div>
              <DialogTitle className="text-lg">{log.repo_full_name}</DialogTitle>
              <p className="text-sm text-muted-foreground">PR #{log.pr_number} · Review #{log.id}</p>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4">
          {/* Meta info */}
          <div className="flex flex-wrap gap-3">
            <Badge variant="outline" className={cn('gap-1.5', statusConfig[log.status].color)}>
              <GitPullRequest className="h-3 w-3" />
              {statusConfig[log.status].label}
            </Badge>
            <Badge variant="outline" className="gap-1.5">
              <Calendar className="h-3 w-3" />
              {format(new Date(log.created_at), 'MMM d, yyyy HH:mm')}
            </Badge>
            <Badge variant="outline">{log.findings_count} findings</Badge>
          </div>

          {/* Summary */}
          {log.ai_metadata?.summary && (
            <Card className="bg-muted/30">
              <CardContent className="p-4">
                <p className="text-sm leading-relaxed">{log.ai_metadata.summary}</p>
              </CardContent>
            </Card>
          )}

          {/* Findings */}
          {findings.length > 0 && (
            <div className="space-y-3">
              <h4>Findings ({findings.length})</h4>
              {findings.map((finding, idx) => {
                const config = severityConfig[finding.severity];
                const Icon = config.icon;
                return (
                  <Card key={idx} className="overflow-hidden border-l-4" style={{ borderLeftColor: finding.severity === 'blocker' ? '#ef4444' : finding.severity === 'critical' ? '#f97316' : finding.severity === 'warning' ? '#f59e0b' : '#3b82f6' }}>
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className={cn('gap-1', config.color)}>
                            <Icon className="h-3 w-3" />
                            {config.label}
                          </Badge>
                          <Badge variant="secondary" className="text-xs">{finding.category}</Badge>
                          {finding.line !== null && (
                            <span className="text-xs text-muted-foreground font-mono">Line {finding.line}</span>
                          )}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium">{finding.message}</p>
                        <p className="text-sm text-muted-foreground mt-1">{finding.explanation}</p>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        <DialogClose onClick={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}
