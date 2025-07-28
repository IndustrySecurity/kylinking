import React, { useState, useEffect } from 'react';
import { Layout, Menu, Avatar, Dropdown, Badge } from 'antd';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
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
  LaptopOutlined,
  InboxOutlined,
  ShoppingOutlined,
  ImportOutlined,
  ExportOutlined,
  AuditOutlined,
  SwapOutlined,
  FileTextOutlined,
  TagsOutlined,
  ReloadOutlined,
  FileSyncOutlined,
  ReconciliationOutlined,
  RetweetOutlined,
  ContainerOutlined,
  RedoOutlined,
  ToolOutlined,
  CalculatorOutlined,
  DatabaseOutlined,
  BarChartOutlined
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
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #f5f5f5;
  }
  
  .username {
    margin-left: 8px;
    font-weight: 500;
    line-height: 1.2;
    
    small {
      margin-top: 2px;
      opacity: 0.7;
    }
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

const MainLayout = () => {
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
  
  // 动态获取租户模块配置
  const [tenantModules, setTenantModules] = useState([]);
  const [modulesLoading, setModulesLoading] = useState(false);

  // 获取租户模块配置
  const fetchTenantModules = async () => {
    if (!user?.tenant_id) return;
    
    setModulesLoading(true);
    try {
      const response = await api.get('/tenant/modules/');
      if (response.data.success) {
        setTenantModules(response.data.data);
      }
    } catch (error) {
      console.error('获取租户模块配置失败:', error);
    } finally {
      setModulesLoading(false);
    }
  };

  // 在用户信息加载后获取模块配置
  useEffect(() => {
    if (user?.tenant_id) {
      fetchTenantModules();
    }
  }, [user?.tenant_id]);

  // 根据模块配置生成菜单项
  const generateMenuItems = () => {
    const baseItems = [
      {
        key: 'dashboard',
        icon: <DashboardOutlined />,
        label: '仪表盘',
        path: '/dashboard',
      }
    ];

    // 管理员菜单
    if (user?.is_superadmin) {
      baseItems.push({
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
      });
    }

    if (user?.is_admin || user?.is_superadmin) {
      baseItems.push({
        key: 'system',
        icon: <SettingOutlined />,
        label: '系统管理',
        path: '/admin/system',
      });
    }

    // 根据租户模块配置动态生成菜单
    const enabledModules = tenantModules.filter(module => module.is_enabled && module.is_visible);
    
    // 生产管理模块
    const productionModule = enabledModules.find(m => m.category === 'production');
    if (productionModule) {
      baseItems.push({
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
      });
    }

    // 销售管理模块
    const salesModule = enabledModules.find(m => m.category === 'sales');
    if (salesModule) {
      baseItems.push({
        key: 'salesManagement',
        icon: <ShoppingOutlined />,
        label: '销售管理',
        path: '/business/sales-management',
      });
    }

    // 仓库管理模块
    const warehouseModule = enabledModules.find(m => m.category === 'warehouse');
    if (warehouseModule) {
      baseItems.push({
        key: 'warehouseManagement',
        icon: <DatabaseOutlined />,
        label: '仓库管理',
        children: [
          {
            key: 'inventoryOverview',
            icon: <BarChartOutlined />, 
            label: '库存总览',
            path: '/business/inventory-overview',
          },
          {
            key: 'materialWarehouse',
            icon: <InboxOutlined />, 
            label: '材料仓库',
            path: '/business/material-warehouse',
          },
          {
            key: 'finishedGoodsWarehouse',
            icon: <ContainerOutlined />, 
            label: '成品仓库',
            path: '/business/finished-goods-warehouse',
          },
        ],
      });
    }

    // 基础档案模块
    const masterDataModule = enabledModules.find(m => m.category === 'master_data');
    if (masterDataModule) {
      baseItems.push({
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
            key: 'productionData',
            label: '生产档案',
            path: '/base-archive/production-data',
          },
          {
            key: 'financialManagement',
            label: '财务管理',
            path: '/base-archive/financial-management',
          },
        ],
      });
    }

    return baseItems;
  };

  const menuItems = generateMenuItems();
  
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
  const getSelectedKey = () => {
    const pathname = location.pathname;
    
    // Helper function to find matching menu item by path
    const findMenuKey = (items, path) => {
      for (const item of items) {
        if (item.path === path) {
          return item.key;
        }
        if (item.children) {
          const childKey = findMenuKey(item.children, path);
          if (childKey) return childKey;
        }
      }
      return null;
    };
    
    // First try exact match
    let key = findMenuKey(menuItems, pathname);
    if (key) {
      return key;
    }
    
    // Then try partial matches for nested paths
    const pathSegments = pathname.split('/');
    for (let i = pathSegments.length; i > 0; i--) {
      const partialPath = pathSegments.slice(0, i).join('/');
      key = findMenuKey(menuItems, partialPath);
      if (key) {
        return key;
      }
    }
    
    return 'dashboard';
  };
  
  const selectedKey = getSelectedKey();
  
  // Determine which parent menus should be open
  const getOpenKeys = () => {
    if (collapsed) return [];
    
    const pathname = location.pathname;
    const openKeys = [];
    
    if (pathname.startsWith('/admin')) openKeys.push('admin');
    if (pathname.startsWith('/production')) openKeys.push('production');
    if (pathname.startsWith('/business')) openKeys.push('warehouseManagement');
    if (pathname.startsWith('/base-archive')) openKeys.push('baseArchive');
    
    return openKeys;
  };
  
  const openKeys = getOpenKeys();

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
                onClick: (e) => {
                  // Handle notification click
                },
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
                  {user ? (user.first_name || user.last_name ? `${user.first_name || ''} ${user.last_name || ''}`.trim() : user.email) : '管理员'}
                  {tenant && <small style={{ display: 'block', fontSize: '12px', color: '#666' }}>{tenant.name}</small>}
                </span>
              </UserInfo>
            </Dropdown>
          </HeaderControls>
        </HeaderWrapper>
        
        {/* Page content */}
        <ContentWrapper>
          <ContentContainer>
            <Outlet />
          </ContentContainer>
        </ContentWrapper>
      </MainContentLayout>
    </RootLayout>
  );
};

export default MainLayout; 