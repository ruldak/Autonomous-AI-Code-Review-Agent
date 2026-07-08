import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Copy,
  Check,
  Github,
  Webhook,
  Settings,
  ArrowRight,
  Shield,
  Terminal,
  Globe,
} from 'lucide-react';
import { useState } from 'react';

function CodeBlock({ code, label }: { code: string; label?: string }) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-lg bg-muted border overflow-hidden">
      {label && (
        <div className="flex items-center justify-between px-3 py-1.5 bg-muted/80 border-b">
          <span className="text-xs font-medium text-muted-foreground">{label}</span>
          <Button variant="ghost" size="sm" className="h-6 gap-1 text-xs" onClick={copy}>
            {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
            {copied ? 'Copied' : 'Copy'}
          </Button>
        </div>
      )}
      <pre className="p-3 text-xs font-mono overflow-x-auto">{code}</pre>
    </div>
  );
}

export default function SetupPage() {
  const baseUrl = 'https://api.your-domain.com';
  const webhookUrl = `${baseUrl}/webhook`;
  const callbackUrl = `${baseUrl}/github/setup`;

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Setup Guide</h1>
        <p className="text-muted-foreground">Configure your GitHub App and connect repositories.</p>
      </div>

      {/* Steps */}
      <div className="space-y-6">
        {/* Step 1 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold">1</div>
              <div>
                <CardTitle className="text-base">Create GitHub App</CardTitle>
                <CardDescription>Register a new GitHub App in your organization settings.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <ArrowRight className="h-4 w-4 mt-0.5 text-primary flex-shrink-0" />
                Go to Settings → Developer Settings → GitHub Apps → New GitHub App
              </li>
              <li className="flex items-start gap-2">
                <ArrowRight className="h-4 w-4 mt-0.5 text-primary flex-shrink-0" />
                Fill in the app name, description, and homepage URL
              </li>
              <li className="flex items-start gap-2">
                <ArrowRight className="h-4 w-4 mt-0.5 text-primary flex-shrink-0" />
                Set the webhook URL and callback URL below
              </li>
            </ul>
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label className="text-xs font-medium mb-1.5 block">Webhook URL</label>
                <CodeBlock code={webhookUrl} label="POST endpoint" />
              </div>
              <div>
                <label className="text-xs font-medium mb-1.5 block">Setup Callback URL</label>
                <CodeBlock code={callbackUrl} label="GET redirect" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Step 2 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold">2</div>
              <div>
                <CardTitle className="text-base">Configure Permissions</CardTitle>
                <CardDescription>Set the required repository permissions for code review.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border p-3 space-y-2">
                <h4 className="text-sm font-medium flex items-center gap-2">
                  <Shield className="h-4 w-4 text-primary" />
                  Repository Permissions
                </h4>
                <div className="space-y-1.5">
                  <Badge variant="secondary" className="text-[10px]">Contents: Read</Badge>
                  <Badge variant="secondary" className="text-[10px]">Pull Requests: Read & Write</Badge>
                  <Badge variant="secondary" className="text-[10px]">Issues: Write</Badge>
                </div>
              </div>
              <div className="rounded-lg border p-3 space-y-2">
                <h4 className="text-sm font-medium flex items-center gap-2">
                  <Webhook className="h-4 w-4 text-primary" />
                  Subscribe to Events
                </h4>
                <div className="space-y-1.5">
                  <Badge variant="secondary" className="text-[10px]">Pull Request</Badge>
                  <Badge variant="secondary" className="text-[10px]">Pull Request Review</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Step 3 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold">3</div>
              <div>
                <CardTitle className="text-base">Install the App</CardTitle>
                <CardDescription>Add the GitHub App to your repositories.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              After creating the app, click "Install App" and select the repositories you want to monitor.
              The system will automatically start reviewing pull requests.
            </p>
            <CodeBlock
              label="Expected webhook payload (pull_request event)"
              code={`{
  "action": "opened",
  "pull_request": {
    "number": 42,
    "title": "Fix payment bug"
  },
  "repository": {
    "full_name": "myorg/payment-system"
  }
}`}
            />
          </CardContent>
        </Card>

        {/* API Reference */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold">4</div>
              <div>
                <CardTitle className="text-base">API Configuration</CardTitle>
                <CardDescription>Configure your frontend environment variables.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <CodeBlock
              label=".env file"
              code={`VITE_API_URL=http://localhost:8000
# Production
# VITE_API_URL=https://api.your-domain.com`}
            />
            <p className="text-xs text-muted-foreground">
              The dashboard will proxy requests to your FastAPI backend. Make sure CORS is enabled on the backend.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
