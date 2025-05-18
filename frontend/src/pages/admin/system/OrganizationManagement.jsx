import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  TreeSelect,
  Select,
  message,
  Tooltip,
  Popconfirm,
  Typography,
  Tree,
  Card,
  Divider
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TeamOutlined,
  FolderOutlined,
  UserSwitchOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { TreeNode } = Tree;

// Since we don't have an organization model yet, we'll simulate 
// an organization API for the frontend design
const OrganizationManagement = ({ tenant, userRole }) => {
  const [organizations, setOrganizations] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [currentOrg, setCurrentOrg] = useState(null);
  const [treeData, setTreeData] = useState([]);
  const [expandedKeys, setExpandedKeys] = useState([]);
  const [assignUserModalVisible, setAssignUserModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [assignForm] = Form.useForm();

  // 模拟获取组织数据
  useEffect(() => {
    if (tenant) {
      fetchOrganizations();
      fetchUsers();
    }
  }, [tenant]);

  // 模拟获取组织列表
  const fetchOrganizations = async () => {
    setLoading(true);
    // 这里模拟从API获取组织数据
    // 实际应用中应该调用真实的API
    setTimeout(() => {
      const mockOrgs = [
        {
          id: '1',
          name: '总公司',
          code: 'HQ',
          description: '公司总部',
          parent_id: null,
          level: 1,
          children: [
            {
              id: '2',
              name: '生产部',
              code: 'PROD',
              description: '负责产品生产',
              parent_id: '1',
              level: 2
            },
            {
              id: '3',
              name: '销售部',
              code: 'SALES',
              description: '负责产品销售',
              parent_id: '1',
              level: 2,
              children: [
                {
                  id: '5',
                  name: '国内销售组',
                  code: 'SALES-CN',
                  description: '负责国内市场',
                  parent_id: '3',
                  level: 3
                },
                {
                  id: '6',
                  name: '国际销售组',
                  code: 'SALES-INT',
                  description: '负责国际市场',
                  parent_id: '3',
                  level: 3
                }
              ]
            }
          ]
        },
        {
          id: '4',
          name: '研发部',
          code: 'RD',
          description: '负责产品研发',
          parent_id: null,
          level: 1
        }
      ];
      
      setOrganizations(flattenOrgs(mockOrgs));
      setTreeData(mockOrgs);
      setExpandedKeys(['1', '3']); // 默认展开的节点
      setLoading(false);
    }, 500);
  };

  // 扁平化组织数据用于表格显示
  const flattenOrgs = (orgs, result = []) => {
    orgs.forEach(org => {
      result.push({
        id: org.id,
        name: org.name,
        code: org.code,
        description: org.description,
        parent_id: org.parent_id,
        level: org.level
      });
      
      if (org.children && org.children.length > 0) {
        flattenOrgs(org.children, result);
      }
    });
    
    return result;
  };

  // 获取用户列表
  const fetchUsers = async () => {
    try {
      const response = await axios.get(`/api/admin/tenants/${tenant.id}/users`, {
        params: { per_page: 100 } // 获取更多用户
      });
      setUsers(response.data.users);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      message.error('获取用户列表失败');
    }
  };

  // 显示创建组织的模态框
  const showCreateModal = (parentOrg = null) => {
    setCurrentOrg(null);
    setModalTitle('创建新组织');
    form.resetFields();
    
    if (parentOrg) {
      form.setFieldsValue({
        parent_id: parentOrg.id
      });
    }
    
    setModalVisible(true);
  };

  // 显示编辑组织的模态框
  const showEditModal = (org) => {
    setCurrentOrg(org);
    setModalTitle('编辑组织');
    
    form.setFieldsValue({
      name: org.name,
      code: org.code,
      description: org.description,
      parent_id: org.parent_id
    });
    
    setModalVisible(true);
  };

  // 显示分配用户的模态框
  const showAssignUserModal = (org) => {
    setCurrentOrg(org);
    assignForm.resetFields();
    setAssignUserModalVisible(true);
  };

  // 处理表单提交（创建或更新组织）
  const handleFormSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      // 这里模拟提交到API
      // 实际应用中应该调用真实的API
      message.success(currentOrg ? '组织更新成功' : '组织创建成功');
      setModalVisible(false);
      fetchOrganizations(); // 重新获取数据
    } catch (error) {
      console.error('Form submission failed:', error);
      message.error('操作失败');
    }
  };

  // 处理分配用户
  const handleAssignUser = async () => {
    try {
      const values = await assignForm.validateFields();
      
      // 这里模拟提交到API
      // 实际应用中应该调用真实的API
      message.success('用户分配成功');
      setAssignUserModalVisible(false);
    } catch (error) {
      console.error('User assignment failed:', error);
      message.error('用户分配失败');
    }
  };

  // 处理组织删除
  const handleDeleteOrg = async (orgId) => {
    // 检查是否有子组织
    const hasChildren = organizations.some(org => org.parent_id === orgId);
    if (hasChildren) {
      message.error('不能删除包含子组织的组织，请先删除其下属组织');
      return;
    }
    
    // 这里模拟从API删除组织
    // 实际应用中应该调用真实的API
    message.success('组织删除成功');
    fetchOrganizations(); // 重新获取数据
  };

  // 处理树节点展开/收起
  const onExpand = (expandedKeys) => {
    setExpandedKeys(expandedKeys);
  };

  // 表格列定义
  const columns = [
    {
      title: '组织名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '组织代码',
      dataIndex: 'code',
      key: 'code',
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
          <Tooltip title="编辑组织">
            <Button 
              icon={<EditOutlined />} 
              onClick={() => showEditModal(record)} 
              type="link" 
              size="small"
            />
          </Tooltip>
          
          <Tooltip title="添加子组织">
            <Button 
              icon={<FolderOutlined />} 
              onClick={() => showCreateModal(record)} 
              type="link" 
              size="small"
            />
          </Tooltip>
          
          <Tooltip title="分配用户">
            <Button 
              icon={<UserSwitchOutlined />} 
              onClick={() => showAssignUserModal(record)} 
              type="link" 
              size="small"
            />
          </Tooltip>
          
          <Tooltip title="删除组织">
            <Popconfirm
              title="确定要删除该组织吗?"
              description="删除组织将同时解除用户与该组织的关联"
              onConfirm={() => handleDeleteOrg(record.id)}
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

  // 渲染组织树节点
  const renderTreeNodes = (data) => {
    return data.map(item => {
      if (item.children && item.children.length > 0) {
        return (
          <TreeNode key={item.id} title={item.name}>
            {renderTreeNodes(item.children)}
          </TreeNode>
        );
      }
      return <TreeNode key={item.id} title={item.name} />;
    });
  };

  return (
    <div className="organization-management">
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={5}>{tenant.name} - 组织管理</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => showCreateModal()}
        >
          创建顶级组织
        </Button>
      </div>

      <Card>
        <div style={{ display: 'flex', gap: '32px' }}>
          <div style={{ width: '30%', minWidth: '250px', borderRight: '1px solid #f0f0f0', paddingRight: '16px' }}>
            <Title level={5}>组织结构树</Title>
            <Tree
              showLine
              defaultExpandedKeys={expandedKeys}
              onExpand={onExpand}
            >
              {renderTreeNodes(treeData)}
            </Tree>
          </div>
          
          <div style={{ flex: 1 }}>
            <Table
              dataSource={organizations}
              columns={columns}
              rowKey="id"
              loading={loading}
              size="small"
              pagination={{ pageSize: 10 }}
            />
          </div>
        </div>
      </Card>

      {/* Organization Create/Edit Modal */}
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
            label="组织名称"
            rules={[{ required: true, message: '请输入组织名称' }]}
          >
            <Input placeholder="请输入组织名称" />
          </Form.Item>
          
          <Form.Item
            name="code"
            label="组织代码"
            rules={[{ required: true, message: '请输入组织代码' }]}
          >
            <Input placeholder="请输入组织代码" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="描述"
          >
            <TextArea rows={4} placeholder="请输入组织描述" />
          </Form.Item>
          
          <Form.Item
            name="parent_id"
            label="父组织"
          >
            <TreeSelect
              style={{ width: '100%' }}
              dropdownStyle={{ maxHeight: 400, overflow: 'auto' }}
              treeData={treeData}
              placeholder="请选择父组织"
              treeDefaultExpandAll
              allowClear
              fieldNames={{ label: 'name', value: 'id', children: 'children' }}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Assign User Modal */}
      <Modal
        title={`分配用户到组织: ${currentOrg?.name}`}
        open={assignUserModalVisible}
        onOk={handleAssignUser}
        onCancel={() => setAssignUserModalVisible(false)}
        maskClosable={false}
        okText="确定"
        cancelText="取消"
      >
        <Form
          form={assignForm}
          layout="vertical"
        >
          <Form.Item
            name="user_ids"
            label="选择用户"
            rules={[{ required: true, message: '请选择至少一个用户' }]}
          >
            <Select
              mode="multiple"
              placeholder="请选择用户"
              style={{ width: '100%' }}
              optionFilterProp="children"
              filterOption={(input, option) =>
                option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
            >
              {users.map(user => (
                <Option key={user.id} value={user.id}>
                  {user.email} ({user.first_name} {user.last_name})
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default OrganizationManagement; 