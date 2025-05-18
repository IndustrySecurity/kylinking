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
  Spin,
  Tabs,
  Descriptions,
  Tree,
  Transfer,
  Empty,
  Checkbox
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  SearchOutlined,
  ReloadOutlined,
  TeamOutlined,
  SafetyOutlined,
  KeyOutlined,
  ArrowLeftOutlined,
  SettingOutlined,
  LockOutlined,
  CheckOutlined,
  CloseOutlined,
  AppstoreOutlined,
  UserOutlined
} from '@ant-design/icons';
import { useApi } from '../../hooks/useApi';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { TextArea } = Input;

const permissionGroups = {
  'tenant': '租户管理',
  'user': '用户管理',
  'role': '角色管理',
  'production': '生产管理',
  'equipment': '设备管理',
  'quality': '质量管理',
  'inventory': '库存管理',
  'employee': '员工管理'
};

const RoleManagement = () => {
  const { tenantId } = useParams();
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [tenant, setTenant] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [permLoading, setPermLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [searchName, setSearchName] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  const [detailRole, setDetailRole] = useState(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('1');
  const [selectedPermissions, setSelectedPermissions] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [form] = Form.useForm();
  const api = useApi();
  const navigate = useNavigate();

  // 获取角色列表
  const fetchRoles = async (page = 1, pageSize = 10, name = '') => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page,
        per_page: pageSize
      });
      
      if (name) {
        params.append('name', name);
      }
      
      const response = await api.get(`/api/admin/tenants/${tenantId}/roles?${params.toString()}`);
      setRoles(response.data.roles);
      setPagination({
        current: response.data.page || 1,
        pageSize: response.data.per_page || 10,
        total: response.data.total || 0
      });
    } catch (error) {
      message.error('获取角色列表失败');
      console.error('Error fetching roles:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取租户信息
  const fetchTenant = async () => {
    try {
      const response = await api.get(`/api/admin/tenants/${tenantId}`);
      setTenant(response.data.tenant);
    } catch (error) {
      message.error('获取租户信息失败');
      console.error('Error fetching tenant:', error);
    }
  };

  // 获取系统权限列表
  const fetchPermissions = async () => {
    try {
      const response = await api.get('/api/admin/permissions');
      setPermissions(response.data || []);
    } catch (error) {
      console.error('Error fetching permissions:', error);
      message.error('获取权限列表失败');
    }
  };

  // 获取用户列表(摘要)
  const fetchUsers = async () => {
    try {
      const response = await api.get(`/api/admin/tenants/${tenantId}/users?per_page=1000`);
      setUsers(response.data.users);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // 获取角色详情
  const fetchRoleDetail = async (roleId) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/admin/tenants/${tenantId}/roles/${roleId}`);
      setDetailRole(response.data.role);
      setSelectedPermissions(response.data.role.permissions.map(p => p.id));
      setSelectedUsers(response.data.role.users.map(u => u.id));
    } catch (error) {
      message.error('获取角色详情失败');
      console.error('Error fetching role detail:', error);
    } finally {
      setLoading(false);
    }
  };

  // 首次加载
  useEffect(() => {
    fetchRoles();
    fetchTenant();
    fetchPermissions();
    fetchUsers();
  }, [tenantId]);

  // 表格变化处理
  const handleTableChange = (pagination) => {
    fetchRoles(pagination.current, pagination.pageSize, searchName);
  };

  // 搜索处理
  const handleSearch = () => {
    fetchRoles(1, pagination.pageSize, searchName);
  };

  // 重置搜索
  const handleReset = () => {
    setSearchName('');
    fetchRoles(1, pagination.pageSize, '');
  };

  // 打开新建角色模态框
  const showCreateModal = () => {
    setEditingRole(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 打开编辑角色模态框
  const showEditModal = (role) => {
    setEditingRole(role);
    form.setFieldsValue({
      name: role.name,
      description: role.description
    });
    setModalVisible(true);
  };

  // 打开角色详情模态框
  const showDetailModal = async (role) => {
    await fetchRoleDetail(role.id);
    setDetailModalVisible(true);
  };

  // 关闭模态框
  const handleCancel = () => {
    setModalVisible(false);
  };

  // 关闭详情模态框
  const handleDetailCancel = () => {
    setDetailModalVisible(false);
    setDetailRole(null);
    setSelectedPermissions([]);
    setSelectedUsers([]);
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingRole) {
        // 更新角色
        await api.put(`/api/admin/tenants/${tenantId}/roles/${editingRole.id}`, values);
        message.success('角色更新成功');
      } else {
        // 创建角色
        await api.post(`/api/admin/tenants/${tenantId}/roles`, values);
        message.success('角色创建成功');
      }
      
      setModalVisible(false);
      fetchRoles(pagination.current, pagination.pageSize, searchName);
    } catch (error) {
      console.error('Form submission error:', error);
      message.error('操作失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // 删除角色
  const handleDeleteRole = async (roleId) => {
    try {
      await api.delete(`/api/admin/tenants/${tenantId}/roles/${roleId}`);
      message.success('角色删除成功');
      fetchRoles(pagination.current, pagination.pageSize, searchName);
    } catch (error) {
      message.error('删除角色失败');
      console.error('Error deleting role:', error);
    }
  };

  // 更新角色权限
  const handleUpdatePermissions = async () => {
    if (!detailRole) return;
    
    try {
      await api.put(`/api/admin/tenants/${tenantId}/roles/${detailRole.id}/permissions`, {
        permission_ids: selectedPermissions
      });
      message.success('权限更新成功');
      await fetchRoleDetail(detailRole.id);
    } catch (error) {
      message.error('更新权限失败');
      console.error('Error updating permissions:', error);
    }
  };

  // 更新角色用户
  const handleUpdateUsers = async () => {
    if (!detailRole) return;
    
    try {
      await api.put(`/api/admin/tenants/${tenantId}/roles/${detailRole.id}/users`, {
        user_ids: selectedUsers
      });
      message.success('用户更新成功');
      await fetchRoleDetail(detailRole.id);
    } catch (error) {
      message.error('更新用户失败');
      console.error('Error updating users:', error);
    }
  };

  // 返回租户管理页面
  const handleBackToTenants = () => {
    navigate('/admin/tenants');
  };

  // 跳转到用户管理
  const handleGoToUsers = () => {
    navigate(`/admin/tenants/${tenantId}/users`);
  };

  // 按组分类权限
  const getPermissionsByGroup = () => {
    const grouped = {};
    
    permissions.forEach(permission => {
      const [group] = permission.name.split(':');
      if (!grouped[group]) {
        grouped[group] = [];
      }
      grouped[group].push(permission);
    });
    
    return grouped;
  };

  // 检查是否全选了某个组的权限
  const isGroupAllSelected = (groupPermissions) => {
    return groupPermissions.every(p => selectedPermissions.includes(p.id));
  };

  // 切换组内所有权限
  const toggleGroupPermissions = (groupPermissions, checked) => {
    let newSelected = [...selectedPermissions];
    
    if (checked) {
      // 添加组内所有权限
      groupPermissions.forEach(p => {
        if (!newSelected.includes(p.id)) {
          newSelected.push(p.id);
        }
      });
    } else {
      // 移除组内所有权限
      newSelected = newSelected.filter(id => !groupPermissions.find(p => p.id === id));
    }
    
    setSelectedPermissions(newSelected);
  };

  // 渲染分组权限
  const renderGroupedPermissions = () => {
    const grouped = getPermissionsByGroup();
    
    return Object.entries(grouped).map(([group, groupPerms]) => (
      <Card 
        key={group} 
        title={
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>{permissionGroups[group] || group}</span>
            <Checkbox 
              checked={isGroupAllSelected(groupPerms)}
              onChange={(e) => toggleGroupPermissions(groupPerms, e.target.checked)}
            />
          </div>
        }
        style={{ marginBottom: 16 }}
        size="small"
      >
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {groupPerms.map(permission => (
            <Checkbox
              key={permission.id}
              checked={selectedPermissions.includes(permission.id)}
              onChange={(e) => {
                const newSelected = e.target.checked
                  ? [...selectedPermissions, permission.id]
                  : selectedPermissions.filter(id => id !== permission.id);
                setSelectedPermissions(newSelected);
              }}
            >
              {permission.description || permission.name}
            </Checkbox>
          ))}
        </div>
      </Card>
    ));
  };

  // 表格列定义
  const columns = [
    {
      title: '角色名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <Avatar 
            style={{ 
              backgroundColor: '#1890ff',
              verticalAlign: 'middle' 
            }}
            icon={<SafetyOutlined />}
            size="small"
          />
          <a onClick={() => showDetailModal(record)}>{text}</a>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '权限数',
      key: 'permissions_count',
      render: (_, record) => {
        const count = record.permissions_count || 0;
        return (
          <Tag color={count > 0 ? 'blue' : 'default'}>
            {count} 个权限
          </Tag>
        );
      },
    },
    {
      title: '用户数',
      key: 'users_count',
      render: (_, record) => {
        const count = record.users_count || 0;
        return (
          <Tag color={count > 0 ? 'green' : 'default'}>
            {count} 个用户
          </Tag>
        );
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<KeyOutlined />} 
              onClick={() => showDetailModal(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => showEditModal(record)}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Popconfirm
              title="确定要删除此角色吗？"
              description="删除后，所有分配此角色的用户将失去对应权限。"
              onConfirm={() => handleDeleteRole(record.id)}
              okText="确定"
              cancelText="取消"
              icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
            >
              <Button 
                type="text" 
                danger
                icon={<DeleteOutlined />}
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className="role-management">
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
              <Breadcrumb.Item>{tenant?.name || '租户'} - 角色管理</Breadcrumb.Item>
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
                  title="角色总数" 
                  value={pagination.total || roles.length} 
                  prefix={<SafetyOutlined />}
                />
              </Col>
              <Col span={8}>
                <a onClick={handleGoToUsers}>
                  <Statistic 
                    title="用户总数" 
                    value={users.length} 
                    prefix={<UserOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </a>
              </Col>
            </Row>
          </Card>
        </Col>
        
        <Col span={24}>
          <Card className="role-list-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <Title level={4}>角色列表</Title>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={showCreateModal}
              >
                新建角色
              </Button>
            </div>
            
            <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center' }}>
              <Input.Search
                placeholder="搜索角色名称"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                onSearch={handleSearch}
                style={{ width: 300, marginRight: 16 }}
                enterButton={<SearchOutlined />}
              />
              <Button icon={<ReloadOutlined />} onClick={handleReset}>重置</Button>
            </div>
            
            <Table
              columns={columns}
              rowKey="id"
              dataSource={roles}
              pagination={pagination}
              loading={loading}
              onChange={handleTableChange}
            />
          </Card>
        </Col>
      </Row>

      {/* 角色表单模态框 */}
      <Modal
        title={editingRole ? '编辑角色' : '新建角色'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={handleCancel}
        maskClosable={false}
        destroyOnClose={true}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="name"
            label="角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          >
            <Input placeholder="请输入角色名称" prefix={<SafetyOutlined />} />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="角色描述"
          >
            <TextArea 
              placeholder="请输入角色描述" 
              autoSize={{ minRows: 3, maxRows: 6 }}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 角色详情模态框 */}
      <Modal
        title={
          <Space>
            <SafetyOutlined />
            <span>角色详情: {detailRole?.name}</span>
          </Space>
        }
        open={detailModalVisible}
        onCancel={handleDetailCancel}
        footer={null}
        width={800}
        destroyOnClose={true}
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: '30px 0' }}>
            <Spin />
          </div>
        ) : detailRole ? (
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane 
              tab={
                <span>
                  <SettingOutlined />
                  基本信息
                </span>
              } 
              key="1"
            >
              <Descriptions bordered column={1} style={{ marginBottom: 24 }}>
                <Descriptions.Item label="角色名称">{detailRole.name}</Descriptions.Item>
                <Descriptions.Item label="角色描述">{detailRole.description || '无描述'}</Descriptions.Item>
                <Descriptions.Item label="创建时间">{new Date(detailRole.created_at).toLocaleString()}</Descriptions.Item>
                <Descriptions.Item label="更新时间">{new Date(detailRole.updated_at).toLocaleString()}</Descriptions.Item>
              </Descriptions>
              
              <Space>
                <Button 
                  type="primary" 
                  icon={<EditOutlined />}
                  onClick={() => {
                    handleDetailCancel();
                    showEditModal(detailRole);
                  }}
                >
                  编辑角色信息
                </Button>
                <Popconfirm
                  title="确定要删除此角色吗？"
                  description="删除后，所有分配此角色的用户将失去对应权限。"
                  onConfirm={() => {
                    handleDeleteRole(detailRole.id);
                    handleDetailCancel();
                  }}
                  okText="确定"
                  cancelText="取消"
                  icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
                >
                  <Button danger icon={<DeleteOutlined />}>删除角色</Button>
                </Popconfirm>
              </Space>
            </TabPane>
            
            <TabPane 
              tab={
                <span>
                  <LockOutlined />
                  权限管理
                  <Badge 
                    count={detailRole.permissions.length} 
                    style={{ marginLeft: 8, backgroundColor: '#1890ff' }} 
                  />
                </span>
              } 
              key="2"
            >
              {permLoading ? (
                <div style={{ textAlign: 'center', padding: '30px 0' }}>
                  <Spin />
                </div>
              ) : permissions.length === 0 ? (
                <Empty description="暂无可用权限" />
              ) : (
                <>
                  <div className="permission-list" style={{ marginBottom: 24 }}>
                    {renderGroupedPermissions()}
                  </div>
                  
                  <div style={{ textAlign: 'right' }}>
                    <Button 
                      type="primary" 
                      icon={<CheckOutlined />}
                      onClick={handleUpdatePermissions}
                    >
                      保存权限设置
                    </Button>
                  </div>
                </>
              )}
            </TabPane>
            
            <TabPane 
              tab={
                <span>
                  <UserOutlined />
                  用户分配
                  <Badge 
                    count={detailRole.users.length} 
                    style={{ marginLeft: 8, backgroundColor: '#52c41a' }} 
                  />
                </span>
              } 
              key="3"
            >
              <Transfer
                dataSource={users.map(user => ({
                  key: user.id,
                  title: `${user.first_name || ''} ${user.last_name || ''} (${user.email})`,
                  description: user.is_admin ? '管理员' : '普通用户'
                }))}
                titles={['可选用户', '已选用户']}
                targetKeys={selectedUsers}
                onChange={setSelectedUsers}
                render={item => item.title}
                listStyle={{
                  width: 350,
                  height: 300,
                }}
                showSearch
                filterOption={(inputValue, option) =>
                  option.title.toLowerCase().indexOf(inputValue.toLowerCase()) > -1
                }
              />
              
              <div style={{ textAlign: 'right', marginTop: 24 }}>
                <Button 
                  type="primary" 
                  icon={<CheckOutlined />}
                  onClick={handleUpdateUsers}
                >
                  保存用户分配
                </Button>
              </div>
            </TabPane>
          </Tabs>
        ) : (
          <Empty description="未找到角色信息" />
        )}
      </Modal>
    </div>
  );
};

export default RoleManagement; 