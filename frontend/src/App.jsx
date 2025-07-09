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

// 基础档案导入
import BaseData from './pages/base-archive/BaseData';
import ProductionData from './pages/base-archive/ProductionData';
import FinancialManagement from './pages/base-archive/FinancialManagement';

// 基础数据相关导入
import CustomerManagement from './pages/base-archive/base-data/CustomerManagement';
import ProductManagement from './pages/base-archive/base-data/ProductManagement';
import SupplierManagement from './pages/base-archive/base-data/SupplierManagement';
import MaterialManagement from './pages/base-archive/base-data/MaterialManagement';
import DepartmentManagement from './pages/base-archive/base-data/DepartmentManagement';
import PositionManagement from './pages/base-archive/base-data/PositionManagement';
import EmployeeManagement from './pages/base-archive/base-data/EmployeeManagement';
// 基础分类相关导入
import CustomerCategoryManagement from './pages/base-archive/base-category/CustomerCategoryManagement';
import ProductCategoryManagement from './pages/base-archive/base-category/ProductCategoryManagement';
import SupplierCategoryManagement from './pages/base-archive/base-category/SupplierCategoryManagement';
import MaterialCategoryManagement from './pages/base-archive/base-category/MaterialCategoryManagement';
import ProcessCategoryManagement from './pages/base-archive/base-category/ProcessCategoryManagement';

// 生产档案相关导入
import TeamGroupManagement from './pages/base-archive/production-archive/TeamGroupManagement';
import MachineManagement from './pages/base-archive/production-archive/MachineManagement';
import WarehouseManagement from './pages/base-archive/production-archive/WarehouseManagement';
import ProcessManagement from './pages/base-archive/production-archive/ProcessManagement';
import BagTypeManagement from './pages/base-archive/production-archive/BagTypeManagement';
import PackageMethodManagement from './pages/base-archive/production-archive/PackageMethodManagement';
import DeliveryMethodManagement from './pages/base-archive/production-archive/DeliveryMethodManagement';
import LossTypeManagement from './pages/base-archive/production-archive/LossTypeManagement';
import SpecificationManagement from './pages/base-archive/production-archive/SpecificationManagement';
import ColorCardManagement from './pages/base-archive/production-archive/ColorCardManagement';
import UnitManagement from './pages/base-archive/production-archive/UnitManagement';

// 生产配置相关导入
import BagRelatedFormulaManagement from './pages/base-archive/production-config/BagRelatedFormulaManagement';
import CalculationSchemeManagement from './pages/base-archive/production-config/CalculationSchemeManagement';
import CalculationParameterManagement from './pages/base-archive/production-config/CalculationParameterManagement';
import QuoteAccessoryManagement from './pages/base-archive/production-config/QuoteAccessoryManagement';
import QuoteInkManagement from './pages/base-archive/production-config/QuoteInkManagement';
import QuoteLossManagement from './pages/base-archive/production-config/QuoteLossManagement';
import QuoteMaterialManagement from './pages/base-archive/production-config/QuoteMaterialManagement';
import QuoteFreightManagement from './pages/base-archive/production-config/QuoteFreightManagement';
import InkOptionManagement from './pages/base-archive/production-config/InkOptionManagement';

// 财务管理导入
import Currency from './pages/base-archive/financial-management/Currency';
import TaxRate from './pages/base-archive/financial-management/TaxRate';
import SettlementMethod from './pages/base-archive/financial-management/SettlementMethod';
import AccountManagement from './pages/base-archive/financial-management/AccountManagement';
import PaymentMethod from './pages/base-archive/financial-management/PaymentMethod';

// 仓库管理导入
import MaterialWarehouse from './pages/business/MaterialWarehouse';
import FinishedGoodsWarehouse from './pages/business/FinishedGoodsWarehouse';
import InventoryOverview from './pages/business/InventoryOverview';

// 销售管理导入
import SalesManagement from './pages/business/SalesManagement';

// 销售功能页面导入
import SalesOrder from './pages/business/sales/SalesOrder';
import DeliveryNotice from './pages/business/sales/DeliveryNotice';
import DeliveryOrder from './pages/business/sales/DeliveryOrder';
import ReturnNotice from './pages/business/sales/ReturnNotice';
import ReturnOrder from './pages/business/sales/ReturnOrder';
import CustomerContract from './pages/business/sales/CustomerContract';
import MonthlyPlan from './pages/business/sales/MonthlyPlan';

