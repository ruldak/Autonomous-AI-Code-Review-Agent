# AI Code Review Dashboard

Dashboard frontend untuk **Autonomous AI Code Review Agent** — sistem review kode otomatis berbasis AI yang terintegrasi dengan GitHub.

## Fitur

- **Dashboard Overview** — Statistik review, success rate, bugs detected
- **Review Logs** — Riwayat review dengan pagination, filtering, dan sorting (TanStack Table v8)
- **Repositories** — Daftar repo yang terhubung dengan metrik masing-masing
- **System Health** — Monitoring status FastAPI, PostgreSQL, dan Redis
- **Setup Guide** — Panduan konfigurasi GitHub App
- **Dark/Light Mode** — Toggle tema
- **Responsive Design** — Mobile-friendly sidebar

## Tech Stack

- React 19 + TypeScript 5
- Vite 6
- Tailwind CSS 3
- TanStack Table v8
- Recharts
- React Router v7
- Lucide React

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Copy environment config
cp .env.example .env

# 3. Start development server
npm run dev
```

## Konfigurasi API

Edit file `.env` dan sesuaikan `VITE_API_URL` dengan base URL backend FastAPI Anda:

```env
# Development (default proxy ke localhost:8000)
VITE_API_URL=/api

# Production
VITE_API_URL=https://api.your-domain.com
```

> **Catatan:** Vite proxy di `vite.config.ts` akan meneruskan request `/api/*` ke `http://localhost:8000` saat development.

## Build untuk Production

```bash
npm run build
```

Output akan berada di folder `dist/`. Deploy ke Vercel, Netlify, atau static host lainnya.

## Struktur Folder

```
src/
├── components/        # UI components (shadcn-style)
│   ├── ui/           # Primitive components
│   ├── Sidebar.tsx
│   ├── Header.tsx
│   ├── Layout.tsx
│   ├── StatCard.tsx
│   ├── ReviewCharts.tsx
│   └── ReviewDetail.tsx
├── pages/            # Route pages
│   ├── Dashboard.tsx
│   ├── LogsPage.tsx
│   ├── RepositoriesPage.tsx
│   ├── HealthPage.tsx
│   ├── SetupPage.tsx
│   └── NotFound.tsx
├── hooks/            # Custom React hooks
│   └── useApi.ts
├── lib/              # Utilities & API client
│   ├── utils.ts
│   └── api.ts
├── types/            # TypeScript types
│   └── api.ts
├── App.tsx
├── main.tsx
└── index.css
```

## API Endpoints yang Digunakan

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/reviews/logs` | GET | Riwayat review (pagination, filter) |
| `/reviews/stats` | GET | Statistik agregat |
| `/health` | GET | Health check |

## Deploy ke Vercel

1. Push ke GitHub
2. Import repo di [vercel.com](https://vercel.com)
3. Set framework preset ke **Vite**
4. Tambahkan environment variable `VITE_API_URL`
5. Deploy!

## License

MIT
