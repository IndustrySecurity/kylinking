import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Form,
  Input,
  Button,
  Checkbox,
  Typography,
  Card,
  message,
  Space,
  Spin,
  Divider
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  LoginOutlined,
  SafetyOutlined
} from '@ant-design/icons';
import { useApi } from '../../hooks/useApi';

const { Title, Text } = Typography;

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const api = useApi();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await api.login(values.email, values.password);
      message.success('登录成功');
      navigate('/admin/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      message.error('登录失败: ' + (error.response?.data?.message || '请检查您的邮箱和密码'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container" style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1890ff 0%, #001529 100%)',
      backgroundSize: 'cover',
      padding: '20px'
    }}>
      <Card
        style={{
          width: 450,
          borderRadius: 8,
          boxShadow: '0 8px 24px rgba(0, 21, 41, 0.12)',
          overflow: 'hidden'
        }}
        bodyStyle={{ padding: '32px 40px' }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Space align="center" direction="vertical" size={16}>
            <div className="logo" style={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              background: 'linear-gradient(120deg, #1890ff, #096dd9)',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              marginBottom: 8
            }}>
              <SafetyOutlined style={{ color: 'white', fontSize: 32 }} />
            </div>
            <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
              智能制造 SaaS 平台
            </Title>
            <Text type="secondary">
              登录后台管理系统
            </Text>
          </Space>
        </div>
        
        <Divider style={{ marginBottom: 32 }} />
        
        <Form
          name="login"
          form={form}
          initialValues={{ remember: true }}
          onFinish={onFinish}
          size="large"
          layout="vertical"
        >
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
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>记住我</Checkbox>
            </Form.Item>
            
            <a href="#" style={{ float: 'right' }}>
              忘记密码?
            </a>
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
              登录
            </Button>
          </Form.Item>
        </Form>
        
        <Divider style={{ margin: '24px 0 16px' }}>
          <Text type="secondary">系统信息</Text>
        </Divider>
        
        <Text type="secondary" style={{ display: 'block', textAlign: 'center' }}>
          版本: v1.0.0 | Copyright © {new Date().getFullYear()} 智能制造 SaaS 平台
        </Text>
      </Card>
    </div>
  );
};

export default Login; 