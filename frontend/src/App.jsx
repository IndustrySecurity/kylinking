import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, Layout, Menu, Button, theme, Spin, message } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  TeamOutlined,
  AppstoreOutlined,
  CloudServerOutlined,
  UserOutlined,
  SettingOutlined,
  SafetyOutlined,
  LogoutOutlined,
  LoginOutlined
} from '@ant-design/icons';

// 页面组件
import Login from './pages/auth/Login';
import Dashboard from './pages/admin/Dashboard';
import TenantManagement from './pages/admin/TenantManagement';
import UserManagement from './pages/admin/UserManagement';
import RoleManagement from './pages/admin/RoleManagement';
import UserProfile from './pages/common/UserProfile';

// Hooks
import { useApi } from './hooks/useApi';

const { Header, Sider, Content } = Layout;

const App = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);
  const { token } = theme.useToken();
  const api = useApi();
  const { isLoggedIn, logout, getUser } = api;
  const user = getUser();

  // 检查登录状态
  useEffect(() => {
    setLoading(false);
  }, [isLoggedIn]);

  // 处理登出
  const handleLogout = async () => {
    try {
      await logout();
      message.success('退出登录成功');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // 未登录情况的内容
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  // 主应用内容
  return (
    <ConfigProvider 
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 4,
        },
        components: {
          Layout: {
            bodyBg: '#f0f2f5',
            headerBg: '#fff',
            siderBg: '#001529',
          },
        },
      }}
    >
      <Router>
        <Routes>
          {/* 登录页面 */}
          <Route 
            path="/login" 
            element={isLoggedIn ? <Navigate to="/admin/dashboard" /> : <Login />} 
          />
          
          {/* 需要登录的页面 */}
          <Route
            path="/*"
            element={
              isLoggedIn ? (
                <Layout style={{ minHeight: '100vh' }}>
                  {/* 侧边栏 */}
                  <Sider trigger={null} collapsible collapsed={collapsed} width={250}>
                    <div className="logo" style={{ 
                      height: '64px', 
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: collapsed ? '16px' : '20px',
                      fontWeight: 'bold',
                      background: 'rgba(255, 255, 255, 0.1)',
                      margin: '16px 0',
                      overflow: 'hidden'
                    }}>
                      {collapsed ? 'SaaS' : '智能制造 SaaS 平台'}
                    </div>
                    
                    <Menu
                      theme="dark"
                      mode="inline"
                      defaultSelectedKeys={['1']}
                      items={[
                        {
                          key: '1',
                          icon: <DashboardOutlined />,
                          label: '仪表盘',
                          path: '/admin/dashboard',
                        },
                        {
                          key: '2',
                          icon: <CloudServerOutlined />,
                          label: '租户管理',
                          path: '/admin/tenants',
                        },
                        {
                          key: '3',
                          icon: <TeamOutlined />,
                          label: '用户管理',
                          path: '/admin/users',
                        },
                        {
                          key: '4',
                          icon: <SafetyOutlined />,
                          label: '角色管理',
                          path: '/admin/roles',
                        },
                        {
                          key: '5',
                          icon: <SettingOutlined />,
                          label: '系统设置',
                          path: '/admin/settings',
                        },
                      ].map(item => ({
                        key: item.key,
                        icon: item.icon,
                        label: <a href={item.path}>{item.label}</a>,
                      }))}
                    />
                  </Sider>
                  
                  {/* 主内容区 */}
                  <Layout>
                    <Header
                      style={{
                        padding: 0,
                        background: token.colorBgContainer,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        boxShadow: '0 1px 4px rgba(0,21,41,.08)',
                      }}
                    >
                      {/* 左侧切换按钮 */}
                      <Button
                        type="text"
                        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        onClick={() => setCollapsed(!collapsed)}
                        style={{ fontSize: '16px', width: 64, height: 64 }}
                      />
                      
                      {/* 右侧用户信息和登出 */}
                      <div style={{ display: 'flex', alignItems: 'center', marginRight: 20 }}>
                        <span style={{ marginRight: 16 }}>
                          欢迎, {user?.first_name} {user?.last_name || user?.email}
                        </span>
                        <Button
                          type="text"
                          icon={<UserOutlined />}
                          style={{ marginRight: 16 }}
                          onClick={() => window.location.href = '/admin/profile'}
                        >
                          个人信息
                        </Button>
                        <Button 
                          type="text" 
                          danger 
                          icon={<LogoutOutlined />}
                          onClick={handleLogout}
                        >
                          退出登录
                        </Button>
                      </div>
                    </Header>
                    
                    <Content
                      style={{
                        margin: '24px 16px',
                        padding: 24,
                        minHeight: 280,
                        background: token.colorBgContainer,
                        borderRadius: token.borderRadius,
                      }}
                    >
                      {/* 内容路由 */}
                      <Routes>
                        <Route path="/admin/dashboard" element={<Dashboard />} />
                        <Route path="/admin/tenants" element={<TenantManagement />} />
                        <Route path="/admin/tenants/:tenantId/users" element={<UserManagement />} />
                        <Route path="/admin/tenants/:tenantId/roles" element={<RoleManagement />} />
                        <Route path="/admin/profile" element={<UserProfile />} />
                        <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
                      </Routes>
                    </Content>
                  </Layout>
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </Router>
    </ConfigProvider>
  );
};

export default App; 