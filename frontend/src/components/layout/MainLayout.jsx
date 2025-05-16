import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, theme } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  SettingOutlined,
  UserOutlined,
  TeamOutlined,
  BarChartOutlined,
  LogoutOutlined,
  AppstoreOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const { Header, Sider, Content } = Layout;

const StyledLayout = styled(Layout)`
  min-height: 100vh;
`;

const Logo = styled.div`
  height: 64px;
  padding: 16px;
  color: white;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
  background: ${props => props.theme.gradientPrimary};
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`;

const StyledHeader = styled(Header)`
  padding: 0 24px;
  background: white;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const StyledContent = styled(Content)`
  margin: 24px;
  padding: 24px;
  background: white;
  border-radius: 8px;
  min-height: 280px;
`;

const MainLayout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = theme.useToken();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: 'admin',
      icon: <AppstoreOutlined />,
      label: '系统管理',
      children: [
        {
          key: '/admin/tenants',
          icon: <TeamOutlined />,
          label: '租户管理',
        },
        {
          key: '/admin/users',
          icon: <UserOutlined />,
          label: '用户管理',
        },
      ],
    },
    {
      key: '/production',
      icon: <BarChartOutlined />,
      label: '生产管理',
    },
    {
      key: '/equipment',
      icon: <SettingOutlined />,
      label: '设备管理',
    },
    {
      key: '/quality',
      icon: <BarChartOutlined />,
      label: '质量管理',
    },
    {
      key: '/inventory',
      icon: <BarChartOutlined />,
      label: '仓储管理',
    },
    {
      key: '/employees',
      icon: <TeamOutlined />,
      label: '人员管理',
    },
  ];

  const userMenu = (
    <Menu
      items={[
        {
          key: 'profile',
          icon: <UserOutlined />,
          label: '个人信息',
        },
        {
          key: 'settings',
          icon: <SettingOutlined />,
          label: '系统设置',
        },
        {
          type: 'divider',
        },
        {
          key: 'logout',
          icon: <LogoutOutlined />,
          label: '退出登录',
        },
      ]}
    />
  );

  return (
    <StyledLayout>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        theme="light"
        style={{
          boxShadow: '2px 0 8px 0 rgba(29,35,41,.05)',
        }}
      >
        <Logo>
          {collapsed ? 'KK' : 'KylinKing云膜智能管理系统'}
        </Logo>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['admin']}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <StyledHeader>
          {React.createElement(
            collapsed ? MenuUnfoldOutlined : MenuFoldOutlined,
            {
              className: 'trigger',
              onClick: () => setCollapsed(!collapsed),
              style: { fontSize: '18px', cursor: 'pointer' },
            }
          )}
          <Dropdown overlay={userMenu} placement="bottomRight">
            <div style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span style={{ marginLeft: 8 }}>管理员</span>
            </div>
          </Dropdown>
        </StyledHeader>
        <StyledContent>
          {children}
        </StyledContent>
      </Layout>
    </StyledLayout>
  );
};

export default MainLayout; 