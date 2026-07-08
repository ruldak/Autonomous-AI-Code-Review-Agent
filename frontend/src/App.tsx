import { Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import Dashboard from '@/pages/Dashboard';
import LogsPage from '@/pages/LogsPage';
import RepositoriesPage from '@/pages/RepositoriesPage';
import HealthPage from '@/pages/HealthPage';
import SetupPage from '@/pages/SetupPage';
import NotFound from '@/pages/NotFound';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/repositories" element={<RepositoriesPage />} />
        <Route path="/health" element={<HealthPage />} />
        <Route path="/setup" element={<SetupPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}

export default App;
