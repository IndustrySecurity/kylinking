import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { ConfigProvider, theme, App as AntApp, message } from 'antd';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import TenantManagement from './pages/admin/TenantManagement';
import UserManagement from './pages/admin/UserManagement';
import SystemManagement from './pages/admin/SystemManagement';
import TenantModuleManagement from './pages/admin/TenantModuleManagement';
import Login from './pages/auth/Login';
import BaseData from './pages/base-archive/BaseData';
import ProductionManagement from './pages/base-archive/ProductionManagement';
import FinancialManagement from './pages/base-archive/FinancialManagement';
import CustomerCategories from './pages/base-archive/base-data/base-category/CustomerCategories';
import ProductCategories from './pages/base-archive/base-data/base-category/ProductCategories';
import SupplierCategories from './pages/base-archive/base-data/base-category/SupplierCategories';
import MaterialCategories from './pages/base-archive/base-data/base-category/MaterialCategories';
import Debug from './pages/auth/Debug';
import { useApi } from './hooks/useApi';
import './index.css';

// Note: React Router warnings can be safely ignored for now
// They're related to future React Router v7 behavior

// 配置全局Message
message.config({
  top: 60,
  duration: 3,
  maxCount: 3,
});

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isLoggedIn, getToken } = useApi();
  const navigate = useNavigate();
  const [checking, setChecking] = useState(true);
  
  useEffect(() => {
    // 检查是否有token
    const token = getToken();
    
    if (!token) {
      navigate('/login', { replace: true });
    }
    
    setChecking(false);
  }, [navigate, getToken]);
  
  if (checking) {
    return <div>正在检查登录状态...</div>;
  }
  
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// 应用根组件
const AppRoot = () => {
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
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/public-debug" element={<Debug />} />
            
            {/* Protected routes within MainLayout */}
            <Route path="/" element={
              <ProtectedRoute>
                <MainLayout>
                  <Navigate to="/dashboard" replace />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <MainLayout>
                  <Dashboard />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            {/* 基础档案路由 */}
            <Route path="/base-archive/base-data" element={
              <ProtectedRoute>
                <MainLayout>
                  <BaseData />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <ProductionManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/financial-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinancialManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            {/* 基础分类路由 */}
            <Route path="/base-archive/base-data/base-category/customer-categories" element={
              <ProtectedRoute>
                <MainLayout>
                  <CustomerCategories />
                </MainLayout>
              </ProtectedRoute>
            } />
            <Route path="/base-archive/base-data/base-category/product-categories" element={
              <ProtectedRoute>
                <MainLayout>
                  <ProductCategories />
                </MainLayout>
              </ProtectedRoute>
            } />
            <Route path="/base-archive/base-data/base-category/supplier-categories" element={
              <ProtectedRoute>
                <MainLayout>
                  <SupplierCategories />
                </MainLayout>
              </ProtectedRoute>
            } />
            <Route path="/base-archive/base-data/base-category/material-categories" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialCategories />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            {/* 平台管理路由 */}
            <Route path="/admin/tenants" element={
              <ProtectedRoute>
                <MainLayout>
                  <TenantManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/modules" element={
              <ProtectedRoute>
                <MainLayout>
                  <TenantModuleManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/users" element={
              <ProtectedRoute>
                <MainLayout>
                  <UserManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/tenants/:tenantId/users" element={
              <ProtectedRoute>
                <MainLayout>
                  <UserManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/system" element={
              <ProtectedRoute>
                <MainLayout>
                  <SystemManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/debug" element={
              <ProtectedRoute>
                <MainLayout>
                  <Debug />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            {/* Redirect all other routes to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AntApp>
    </ConfigProvider>
  );
};

// 保持导出的App组件形式不变
const App = () => {
  return <AppRoot />;
};

export default App; 