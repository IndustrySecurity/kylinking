import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Space,
  Button,
  Tag,
  Modal,
  Form,
  Input,
  Switch,
  message,
  Popconfirm,
  Typography,
  Tooltip,
  Row,
  Col,
  Statistic,
  Divider,
  Badge,
  Select,
  Avatar,
  Breadcrumb,
  Progress
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  SearchOutlined,
  ReloadOutlined,
  UserOutlined,
  LockOutlined,
  TeamOutlined,
  SafetyOutlined,
  MailOutlined,
  KeyOutlined,
  ArrowLeftOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { useApi } from '../../hooks/useApi';

const { Title, Text } = Typography;
const { Option } = Select;
const { Password } = Input;

const UserManagement = () => {
  const { tenantId } = useParams();
  const [users, setUsers] = useState([]);
  const [tenant, setTenant] = useState(null);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [searchEmail, setSearchEmail] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [filterActive, setFilterActive] = useState(null);
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const api = useApi();
  const navigate = useNavigate();

  // 获取用户列表
  const fetchUsers = async (page = 1, pageSize = 10, email = '', active = null) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page,
        per_page: pageSize
      });
      
      if (email) {
        params.append('email', email);
      }
      
      if (active !== null) {
        params.append('active', active);
      }
      
      console.log(`Fetching users from: /admin/tenants/${tenantId}/users?${params.toString()}`);
      const response = await api.get(`/admin/tenants/${tenantId}/users?${params.toString()}`);
      console.log('Users response:', response.data);
      setUsers(response.data.users);
      setPagination({
        current: response.data.page,
        pageSize: response.data.per_page,
        total: response.data.total
      });
    } catch (error) {
      console.error('Error fetching users:', error.response || error);
      message.error('获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取租户信息
  const fetchTenant = async () => {
    try {
      console.log(`Fetching tenant from: /admin/tenants/${tenantId}`);
      const response = await api.get(`/admin/tenants/${tenantId}`);
      console.log('Tenant response:', response.data);
      setTenant(response.data.tenant);
    } catch (error) {
      console.error('Error fetching tenant:', error.response || error);
      message.error('获取租户信息失败');
    }
  };

  // 获取角色列表
  const fetchRoles = async () => {
    try {
      console.log(`Fetching roles from: /admin/tenants/${tenantId}/roles`);
      const response = await api.get(`/admin/tenants/${tenantId}/roles`);
      console.log('Roles response:', response.data);
      setRoles(response.data.roles);
    } catch (error) {
      console.error('Error fetching roles:', error.response || error);
    }
  };

  // 首次加载
  useEffect(() => {
    fetchUsers();
    fetchTenant();
    fetchRoles();
  }, [tenantId]);

  // 表格变化处理
  const handleTableChange = (pagination) => {
    fetchUsers(pagination.current, pagination.pageSize, searchEmail, filterActive);
  };

  // 搜索处理
  const handleSearch = () => {
    fetchUsers(1, pagination.pageSize, searchEmail, filterActive);
  };

  // 重置搜索
  const handleReset = () => {
    setSearchEmail('');
    setFilterActive(null);
    fetchUsers(1, pagination.pageSize, '', null);
  };

  // 状态筛选
  const handleStatusChange = (value) => {
    setFilterActive(value);
    fetchUsers(1, pagination.pageSize, searchEmail, value);
  };

  // 打开新建用户模态框
  const showCreateModal = () => {
    setEditingUser(null);
    form.resetFields();
    form.setFieldsValue({
      is_active: true,
      is_admin: false
    });
    setModalVisible(true);
  };

  // 打开编辑用户模态框
  const showEditModal = (user) => {
    setEditingUser(user);
    form.setFieldsValue({
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      is_active: user.is_active,
      is_admin: user.is_admin,
      roles: []
    });
    setModalVisible(true);
  };

  // 打开修改密码模态框
  const showPasswordModal = (user) => {
    setEditingUser(user);
    passwordForm.resetFields();
    setPasswordModalVisible(true);
  };

  // 关闭模态框
  const handleCancel = () => {
    setModalVisible(false);
  };

  // 关闭密码模态框
  const handlePasswordCancel = () => {
    setPasswordModalVisible(false);
  };

  // 提交用户表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      console.log('Form values being submitted:', values);
      
      if (editingUser) {
        // 更新用户
        console.log(`Updating user at: /admin/tenants/${tenantId}/users/${editingUser.id}`);
        const response = await api.put(`/admin/tenants/${tenantId}/users/${editingUser.id}`, values);
        console.log('Update user response:', response.data);
        message.success('用户更新成功');
      } else {
        // 创建用户
        console.log(`Creating user at: /admin/tenants/${tenantId}/users`);
        const response = await api.post(`/admin/tenants/${tenantId}/users`, values);
        console.log('Create user response:', response.data);
        message.success('用户创建成功');
      }
      
      setModalVisible(false);
      fetchUsers(pagination.current, pagination.pageSize, searchEmail, filterActive);
    } catch (error) {
      console.error('Form submission error:', error.response || error);
      message.error('操作失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // 提交密码修改
  const handlePasswordSubmit = async () => {
    try {
      const values = await passwordForm.validateFields();
      
      await api.post(`/admin/tenants/${tenantId}/users/${editingUser.id}/reset-password`, {
        password: values.password
      });
      
      message.success('密码修改成功');
      setPasswordModalVisible(false);
    } catch (error) {
      console.error('Password reset error:', error);
      message.error('密码修改失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // 停用/启用用户
  const handleToggleUserStatus = async (user) => {
    try {
      await api.patch(`/admin/tenants/${tenantId}/users/${user.id}/toggle-status`);
      message.success(`用户已${user.is_active ? '停用' : '启用'}`);
      fetchUsers(pagination.current, pagination.pageSize, searchEmail, filterActive);
    } catch (error) {
      message.error('操作失败');
      console.error('Error toggling user status:', error);
    }
  };

  // 返回租户管理页面
  const handleBackToTenants = () => {
    navigate('/admin/tenants');
  };

  // 获取密码强度
  const getPasswordStrength = (password) => {
    if (!password) return 0;
    
    let strength = 0;
    
    // 长度检查
    if (password.length >= 8) strength += 25;
    
    // 大写字母检查
    if (/[A-Z]/.test(password)) strength += 25;
    
    // 数字检查
    if (/\d/.test(password)) strength += 25;
    
    // 特殊字符检查
    if (/[^A-Za-z0-9]/.test(password)) strength += 25;
    
    return strength;
  };

  // 获取密码强度的级别和颜色
  const getPasswordStrengthLevel = (strength) => {
    if (strength >= 100) return { color: '#52c41a', text: '非常强' };
    if (strength >= 75) return { color: '#52c41a', text: '强' };
    if (strength >= 50) return { color: '#faad14', text: '中等' };
    if (strength >= 25) return { color: '#f5222d', text: '弱' };
    return { color: '#f5222d', text: '非常弱' };
  };

  // 表格列定义
  const columns = [
    {
      title: '用户信息',
      key: 'user_info',
      render: (_, record) => (
        <Space>
          <Avatar 
            style={{ 
              backgroundColor: record.is_admin ? '#722ed1' : '#1890ff',
              verticalAlign: 'middle' 
            }}
            icon={<UserOutlined />}
            size="large"
          />
          <span>
            <Text strong style={{ display: 'block' }}>{record.first_name} {record.last_name}</Text>
            <Text type="secondary">{record.email}</Text>
            {record.is_admin && (
              <Tag color="purple" style={{ marginLeft: 8 }}>管理员</Tag>
            )}
          </span>
        </Space>
      ),
    },
    {
      title: '角色',
      key: 'roles',
      render: (_, record) => (
        <>
          <Text type="secondary">无角色</Text>
        </>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Badge
          status={isActive ? 'success' : 'error'}
          text={
            <Tag color={isActive ? 'success' : 'error'} style={{ borderRadius: '20px', padding: '0 10px' }}>
              {isActive ? '活跃' : '停用'}
            </Tag>
          }
        />
      ),
      filters: [
        { text: '活跃', value: true },
        { text: '停用', value: false },
      ],
    },
    {
      title: '最后登录',
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      render: (date) => date ? new Date(date).toLocaleString() : '从未登录',
      sorter: (a, b) => {
        if (!a.last_login_at && !b.last_login_at) return 0;
        if (!a.last_login_at) return 1;
        if (!b.last_login_at) return -1;
        return new Date(b.last_login_at) - new Date(a.last_login_at);
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString(),
      sorter: (a, b) => new Date(b.created_at) - new Date(a.created_at),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              onClick={() => showEditModal(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => showEditModal(record)}
            />
          </Tooltip>
          <Tooltip title="修改密码">
            <Button 
              type="text" 
              icon={<KeyOutlined />} 
              onClick={() => showPasswordModal(record)}
            />
          </Tooltip>
          <Tooltip title={record.is_active ? "停用" : "启用"}>
            <Popconfirm
              title={`确定要${record.is_active ? '停用' : '启用'}此用户吗？`}
              onConfirm={() => handleToggleUserStatus(record)}
              okText="确定"
              cancelText="取消"
              icon={<ExclamationCircleOutlined style={{ color: record.is_active ? 'red' : 'green' }} />}
            >
              <Button 
                type="text" 
                danger={record.is_active}
                icon={record.is_active ? <DeleteOutlined /> : <UserOutlined />}
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className="user-management">
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card>
            <Breadcrumb style={{ marginBottom: 16 }}>
              <Breadcrumb.Item>
                <a onClick={handleBackToTenants}>
                  <ArrowLeftOutlined style={{ marginRight: 8 }} />
                  租户管理
                </a>
              </Breadcrumb.Item>
              <Breadcrumb.Item>{tenant?.name || '租户'} - 用户管理</Breadcrumb.Item>
            </Breadcrumb>
            
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Statistic 
                  title="租户名称" 
                  value={tenant?.name || '-'} 
                  prefix={<TeamOutlined />}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="用户总数" 
                  value={pagination.total} 
                  prefix={<UserOutlined />}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="管理员数" 
                  value={(users || []).filter(user => user.is_admin).length} 
                  prefix={<SafetyOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>
        
        <Col span={24}>
          <Card className="user-list-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <Title level={4}>用户列表</Title>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={showCreateModal}
              >
                新建用户
              </Button>
            </div>
            
            <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center' }}>
              <Input.Search
                placeholder="搜索用户邮箱"
                value={searchEmail}
                onChange={(e) => setSearchEmail(e.target.value)}
                onSearch={handleSearch}
                style={{ width: 300, marginRight: 16 }}
                enterButton={<SearchOutlined />}
              />
              <Select
                placeholder="状态筛选"
                style={{ width: 120, marginRight: 16 }}
                allowClear
                onChange={handleStatusChange}
                value={filterActive}
              >
                <Option value={true}>活跃</Option>
                <Option value={false}>停用</Option>
              </Select>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>重置</Button>
            </div>
            
            <Table
              columns={columns}
              rowKey="id"
              dataSource={users}
              pagination={pagination}
              loading={loading}
              onChange={handleTableChange}
            />
          </Card>
        </Col>
      </Row>

      {/* 用户表单模态框 */}
      <Modal
        title={editingUser ? '编辑用户' : '新建用户'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={handleCancel}
        width={700}
        maskClosable={false}
        destroyOnClose={true}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="email"
                label="电子邮箱"
                rules={[
                  { required: true, message: '请输入电子邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input 
                  placeholder="请输入电子邮箱" 
                  prefix={<MailOutlined />} 
                  disabled={editingUser !== null}
                />
              </Form.Item>
            </Col>
            
            {!editingUser && (
              <Col span={12}>
                <Form.Item
                  name="password"
                  label="密码"
                  rules={[
                    { required: !editingUser, message: '请输入密码' },
                    { min: 8, message: '密码长度至少为8个字符' },
                    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字' }
                  ]}
                >
                  <Input.Password 
                    placeholder="请输入密码" 
                    prefix={<LockOutlined />}
                  />
                </Form.Item>
              </Col>
            )}
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="first_name"
                label="名"
              >
                <Input placeholder="请输入名" prefix={<UserOutlined />} />
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="last_name"
                label="姓"
              >
                <Input placeholder="请输入姓" prefix={<UserOutlined />} />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="is_active"
                label="是否激活"
                valuePropName="checked"
              >
                <Switch checkedChildren="活跃" unCheckedChildren="停用" />
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="is_admin"
                label="是否管理员"
                valuePropName="checked"
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            name="roles"
            label="角色"
          >
            <Select
              mode="multiple"
              placeholder="请选择角色"
              style={{ width: '100%' }}
              optionFilterProp="children"
            >
              {(roles || []).map(role => (
                <Option key={role.id} value={role.id}>
                  {role.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 修改密码模态框 */}
      <Modal
        title="修改密码"
        open={passwordModalVisible}
        onOk={handlePasswordSubmit}
        onCancel={handlePasswordCancel}
        maskClosable={false}
        destroyOnClose={true}
      >
        {editingUser && (
          <Form
            form={passwordForm}
            layout="vertical"
          >
            <Form.Item style={{ marginBottom: 0 }}>
              <Text>正在为用户 <Text strong>{editingUser.email}</Text> 修改密码</Text>
            </Form.Item>
            
            <Form.Item
              name="password"
              label="新密码"
              rules={[
                { required: true, message: '请输入新密码' },
                { min: 8, message: '密码长度至少为8个字符' },
                { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字' }
              ]}
            >
              <Input.Password 
                placeholder="请输入新密码" 
                prefix={<LockOutlined />} 
                onChange={e => {
                  const strength = getPasswordStrength(e.target.value);
                  const strengthLevel = getPasswordStrengthLevel(strength);
                  passwordForm.setFieldsValue({ strength });
                }}
              />
            </Form.Item>
            
            <Form.Item
              name="strength"
              label="密码强度"
            >
              {({ getFieldValue }) => {
                const password = passwordForm.getFieldValue('password');
                const strength = getPasswordStrength(password);
                const strengthLevel = getPasswordStrengthLevel(strength);
                
                return (
                  <div>
                    <Progress 
                      percent={strength} 
                      status="active" 
                      strokeColor={strengthLevel.color}
                      size="small"
                    />
                    <Text style={{ color: strengthLevel.color }}>{strengthLevel.text}</Text>
                  </div>
                );
              }}
            </Form.Item>
            
            <Form.Item
              name="confirm"
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
              <Input.Password 
                placeholder="请再次输入新密码" 
                prefix={<LockOutlined />}
              />
            </Form.Item>
          </Form>
        )}
      </Modal>
    </div>
  );
};

export default UserManagement; 