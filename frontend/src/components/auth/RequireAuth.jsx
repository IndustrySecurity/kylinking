import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import { Spin } from 'antd';

/**
 * 需要认证的路由守卫组件
 * @param {Object} props
 * @param {boolean} props.requireAdmin - 是否需要管理员权限
 * @param {React.ReactNode} props.children - 子组件
 */
const RequireAuth = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  const location = useLocation();

  // 如果正在加载认证状态，显示加载中
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip="认证中..." />
      </div>
    );
  }

  // 如果未认证，重定向到登录页面
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 如果需要管理员权限但用户不是管理员，重定向到首页
  if (requireAdmin && !isAdmin) {
    return <Navigate to="/dashboard" state={{ from: location }} replace />;
  }

  // 认证成功，渲染子组件
  return children;
};

export default RequireAuth; 