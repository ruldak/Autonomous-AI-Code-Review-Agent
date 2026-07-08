import { useHealth } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import {
  Activity,
  Database,
  Server,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Wifi,
  Cpu,
  HardDrive,
  Clock,
} from 'lucide-react';
import { useState, useEffect } from 'react';

export default function HealthPage() {
  const { data, loading } = useHealth();
  const [uptime, setUptime] = useState(0);
  const [lastCheck, setLastCheck] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setUptime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const services = [
    {
      name: 'FastAPI Server',
      status: data?.status === 'healthy' ? 'healthy' : 'unhealthy',
      icon: Server,
      description: 'Main application server',
    },
    {
      name: 'PostgreSQL Database',
      status: data?.status === 'healthy' ? 'healthy' : 'unhealthy',
      icon: Database,
      description: 'Primary data store',
    },
    {
      name: 'Redis Cache',
      status: data?.status === 'healthy' ? 'healthy' : 'unhealthy',
      icon: Cpu,
      description: 'Task queue & caching',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Health</h1>
          <p className="text-muted-foreground">Monitor the health and status of all system components.</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => window.location.reload()} className="gap-1">
          <RefreshCw className="h-3.5 w-3.5" /> Refresh
        </Button>
      </div>

      {/* Overall Status */}
      <Card className={data?.status === 'healthy' ? 'border-success/30' : 'border-destructive/30'}>
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className={`flex h-14 w-14 items-center justify-center rounded-full ${data?.status === 'healthy' ? 'bg-success/10' : 'bg-destructive/10'}`}>
              {data?.status === 'healthy' ? (
                <CheckCircle2 className="h-7 w-7 text-success" />
              ) : (
                <XCircle className="h-7 w-7 text-destructive" />
              )}
            </div>
            <div>
              <h2 className="text-xl font-semibold">
                {data?.status === 'healthy' ? 'All Systems Operational' : 'System Issues Detected'}
              </h2>
              <p className="text-sm text-muted-foreground">
                Last checked: {lastCheck.toLocaleTimeString()}
              </p>
            </div>
            <div className="ml-auto text-right">
              <p className="text-2xl font-mono font-bold">{formatUptime(uptime)}</p>
              <p className="text-xs text-muted-foreground">Session uptime</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Services Grid */}
      <div className="grid gap-4 md:grid-cols-3">
        {loading ? (
          <>
            <Skeleton className="h-[160px]" />
            <Skeleton className="h-[160px]" />
            <Skeleton className="h-[160px]" />
          </>
        ) : (
          services.map((service) => (
            <Card key={service.name} className={service.status === 'healthy' ? 'border-success/20' : 'border-destructive/20'}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                    <service.icon className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <Badge
                    variant={service.status === 'healthy' ? 'success' : 'destructive'}
                    className="text-[10px]"
                  >
                    {service.status === 'healthy' ? 'Healthy' : 'Down'}
                  </Badge>
                </div>
                <CardTitle className="text-base mt-2">{service.name}</CardTitle>
                <CardDescription>{service.description}</CardDescription>
              </CardHeader>
            </Card>
          ))
        )}
      </div>

      {/* Raw Response */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Raw Health Response</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="rounded-lg bg-muted p-4 text-xs font-mono overflow-x-auto">
            {loading ? 'Loading...' : JSON.stringify(data, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
