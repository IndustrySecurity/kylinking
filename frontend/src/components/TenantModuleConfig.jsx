import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Switch,
  Button,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Tabs,
  Statistic,
  Row,
  Col,
  Badge,
  Tooltip,
  Drawer,
  Divider
} from 'antd';
import {
  SettingOutlined,
  EyeOutlined,
  EditOutlined,
  ExportOutlined,
  ReloadOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;
const { Option } = Select;
const { TextArea } = Input;

const TenantModuleConfig = () => {
  const [modules, setModules] = useState([]);
  const [configSummary, setConfigSummary] = useState({});
  const [loading, setLoading] = useState(false);
  const [fieldModalVisible, setFieldModalVisible] = useState(false);
  const [selectedModule, setSelectedModule] = useState(null);
  const [moduleFields, setModuleFields] = useState([]);
  const [fieldConfigForm] = Form.useForm();
  const [extensionDrawerVisible, setExtensionDrawerVisible] = useState(false);
  const [extensions, setExtensions] = useState([]);
  const [activeTab, setActiveTab] = useState('modules');

  // 获取租户模块列表
  const fetchModules = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/tenant/modules/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.data.success) {
        setModules(response.data.data);
      }
    } catch (error) {
      message.error('获取模块列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取配置概要
  const fetchConfigSummary = async () => {
    try {
      const response = await axios.get('/api/tenant/modules/config', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.data.success) {
        setConfigSummary(response.data.data);
      }
    } catch (error) {
      message.error('获取配置概要失败');
    }
  };

  // 获取扩展列表
  const fetchExtensions = async () => {
    try {
      const response = await axios.get('/api/tenant/modules/extensions', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.data.success) {
        setExtensions(response.data.data);
      }
    } catch (error) {
      message.error('获取扩展列表失败');
    }
  };

  useEffect(() => {
    fetchModules();
    fetchConfigSummary();
    fetchExtensions();
  }, []);

  // 配置模块启用状态
  const handleModuleToggle = async (moduleId, enabled) => {
    try {
      const response = await axios.post(`/api/tenant/modules/${moduleId}/configure`, {
        is_enabled: enabled
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.data.success) {
        message.success(`模块${enabled ? '启用' : '禁用'}成功`);
        fetchModules();
        fetchConfigSummary();
      }
    } catch (error) {
      message.error(`模块配置失败: ${error.response?.data?.error || error.message}`);
    }
  };

  // 配置模块可见性
  const handleModuleVisibilityToggle = async (moduleId, visible) => {
    try {
      const response = await axios.post(`/api/tenant/modules/${moduleId}/configure`, {
        is_visible: visible
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.data.success) {
        message.success(`模块${visible ? '显示' : '隐藏'}成功`);
        fetchModules();
      }
    } catch (error) {
      message.error(`模块配置失败: ${error.response?.data?.error || error.message}`);
    }
  };

  // 获取模块字段
  const fetchModuleFields = async (moduleId) => {
    try {
      const response = await axios.get(`/api/tenant/modules/${moduleId}/fields`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.data.success) {
        setModuleFields(response.data.data);
      }
    } catch (error) {
      message.error('获取模块字段失败');
    }
  };

  // 打开字段配置模态框
  const handleConfigureFields = (module) => {
    setSelectedModule(module);
    setFieldModalVisible(true);
    fetchModuleFields(module.id);
  };

  // 配置字段
  const handleFieldConfig = async (fieldId, config) => {
    try {
      const response = await axios.post(
        `/api/tenant/modules/${selectedModule.id}/fields/${fieldId}/configure`,
        config,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }
      );
      
      if (response.data.success) {
        message.success('字段配置成功');
        fetchModuleFields(selectedModule.id);
      }
    } catch (error) {
      message.error(`字段配置失败: ${error.response?.data?.error || error.message}`);
    }
  };

  // 初始化租户配置
  const handleInitializeConfig = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/tenant/modules/config/initialize', {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.data.success) {
        message.success('租户配置初始化成功');
        fetchModules();
        fetchConfigSummary();
      }
    } catch (error) {
      message.error(`初始化失败: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 导出配置
  const handleExportConfig = async () => {
    try {
      const response = await axios.get('/api/tenant/modules/config/export', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.data.success) {
        const configData = JSON.stringify(response.data.data, null, 2);
        const blob = new Blob([configData], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tenant-config-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
        message.success('配置导出成功');
      }
    } catch (error) {
      message.error('配置导出失败');
    }
  };

  const moduleColumns = [
    {
      title: '模块名称',
      dataIndex: 'display_name',
      key: 'display_name',
      render: (text, record) => (
        <Space>
          <span>{text}</span>
          {record.is_core && <Tag color="gold">核心模块</Tag>}
        </Space>
      )
    },
    {
      title: '类别',
      dataIndex: 'category',
      key: 'category',
      render: (category) => {
        const categoryMap = {
          production: { color: 'blue', text: '生产' },
          quality: { color: 'green', text: '质量' },
          inventory: { color: 'orange', text: '库存' },
          maintenance: { color: 'purple', text: '维护' },
          analytics: { color: 'cyan', text: '分析' }
        };
        const config = categoryMap[category] || { color: 'default', text: category };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '状态',
      key: 'status',
      render: (_, record) => (
        <Space>
          <Badge 
            status={record.is_enabled ? 'success' : 'default'} 
            text={record.is_enabled ? '已启用' : '未启用'} 
          />
          {record.is_enabled && !record.is_visible && (
            <Tag color="orange">已隐藏</Tag>
          )}
        </Space>
      )
    },
    {
      title: '启用',
      key: 'enabled',
      render: (_, record) => (
        <Switch
          checked={record.is_enabled}
          onChange={(checked) => handleModuleToggle(record.id, checked)}
          disabled={record.is_core}
        />
      )
    },
    {
      title: '显示',
      key: 'visible',
      render: (_, record) => (
        <Switch
          checked={record.is_visible}
          onChange={(checked) => handleModuleVisibilityToggle(record.id, checked)}
          disabled={!record.is_enabled}
        />
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => {
                Modal.info({
                  title: record.display_name,
                  content: (
                    <div>
                      <p><strong>描述:</strong> {record.description}</p>
                      <p><strong>版本:</strong> {record.version}</p>
                      <p><strong>依赖:</strong> {record.dependencies?.join(', ') || '无'}</p>
                    </div>
                  ),
                  width: 600
                });
              }}
            />
          </Tooltip>
          <Tooltip title="配置字段">
            <Button
              type="text"
              icon={<SettingOutlined />}
              onClick={() => handleConfigureFields(record)}
              disabled={!record.is_enabled}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  const fieldColumns = [
    {
      title: '字段名称',
      dataIndex: 'display_name',
      key: 'display_name',
      render: (text, record) => (
        <Space>
          <span>{text}</span>
          {record.is_system_field && <Tag color="red" size="small">系统</Tag>}
          {record.is_required && <Tag color="orange" size="small">必填</Tag>}
        </Space>
      )
    },
    {
      title: '字段类型',
      dataIndex: 'field_type',
      key: 'field_type',
      render: (type) => <Tag>{type}</Tag>
    },
    {
      title: '自定义标签',
      dataIndex: 'custom_label',
      key: 'custom_label',
      render: (label, record) => label || record.display_name
    },
    {
      title: '状态',
      key: 'field_status',
      render: (_, record) => (
        <Space>
          <Switch
            size="small"
            checked={record.is_enabled}
            onChange={(checked) => handleFieldConfig(record.id, { is_enabled: checked })}
            disabled={record.is_system_field}
          />
          <span>{record.is_enabled ? '启用' : '禁用'}</span>
        </Space>
      )
    },
    {
      title: '操作',
      key: 'field_actions',
      render: (_, record) => (
        <Button
          type="text"
          icon={<EditOutlined />}
          onClick={() => {
            fieldConfigForm.setFieldsValue({
              custom_label: record.custom_label,
              custom_placeholder: record.custom_placeholder,
              custom_help_text: record.custom_help_text,
              is_required: record.is_required_override,
              is_readonly: record.is_readonly,
              display_order: record.display_order,
              column_width: record.column_width,
              field_group: record.field_group
            });
            
            Modal.confirm({
              title: `配置字段: ${record.display_name}`,
              content: (
                <Form form={fieldConfigForm} layout="vertical">
                  <Form.Item name="custom_label" label="自定义标签">
                    <Input placeholder={record.display_name} />
                  </Form.Item>
                  <Form.Item name="custom_placeholder" label="占位符">
                    <Input />
                  </Form.Item>
                  <Form.Item name="custom_help_text" label="帮助文本">
                    <TextArea rows={2} />
                  </Form.Item>
                  <Row gutter={16}>
                    <Col span={8}>
                      <Form.Item name="is_required" valuePropName="checked" label="必填">
                        <Switch disabled={record.is_system_field} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item name="is_readonly" valuePropName="checked" label="只读">
                        <Switch />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item name="display_order" label="显示顺序">
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item name="column_width" label="列宽度(%)">
                        <InputNumber min={1} max={100} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="field_group" label="字段分组">
                        <Input />
                      </Form.Item>
                    </Col>
                  </Row>
                </Form>
              ),
              width: 600,
              onOk: async () => {
                const values = fieldConfigForm.getFieldsValue();
                await handleFieldConfig(record.id, values);
              }
            });
          }}
          disabled={!record.is_configurable}
        >
          配置
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card title="租户模块配置" style={{ marginBottom: '24px' }}>
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Statistic
              title="已启用模块"
              value={configSummary.enabled_modules || 0}
              suffix={`/ ${configSummary.total_modules || 0}`}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="模块覆盖率"
              value={configSummary.module_coverage || 0}
              suffix="%"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="自定义字段配置"
              value={configSummary.custom_field_configs || 0}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="扩展数量"
              value={configSummary.extensions || 0}
            />
          </Col>
        </Row>

        <Space style={{ marginBottom: '16px' }}>
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            onClick={handleInitializeConfig}
            loading={loading}
          >
            初始化配置
          </Button>
          <Button
            icon={<ExportOutlined />}
            onClick={handleExportConfig}
          >
            导出配置
          </Button>
          <Button
            icon={<SettingOutlined />}
            onClick={() => setExtensionDrawerVisible(true)}
          >
            管理扩展
          </Button>
        </Space>

        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="模块配置" key="modules">
            <Table
              columns={moduleColumns}
              dataSource={modules}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* 字段配置模态框 */}
      <Modal
        title={`${selectedModule?.display_name} - 字段配置`}
        visible={fieldModalVisible}
        onCancel={() => setFieldModalVisible(false)}
        width={1000}
        footer={null}
      >
        <Table
          columns={fieldColumns}
          dataSource={moduleFields}
          rowKey="id"
          size="small"
          pagination={{ pageSize: 8 }}
        />
      </Modal>

      {/* 扩展管理抽屉 */}
      <Drawer
        title="扩展管理"
        visible={extensionDrawerVisible}
        onClose={() => setExtensionDrawerVisible(false)}
        width={600}
      >
        <div>
          <Button type="primary" style={{ marginBottom: '16px' }}>
            创建扩展
          </Button>
          {extensions.map(ext => (
            <Card key={ext.id} size="small" style={{ marginBottom: '12px' }}>
              <Card.Meta
                title={ext.extension_name}
                description={
                  <div>
                    <Tag>{ext.extension_type}</Tag>
                    <p style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                      {ext.extension_key}
                    </p>
                  </div>
                }
              />
            </Card>
          ))}
        </div>
      </Drawer>
    </div>
  );
};

export default TenantModuleConfig; 