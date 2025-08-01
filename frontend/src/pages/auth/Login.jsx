import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Form,
  Input,
  Button,
  Checkbox,
  Typography,
  Card,
  message,
  Space,
  Divider,
  Select,
  Tabs,
  Row,
  Col,
  Alert
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  LoginOutlined,
  SafetyOutlined,
  BuildOutlined,
  GlobalOutlined
} from '@ant-design/icons';
import { useApi } from '../../hooks/useApi';
import styled from 'styled-components';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

// Styled components
const LoginContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1890ff 0%, #001529 100%);
  padding: 20px;
`;

const StyledCard = styled(Card)`
  width: 480px;
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(0, 21, 41, 0.12);
  overflow: hidden;
`;

const Logo = styled.div`
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(120deg, #1890ff, #096dd9);
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 8px;
`;

const TenantBadge = styled.div`
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background: rgba(24, 144, 255, 0.1);
  border-radius: 16px;
  color: #1890ff;
  margin-top: 8px;
  font-size: 14px;
`;

// Main Login component
const Login = () => {
  const [loading, setLoading] = useState(false);
  const [currentTenant, setCurrentTenant] = useState(null);
  const [loginMode, setLoginMode] = useState('tenant'); // 'tenant' or 'admin'
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const location = useLocation();
  const api = useApi();

  // 检测当前租户信息（基于域名）
  useEffect(() => {
    const detectTenant = () => {
      // 从URL获取租户信息，格式为 tenant.domain.com 或 domain.com/tenant/login
      const hostname = window.location.hostname;
      const pathParts = window.location.pathname.split('/');
      
      // 检查是否为管理员平台域名
      if (hostname === 'admin.kylinking.com' || hostname === 'localhost' || hostname === '127.0.0.1') {
        setLoginMode('admin');
        return;
      }
      
      // 检查子域名格式，例如 tenant-name.kylinking.com
      const hostParts = hostname.split('.');
      if (hostParts.length > 2 && hostParts[0] !== 'www' && hostParts[0] !== 'admin') {
        setCurrentTenant({
          name: hostParts[0],
          slug: hostParts[0],
          domain: hostname
        });
        return;
      }
      
      // 检查URL路径格式，例如 kylinking.com/tenant-name/login
      if (pathParts.length > 1 && pathParts[1] !== 'login' && pathParts[1] !== 'admin') {
        setCurrentTenant({
          name: pathParts[1],
          slug: pathParts[1],
          domain: `${pathParts[1]}.${hostname}`
        });
        return;
      }
      
      // 默认显示租户登录，但不预设租户
      setLoginMode('tenant');
    };
    
    detectTenant();
  }, [location]);

  // 登录处理函数
  const onFinish = async (values) => {
    setLoading(true);
    try {
      // 记录登录尝试
      message.loading('正在登录...', 0);
      
      // 根据登录模式选择合适的登录端点
      const endpoint = loginMode === 'admin' ? '/auth/admin-login' : '/auth/login';
      
      // 调用登录API
      const result = await api.login(values.email, values.password, currentTenant?.slug, endpoint);
      
      message.destroy();
      
      if (result && result.access_token) {
        // 验证用户权限与登录模式是否匹配
        const user = result.user;
        
        if (loginMode === 'admin') {
          // 平台管理员登录模式：验证用户是否有超级管理员权限
          if (!user.is_superadmin) {
            message.error('此账号没有超级管理员权限，请使用租户登录');
            return;
          }
          message.success('登录成功！');
          navigate('/dashboard');
        } else {
          // 租户登录模式：验证用户是否为普通租户用户
          if (user.is_superadmin) {
            message.error('超级管理员请使用平台管理员登录入口');
            return;
          }
          message.success('登录成功！');
          navigate('/dashboard');
        }
      } else {
        message.error('登录失败，服务器返回无效数据');
      }
    } catch (error) {
      message.destroy();
      
      // 不同错误状态的处理
      if (error.response) {
        const { status, data } = error.response;
        switch (status) {
          case 401:
            message.error('用户名或密码错误');
            break;
          case 403:
            if (loginMode === 'admin') {
              message.error('此账号没有管理员权限，请使用租户登录');
            } else {
              message.error('账户已被禁用或无访问权限');
            }
            break;
          case 429:
            message.error('登录尝试次数过多，请稍后再试');
            break;
          default:
            message.error(data?.message || '登录失败，请稍后重试');
        }
      } else if (error.request) {
        message.error('网络连接失败，请检查网络设置');
      } else {
        message.error('登录过程中出现未知错误');
      }
    } finally {
      setLoading(false);
    }
  };

  // 切换登录模式
  const handleModeChange = (mode) => {
    setLoginMode(mode);
    form.resetFields();
  };

  // 定义Tabs项
  const tabItems = [
    {
      key: 'tenant',
      label: '租户登录'
    },
    {
      key: 'admin',
      label: '平台管理员'
    }
  ];

  return (
    <LoginContainer>
      <StyledCard styles={{ body: { padding: '32px 40px' } }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Space align="center" direction="vertical" size={12}>
            <Logo>
              <SafetyOutlined style={{ color: 'white', fontSize: 36 }} />
            </Logo>
            <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
              {loginMode === 'admin' ? '管理员后台' : '薄膜智能管理平台'}
            </Title>
            <Text type="secondary">
              {loginMode === 'admin' ? '平台超级管理员入口' : '企业租户登录入口'}
            </Text>
            
            {currentTenant && (
              <TenantBadge>
                <BuildOutlined style={{ marginRight: 8 }} />
                {currentTenant.name}
              </TenantBadge>
            )}
          </Space>
        </div>
        
        <Tabs 
          activeKey={loginMode} 
          onChange={handleModeChange}
          centered
          style={{ marginBottom: 24 }}
          items={tabItems}
        />
        
        {loginMode === 'admin' && (
          <Alert
            message="管理员登录入口"
            description="此入口仅限平台超级管理员访问，用于管理整个平台的租户与系统设置。"
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}
        
        <Form
          name="login"
          form={form}
          initialValues={{ 
            remember: true,
            email: loginMode === 'admin' ? 'admin@kylinking.com' : '',
            password: loginMode === 'admin' ? 'admin123' : ''
          }}
          onFinish={onFinish}
          size="large"
          layout="vertical"
        >
          {loginMode === 'tenant' && !currentTenant && (
            <Alert
              message="租户自动识别"
              description="系统将根据您的邮箱地址或当前域名自动识别您所属的租户。"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
          )}
          
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱!' },
              { type: 'email', message: '请输入有效的邮箱地址!' }
            ]}
          >
            <Input 
              prefix={<UserOutlined className="site-form-item-icon" />} 
              placeholder="邮箱"
              autoComplete="username"
              size="large"
            />
          </Form.Item>
          
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password
              prefix={<LockOutlined className="site-form-item-icon" />}
              placeholder="密码"
              autoComplete="current-password"
              size="large"
            />
          </Form.Item>
          
          <Form.Item>
            <Row justify="space-between">
              <Col>
                <Form.Item name="remember" valuePropName="checked" noStyle>
                  <Checkbox>记住我</Checkbox>
                </Form.Item>
              </Col>
              <Col>
                <a href="#" style={{ float: 'right' }}>
                  忘记密码?
                </a>
              </Col>
            </Row>
          </Form.Item>
          
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              icon={<LoginOutlined />}
              loading={loading}
              style={{ height: 46 }}
            >
              {loginMode === 'admin' ? '管理员登录' : '登录系统'}
            </Button>
          </Form.Item>
        </Form>
        
        {loginMode === 'tenant' && (
          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <Text type="secondary">还没有企业账号? </Text>
            <a href="#contact">联系我们开通</a>
          </div>
        )}
        
        <Divider style={{ margin: '24px 0 16px' }}>
          <Text type="secondary">系统信息</Text>
        </Divider>
        
        <Text type="secondary" style={{ display: 'block', textAlign: 'center' }}>
          <GlobalOutlined style={{ marginRight: 8 }} />
          KylinKing云膜智能管理系统 v1.0.0 | Copyright © {new Date().getFullYear()}
        </Text>
      </StyledCard>
    </LoginContainer>
  );
};

export default Login; 