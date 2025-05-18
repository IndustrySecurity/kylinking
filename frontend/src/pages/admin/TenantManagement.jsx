import React, { useState, useEffect } from 'react';
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
  Avatar
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  SearchOutlined,
  ReloadOutlined,
  UserOutlined,
  BuildOutlined,
  CloudServerOutlined,
  SettingOutlined,
  TeamOutlined,
  GlobalOutlined
} from '@ant-design/icons';
import { useApi } from '../../hooks/useApi';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';

const { Title, Text } = Typography;
const { Option } = Select;

const StyledCard = styled(Card)`
  .ant-card-head {
    border-bottom: none;
  }
`;

const TenantManagement = () => {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [stats, setStats] = useState({
    tenants: { total: 0, active: 0 },
    users: { total: 0, admin: 0 }
  });
  const [searchName, setSearchName] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [editingTenant, setEditingTenant] = useState(null);
  const [currentTenant, setCurrentTenant] = useState(null);
  const [filterStatus, setFilterStatus] = useState(null);
  const [form] = Form.useForm();
  const api = useApi();
  const navigate = useNavigate();

  // 获取租户列表
  const fetchTenants = async (page = 1, pageSize = 10, name = '', status = null) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page,
        per_page: pageSize
      });
      
      if (name) {
        params.append('name', name);
      }
      
      if (status !== null) {
        params.append('status', status);
      }
      
      const response = await api.get(`/api/admin/tenants?${params.toString()}`);
      
      if (response.data) {
        setTenants(response.data.tenants || []);
        setPagination({
          current: response.data.page || 1,
          pageSize: response.data.per_page || 10,
          total: response.data.total || 0
        });
      } else {
        message.error('获取租户列表失败');
      }
    } catch (error) {
      console.error('Error fetching tenants:', error);
      if (error.response && error.response.status === 401) {
        message.error('登录已过期，请重新登录');
        setTimeout(() => navigate('/login'), 1500);
      } else if (error.response && error.response.status === 403) {
        message.error('没有权限访问租户列表');
      } else {
        message.error('获取租户列表失败: ' + (error.message || '未知错误'));
      }
    } finally {
      setLoading(false);
    }
  };

  // 获取统计数据
  const fetchStats = async () => {
    setStatsLoading(true);
    try {
      const response = await api.get('/api/admin/stats');
      if (response.data && response.data.stats) {
        setStats(response.data.stats);
      } else {
        message.error('获取统计数据失败，返回格式不正确');
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
      if (error.response && error.response.status === 401) {
        message.error('登录已过期，请重新登录');
      } else {
        message.error('获取统计数据失败: ' + (error.message || '未知错误'));
      }
    } finally {
      setStatsLoading(false);
    }
  };

  // 首次加载
  useEffect(() => {
    fetchTenants();
    fetchStats();
  }, []);

  // 表格变化处理
  const handleTableChange = (pagination) => {
    fetchTenants(pagination.current, pagination.pageSize, searchName, filterStatus);
  };

  // 搜索处理
  const handleSearch = () => {
    fetchTenants(1, pagination.pageSize, searchName, filterStatus);
  };

  // 重置搜索
  const handleReset = () => {
    setSearchName('');
    setFilterStatus(null);
    fetchTenants(1, pagination.pageSize, '', null);
  };

  // 状态筛选
  const handleStatusChange = (value) => {
    setFilterStatus(value);
    fetchTenants(1, pagination.pageSize, searchName, value);
  };

  // 打开新建租户模态框
  const showCreateModal = () => {
    setEditingTenant(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 打开编辑租户模态框
  const showEditModal = (tenant) => {
    setEditingTenant(tenant);
    form.setFieldsValue({
      name: tenant.name,
      slug: tenant.slug,
      schema_name: tenant.schema_name,
      contact_email: tenant.contact_email,
      contact_phone: tenant.contact_phone,
      domain: tenant.domain,
      is_active: tenant.is_active
    });
    setModalVisible(true);
  };

  // 打开租户详情
  const showTenantDetail = (tenant) => {
    setCurrentTenant(tenant);
    setDetailModalVisible(true);
  };

  // 关闭模态框
  const handleCancel = () => {
    setModalVisible(false);
  };

  // 关闭详情模态框
  const handleDetailCancel = () => {
    setDetailModalVisible(false);
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      console.log("Form values being submitted:", values);
      
      if (editingTenant) {
        // 更新租户
        await api.put(`/api/admin/tenants/${editingTenant.id}`, values);
        message.success('租户更新成功');
      } else {
        // 创建租户
        await api.post('/api/admin/tenants', values);
        message.success('租户创建成功');
      }
      
      setModalVisible(false);
      fetchTenants(pagination.current, pagination.pageSize, searchName, filterStatus);
      fetchStats(); // 刷新统计
    } catch (error) {
      console.error('Form submission error:', error);
      message.error('操作失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // 停用租户
  const handleDeactivate = async (id) => {
    try {
      await api.delete(`/api/admin/tenants/${id}`);
      message.success('租户已停用');
      fetchTenants(pagination.current, pagination.pageSize, searchName, filterStatus);
      fetchStats(); // 刷新统计
    } catch (error) {
      message.error('停用租户失败');
      console.error('Error deactivating tenant:', error);
    }
  };

  // 管理租户用户
  const handleManageUsers = (tenant) => {
    navigate(`/admin/tenants/${tenant.id}/users`);
  };

  // 表格列定义
  const columns = [
    {
      title: '租户信息',
      key: 'name',
      render: (_, record) => (
        <Space>
          <Avatar 
            style={{ 
              backgroundColor: colorFromName(record.name),
              verticalAlign: 'middle' 
            }}
            size="large"
          >
            {record.name.charAt(0).toUpperCase()}
          </Avatar>
          <span>
            <Text strong style={{ display: 'block' }}>{record.name}</Text>
            <Text type="secondary">{record.slug}</Text>
          </span>
        </Space>
      ),
    },
    {
      title: '访问域名',
      key: 'domain',
      render: (_, record) => {
        const domain = record.domain || `${record.slug}.saasplatform.com`;
        return (
          <a href={`https://${domain}`} target="_blank" rel="noopener noreferrer">
            <GlobalOutlined style={{ marginRight: 8 }} />
            {domain}
          </a>
        );
      },
    },
    {
      title: '联系邮箱',
      dataIndex: 'contact_email',
      key: 'contact_email',
      render: email => <a href={`mailto:${email}`}>{email}</a>,
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
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString(),
      sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<BuildOutlined />} 
              onClick={() => showTenantDetail(record)}
            />
          </Tooltip>
          <Tooltip title="管理用户">
            <Button 
              type="text" 
              icon={<TeamOutlined />} 
              onClick={() => handleManageUsers(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => showEditModal(record)}
            />
          </Tooltip>
          <Tooltip title="停用">
            <Popconfirm
              title="确定要停用此租户吗？"
              description="停用后租户将无法访问系统。"
              onConfirm={() => handleDeactivate(record.id)}
              okText="确定"
              cancelText="取消"
              icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
            >
              <Button 
                type="text" 
                danger 
                icon={<DeleteOutlined />} 
                disabled={!record.is_active}
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 生成基于租户名称的颜色
  const colorFromName = (name) => {
    const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96'];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  return (
    <div className="tenant-management">
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card className="stats-card" loading={statsLoading}>
            <Row gutter={48}>
              <Col span={6}>
                <Statistic 
                  title="总租户数" 
                  value={stats.tenants.total} 
                  prefix={<CloudServerOutlined />} 
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={6}>
                <Statistic 
                  title="活跃租户" 
                  value={stats.tenants.active} 
                  prefix={<CloudServerOutlined />} 
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={6}>
                <Statistic 
                  title="总用户数" 
                  value={stats.users.total} 
                  prefix={<UserOutlined />} 
                  valueStyle={{ color: '#faad14' }}
                />
              </Col>
              <Col span={6}>
                <Statistic 
                  title="管理员用户" 
                  value={stats.users.admin} 
                  prefix={<UserOutlined />} 
                  valueStyle={{ color: '#722ed1' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
        
        <Col span={24}>
          <Card className="tenant-list-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <Title level={4}>租户管理</Title>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={showCreateModal}
              >
                新建租户
              </Button>
            </div>
            
            <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center' }}>
              <Input.Search
                placeholder="搜索租户名称"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                onSearch={handleSearch}
                style={{ width: 300, marginRight: 16 }}
                enterButton={<SearchOutlined />}
              />
              <Select
                placeholder="状态筛选"
                style={{ width: 120, marginRight: 16 }}
                allowClear
                onChange={handleStatusChange}
                value={filterStatus}
              >
                <Option value={true}>活跃</Option>
                <Option value={false}>停用</Option>
              </Select>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>重置</Button>
            </div>
            
            <Table
              columns={columns}
              rowKey="id"
              dataSource={tenants}
              pagination={pagination}
              loading={loading}
              onChange={handleTableChange}
              expandable={{
                expandedRowRender: record => (
                  <div style={{ margin: 0 }}>
                    <p><strong>Schema名称:</strong> {record.schema_name}</p>
                    <p><strong>联系电话:</strong> {record.contact_phone || '未设置'}</p>
                    <p><strong>更新时间:</strong> {new Date(record.updated_at).toLocaleString()}</p>
                  </div>
                ),
              }}
            />
          </Card>
        </Col>
      </Row>
      
      {/* 租户表单模态框 */}
      <Modal
        title={editingTenant ? '编辑租户' : '新建租户'}
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
                name="name"
                label="租户名称"
                rules={[{ required: true, message: '请输入租户名称' }]}
              >
                <Input placeholder="请输入租户名称" prefix={<BuildOutlined />} />
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="slug"
                label="唯一标识"
                rules={[{ required: editingTenant === null, message: '请输入唯一标识' }]}
                tooltip="用于生成子域名，只能包含小写字母、数字和连字符，不能以连字符开头或结尾"
              >
                <Input placeholder="请输入唯一标识" disabled={editingTenant !== null} prefix={<CloudServerOutlined />} />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="schema_name"
                label="数据库Schema名称"
                rules={[{ required: editingTenant === null, message: '请输入Schema名称' }]}
                tooltip="数据库Schema名称，只能包含字母、数字和下划线，且必须以字母开头"
              >
                <Input placeholder="请输入Schema名称" disabled={editingTenant !== null} />
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="contact_email"
                label="联系邮箱"
                rules={[
                  { required: true, message: '请输入联系邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input placeholder="请输入联系邮箱" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="contact_phone"
                label="联系电话"
              >
                <Input placeholder="请输入联系电话" />
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="domain"
                label="自定义域名"
                tooltip="如果不设置，将使用默认子域名"
              >
                <Input placeholder="请输入自定义域名" prefix={<GlobalOutlined />} />
              </Form.Item>
            </Col>
          </Row>
          
          {editingTenant && (
            <Form.Item
              name="is_active"
              label="是否激活"
              valuePropName="checked"
            >
              <Switch checkedChildren="激活" unCheckedChildren="停用" />
            </Form.Item>
          )}
          
          {!editingTenant && (
            <div>
              <Divider orientation="left">初始管理员账户</Divider>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name={['admin', 'email']}
                    label="管理员邮箱"
                    rules={[{ type: 'email', message: '请输入有效的邮箱地址' }]}
                  >
                    <Input placeholder="管理员邮箱" prefix={<UserOutlined />} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name={['admin', 'password']}
                    label="管理员密码"
                    rules={[
                      { min: 8, message: '密码长度至少为8个字符' },
                      { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字' }
                    ]}
                  >
                    <Input.Password placeholder="密码" />
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name={['admin', 'first_name']}
                    label="管理员名"
                  >
                    <Input placeholder="名" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name={['admin', 'last_name']}
                    label="管理员姓"
                  >
                    <Input placeholder="姓" />
                  </Form.Item>
                </Col>
              </Row>
            </div>
          )}
        </Form>
      </Modal>

      {/* 租户详情模态框 */}
      <Modal
        title="租户详情"
        open={detailModalVisible}
        onCancel={handleDetailCancel}
        footer={[
          <Button key="close" onClick={handleDetailCancel}>
            关闭
          </Button>,
          <Button 
            key="edit" 
            type="primary" 
            onClick={() => {
              handleDetailCancel();
              showEditModal(currentTenant);
            }}
          >
            编辑租户
          </Button>,
        ]}
        width={700}
      >
        {currentTenant && (
          <div className="tenant-details">
            <Row gutter={[16, 24]}>
              <Col span={24}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                  <Avatar 
                    size={64} 
                    style={{ backgroundColor: colorFromName(currentTenant.name), marginRight: 16 }}
                  >
                    {currentTenant.name.charAt(0).toUpperCase()}
                  </Avatar>
                  <div>
                    <Title level={3} style={{ margin: 0 }}>{currentTenant.name}</Title>
                    <Badge 
                      status={currentTenant.is_active ? 'success' : 'error'} 
                      text={currentTenant.is_active ? '活跃' : '停用'} 
                    />
                  </div>
                </div>
              </Col>
              
              <Col span={12}>
                <Statistic 
                  title="租户 ID" 
                  value={currentTenant.id} 
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="唯一标识" 
                  value={currentTenant.slug} 
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              
              <Col span={12}>
                <Statistic 
                  title="Schema 名称" 
                  value={currentTenant.schema_name} 
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="域名" 
                  value={currentTenant.domain || `${currentTenant.slug}.saasplatform.com`} 
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              
              <Col span={12}>
                <Statistic 
                  title="联系邮箱" 
                  value={currentTenant.contact_email} 
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="联系电话" 
                  value={currentTenant.contact_phone || '未设置'} 
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              
              <Col span={12}>
                <Statistic 
                  title="创建时间" 
                  value={new Date(currentTenant.created_at).toLocaleString()} 
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="更新时间" 
                  value={new Date(currentTenant.updated_at).toLocaleString()} 
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              
              <Col span={24}>
                <Divider orientation="left">快捷操作</Divider>
                <Space size="middle">
                  <Button 
                    type="primary" 
                    icon={<TeamOutlined />}
                    onClick={() => {
                      handleDetailCancel();
                      handleManageUsers(currentTenant);
                    }}
                  >
                    管理用户
                  </Button>
                  <Button 
                    icon={<SettingOutlined />}
                    onClick={() => {
                      handleDetailCancel();
                      showEditModal(currentTenant);
                    }}
                  >
                    编辑设置
                  </Button>
                  <Popconfirm
                    title="确定要停用此租户吗？"
                    description="停用后租户将无法访问系统。"
                    onConfirm={() => {
                      handleDetailCancel();
                      handleDeactivate(currentTenant.id);
                    }}
                    okText="确定"
                    cancelText="取消"
                    icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
                  >
                    <Button 
                      danger 
                      icon={<DeleteOutlined />} 
                      disabled={!currentTenant.is_active}
                    >
                      停用租户
                    </Button>
                  </Popconfirm>
                </Space>
              </Col>
            </Row>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TenantManagement; 