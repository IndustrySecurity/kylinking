import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Switch,
  Select,
  message,
  Tooltip,
  Popconfirm,
  Typography,
  Card,
  Tag
} from 'antd';
import {
  UserAddOutlined,
  EditOutlined,
  DeleteOutlined,
  KeyOutlined,
  ExclamationCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { useApi } from '../../../hooks/useApi';

const { Title } = Typography;
const { Option } = Select;

// 帮助函数：添加延迟
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const UserManagement = ({ tenant, userRole }) => {
  const api = useApi();
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [rolesLoading, setRolesLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const [resetPasswordVisible, setResetPasswordVisible] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  // Fetch users when component mounts or tenant changes
  useEffect(() => {
    if (tenant?.id) {
      // 加载时先加载用户，然后再延迟加载角色
      fetchUsers();
      setTimeout(() => {
        fetchRoles();
      }, 1000); // 延迟1秒后再加载角色
    }
  }, [tenant?.id]); // Only depend on tenant ID, not the entire object

  // Fetch users list with pagination
  const fetchUsers = async (page = 1, pageSize = 10) => {
    if (!tenant?.id || loading) return;
    
    setLoading(true);
    try {
      // 添加延迟以减少API调用频率
      await sleep(500);
      
      const response = await api.get(`/api/admin/tenants/${tenant.id}/users`, {
        params: {
          page,
          per_page: pageSize
        }
      });
      
      const { users, total, pages } = response.data;
      setUsers(users);
      setPagination({
        current: page,
        pageSize: pageSize,
        total,
        pages
      });
    } catch (error) {
      message.error('获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  // Fetch roles for the tenant
  const fetchRoles = async () => {
    if (!tenant?.id || rolesLoading) return;
    
    setRolesLoading(true);
    try {
      // 添加延迟以减少API调用频率
      await sleep(600);
      
      const response = await api.get(`/api/admin/tenants/${tenant.id}/roles`);
      setRoles(response.data.roles);
    } catch (error) {
      message.error('获取角色列表失败');
    } finally {
      setRolesLoading(false);
    }
  };

  // Handle table change (pagination, filters, sorter)
  const handleTableChange = (pagination) => {
    fetchUsers(pagination.current, pagination.pageSize);
  };

  // Open modal for creating a new user
  const showCreateModal = () => {
    setCurrentUser(null);
    setModalTitle('创建新用户');
    form.resetFields();
    setModalVisible(true);
  };

  // Open modal for editing an existing user
  const showEditModal = (user) => {
    setCurrentUser(user);
    setModalTitle('编辑用户');
    
    form.setFieldsValue({
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      is_active: user.is_active,
      is_admin: user.is_admin,
      roles: user.roles?.map(role => role.id) || []
    });
    
    setModalVisible(true);
  };

  // Open modal for resetting user password
  const showResetPasswordModal = (user) => {
    setCurrentUser(user);
    passwordForm.resetFields();
    setResetPasswordVisible(true);
  };

  // Handle form submission (create or update user)
  const handleFormSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      await sleep(300); // 添加延迟
      
      if (currentUser) {
        // Update existing user
        await api.put(`/api/admin/tenants/${tenant.id}/users/${currentUser.id}`, values);
        message.success('用户更新成功');
      } else {
        // Create new user
        await api.post(`/api/admin/tenants/${tenant.id}/users`, values);
        message.success('用户创建成功');
      }
      
      setModalVisible(false);
      
      // 延迟重新加载数据
      setTimeout(() => {
        fetchUsers(pagination.current, pagination.pageSize);
      }, 500);
    } catch (error) {
      message.error('操作失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // Handle password reset submission
  const handlePasswordReset = async () => {
    try {
      const values = await passwordForm.validateFields();
      
      await sleep(300); // 添加延迟
      
      await api.post(`/api/admin/tenants/${tenant.id}/users/${currentUser.id}/reset-password`, {
        password: values.password
      });
      
      message.success('密码重置成功');
      setResetPasswordVisible(false);
    } catch (error) {
      message.error('密码重置失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // Toggle user active status
  const toggleUserStatus = async (user) => {
    try {
      await sleep(300); // 添加延迟
      
      await api.patch(`/api/admin/tenants/${tenant.id}/users/${user.id}/toggle-status`);
      message.success(`用户状态已${user.is_active ? '禁用' : '启用'}`);
      
      // 延迟重新加载数据
      setTimeout(() => {
        fetchUsers(pagination.current, pagination.pageSize);
      }, 500);
    } catch (error) {
      message.error('操作失败');
    }
  };

  // Table columns definition
  const columns = [
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '姓名',
      key: 'name',
      render: (_, record) => (
        <span>{[record.first_name, record.last_name].filter(Boolean).join(' ') || '-'}</span>
      ),
    },
    {
      title: '角色',
      key: 'roles',
      render: (_, record) => (
        <span>
          {record.is_admin ? <Tag color="blue">管理员</Tag> : null}
          {record.roles?.map(role => (
            <Tag key={role.id}>{role.name}</Tag>
          )) || '-'}
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: is_active => (
        <span style={{ color: is_active ? 'green' : 'red' }}>
          {is_active ? '启用' : '禁用'}
        </span>
      ),
    },
    {
      title: '上次登录',
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      render: (last_login_at) => last_login_at ? new Date(last_login_at).toLocaleString() : '从未登录'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="编辑用户">
            <Button 
              icon={<EditOutlined />} 
              onClick={() => showEditModal(record)} 
              type="link" 
              size="small"
            />
          </Tooltip>
          
          <Tooltip title="重置密码">
            <Button 
              icon={<KeyOutlined />} 
              onClick={() => showResetPasswordModal(record)} 
              type="link" 
              size="small"
            />
          </Tooltip>
          
          <Tooltip title={record.is_active ? '禁用用户' : '启用用户'}>
            <Popconfirm
              title={`确定要${record.is_active ? '禁用' : '启用'}该用户吗?`}
              onConfirm={() => toggleUserStatus(record)}
              okText="确定"
              cancelText="取消"
            >
              <Button 
                icon={record.is_active ? <DeleteOutlined /> : <SyncOutlined />} 
                type="link" 
                size="small"
                danger={record.is_active}
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className="user-management">
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <Title level={5}>{tenant.name} - 用户管理</Title>
        <div>
          <Button
            type="primary"
            icon={<UserAddOutlined />}
            onClick={showCreateModal}
            style={{ marginRight: '8px' }}
          >
            创建用户
          </Button>
          <Button
            icon={<SyncOutlined />}
            onClick={() => fetchUsers(1, pagination.pageSize)}
          >
            刷新
          </Button>
        </div>
      </div>

      <Table
        dataSource={users}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={pagination}
        onChange={handleTableChange}
        locale={{
          emptyText: loading ? '加载中...' : '暂无数据'
        }}
      />

      {/* User Create/Edit Modal */}
      <Modal
        title={modalTitle}
        open={modalVisible}
        onOk={handleFormSubmit}
        onCancel={() => setModalVisible(false)}
        maskClosable={false}
        okText="确定"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input disabled={!!currentUser} placeholder="请输入邮箱" />
          </Form.Item>
          
          {!currentUser && (
            <Form.Item
              name="password"
              label="密码"
              rules={[
                { required: !currentUser, message: '请输入密码' },
                { min: 6, message: '密码长度至少为6个字符' }
              ]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}
          
          <Form.Item
            name="first_name"
            label="名"
          >
            <Input placeholder="请输入名" />
          </Form.Item>
          
          <Form.Item
            name="last_name"
            label="姓"
          >
            <Input placeholder="请输入姓" />
          </Form.Item>
          
          <Form.Item
            name="is_active"
            label="启用状态"
            valuePropName="checked"
            initialValue={true}
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
          
          <Form.Item
            name="is_admin"
            label="管理员权限"
            valuePropName="checked"
            initialValue={false}
          >
            <Switch checkedChildren="是" unCheckedChildren="否" />
          </Form.Item>
          
          <Form.Item
            name="roles"
            label="角色"
          >
            <Select
              mode="multiple"
              placeholder="请选择角色"
              style={{ width: '100%' }}
            >
              {roles.map(role => (
                <Option key={role.id} value={role.id}>{role.name}</Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Password Reset Modal */}
      <Modal
        title="重置密码"
        open={resetPasswordVisible}
        onOk={handlePasswordReset}
        onCancel={() => setResetPasswordVisible(false)}
        maskClosable={false}
        okText="确定"
        cancelText="取消"
      >
        <Form
          form={passwordForm}
          layout="vertical"
        >
          <Form.Item
            name="password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码长度至少为6个字符' }
            ]}
          >
            <Input.Password placeholder="请输入新密码" />
          </Form.Item>
          
          <Form.Item
            name="confirmPassword"
            label="确认密码"
            dependencies={['password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不匹配'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement; 