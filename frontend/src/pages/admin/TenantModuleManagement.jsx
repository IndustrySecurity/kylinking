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
  message,
  Typography,
  Row,
  Col,
  Statistic,
  Select,
  Switch,
  Tabs,
  Drawer,
  Descriptions,
  Badge,
  Tooltip,
  Divider,
  InputNumber
} from 'antd';
import {
  PlusOutlined,
  SettingOutlined,
  EyeOutlined,
  EditOutlined,
  BarChartOutlined,
  DatabaseOutlined,
  AppstoreOutlined,
  UserOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useApi } from '../../hooks/useApi';
import DebugAuth from '../../components/DebugAuth';

const { Title } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { TextArea } = Input;

const TenantModuleManagement = () => {
  const [modules, setModules] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [tenantModules, setTenantModules] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [configDrawerVisible, setConfigDrawerVisible] = useState(false);
  const [selectedModule, setSelectedModule] = useState(null);
  const [form] = Form.useForm();
  const api = useApi();

  // 获取系统模块列表
  const fetchModules = async () => {
    try {
      setLoading(true);
      const response = await api.get('/admin/modules/');
      if (response.data.success) {
        setModules(response.data.data);
      }
    } catch (error) {
      message.error('获取模块列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取租户列表
  const fetchTenants = async () => {
    try {
      const response = await api.get('/admin/tenants');
      console.log('租户API响应:', response.data); // 调试日志
      
      // 适应后端实际的API响应格式
      if (response.data.tenants) {
        setTenants(response.data.tenants);
      } else if (response.data.success && response.data.data) {
        setTenants(response.data.data);
      } else {
        console.error('无法解析租户数据:', response.data);
        message.error('租户数据格式错误');
      }
    } catch (error) {
      console.error('获取租户列表失败:', error);
      message.error('获取租户列表失败');
    }
  };

  // 获取租户模块配置
  const fetchTenantModules = async (tenantId) => {
    if (!tenantId) return;
    
    try {
      setLoading(true);
      const response = await api.get(`/admin/modules/tenants/${tenantId}/modules`);
      if (response.data.success) {
        setTenantModules(response.data.data.modules);
      }
    } catch (error) {
      message.error('获取租户模块配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取统计信息
  const fetchStatistics = async () => {
    try {
      const response = await api.get('/admin/modules/statistics');
      if (response.data.success) {
        setStatistics(response.data.data);
      }
    } catch (error) {
      message.error('获取统计信息失败');
    }
  };

  // 初始化租户模块
  const initializeTenantModules = async (tenantId) => {
    try {
      setLoading(true);
      const response = await api.post(`/admin/modules/tenants/${tenantId}/initialize`);
      if (response.data.success) {
        message.success('租户模块初始化成功');
        fetchTenantModules(tenantId);
        fetchStatistics();
      }
    } catch (error) {
      message.error('初始化失败');
    } finally {
      setLoading(false);
    }
  };

  // 配置租户模块
  const configureTenantModule = async (tenantId, moduleId, config) => {
    try {
      const response = await api.post(`/admin/modules/tenants/${tenantId}/modules/${moduleId}/configure`, config);
      if (response.data.success) {
        message.success('模块配置成功');
        fetchTenantModules(tenantId);
        fetchStatistics();
        return true;
      }
    } catch (error) {
      message.error('配置失败');
      return false;
    }
  };

  useEffect(() => {
    fetchModules();
    fetchTenants();
    fetchStatistics();
  }, []);

  useEffect(() => {
    if (selectedTenant) {
      fetchTenantModules(selectedTenant);
    }
  }, [selectedTenant]);

  // 模块表格列定义
  const moduleColumns = [
    {
      title: '模块名称',
      dataIndex: 'display_name',
      key: 'display_name',
      render: (text, record) => (
        <Space>
          <span>{text}</span>
          {record.is_core && <Tag color="red">核心</Tag>}
        </Space>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      render: (category) => <Tag color="blue">{category}</Tag>,
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: '状态',
      key: 'status',
      render: (_, record) => (
        <Space>
          <Badge 
            status={record.is_enabled ? 'success' : 'default'} 
            text={record.is_enabled ? '已启用' : '已禁用'} 
          />
          {record.is_visible && <Tag color="green">可见</Tag>}
        </Space>
      ),
    },
    {
      title: '配置时间',
      dataIndex: 'configured_at',
      key: 'configured_at',
      render: (time) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<SettingOutlined />}
            onClick={() => openConfigDrawer(record)}
          >
            配置
          </Button>
        </Space>
      ),
    },
  ];

  // 打开配置抽屉
  const openConfigDrawer = (module) => {
    setSelectedModule(module);
    form.setFieldsValue({
      is_enabled: module.is_enabled,
      is_visible: module.is_visible,
      custom_config: JSON.stringify(module.custom_config || {}, null, 2),
    });
    setConfigDrawerVisible(true);
  };

  // 保存模块配置
  const handleSaveConfig = async () => {
    try {
      const values = await form.validateFields();
      let customConfig = {};
      
      if (values.custom_config) {
        try {
          customConfig = JSON.parse(values.custom_config);
        } catch (e) {
          message.error('自定义配置JSON格式错误');
          return;
        }
      }

      const success = await configureTenantModule(selectedTenant, selectedModule.id, {
        is_enabled: values.is_enabled,
        is_visible: values.is_visible,
        custom_config: customConfig,
      });

      if (success) {
        setConfigDrawerVisible(false);
      }
    } catch (error) {
      console.error('保存配置失败:', error);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>租户模块管理</Title>
      
      {/* 临时调试组件 */}
      <DebugAuth />
      
      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总租户数"
              value={statistics.total_tenants || 0}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总模块数"
              value={statistics.total_modules || 0}
              prefix={<AppstoreOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃租户"
              value={statistics.tenant_statistics?.length || 0}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均模块覆盖率"
              value={
                statistics.tenant_statistics?.length > 0
                  ? (statistics.tenant_statistics.reduce((sum, t) => sum + t.module_coverage, 0) / statistics.tenant_statistics.length).toFixed(1)
                  : 0
              }
              suffix="%"
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 租户选择 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={8}>
            <Select
              placeholder="选择租户"
              style={{ width: '100%' }}
              value={selectedTenant}
              onChange={setSelectedTenant}
              showSearch
              optionFilterProp="children"
            >
              {tenants.map(tenant => (
                <Option key={tenant.id} value={tenant.id}>
                  {tenant.name}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={16}>
            <Space>
              {selectedTenant && (
                <>
                  <Button
                    type="primary"
                    icon={<ReloadOutlined />}
                    onClick={() => initializeTenantModules(selectedTenant)}
                    loading={loading}
                  >
                    初始化模块
                  </Button>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={() => fetchTenantModules(selectedTenant)}
                  >
                    刷新
                  </Button>
                </>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 模块列表 */}
      {selectedTenant && (
        <Card title={`租户模块配置 - ${tenants.find(t => t.id === selectedTenant)?.name}`}>
          <Table
            columns={moduleColumns}
            dataSource={tenantModules}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
            }}
          />
        </Card>
      )}

      {/* 配置抽屉 */}
      <Drawer
        title={`配置模块: ${selectedModule?.display_name}`}
        width={600}
        open={configDrawerVisible}
        onClose={() => setConfigDrawerVisible(false)}
        extra={
          <Space>
            <Button onClick={() => setConfigDrawerVisible(false)}>取消</Button>
            <Button type="primary" onClick={handleSaveConfig}>
              保存
            </Button>
          </Space>
        }
      >
        {selectedModule && (
          <Form form={form} layout="vertical">
            <Descriptions title="模块信息" bordered size="small" style={{ marginBottom: 24 }}>
              <Descriptions.Item label="模块名称">{selectedModule.display_name}</Descriptions.Item>
              <Descriptions.Item label="分类">{selectedModule.category}</Descriptions.Item>
              <Descriptions.Item label="版本">{selectedModule.version}</Descriptions.Item>
              <Descriptions.Item label="是否核心模块" span={3}>
                {selectedModule.is_core ? '是' : '否'}
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={3}>
                {selectedModule.description}
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <Form.Item
              name="is_enabled"
              label="启用模块"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="is_visible"
              label="模块可见"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="custom_config"
              label="自定义配置 (JSON)"
            >
              <TextArea
                rows={10}
                placeholder="请输入有效的JSON配置"
              />
            </Form.Item>
          </Form>
        )}
      </Drawer>
    </div>
  );
};

export default TenantModuleManagement; 