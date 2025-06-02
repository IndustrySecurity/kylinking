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
  InputNumber,
  Tooltip
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { bagTypeApi } from '../../api/bagType';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const BagTypeManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingBagType, setEditingBagType] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [enabledFilter, setEnabledFilter] = useState(undefined);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });

  // 表单和选项数据
  const [form] = Form.useForm();
  const [formOptions, setFormOptions] = useState({
    units: [],
    spec_expressions: []
  });

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await bagTypeApi.getBagTypes({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        is_enabled: enabledFilter,
        ...params
      });

      if (response.data.success) {
        const { bag_types, total, current_page } = response.data.data;
        
        // 为每行数据添加key
        const dataWithKeys = bag_types.map((item, index) => ({
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

  // 加载表单选项数据
  const loadFormOptions = async () => {
    try {
      const response = await bagTypeApi.getFormOptions();
      if (response.data.success) {
        setFormOptions(response.data.data);
      }
    } catch (error) {
      message.error('加载选项数据失败：' + (error.response?.data?.message || error.message));
    }
  };

  // 初始加载
  useEffect(() => {
    loadData();
    loadFormOptions();
  }, []);

  // 监听搜索和筛选条件变化
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      setPagination(prev => ({ ...prev, current: 1 }));
      loadData({ page: 1 });
    }, 300);

    return () => clearTimeout(delayedSearch);
  }, [searchText, enabledFilter]);

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setEnabledFilter(undefined);
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '', is_enabled: undefined });
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize
    });
  };

  // 显示新增/编辑模态框
  const showModal = (record = null) => {
    setEditingBagType(record);
    if (record) {
      form.setFieldsValue({
        ...record,
        // 确保数值字段正确显示
        difficulty_coefficient: record.difficulty_coefficient || 0,
        bag_making_unit_price: record.bag_making_unit_price || 0,
        sort_order: record.sort_order || 0
      });
    } else {
      form.resetFields();
      form.setFieldsValue({
        is_enabled: true,
        is_strict_bag_type: true,
        difficulty_coefficient: 0,
        bag_making_unit_price: 0,
        sort_order: 0
      });
    }
    setModalVisible(true);
  };

  // 保存袋型
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      let response;
      if (editingBagType) {
        response = await bagTypeApi.updateBagType(editingBagType.id, values);
        if (response.data.success) {
          message.success('更新成功');
        }
      } else {
        response = await bagTypeApi.createBagType(values);
        if (response.data.success) {
          message.success('创建成功');
        }
      }

      setModalVisible(false);
      loadData();
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        message.error('保存失败：' + (error.response?.data?.message || error.message));
      }
    }
  };

  // 删除袋型
  const handleDelete = async (id) => {
    try {
      await bagTypeApi.deleteBagType(id);
      message.success('删除成功');
      loadData();
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.message || error.message));
    }
  };

  const handleStatusChange = async (id, checked) => {
    try {
      await bagTypeApi.updateBagType(id, { is_enabled: checked });
      message.success('状态更新成功');
      loadData();
    } catch (error) {
      message.error('状态更新失败：' + (error.response?.data?.message || error.message));
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '袋型名称',
      dataIndex: 'bag_type_name',
      key: 'bag_type_name',
      width: 150,
      fixed: 'left',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '规格表达式',
      dataIndex: 'spec_expression',
      key: 'spec_expression',
      width: 150,
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      )
    },
    {
      title: '生产单位',
      dataIndex: 'production_unit_name',
      key: 'production_unit_name',
      width: 100,
      align: 'center'
    },
    {
      title: '销售单位',
      dataIndex: 'sales_unit_name',
      key: 'sales_unit_name',
      width: 100,
      align: 'center'
    },
    {
      title: '难易系数',
      dataIndex: 'difficulty_coefficient',
      key: 'difficulty_coefficient',
      width: 120,
      render: (value) => value ? Number(value).toFixed(2) : '0.00'
    },
    {
      title: '制袋单价',
      dataIndex: 'bag_making_unit_price',
      key: 'bag_making_unit_price',
      width: 120,
      render: (value) => value ? Number(value).toFixed(2) : '0.00'
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      align: 'center'
    },
    {
      title: '卷膜',
      dataIndex: 'is_roll_film',
      key: 'is_roll_film',
      width: 80,
      align: 'center',
      render: (value) => <Switch checked={value} disabled size="small" />
    },
    {
      title: '严格袋型',
      dataIndex: 'is_strict_bag_type',
      key: 'is_strict_bag_type',
      width: 100,
      align: 'center',
      render: (value) => <Switch checked={value} disabled size="small" />
    },
    {
      title: '自定规格',
      dataIndex: 'is_custom_spec',
      key: 'is_custom_spec',
      width: 100,
      align: 'center',
      render: (value) => <Switch checked={value} disabled size="small" />
    },
    {
      title: '工序判断',
      dataIndex: 'is_process_judgment',
      key: 'is_process_judgment',
      width: 100,
      align: 'center',
      render: (value) => <Switch checked={value} disabled size="small" />
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 100,
      align: 'center',
      render: (enabled, record) => (
        <Switch
          checked={enabled}
          size="small"
          onChange={(checked) => handleStatusChange(record.id, checked)}
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
      align: 'center'
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      align: 'center',
      render: (text) => text ? new Date(text).toLocaleString() : ''
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right',
      align: 'center',
      render: (_, record) => (
        <Space>
          <Button
            icon={<EditOutlined />}
            type="link"
            size="small"
            onClick={() => showModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这个袋型吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              icon={<DeleteOutlined />}
              type="link"
              size="small"
              danger
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>袋型管理</Title>
        </div>

        {/* 搜索和筛选区域 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Input
              placeholder="搜索袋型名称、规格表达式"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder="状态筛选"
              value={enabledFilter}
              onChange={setEnabledFilter}
              allowClear
              style={{ width: '100%' }}
            >
              <Option value={true}>启用</Option>
              <Option value={false}>停用</Option>
            </Select>
          </Col>
          <Col span={14}>
            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => showModal()}
              >
                新增袋型
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => loadData()}
              >
                刷新
              </Button>
              <Button onClick={handleReset}>重置</Button>
            </Space>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 'max-content' }}
          size="small"
        />
      </Card>

      {/* 新增/编辑模态框 */}
      <Modal
        title={editingBagType ? '编辑袋型' : '新增袋型'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={800}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="袋型名称"
                name="bag_type_name"
                rules={[{ required: true, message: '请输入袋型名称' }]}
              >
                <Input placeholder="请输入袋型名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="规格表达式"
                name="spec_expression"
              >
                <Select
                  placeholder="请选择规格表达式"
                  allowClear
                  showSearch
                  optionFilterProp="children"
                >
                  {formOptions.spec_expressions.map(item => (
                    <Option key={item.value} value={item.value} title={item.description}>
                      {item.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="生产单位"
                name="production_unit_id"
              >
                <Select placeholder="请选择生产单位" allowClear>
                  {formOptions.units.map(unit => (
                    <Option key={unit.value} value={unit.value}>
                      {unit.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="销售单位"
                name="sales_unit_id"
              >
                <Select placeholder="请选择销售单位" allowClear>
                  {formOptions.units.map(unit => (
                    <Option key={unit.value} value={unit.value}>
                      {unit.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="difficulty_coefficient"
                label="难易系数"
                rules={[
                  { type: 'number', min: 0, message: '难易系数不能小于0' }
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入难易系数"
                  min={0}
                  precision={2}
                  step={0.01}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="bag_making_unit_price"
                label="制袋单价"
                rules={[
                  { type: 'number', min: 0, message: '制袋单价不能小于0' }
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入制袋单价"
                  min={0}
                  precision={2}
                  step={0.01}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="排序"
                name="sort_order"
              >
                <InputNumber 
                  min={0} 
                  style={{ width: '100%' }} 
                  placeholder="0"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item
                label="卷膜"
                name="is_roll_film"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                label="停用"
                name="is_disabled"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                label="自定规格"
                name="is_custom_spec"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                label="严格袋型"
                name="is_strict_bag_type"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item
                label="工序判断"
                name="is_process_judgment"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                label="是否纸尿裤"
                name="is_diaper"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                label="是否编织袋"
                name="is_woven_bag"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                label="是否标签"
                name="is_label"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="是否天线"
                name="is_antenna"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="是否启用"
                name="is_enabled"
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
        </Form>
      </Modal>
    </div>
  );
};

export default BagTypeManagement; 