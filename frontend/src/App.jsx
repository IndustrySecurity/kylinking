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
import PackageMethodManagement from './pages/base-archive/PackageMethodManagement';
import DeliveryMethodManagement from './pages/base-archive/DeliveryMethodManagement';
import ColorCardManagement from './pages/base-archive/ColorCardManagement';
import UnitManagement from './pages/base-archive/UnitManagement';
import SpecificationManagement from './pages/base-archive/SpecificationManagement';
import CustomerCategoryManagement from './pages/base-archive/CustomerCategoryManagement';
import SupplierCategoryManagement from './pages/base-archive/SupplierCategoryManagement';
import MaterialCategoryManagement from './pages/base-archive/MaterialCategoryManagement';
import ProductCategoryManagement from './pages/base-archive/ProductCategoryManagement';
import InkOptionManagement from './pages/base-archive/InkOptionManagement';
import QuoteFreightManagement from './pages/base-archive/QuoteFreightManagement';
import LossTypeManagement from './pages/base-archive/LossTypeManagement';
import Currency from './pages/base-archive/financial-management/Currency';
import TaxRate from './pages/base-archive/financial-management/TaxRate';
import SettlementMethod from './pages/base-archive/financial-management/SettlementMethod';
import AccountManagement from './pages/base-archive/financial-management/AccountManagement';
import PaymentMethod from './pages/base-archive/financial-management/PaymentMethod';
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
            
            <Route path="/base-archive/package-methods" element={
              <ProtectedRoute>
                <MainLayout>
                  <PackageMethodManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/delivery-methods" element={
              <ProtectedRoute>
                <MainLayout>
                  <DeliveryMethodManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/color-cards" element={
              <ProtectedRoute>
                <MainLayout>
                  <ColorCardManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/units" element={
              <ProtectedRoute>
                <MainLayout>
                  <UnitManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/specifications" element={
              <ProtectedRoute>
                <MainLayout>
                  <SpecificationManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/customer-category-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <CustomerCategoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/supplier-category-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <SupplierCategoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/material-category-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialCategoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/product-categories" element={
              <ProtectedRoute>
                <MainLayout>
                  <ProductCategoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/ink-options" element={
              <ProtectedRoute>
                <MainLayout>
                  <InkOptionManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/quote-freights" element={
              <ProtectedRoute>
                <MainLayout>
                  <QuoteFreightManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/loss-type-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <LossTypeManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            {/* 基础档案 - 生产管理 */}
            <Route path="/base-archive/production-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <ProductionManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            {/* 基础档案 - 财务管理 */}
            <Route path="/base-archive/financial-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinancialManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            {/* 财务管理子页面 */}
            <Route path="/base-archive/financial-management/currency" element={
              <ProtectedRoute>
                <MainLayout>
                  <Currency />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/financial-management/tax-rate" element={
              <ProtectedRoute>
                <MainLayout>
                  <TaxRate />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/financial-management/settlement-method" element={
              <ProtectedRoute>
                <MainLayout>
                  <SettlementMethod />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/financial-management/account-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <AccountManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/financial-management/payment-method" element={
              <ProtectedRoute>
                <MainLayout>
                  <PaymentMethod />
                </MainLayout>
              </ProtectedRoute>
            } />

            
            {/* 生产档案路由 */}
            <Route path="/production/archive/packaging" element={
              <ProtectedRoute>
                <MainLayout>
                  <PackageMethodManagement />
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