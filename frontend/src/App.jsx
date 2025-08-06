import React, { useEffect, useState, startTransition } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, Outlet, useLocation } from 'react-router-dom';
import { ConfigProvider, theme, App as AntApp, message } from 'antd';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import TenantManagement from './pages/admin/TenantManagement';
import UserManagement from './pages/admin/UserManagement';
import SystemManagement from './pages/admin/SystemManagement';
import TenantModuleManagement from './pages/admin/TenantModuleManagement';
import Login from './pages/auth/Login';
import UserProfile from './pages/profile/UserProfile';

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
import TeamGroupManagement from './pages/base-archive/base-data/TeamGroupManagement';
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

// 生产管理导入
import ProductionSchedule from './pages/production/ProductionSchedule';
import ProductionMonitor from './pages/production/ProductionMonitor';

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
      startTransition(() => {
        navigate('/login', { replace: true });
      });
    }
    
    setChecking(false);
  }, [navigate, getToken, isLoggedIn]);
  
  if (checking) {
    return <div>正在检查登录状态...</div>;
  }
  
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// 调试组件
const RouteDebug = ({ path, element }) => {
  const location = useLocation();
  
  useEffect(() => {
    console.log(`Route Debug: ${path} matched for location: ${location.pathname}`);
  }, [location.pathname, path]);
  
  return element;
};