// 成品仓库子页面导入
import FinishedGoodsInbound from './pages/business/finished-goods/FinishedGoodsInbound';
import FinishedGoodsOutbound from './pages/business/finished-goods/FinishedGoodsOutbound';
import FinishedGoodsCount from './pages/business/finished-goods/FinishedGoodsCount';
import FinishedGoodsTransfer from './pages/business/finished-goods/FinishedGoodsTransfer';
import FinishedGoodsWeighingSlip from './pages/business/finished-goods/FinishedGoodsWeighingSlip';
import PackingWeighingSlip from './pages/business/finished-goods/PackingWeighingSlip';
import RewindingOutputReport from './pages/business/finished-goods/RewindingOutputReport';
import BagPickingOutputReport from './pages/business/finished-goods/BagPickingOutputReport';
import SemiFinishedInbound from './pages/business/finished-goods/SemiFinishedInbound';
import SemiFinishedOutbound from './pages/business/finished-goods/SemiFinishedOutbound';
import BagPickingReturn from './pages/business/finished-goods/BagPickingReturn';
import FinishedGoodsToTray from './pages/business/finished-goods/FinishedGoodsToTray';
import FinishedGoodsRework from './pages/business/finished-goods/FinishedGoodsRework';
import FinishedGoodsPacking from './pages/business/finished-goods/FinishedGoodsPacking';
import SemiFinishedWeighing from './pages/business/finished-goods/SemiFinishedWeighing';
import FinishedGoodsInboundAccounting from './pages/business/finished-goods/FinishedGoodsInboundAccounting';

// 材料仓库子页面导入
import MaterialInbound from './pages/business/material-warehouse/MaterialInbound';
import MaterialOutbound from './pages/business/material-warehouse/MaterialOutbound';
import MaterialCount from './pages/business/material-warehouse/MaterialCount';
import MaterialTransfer from './pages/business/material-warehouse/MaterialTransfer';

import Debug from './pages/auth/Debug';

