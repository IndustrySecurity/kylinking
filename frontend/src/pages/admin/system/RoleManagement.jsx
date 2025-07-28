import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  message,
  Tooltip,
  Popconfirm,
  Typography,
  Badge,
  Tabs,
  Card,
  Transfer
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TeamOutlined,
  KeyOutlined,
  ExclamationCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { useApi } from '../../../hooks/useApi';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { TextArea } = Input;

// Helper function to add delay
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const RoleManagement = ({ tenant, userRole }) => {
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [currentRole, setCurrentRole] = useState(null);
  const [roleUsersModalVisible, setRoleUsersModalVisible] = useState(false);
  const [rolePermissionsModalVisible, setRolePermissionsModalVisible] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const api = useApi();
  const [form] = Form.useForm();
  const [targetKeys, setTargetKeys] = useState([]);
  const [permissionTargetKeys, setPermissionTargetKeys] = useState([]);
  const [selectedKeys, setSelectedKeys] = useState([]);
  const [permissionSelectedKeys, setPermissionSelectedKeys] = useState([]);

  // Fetch roles when component mounts or tenant changes
  useEffect(() => {
    let isMounted = true;
    
    const initializeComponent = async () => {
      if (tenant?.id) {
        if (isMounted) {
          await fetchRoles();
          await fetchPermissions();
        }
      }
    };
    
    initializeComponent();
    
    // Cleanup function to prevent updates on unmounted component
    return () => {
      isMounted = false;
    };
  }, [tenant?.id]); // Only depend on tenant ID to prevent unnecessary rerenders

  // 获取角色列表
  const fetchRoles = async () => {
    await fetchRolesWithParams(pagination.current, pagination.pageSize);
  };

  // 带参数获取角色列表
  const fetchRolesWithParams = async (page, pageSize) => {
    if (loading) return;
    
    setLoading(true);
    
    try {
      const response = await api.get(`/admin/tenants/${tenant.id}/roles`, {
        params: {
          page: page,
          per_page: pageSize
        }
      });
      
      const { roles, total, pages } = response.data;
      setRoles(roles);
      setPagination(prev => ({
        ...prev,
        current: page,
        pageSize: pageSize,
        total,
        pages
      }));
    } catch (error) {
      message.error('获取角色列表失败');
    } finally {
      setLoading(false);
    }
  };

  // Fetch permissions
  const fetchPermissions = async () => {
    try {
      const response = await api.get('/admin/permissions');
      setPermissions(response.data.permissions.map(p => ({
        key: p.id,
        title: p.name,
        description: p.description
      })));
    } catch (error) {
      message.error('获取权限列表失败');
    }
  };

  // Fetch tenant users for role assignment
  const fetchUsers = async () => {
    let usersLoading = true;
    try {
      const response = await api.get(`/admin/tenants/${tenant.id}/users`, {
        params: { per_page: 100 } // Get more users for selection
      });
      setUsers(response.data.users.map(u => ({
        key: u.id,
        title: u.email,
        description: [u.first_name, u.last_name].filter(Boolean).join(' ') || ''
      })));
    } catch (error) {
      message.error('获取用户列表失败');
    } finally {
      usersLoading = false;
    }
  };

  // Handle table change (pagination, filters, sorter)
  const handleTableChange = (newPagination) => {
    setPagination(prev => ({
      ...prev,
      current: newPagination.current,
      pageSize: newPagination.pageSize
    }));
    
    // 使用新的分页参数直接调用API
    fetchRolesWithParams(newPagination.current, newPagination.pageSize);
  };

  // Open modal for creating a new role
  const showCreateModal = () => {
    setCurrentRole(null);
    setModalTitle('创建新角色');
    form.resetFields();
    setModalVisible(true);
  };

  // Open modal for editing an existing role
  const showEditModal = (role) => {
    setCurrentRole(role);
    setModalTitle('编辑角色');
    
    form.setFieldsValue({
      name: role.name,
      description: role.description
    });
    
    setModalVisible(true);
  };

  // Open modal for managing role users
  const showRoleUsersModal = async (role) => {
    setCurrentRole(role);
    
    // Start loading state
    setLoading(true);
    
    await fetchUsers();
    
    // Get role details with assigned users
    try {
      const response = await api.get(`/admin/tenants/${tenant.id}/roles/${role.id}`);
      const roleData = response.data.role;
      
      // Set target keys for transfer component (user IDs assigned to this role)
      setTargetKeys(roleData.users.map(u => u.id));
    } catch (error) {
      message.error('获取角色详情失败');
    } finally {
      // Make sure to end loading state
      setLoading(false);
      
      // Now show the modal
      setRoleUsersModalVisible(true);
    }
  };

  // Open modal for managing role permissions
  const showRolePermissionsModal = async (role) => {
    setCurrentRole(role);
    
    // Start loading state
    setLoading(true);
    
    // Get role details with assigned permissions
    try {
      const response = await api.get(`/admin/tenants/${tenant.id}/roles/${role.id}`);
      const roleData = response.data.role;
      
      // Set target keys for transfer component (permission IDs assigned to this role)
      setPermissionTargetKeys(roleData.permissions.map(p => p.id));
    } catch (error) {
      message.error('获取角色详情失败');
    } finally {
      // Make sure to end loading state
      setLoading(false);
      
      // Now show the modal
      setRolePermissionsModalVisible(true);
    }
  };

  // Handle form submission (create or update role)
  const handleFormSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (currentRole) {
        // Update existing role
        await api.put(`/admin/tenants/${tenant.id}/roles/${currentRole.id}`, values);
        message.success('角色更新成功');
      } else {
        // Create new role
        await api.post(`/admin/tenants/${tenant.id}/roles`, values);
        message.success('角色创建成功');
      }
      
      setModalVisible(false);
      
      // Add delay before refreshing data
      setTimeout(() => {
        fetchRoles(pagination.current, pagination.pageSize);
      }, 800);
    } catch (error) {
      message.error('操作失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // Handle delete role
  const handleDeleteRole = async (roleId) => {
    try {
      await api.delete(`/admin/tenants/${tenant.id}/roles/${roleId}`);
      message.success('角色删除成功');
      
      // Add delay before refreshing data
      setTimeout(() => {
        fetchRoles(pagination.current, pagination.pageSize);
      }, 800);
    } catch (error) {
      message.error('删除角色失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // Handle role user changes
  const handleRoleUserChange = (nextTargetKeys) => {
    setTargetKeys(nextTargetKeys);
  };

  // Handle role permission changes
  const handleRolePermissionChange = (nextTargetKeys) => {
    setPermissionTargetKeys(nextTargetKeys);
  };

  // Save role users
  const saveRoleUsers = async () => {
    try {
      await api.put(`/admin/tenants/${tenant.id}/roles/${currentRole.id}/users`, {
        user_ids: targetKeys
      });
      
      message.success('用户分配成功');
      setRoleUsersModalVisible(false);
      
      // Add delay before refreshing data
      setTimeout(() => {
        fetchRoles(pagination.current, pagination.pageSize);
      }, 800);
    } catch (error) {
      message.error('保存用户分配失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // Save role permissions
  const saveRolePermissions = async () => {
    try {
      await api.put(`/admin/tenants/${tenant.id}/roles/${currentRole.id}/permissions`, {
        permission_ids: permissionTargetKeys
      });
      
      message.success('权限分配成功');
      setRolePermissionsModalVisible(false);
      
      // Add delay before refreshing data
      setTimeout(() => {
        fetchRoles(pagination.current, pagination.pageSize);
      }, 800);
    } catch (error) {
      message.error('保存权限分配失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // Table columns definition
  const columns = [
    {
      title: '角色名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '用户数量',
      dataIndex: 'users_count',
      key: 'users_count',
    },
    {
      title: '权限数量',
      dataIndex: 'permissions_count',
      key: 'permissions_count',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="编辑角色">
            <Button 
              icon={<EditOutlined />} 
              onClick={() => showEditModal(record)} 
              type="link" 
              size="small"
            />
          </Tooltip>
          
          <Tooltip title="分配用户">
            <Button 
              icon={<TeamOutlined />} 
              onClick={() => showRoleUsersModal(record)} 
              type="link" 
              size="small"
            />
          </Tooltip>
          
          <Tooltip title="分配权限">
            <Button 
              icon={<KeyOutlined />} 
              onClick={() => showRolePermissionsModal(record)} 
              type="link" 
              size="small"
            />
          </Tooltip>
          
          <Tooltip title="删除角色">
            <Popconfirm
              title="确定要删除该角色吗?"
              description="删除后无法恢复，已分配该角色的用户将失去对应权限。"
              onConfirm={() => handleDeleteRole(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button 
                icon={<DeleteOutlined />} 
                type="link" 
                danger
                size="small"
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className="role-management">
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={5}>{tenant.name} - 角色管理</Title>
        <div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={showCreateModal}
            style={{ marginRight: '8px' }}
          >
            创建角色
          </Button>
          <Button
            icon={<SyncOutlined />}
            onClick={() => fetchRoles(pagination.current, pagination.pageSize)}
          >
            刷新
          </Button>
        </div>
      </div>

      <Table
        dataSource={roles}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{
          ...pagination,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          pageSizeOptions: ['5', '10', '20', '50']
        }}
        onChange={handleTableChange}
      />

      {/* Role Create/Edit Modal */}
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
            name="name"
            label="角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          >
            <Input placeholder="请输入角色名称" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="描述"
          >
            <TextArea rows={4} placeholder="请输入角色描述" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Role Users Modal */}
      <Modal
        title={`分配用户到角色: ${currentRole?.name}`}
        open={roleUsersModalVisible}
        onOk={saveRoleUsers}
        onCancel={() => setRoleUsersModalVisible(false)}
        width={800}
        maskClosable={false}
        okText="保存"
        cancelText="取消"
      >
        <Transfer
          dataSource={users}
          titles={['可选用户', '已选用户']}
          targetKeys={targetKeys}
          selectedKeys={selectedKeys}
          onChange={handleRoleUserChange}
          onSelectChange={(sourceSelectedKeys, targetSelectedKeys) => {
            setSelectedKeys([...sourceSelectedKeys, ...targetSelectedKeys]);
          }}
          render={item => item.title + (item.description ? ` (${item.description})` : '')}
          listStyle={{
            width: 350,
            height: 400,
          }}
        />
      </Modal>

      {/* Role Permissions Modal */}
      <Modal
        title={`分配权限到角色: ${currentRole?.name}`}
        open={rolePermissionsModalVisible}
        onOk={saveRolePermissions}
        onCancel={() => setRolePermissionsModalVisible(false)}
        width={800}
        maskClosable={false}
        okText="保存"
        cancelText="取消"
      >
        <Transfer
          dataSource={permissions}
          titles={['可选权限', '已选权限']}
          targetKeys={permissionTargetKeys}
          selectedKeys={permissionSelectedKeys}
          onChange={handleRolePermissionChange}
          onSelectChange={(sourceSelectedKeys, targetSelectedKeys) => {
            setPermissionSelectedKeys([...sourceSelectedKeys, ...targetSelectedKeys]);
          }}
          render={item => (
            <div>
              <div>{item.title}</div>
              {item.description && <div style={{ fontSize: '12px', color: '#999' }}>{item.description}</div>}
            </div>
          )}
          listStyle={{
            width: 350,
            height: 400,
          }}
        />
      </Modal>
    </div>
  );
};

export default RoleManagement; 