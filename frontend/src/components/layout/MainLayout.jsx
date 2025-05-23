import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Badge } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  AppstoreOutlined,
  UserOutlined,
  SettingOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  LogoutOutlined,
  UserSwitchOutlined,
  LaptopOutlined
} from '@ant-design/icons';
import styled, { css } from 'styled-components';
import { useApi } from '../../hooks/useApi';

const { Header, Sider, Content } = Layout;

// Root layout container
const RootLayout = styled(Layout)`
  min-height: 100vh;
`;

// Sidebar styles
const SidebarLayout = styled(Sider)`
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 10;
  height: 100vh;
  overflow: hidden auto;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  
  .ant-layout-sider-children {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
`;

// Logo container
const LogoContainer = styled.div`
  height: 64px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
`;

// Logo text
const LogoText = styled.div`
  color: white;
  font-size: ${props => props.$collapsed ? '1rem' : '1.25rem'};
  font-weight: bold;
  text-align: center;
  white-space: nowrap;
  transition: all 0.2s;
`;

// Main content area that adjusts based on sidebar state
const MainContentLayout = styled(Layout)`
  margin-left: ${props => props.$collapsed ? '80px' : '200px'};
  transition: margin-left 0.2s;
`;

// Header styles
const HeaderWrapper = styled(Header)`
  padding: 0;
  background: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 9;
  width: 100%;
`;

// Collapse button
const CollapseButton = styled.div`
  padding: 0 24px;
  font-size: 18px;
  line-height: 64px;
  cursor: pointer;
  transition: color 0.3s;
  
  &:hover {
    color: #1890ff;
  }
`;

// Header controls
const HeaderControls = styled.div`
  display: flex;
  align-items: center;
  padding-right: 24px;
`;

// Header icon button
const IconButton = styled.div`
  padding: 0 12px;
  cursor: pointer;
  font-size: 18px;
  
  &:hover {
    color: #1890ff;
  }
`;

// User info container
const UserInfo = styled.div`
  display: flex;
  align-items: center;
  margin-left: 12px;
  cursor: pointer;
  
  .username {
    margin-left: 8px;
    font-weight: 500;
  }
`;

// Main content wrapper
const ContentWrapper = styled(Content)`
  margin: 24px;
  flex: 1;
  overflow: auto;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 0;
`;

// Inner content container
const ContentContainer = styled.div`
  padding: 24px;
  background: white;
  border-radius: 4px;
  min-height: calc(100vh - 64px - 48px);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
`;

const MainLayout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const api = useApi();
  const user = api.getUser();
  const tenant = api.getCurrentTenant();
  
  // Toggle sidebar collapsed state
  const toggleCollapsed = () => {
    setCollapsed(!collapsed);
  };
  
  // Menu items configuration
  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
      path: '/dashboard',
    },
    // Show system management menu only for superadmin users
    user?.is_superadmin && {
      key: 'admin',
      icon: <AppstoreOutlined />,
      label: '平台管理',
      children: [
        {
          key: 'tenants',
          label: '租户管理',
          path: '/admin/tenants',
        },
        {
          key: 'modules',
          label: '模块管理',
          path: '/admin/modules',
        },
      ],
    },
    // Show system management for both admin and superadmin
    (user?.is_admin || user?.is_superadmin) && {
      key: 'system',
      icon: <SettingOutlined />,
      label: '系统管理',
      path: '/admin/system',
    },
    {
      key: 'production',
      icon: <LaptopOutlined />,
      label: '生产管理',
      children: [
        {
          key: 'schedule',
          label: '生产计划',
          path: '/production/schedule',
        },
        {
          key: 'monitor',
          label: '生产监控',
          path: '/production/monitor',
        },
      ],
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
      path: '/settings',
    },
    {
      key: 'baseArchive',
      icon: <AppstoreOutlined />,
      label: '基础档案',
      children: [
        {
          key: 'baseData',
          label: '基础数据',
          path: '/base-archive/base-data',
        },
        {
          key: 'productionManagement',
          label: '生产管理',
          path: '/base-archive/production-management',
        },
        {
          key: 'financialManagement',
          label: '财务管理',
          path: '/base-archive/financial-management',
        },
      ],
    },
  ];
  
  // User dropdown menu items
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      key: 'switch',
      icon: <UserSwitchOutlined />,
      label: '切换租户',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
    },
  ];
  
  // Notification dropdown items
  const notificationItems = [
    {
      key: 'notification1',
      label: '设备MCL-235需要维护',
    },
    {
      key: 'notification2',
      label: '今日生产计划已完成85%',
    },
    {
      key: 'notification3',
      label: '系统将于今晚23:00进行维护',
    },
  ];

  // Handle menu click
  const handleMenuClick = ({ key }) => {
    const findPath = (items) => {
      for (const item of items) {
        if (item.key === key) {
          return item.path;
        }
        if (item.children) {
          const path = findPath(item.children);
          if (path) return path;
        }
      }
      return null;
    };

    const path = findPath(menuItems);
    if (path) {
      navigate(path);
    }
  };
  
  // Handle user menu actions
  const handleUserMenuClick = ({ key }) => {
    if (key === 'logout') {
      api.logout();
    } else if (key === 'profile') {
      navigate('/profile');
    } else if (key === 'switch') {
      // Handle tenant switching
      navigate('/login');
    }
  };
  
  // Determine selected menu key from current path
  const selectedKey = location.pathname.split('/')[1] || 'dashboard';
  // Only show open keys when sidebar is expanded
  const openKeys = collapsed ? [] : ['admin', 'production', 'baseArchive'];

  return (
    <RootLayout>
      {/* Sidebar */}
      <SidebarLayout 
        width={200} 
        collapsible 
        collapsed={collapsed}
        trigger={null} 
        theme="dark"
      >
        <LogoContainer>
          <LogoText $collapsed={collapsed}>
            {collapsed ? 'KK' : 'KylinKing'}
          </LogoText>
        </LogoContainer>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          defaultOpenKeys={openKeys}
          style={{ flex: 1, borderRight: 0 }}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </SidebarLayout>
      
      {/* Main content area */}
      <MainContentLayout $collapsed={collapsed}>
        {/* Header */}
        <HeaderWrapper>
          <CollapseButton onClick={toggleCollapsed}>
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </CollapseButton>
          
          <HeaderControls>
            {/* Notifications */}
            <Dropdown
              menu={{ 
                items: notificationItems,
                onClick: (e) => console.log('Clicked notification', e.key),
              }}
              placement="bottomRight"
              arrow
            >
              <IconButton>
                <Badge count={3} size="small">
                  <BellOutlined style={{ fontSize: '18px' }} />
                </Badge>
              </IconButton>
            </Dropdown>
            
            {/* User menu */}
            <Dropdown
              menu={{ 
                items: userMenuItems,
                onClick: handleUserMenuClick,
              }}
              placement="bottomRight"
              arrow
            >
              <UserInfo>
                <Avatar 
                  style={{ backgroundColor: '#1890ff' }} 
                  icon={<UserOutlined />} 
                />
                <span className="username">
                  {user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email : '管理员'}
                  {tenant && <small style={{ display: 'block', fontSize: '12px' }}>{tenant.name}</small>}
                </span>
              </UserInfo>
            </Dropdown>
          </HeaderControls>
        </HeaderWrapper>
        
        {/* Page content */}
        <ContentWrapper>
          <ContentContainer>
            {children}
          </ContentContainer>
        </ContentWrapper>
      </MainContentLayout>
    </RootLayout>
  );
};

export default MainLayout; 