import { useApi } from './hooks/useApi';
import './index.css';

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
        <Router future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}>
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
            
            {/* 生产档案路由 */}
            <Route path="/base-archive/production-data" element={
              <ProtectedRoute>
                <MainLayout>
                  <ProductionData />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            {/* 基础数据路由 */}
            <Route path="/base-archive/base-data/customer-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <CustomerManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-data/product-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <ProductManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-data/supplier-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <SupplierManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-data/material-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-data/department-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <DepartmentManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-data/position-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <PositionManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-data/employee-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <EmployeeManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            

            
            {/* 基础分类路由 */}
            <Route path="/base-archive/base-category/customer-category-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <CustomerCategoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-category/product-category-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <ProductCategoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-category/supplier-category-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <SupplierCategoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-category/material-category-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialCategoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/base-category/process-category-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <ProcessCategoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            

            
            {/* 生产档案路由 */}
            <Route path="/base-archive/production-archive/team-group-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <TeamGroupManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-archive/machine-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <MachineManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-archive/warehouse-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <WarehouseManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-archive/process-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <ProcessManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            

            
            <Route path="/base-archive/production-archive/bag-type-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <BagTypeManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-archive/package-method-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <PackageMethodManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-archive/delivery-method-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <DeliveryMethodManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-archive/loss-type-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <LossTypeManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-archive/specification-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <SpecificationManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-archive/color-card-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <ColorCardManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-archive/unit-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <UnitManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            {/* 生产配置路由 */}
            
            <Route path="/base-archive/production-config/bag-related-formula-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <BagRelatedFormulaManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-config/calculation-scheme-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <CalculationSchemeManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-config/calculation-parameter-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <CalculationParameterManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-config/quote-accessory-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <QuoteAccessoryManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-config/quote-ink-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <QuoteInkManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-config/quote-loss-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <QuoteLossManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-config/quote-material-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <QuoteMaterialManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-config/quote-freight-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <QuoteFreightManagement />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/base-archive/production-config/ink-option-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <InkOptionManagement />
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

            {/* 销售管理路由 */}
            <Route path="/business/sales-management" element={
              <ProtectedRoute>
                <MainLayout>
                  <SalesManagement />
                </MainLayout>
              </ProtectedRoute>
            } />

            {/* 销售功能页面路由 */}
            <Route path="/business/sales/sales-order" element={
              <ProtectedRoute>
                <MainLayout>
                  <SalesOrder />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/sales/delivery-notice" element={
              <ProtectedRoute>
                <MainLayout>
                  <DeliveryNotice />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/sales/delivery-order" element={
              <ProtectedRoute>
                <MainLayout>
                  <DeliveryOrder />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/sales/return-notice" element={
              <ProtectedRoute>
                <MainLayout>
                  <ReturnNotice />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/sales/return-order" element={
              <ProtectedRoute>
                <MainLayout>
                  <ReturnOrder />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/sales/customer-contract" element={
              <ProtectedRoute>
                <MainLayout>
                  <CustomerContract />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/sales/monthly-plan" element={
              <ProtectedRoute>
                <MainLayout>
                  <MonthlyPlan />
                </MainLayout>
              </ProtectedRoute>
            } />

            {/* 仓库管理路由 */}
            <Route path="/business/inventory-overview" element={
              <ProtectedRoute>
                <MainLayout>
                  <InventoryOverview />
                </MainLayout>
              </ProtectedRoute>
            } />

            <Route path="/business/material-warehouse" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialWarehouse />
                </MainLayout>
              </ProtectedRoute>
            } />

            <Route path="/business/finished-goods-warehouse" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsWarehouse />
                </MainLayout>
              </ProtectedRoute>
            } />

            {/* 成品仓库子页面路由 */}
            <Route path="/business/finished-goods/inbound" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsInbound />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/outbound" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsOutbound />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/inventory" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsCount />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/transfer" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsTransfer />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/weighing-slip" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsWeighingSlip />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/packing-weighing-slip" element={
              <ProtectedRoute>
                <MainLayout>
                  <PackingWeighingSlip />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/rewinding-output-report" element={
              <ProtectedRoute>
                <MainLayout>
                  <RewindingOutputReport />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/bag-picking-output-report" element={
              <ProtectedRoute>
                <MainLayout>
                  <BagPickingOutputReport />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/semi-finished-inbound" element={
              <ProtectedRoute>
                <MainLayout>
                  <SemiFinishedInbound />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/semi-finished-outbound" element={
              <ProtectedRoute>
                <MainLayout>
                  <SemiFinishedOutbound />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/bag-picking-return" element={
              <ProtectedRoute>
                <MainLayout>
                  <BagPickingReturn />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/to-tray" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsToTray />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/rework" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsRework />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/packing" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsPacking />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/semi-finished-weighing" element={
              <ProtectedRoute>
                <MainLayout>
                  <SemiFinishedWeighing />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/finished-goods/inbound-accounting" element={
              <ProtectedRoute>
                <MainLayout>
                  <FinishedGoodsInboundAccounting />
                </MainLayout>
              </ProtectedRoute>
            } />

            {/* 材料仓库路由 */}
            <Route path="/business/material-warehouse" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialWarehouse />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/material-warehouse/inbound" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialInbound />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/material-warehouse/outbound" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialOutbound />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/material-warehouse/count" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialCount />
                </MainLayout>
              </ProtectedRoute>
            } />
            
            <Route path="/business/material-warehouse/transfer" element={
              <ProtectedRoute>
                <MainLayout>
                  <MaterialTransfer />
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
            
            {/* 兼容旧路径重定向 */}
            <Route path="/base-archive/customer-management" element={
              <Navigate to="/base-archive/base-data/customer-management" replace />
            } />
            <Route path="/base-archive/product-management" element={
              <Navigate to="/base-archive/base-data/product-management" replace />
            } />
            <Route path="/base-archive/supplier-management" element={
              <Navigate to="/base-archive/base-data/supplier-management" replace />
            } />
            <Route path="/base-archive/material-management" element={
              <Navigate to="/base-archive/base-data/material-management" replace />
            } />
            <Route path="/base-archive/departments" element={
              <Navigate to="/base-archive/base-data/department-management" replace />
            } />
            <Route path="/base-archive/positions" element={
              <Navigate to="/base-archive/base-data/position-management" replace />
            } />
            <Route path="/base-archive/employees" element={
              <Navigate to="/base-archive/base-data/employee-management" replace />
            } />
            <Route path="/base-archive/units" element={
              <Navigate to="/base-archive/production/production-archive/unit-management" replace />
            } />
            <Route path="/base-archive/customer-category-management" element={
              <Navigate to="/base-archive/base-category/customer-category-management" replace />
            } />
            <Route path="/base-archive/product-categories" element={
              <Navigate to="/base-archive/base-category/product-category-management" replace />
            } />
            <Route path="/base-archive/supplier-category-management" element={
              <Navigate to="/base-archive/base-category/supplier-category-management" replace />
            } />
            <Route path="/base-archive/material-category-management" element={
              <Navigate to="/base-archive/base-category/material-category-management" replace />
            } />
            <Route path="/base-archive/process-categories" element={
              <Navigate to="/base-archive/base-category/process-category-management" replace />
            } />
            <Route path="/base-archive/color-cards" element={
              <Navigate to="/base-archive/production/production-archive/color-card-management" replace />
            } />
            <Route path="/production/config/bag-formula" element={
              <Navigate to="/base-archive/production/production-config/bag-related-formula-management" replace />
            } />
            <Route path="/production/archive/process" element={
              <Navigate to="/base-archive/production/production-archive/process-management" replace />
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