// 通用调试组件
const UniversalDebug = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [forceRefresh, setForceRefresh] = useState(false);
  
  useEffect(() => {
    console.log(`Universal Debug: Current location is ${location.pathname}`);
    console.log(`Browser URL: ${window.location.pathname}`);
    
    // 强制同步浏览器URL和React Router状态
    const currentPath = window.location.pathname;
    if (location.pathname !== currentPath) {
      console.log(`Route sync: Browser path ${currentPath} != Router path ${location.pathname}, forcing sync`);
      
      // 如果差异太大，强制刷新页面
      if (Math.abs(location.pathname.split('/').length - currentPath.split('/').length) > 1) {
        console.log('Large path difference detected, forcing page refresh');
        window.location.reload();
        return;
      }
      
      // 使用 startTransition 确保在下一个事件循环中执行
      startTransition(() => {
        navigate(currentPath, { replace: true });
      });
    }
  }, [location.pathname, navigate]);
  
  // 监听浏览器URL变化
  useEffect(() => {
    const handlePopState = () => {
      const currentPath = window.location.pathname;
      console.log(`PopState detected: ${currentPath}`);
      if (location.pathname !== currentPath) {
        console.log(`Forcing navigation to: ${currentPath}`);
        startTransition(() => {
          navigate(currentPath, { replace: true });
        });
      }
    };
    
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [location.pathname, navigate]);
  
  // 添加强制刷新按钮（仅在开发环境）
  if (process.env.NODE_ENV === 'development') {
    return (
      <div style={{ position: 'fixed', top: 10, right: 10, zIndex: 9999 }}>
        <button 
          onClick={() => window.location.reload()}
          style={{ 
            background: 'red', 
            color: 'white', 
            border: 'none', 
            padding: '5px 10px',
            borderRadius: '3px',
            cursor: 'pointer'
          }}
        >
          强制刷新
        </button>
      </div>
    );
  }
  
  return null;
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
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/public-debug" element={<Debug />} />
            
            {/* Protected routes with MainLayout */}
            <Route element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/profile" element={<UserProfile />} />
              
              {/* 基础档案路由 */}
              <Route path="/base-archive/base-data" element={<BaseData />} />
              <Route path="/base-archive/production-data" element={<ProductionData />} />
              
              {/* 基础数据路由 */}
              <Route path="/base-archive/base-data/customer-management" element={<CustomerManagement />} />
              <Route path="/base-archive/base-data/product-management" element={<ProductManagement />} />
              <Route path="/base-archive/base-data/supplier-management" element={<SupplierManagement />} />
              <Route path="/base-archive/base-data/material-management" element={<MaterialManagement />} />
              <Route path="/base-archive/base-data/department-management" element={<DepartmentManagement />} />
              <Route path="/base-archive/base-data/position-management" element={<PositionManagement />} />
              <Route path="/base-archive/base-data/employee-management" element={<EmployeeManagement />} />
              <Route path="/base-archive/base-data/team-group-management" element={<TeamGroupManagement />} />
              
              {/* 基础分类路由 */}
              <Route path="/base-archive/base-category/customer-category-management" element={<CustomerCategoryManagement />} />
              <Route path="/base-archive/base-category/product-category-management" element={<ProductCategoryManagement />} />
              <Route path="/base-archive/base-category/supplier-category-management" element={<SupplierCategoryManagement />} />
              <Route path="/base-archive/base-category/material-category-management" element={<MaterialCategoryManagement />} />
              <Route path="/base-archive/base-category/process-category-management" element={<ProcessCategoryManagement />} />
              
              {/* 生产档案路由 */}
              <Route path="/base-archive/production-archive/team-group-management" element={<TeamGroupManagement />} />
              <Route path="/base-archive/production-archive/machine-management" element={<MachineManagement />} />
              <Route path="/base-archive/production-archive/warehouse-management" element={<WarehouseManagement />} />
              <Route path="/base-archive/production-archive/process-management" element={<ProcessManagement />} />
              <Route path="/base-archive/production-archive/bag-type-management" element={<BagTypeManagement />} />
              <Route path="/base-archive/production-archive/package-method-management" element={<PackageMethodManagement />} />
              <Route path="/base-archive/production-archive/delivery-method-management" element={<DeliveryMethodManagement />} />
              <Route path="/base-archive/production-archive/loss-type-management" element={<LossTypeManagement />} />
              <Route path="/base-archive/production-archive/specification-management" element={<SpecificationManagement />} />
              <Route path="/base-archive/production-archive/color-card-management" element={<ColorCardManagement />} />
              <Route path="/base-archive/production-archive/unit-management" element={<UnitManagement />} />
              
              {/* 生产配置路由 */}
              <Route path="/base-archive/production-config/bag-related-formula-management" element={<BagRelatedFormulaManagement />} />
              <Route path="/base-archive/production-config/calculation-scheme-management" element={<CalculationSchemeManagement />} />
              <Route path="/base-archive/production-config/calculation-parameter-management" element={<CalculationParameterManagement />} />
              <Route path="/base-archive/production-config/quote-accessory-management" element={<QuoteAccessoryManagement />} />
              <Route path="/base-archive/production-config/quote-ink-management" element={<QuoteInkManagement />} />
              <Route path="/base-archive/production-config/quote-loss-management" element={<QuoteLossManagement />} />
              <Route path="/base-archive/production-config/quote-material-management" element={<QuoteMaterialManagement />} />
              <Route path="/base-archive/production-config/quote-freight-management" element={<QuoteFreightManagement />} />
              <Route path="/base-archive/production-config/ink-option-management" element={<InkOptionManagement />} />
              
              {/* 基础档案 - 财务管理 */}
              <Route path="/base-archive/financial-management" element={<FinancialManagement />} />
              
              {/* 财务管理子页面 */}
              <Route path="/base-archive/financial-management/currency" element={<Currency />} />
              <Route path="/base-archive/financial-management/tax-rate" element={<TaxRate />} />
              <Route path="/base-archive/financial-management/settlement-method" element={<SettlementMethod />} />
              <Route path="/base-archive/financial-management/account-management" element={<AccountManagement />} />
              <Route path="/base-archive/financial-management/payment-method" element={<PaymentMethod />} />

              {/* 仓库管理路由 */}
              <Route path="/business/inventory-overview" element={<InventoryOverview />} />
              <Route path="/business/material-warehouse" element={<MaterialWarehouse />} />
              <Route path="/business/finished-goods-warehouse" element={<FinishedGoodsWarehouse />} />

              {/* 销售管理路由 */}
              <Route path="/business/sales-management" element={<SalesManagement />} />

              {/* 销售功能页面路由 */}
              <Route path="/business/sales/sales-order" element={<SalesOrder />} />
              <Route path="/business/sales/delivery-notice" element={<DeliveryNotice />} />
              <Route path="/business/sales/delivery-order" element={<DeliveryOrder />} />
              <Route path="/business/sales/return-notice" element={<ReturnNotice />} />
              <Route path="/business/sales/return-order" element={<ReturnOrder />} />
              <Route path="/business/sales/customer-contract" element={<CustomerContract />} />
              <Route path="/business/sales/monthly-plan" element={<MonthlyPlan />} />

              {/* 成品仓库子页面 */}
              <Route path="/business/finished-goods/inbound" element={<FinishedGoodsInbound />} />
              <Route path="/business/finished-goods/outbound" element={<FinishedGoodsOutbound />} />
              <Route path="/business/finished-goods/count" element={<FinishedGoodsCount />} />
              <Route path="/business/finished-goods/transfer" element={<FinishedGoodsTransfer />} />
              <Route path="/business/finished-goods/weighing-slip" element={<FinishedGoodsWeighingSlip />} />
              <Route path="/business/finished-goods/packing-weighing-slip" element={<PackingWeighingSlip />} />
              <Route path="/business/finished-goods/rewinding-output-report" element={<RewindingOutputReport />} />
              <Route path="/business/finished-goods/bag-picking-output-report" element={<BagPickingOutputReport />} />
              <Route path="/business/finished-goods/semi-finished-inbound" element={<SemiFinishedInbound />} />
              <Route path="/business/finished-goods/semi-finished-outbound" element={<SemiFinishedOutbound />} />
              <Route path="/business/finished-goods/bag-picking-return" element={<BagPickingReturn />} />
              <Route path="/business/finished-goods/to-tray" element={<FinishedGoodsToTray />} />
              <Route path="/business/finished-goods/rework" element={<FinishedGoodsRework />} />
              <Route path="/business/finished-goods/packing" element={<FinishedGoodsPacking />} />
              <Route path="/business/finished-goods/semi-finished-weighing" element={<SemiFinishedWeighing />} />
              <Route path="/business/finished-goods/inbound-accounting" element={<FinishedGoodsInboundAccounting />} />

              {/* 材料仓库子页面 */}
              <Route path="/business/material-warehouse/inbound" element={<MaterialInbound />} />
              <Route path="/business/material-warehouse/outbound" element={<MaterialOutbound />} />
              <Route path="/business/material-warehouse/count" element={<MaterialCount />} />
              <Route path="/business/material-warehouse/transfer" element={<MaterialTransfer />} />

              {/* 生产管理路由 */}
              <Route path="/production/schedule" element={<ProductionSchedule />} />
              <Route path="/production/monitor" element={<ProductionMonitor />} />

              {/* 平台管理路由 */}
              <Route path="/admin/tenants" element={<TenantManagement />} />
              <Route path="/admin/modules" element={<TenantModuleManagement />} />
              <Route path="/admin/users" element={<UserManagement />} />
              <Route path="/admin/tenants/:tenantId/users" element={<UserManagement />} />
              <Route path="/admin/system" element={<SystemManagement />} />
              
              <Route path="/debug" element={<Debug />} />
              
              {/* Redirect all other routes to dashboard */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
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