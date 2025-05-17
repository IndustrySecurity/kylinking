import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme, App as AntApp } from 'antd';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import TenantManagement from './pages/admin/TenantManagement';
import UserManagement from './pages/admin/UserManagement';
import './index.css';

// Note: React Router warnings can be safely ignored for now
// They're related to future React Router v7 behavior

const App = () => {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 4,
          fontFamily: "'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        },
      }}
    >
      <AntApp>
        <Router>
          <MainLayout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/admin/tenants" element={<TenantManagement />} />
              <Route path="/admin/tenants/:tenantId/users" element={<UserManagement />} />
              {/* 其他路由将在后续添加 */}
            </Routes>
          </MainLayout>
        </Router>
      </AntApp>
    </ConfigProvider>
  );
};

export default App; 