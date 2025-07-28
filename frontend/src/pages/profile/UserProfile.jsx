import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Avatar,
  Typography,
  Descriptions,
  Tag,
  Tabs,
  Button,
  Space,
  Modal,
  Form,
  Input,
  message,
  Spin
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  SafetyOutlined,
  KeyOutlined,
  EditOutlined,
  SaveOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';
import { useApi } from '../../hooks/useApi';

const { Title, Text } = Typography;

const UserProfile = () => {
  const api = useApi();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [tenant, setTenant] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  // 获取用户信息
  useEffect(() => {
    const fetchUserInfo = async () => {
      setLoading(true);
      try {
        // 从API获取完整的用户信息
        let userInfo;
        try {
          const response = await api.get('/auth/me');
          userInfo = response.data.user;
        } catch (apiError) {
          // 如果API不可用，使用本地存储的用户信息
          userInfo = api.getUser();
        }
        
        const tenantInfo = api.getCurrentTenant();
        
        setUser(userInfo);
        setTenant(tenantInfo);
      } catch (error) {
        message.error('获取用户信息失败');
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, []);

  // 当编辑模态框打开时，设置表单数据
  useEffect(() => {
    if (editModalVisible && user) {
      form.setFieldsValue({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email
      });
    }
  }, [editModalVisible, user, form]);

  // 保存个人信息
  const handleSaveProfile = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      
      try {
        // 调用API更新个人信息
        await api.put('/auth/profile', values);
        message.success('个人信息更新成功，重新登录后生效');
      } catch (apiError) {
        // 如果API不可用，只更新本地状态
        message.info('更新失败，请稍后重试');
      }
      
      // 更新本地状态
      const updatedUser = { ...user, ...values };
      setUser(updatedUser);
      
      setEditModalVisible(false);
    } catch (error) {
      message.error('表单验证失败，请检查输入');
    } finally {
      setLoading(false);
    }
  };

  // 修改密码
  const handleChangePassword = async () => {
    try {
      const values = await passwordForm.validateFields();
      setLoading(true);
      
      try {
        // 调用修改密码API
        await api.put('/auth/change-password', {
          current_password: values.current_password,
          new_password: values.new_password
        });
        
        message.success('密码修改成功');
        setPasswordModalVisible(false);
        passwordForm.resetFields();
      } catch (apiError) {
        if (apiError.response?.status === 400) {
          message.error(apiError.response.data.message || '密码修改失败');
        } else {
          message.error('密码修改失败，请重试');
        }
      }
    } catch (error) {
      message.error('表单验证失败，请检查输入');
    } finally {
      setLoading(false);
    }
  };

  // 基本信息表单
  const BasicInfoForm = () => (
    <div>
      <Row gutter={16}>
        <Col span={12}>
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontWeight: 'bold', marginBottom: 8 }}>姓</div>
            <div>{user?.first_name || '-'}</div>
          </div>
        </Col>
        <Col span={12}>
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontWeight: 'bold', marginBottom: 8 }}>名</div>
            <div>{user?.last_name || '-'}</div>
          </div>
        </Col>
      </Row>
      
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontWeight: 'bold', marginBottom: 8 }}>邮箱</div>
        <div>{user?.email || '-'}</div>
      </div>
      
      <Button 
        type="primary" 
        icon={<EditOutlined />}
        onClick={() => setEditModalVisible(true)}
      >
        编辑信息
      </Button>
    </div>
  );

  // 安全设置
  const SecuritySettings = () => (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Card size="small">
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={5}>修改密码</Title>
            <Text type="secondary">定期更换密码可以提高账户安全性</Text>
          </Col>
          <Col>
            <Button 
              type="primary" 
              icon={<KeyOutlined />}
              onClick={() => setPasswordModalVisible(true)}
            >
              修改密码
            </Button>
          </Col>
        </Row>
      </Card>
    </Space>
  );

  // Tabs配置
  const tabItems = [
    {
      key: 'basic',
      label: (
        <span>
          <UserOutlined />
          基本信息
        </span>
      ),
      children: <BasicInfoForm />
    },
    {
      key: 'security',
      label: (
        <span>
          <SafetyOutlined />
          安全设置
        </span>
      ),
      children: <SecuritySettings />
    }
  ];

  if (loading && !user) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="user-profile">
      {/* 返回按钮 */}
      <div style={{ marginBottom: 16 }}>
        <Button 
          type="default" 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/dashboard')}
        >
          返回仪表盘
        </Button>
      </div>
      
      <Row gutter={[24, 24]}>
        {/* 用户基本信息卡片 */}
        <Col xs={24} lg={8}>
          <Card>
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Avatar 
                size={80} 
                icon={<UserOutlined />} 
                style={{ backgroundColor: '#1890ff', marginBottom: 16 }}
              />
              <Title level={3} style={{ margin: '8px 0' }}>
                {user ? `${user.first_name || ''}${user.last_name || ''}` : '用户'}
              </Title>
              <Text type="secondary">{user?.email}</Text>
              {tenant && (
                <div style={{ marginTop: 8 }}>
                  <Tag color="blue">{tenant.name}</Tag>
                </div>
              )}
            </div>
            
            <Descriptions column={1} size="small">
              <Descriptions.Item label="用户ID">{user?.id}</Descriptions.Item>
              <Descriptions.Item label="邮箱">
                <MailOutlined style={{ marginRight: 8 }} />
                {user?.email}
              </Descriptions.Item>
              <Descriptions.Item label="角色">
                {user?.is_superadmin ? '超级管理员' : user?.is_admin ? '管理员' : '普通用户'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 详细信息标签页 */}
        <Col xs={24} lg={16}>
          <Card>
            <Tabs defaultActiveKey="basic" items={tabItems} />
          </Card>
        </Col>
      </Row>

      {/* 编辑个人信息模态框 */}
      <Modal
        title="编辑个人信息"
        open={editModalVisible}
        onOk={handleSaveProfile}
        onCancel={() => {
          setEditModalVisible(false);
          form.resetFields();
        }}
        okText="保存"
        cancelText="取消"
        confirmLoading={loading}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="first_name"
            label="姓"
            rules={[{ required: true, message: '请输入姓' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="请输入姓" />
          </Form.Item>
          
          <Form.Item
            name="last_name"
            label="名"
            rules={[{ required: true, message: '请输入名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="请输入名" />
          </Form.Item>
          
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="请输入邮箱" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 修改密码模态框 */}
      <Modal
        title="修改密码"
        open={passwordModalVisible}
        onOk={handleChangePassword}
        onCancel={() => {
          setPasswordModalVisible(false);
          passwordForm.resetFields();
        }}
        okText="确认修改"
        cancelText="取消"
        confirmLoading={loading}
      >
        <Form
          form={passwordForm}
          layout="vertical"
        >
          <Form.Item
            name="current_password"
            label="当前密码"
            rules={[
              { required: true, message: '请输入当前密码' },
              { min: 6, message: '密码长度至少为6个字符' }
            ]}
          >
            <Input.Password placeholder="请输入当前密码" />
          </Form.Item>
          
          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码长度至少为6个字符' }
            ]}
          >
            <Input.Password placeholder="请输入新密码" />
          </Form.Item>
          
          <Form.Item
            name="confirm_password"
            label="确认新密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不匹配'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="请确认新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserProfile; 