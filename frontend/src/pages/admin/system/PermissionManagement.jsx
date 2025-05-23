import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  message,
  Tooltip,
  Badge,
  Typography,
  Card,
  Tag,
  Popconfirm
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  InfoCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { useApi } from '../../../hooks/useApi';

const { Title } = Typography;
const { TextArea } = Input;

// Helper function to add delay
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const PermissionManagement = ({ tenant, userRole }) => {
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [currentPermission, setCurrentPermission] = useState(null);
  const [permissionDetails, setPermissionDetails] = useState(null);
  const [detailsModalVisible, setDetailsModalVisible] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const api = useApi();
  const [form] = Form.useForm();

  // Fetch permissions when component mounts
  useEffect(() => {
    fetchPermissions();
  }, []);

  // Fetch permissions list
  const fetchPermissions = async () => {
    if (loading) return; // Prevent concurrent fetches
    
    setLoading(true);
    try {
      // Add delay to slow down API calls
      await sleep(600);
      
      const response = await api.get('/admin/permissions');
      setPermissions(response.data.permissions);
      setPagination({
        ...pagination,
        total: response.data.permissions.length
      });
    } catch (error) {
      message.error('获取权限列表失败');
    } finally {
      setLoading(false);
    }
  };

  // Show modal to create new permission
  // Note: This is simulated as creating new permissions might be a system-level operation
  const showCreateModal = () => {
    // Only super admin can create new permissions
    if (!userRole?.isSuperAdmin) {
      message.warning('只有超级管理员可以创建新权限');
      return;
    }
    
    setCurrentPermission(null);
    setModalTitle('创建新权限');
    form.resetFields();
    setModalVisible(true);
  };

  // Show permission editing modal
  const showEditModal = (permission) => {
    // Only super admin can edit permissions
    if (!userRole?.isSuperAdmin) {
      message.warning('只有超级管理员可以编辑权限');
      return;
    }
    
    setCurrentPermission(permission);
    setModalTitle('编辑权限');
    
    form.setFieldsValue({
      name: permission.name,
      description: permission.description
    });
    
    setModalVisible(true);
  };

  // Show permission details
  const showDetailsModal = (permission) => {
    setPermissionDetails(permission);
    setDetailsModalVisible(true);
  };

  // Handle form submission (create or update permission)
  const handleFormSubmit = async () => {
    if (!userRole?.isSuperAdmin) {
      message.error('只有超级管理员可以管理权限');
      setModalVisible(false);
      return;
    }
    
    try {
      const values = await form.validateFields();
      
      // Add delay before API call simulation
      await sleep(500);
      
      // This is a placeholder - the backend endpoint for creating/editing permissions
      // might not be implemented since permissions are typically predefined
      
      if (currentPermission) {
        // Update permission simulation - in a real app, this would call the API
        message.success('权限更新成功');
      } else {
        // Create permission simulation - in a real app, this would call the API
        message.success('权限创建成功');
      }
      
      setModalVisible(false);
      
      // Add delay before refreshing permissions
      setTimeout(() => {
        fetchPermissions();
      }, 800);
    } catch (error) {
      message.error('操作失败');
    }
  };

  // Table columns definition
  const columns = [
    {
      title: '权限名称',
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
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button 
              icon={<InfoCircleOutlined />} 
              onClick={() => showDetailsModal(record)} 
              type="link" 
              size="small"
            />
          </Tooltip>
          
          {userRole?.isSuperAdmin && (
            <>
              <Tooltip title="编辑权限">
                <Button 
                  icon={<EditOutlined />} 
                  onClick={() => showEditModal(record)} 
                  type="link" 
                  size="small"
                />
              </Tooltip>
              
              <Tooltip title="删除权限">
                <Button 
                  icon={<DeleteOutlined />} 
                  type="link" 
                  danger
                  size="small"
                  onClick={() => message.warning('系统不允许删除预设权限')}
                />
              </Tooltip>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div className="permission-management">
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={5}>{tenant.name} - 权限管理</Title>
        {userRole?.isSuperAdmin && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={showCreateModal}
          >
            创建权限
          </Button>
        )}
      </div>

      <Table
        dataSource={permissions}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={pagination}
      />

      {/* Permission Create/Edit Modal */}
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
            label="权限名称"
            rules={[{ required: true, message: '请输入权限名称' }]}
          >
            <Input placeholder="请输入权限名称" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="描述"
          >
            <TextArea rows={4} placeholder="请输入权限描述" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Permission Details Modal */}
      <Modal
        title="权限详情"
        open={detailsModalVisible}
        onCancel={() => setDetailsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailsModalVisible(false)}>
            关闭
          </Button>
        ]}
      >
        {permissionDetails && (
          <div>
            <p><strong>权限名称：</strong> {permissionDetails.name}</p>
            <p><strong>描述：</strong> {permissionDetails.description || '无描述'}</p>
            <p><strong>创建时间：</strong> {new Date(permissionDetails.created_at).toLocaleString()}</p>
            <p><strong>最后更新：</strong> {new Date(permissionDetails.updated_at).toLocaleString()}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PermissionManagement; 