import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Select,
  Space,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Form,
  Modal,
  Switch,
  Tag,
  Tooltip,
  TreeSelect
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { warehouseApi } from '../../../api/base-archive/production-archive/warehouse';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const WarehouseManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [warehouseTypeFilter, setWarehouseTypeFilter] = useState(undefined);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });

  // 表单和选项数据
  const [form] = Form.useForm();
  const [warehouseTypes, setWarehouseTypes] = useState([]);
  const [accountingMethods, setAccountingMethods] = useState([]);
  const [circulationTypes, setCirculationTypes] = useState([]);
  const [warehouseOptions, setWarehouseOptions] = useState([]);

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await warehouseApi.getWarehouses({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        warehouse_type: warehouseTypeFilter,
        ...params
      });

      if (response.data.success) {
        const { warehouses, total, current_page } = response.data.data;
        
        const dataWithKeys = (warehouses || []).map((item, index) => ({
          ...item,
          key: item.id || `temp_${index}`
        }));
        
        setData(dataWithKeys);
        setPagination(prev => ({
          ...prev,
          total,
          current: current_page
        }));
      }
    } catch (error) {
      message.error('加载数据失败：' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  // 初始化选项数据（使用默认值）
  const loadOptions = () => {
    // 直接设置默认选项，不再调用可能失败的API
    setWarehouseTypes([
      { value: 'material', label: '材料仓' },
      { value: 'finished_goods', label: '成品仓' },
      { value: 'semi_finished', label: '半成品仓' },
      { value: 'waste', label: '废料仓' }
    ]);

    setAccountingMethods([
      { value: 'individual_cost', label: '个别计价' },
      { value: 'weighted_average', label: '加权平均' },
      { value: 'moving_average', label: '移动平均' },
      { value: 'fifo', label: '先进先出' },
      { value: 'lifo', label: '后进先出' }
    ]);

    setCirculationTypes([
      { value: 'on_site_circulation', label: '现场流转' },
      { value: 'warehouse_circulation', label: '仓库流转' },
      { value: 'external_circulation', label: '外部流转' }
    ]);

    // 仓库选项暂时设为空，可以在需要时从数据中提取
    setWarehouseOptions([]);
  };

  // 初始加载
  useEffect(() => {
    loadData();
    loadOptions();
  }, []);

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setWarehouseTypeFilter(undefined);
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '', warehouse_type: '' });
  };

  // 刷新数据
  const handleRefresh = () => {
    loadData();
    loadOptions();
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize
    });
  };

  // 打开编辑模态框
  const handleEdit = async (record = null) => {
    if (record) {
      // 编辑模式，填充表单数据
      const formData = {
        ...record,
        warehouse_type: record.warehouse_type || 'material',
        accounting_method: record.accounting_method || 'individual_cost',
        circulation_type: record.circulation_type || 'on_site_circulation',
        parent_warehouse_id: record.parent_warehouse_id || undefined,
      };
      form.setFieldsValue(formData);
    } else {
      // 新增模式，先重置表单并清空所有字段
      form.resetFields();
      
      // 等待一个微任务周期，确保表单完全重置
      await new Promise(resolve => setTimeout(resolve, 0));
      
      // 设置默认值，使用简单的时间戳作为仓库编号
      const defaultWarehouseCode = `WH${Date.now().toString().slice(-6)}`;
      form.setFieldsValue({
        warehouse_code: defaultWarehouseCode,
        warehouse_name: '',
        warehouse_type: 'material',
        parent_warehouse_id: undefined,
        accounting_method: 'individual_cost',
        circulation_type: 'on_site_circulation',
        exclude_from_operations: false,
        is_abnormal: false,
        is_carryover_warehouse: false,
        exclude_from_docking: false,
        is_in_stocktaking: false,
        description: '',
        sort_order: 0,
        is_enabled: true
      });
    }
    setModalVisible(true);
    setEditingWarehouse(record);
  };

  // 保存仓库
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      let response;
      if (editingWarehouse) {
        response = await warehouseApi.updateWarehouse(editingWarehouse.id, values);
        if (response.data.success) {
          message.success('更新成功');
        }
      } else {
        response = await warehouseApi.createWarehouse(values);
        if (response.data.success) {
          message.success('创建成功');
        }
      }

      setModalVisible(false);
      loadData();
      loadOptions(); // 重新加载选项数据以更新上级仓库列表
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        message.error('保存失败：' + (error.response?.data?.message || error.message));
      }
    }
  };

  // 删除仓库
  const handleDelete = async (id) => {
    try {
      const response = await warehouseApi.deleteWarehouse(id);
      if (response.data.success) {
        message.success('删除成功');
        loadData();
        loadOptions(); // 重新加载选项数据
      }
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.message || error.message));
    }
  };

  // 构建仓库树形数据
  const buildWarehouseTreeData = (warehouses, currentId = null) => {
    return warehouses
      .filter(item => item.value !== currentId) // 排除自己
      .map(item => ({
        title: item.label,
        value: item.value,
        key: item.value
      }));
  };

  // 获取仓库类型标签颜色
  const getWarehouseTypeColor = (type) => {
    const colorMap = {
      'material': 'blue',
      'finished_goods': 'green',
      'semi_finished': 'orange',
      'plate_roller': 'purple'
    };
    return colorMap[type] || 'default';
  };

  // 表格列定义
  const columns = [
    {
      title: '仓库编号',
      dataIndex: 'warehouse_code',
      key: 'warehouse_code',
      width: 120,
      render: (text) => text
    },
    {
      title: '仓库名称',
      dataIndex: 'warehouse_name',
      key: 'warehouse_name',
      width: 150,
      render: (text) => <span style={{ fontWeight: 500 }}>{text}</span>
    },
    {
      title: '仓库类型',
      dataIndex: 'warehouse_type',
      key: 'warehouse_type',
      width: 120,
      render: (type) => {
        const typeObj = warehouseTypes.find(t => t.value === type);
        return typeObj ? (
          <Tag color={getWarehouseTypeColor(type)}>{typeObj.label}</Tag>
        ) : type;
      }
    },
    {
      title: '上级仓库',
      dataIndex: 'parent_warehouse_name',
      key: 'parent_warehouse_name',
      width: 120,
      render: (text) => text || '-'
    },
    {
      title: '核算方式',
      dataIndex: 'accounting_method',
      key: 'accounting_method',
      width: 100,
      render: (method) => {
        const methodObj = accountingMethods.find(m => m.value === method);
        return methodObj ? methodObj.label : (method || '-');
      }
    },
    {
      title: '流转类型',
      dataIndex: 'circulation_type',
      key: 'circulation_type',
      width: 100,
      render: (type) => {
        const typeObj = circulationTypes.find(t => t.value === type);
        return typeObj ? typeObj.label : (type || '-');
      }
    },
    {
      title: '状态标识',
      key: 'status_flags',
      width: 200,
      render: (_, record) => (
        <Space wrap>
          {record.exclude_from_operations && <Tag color="red">不参与运行</Tag>}
          {record.is_abnormal && <Tag color="orange">异常</Tag>}
          {record.is_carryover_warehouse && <Tag color="blue">结转仓</Tag>}
          {record.exclude_from_docking && <Tag color="purple">不对接</Tag>}
          {record.is_in_stocktaking && <Tag color="cyan">盘点中</Tag>}
        </Space>
      )
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      align: 'center'
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      align: 'center',
      render: (enabled) => (
        <Switch 
          checked={enabled}
          disabled
          size="small"
        />
      )
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      key: 'created_by_name',
      width: 100,
      align: 'center'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      align: 'center',
      render: (text) => text ? new Date(text).toLocaleString() : ''
    },
    {
      title: '修改人',
      dataIndex: 'updated_by_name',
      key: 'updated_by_name',
      width: 100,
      align: 'center',
      render: (text) => text || '-'
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      align: 'center',
      render: (text) => text ? new Date(text).toLocaleString() : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      align: 'center',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这个仓库吗？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={4} style={{ margin: 0 }}>仓库管理</Title>
            </Col>
            <Col>
              <Space>
                <Input
                  placeholder="搜索仓库编号、名称"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={handleSearch}
                  style={{ width: 200 }}
                  prefix={<SearchOutlined />}
                />
                <Select
                  placeholder="选择仓库类型"
                  value={warehouseTypeFilter}
                  onChange={setWarehouseTypeFilter}
                  style={{ width: 150 }}
                  allowClear
                >
                  {warehouseTypes.map(type => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
                <Button onClick={handleSearch} type="primary">
                  搜索
                </Button>
                <Button onClick={handleReset}>
                  重置
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => handleEdit()}
                >
                  新增仓库
                </Button>
                <Button 
                  icon={<ReloadOutlined />}
                  onClick={handleRefresh}
                >
                  刷新
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        <Table
          dataSource={data}
          columns={columns}
          rowKey="key"
          pagination={pagination}
          loading={loading}
          onChange={handleTableChange}
          scroll={{ x: 2000 }}
          size="small"
        />
      </Card>

      {/* 编辑模态框 */}
      <Modal
        title={editingWarehouse ? '编辑仓库' : '新增仓库'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        width={800}
        footer={[
          <Button key="cancel" onClick={() => setModalVisible(false)}>
            取消
          </Button>,
          <Button key="submit" type="primary" onClick={handleSave}>
            保存
          </Button>
        ]}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            warehouse_type: 'material',
            accounting_method: 'individual_cost',
            circulation_type: 'on_site_circulation',
            sort_order: 0,
            is_enabled: true,
            exclude_from_operations: false,
            is_abnormal: false,
            is_carryover_warehouse: false,
            exclude_from_docking: false,
            is_in_stocktaking: false
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="仓库编号"
                name="warehouse_code"
              >
                <Input placeholder="系统自动生成" disabled />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="仓库名称"
                name="warehouse_name"
                rules={[{ required: true, message: '请输入仓库名称' }]}
              >
                <Input placeholder="请输入仓库名称" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="仓库类型"
                name="warehouse_type"
              >
                <Select placeholder="请选择仓库类型">
                  {warehouseTypes.map(type => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="上级仓库"
                name="parent_warehouse_id"
              >
                <Select 
                  placeholder="请选择上级仓库"
                  allowClear
                  showSearch
                  filterOption={(input, option) =>
                    (option?.children ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                >
                  {buildWarehouseTreeData(warehouseOptions, editingWarehouse?.id).map(item => (
                    <Option key={item.value} value={item.value}>
                      {item.title}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="核算方式"
                name="accounting_method"
              >
                <Select placeholder="请选择核算方式">
                  {accountingMethods.map(method => (
                    <Option key={method.value} value={method.value}>
                      {method.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="流转类型"
                name="circulation_type"
              >
                <Select placeholder="请选择流转类型">
                  {circulationTypes.map(type => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <div style={{ margin: '16px 0 8px 0', fontSize: '14px', fontWeight: 500, color: '#262626' }}>
            状态标识
          </div>
          
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="不参与运行"
                name="exclude_from_operations"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="异常"
                name="is_abnormal"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="结转仓"
                name="is_carryover_warehouse"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="不对接"
                name="exclude_from_docking"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="盘点中"
                name="is_in_stocktaking"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="描述"
            name="description"
          >
            <TextArea rows={3} placeholder="请输入描述" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="排序"
                name="sort_order"
              >
                <Input type="number" placeholder="排序值" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="是否启用"
                name="is_enabled"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default WarehouseManagement; 