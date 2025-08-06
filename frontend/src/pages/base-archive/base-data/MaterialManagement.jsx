import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Switch,
  InputNumber,
  Select,
  Space,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Form,
  Modal,
  Tabs,
  Divider,
  Checkbox,
  DatePicker,
  Upload,
  Tag,
  Tooltip,
  Badge
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined,

  UploadOutlined,
  DownloadOutlined,
  FilterOutlined,
  ClearOutlined,
  CopyOutlined
} from '@ant-design/icons';
import { materialManagementApi } from '../../../api/base-archive/base-data/materialManagement';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const MaterialManagement = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });

  // 表单和模态框状态
  const [form] = Form.useForm();
  const [modalVisible, setModalVisible] = useState(false);

  const [currentRecord, setCurrentRecord] = useState(null);
  const [modalType, setModalType] = useState('add'); // add, edit, view

  // 搜索和过滤状态
  const [searchText, setSearchText] = useState('');
  const [materialCategoryFilter, setMaterialCategoryFilter] = useState('');
  const [inspectionTypeFilter, setInspectionTypeFilter] = useState('');
  const [enabledFilter, setEnabledFilter] = useState('');

  // 选项数据
  const [options, setOptions] = useState({
    material_categories: [],
    units: [],
    calculation_schemes: [],
    inspection_types: [],
    security_codes: [],
    subjects: []
  });

  // 表格列定义
  const columns = [
    {
      title: '材料编号',
      dataIndex: 'material_code',
      key: 'material_code',
      width: 120,
      fixed: 'left',
      render: (text) => <Text code>{text}</Text>
    },
    {
      title: '材料名称',
      dataIndex: 'material_name',
      key: 'material_name',
      width: 200,
      fixed: 'left',
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          <Text strong>{text}</Text>
        </Tooltip>
      )
    },
    {
      title: '材料分类',
      dataIndex: 'material_category_id',
      key: 'material_category_id',
      width: 150,
      ellipsis: true,
      render: (categoryId) => {
        if (!categoryId) return '-';
        const category = options.material_categories?.find(cat => cat.id === categoryId);
        return category ? (
          <Tooltip placement="topLeft" title={category.material_name || category.name}>
            <Text>{category.material_name || category.name}</Text>
          </Tooltip>
        ) : (
          <Text type="secondary">{categoryId}</Text>
        );
      }
    },
    {
      title: '材料属性',
      dataIndex: 'material_attribute',
      key: 'material_attribute',
      width: 100,
      render: (text) => text ? <Tag color="blue">{text}</Tag> : null
    },
    {
      title: '单位',
      dataIndex: 'unit_name',
      key: 'unit_name',
      width: 80
    },
    {
      title: '规格型号',
      dataIndex: 'specification_model',
      key: 'specification_model',
      width: 150,
      ellipsis: true
    },
    {
      title: '密度',
      dataIndex: 'density',
      key: 'density',
      width: 80,
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '检验类型',
      dataIndex: 'inspection_type',
      key: 'inspection_type',
      width: 100,
      render: (value) => {
        const colorMap = {
          'exempt': 'green',
          'spot_check': 'orange',
          'full_check': 'red'
        };
        const textMap = {
          'exempt': '免检',
          'spot_check': '抽检',
          'full_check': '全检'
        };
        return <Tag color={colorMap[value]}>{textMap[value] || value}</Tag>;
      }
    },
    {
      title: '采购价',
      dataIndex: 'purchase_price',
      key: 'purchase_price',
      width: 100,
      align: 'right',
      render: (value) => value ? `¥${value}` : '-'
    },
    {
      title: '最近采购价',
      dataIndex: 'latest_purchase_price',
      key: 'latest_purchase_price',
      width: 120,
      align: 'right',
      render: (value) => value ? `¥${value}` : '-'
    },
    {
      title: '库存信息',
      key: 'stock_info',
      width: 120,
      render: (_, record) => (
        <div>
          {record.min_stock_start && (
            <div><Text type="secondary">最小: {record.min_stock_start}</Text></div>
          )}
          {record.max_stock && (
            <div><Text type="secondary">最大: {record.max_stock}</Text></div>
          )}
        </div>
      )
    },
    {
      title: '启用状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 100,
      align: 'center',
      render: (enabled) => (
        <Badge 
          status={enabled ? "success" : "default"} 
          text={enabled ? "启用" : "禁用"} 
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
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
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopy(record)}
          >
            复制
          </Button>
          <Popconfirm
            title="确定删除这条材料记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
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
      ),
    },
  ];

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await materialManagementApi.getMaterials({
        page: pagination.current,
        page_size: pagination.pageSize,
        search: searchText,
        material_category_id: materialCategoryFilter,
        inspection_type: inspectionTypeFilter,
        is_enabled: enabledFilter,
        ...params
      });

      if (response.data.success) {
        setData(response.data.data.items || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.data.total || 0,
          current: response.data.data.page || 1
        }));
      } else {
        // 如果表不存在，显示空数据
        setData([]);
        setPagination(prev => ({
          ...prev,
          total: 0,
          current: 1
        }));
      }
    } catch (error) {
      console.error('加载数据失败：', error);
      if (error.message.includes('does not exist')) {
        message.warning('材料管理表尚未创建，请联系系统管理员');
        setData([]);
      } else {
        message.error('加载数据失败：' + error.message);
        setData([]);
      }
    } finally {
      setLoading(false);
    }
  };

  // 加载表单选项
  const loadOptions = async () => {
    try {
      const response = await materialManagementApi.getFormOptions();
      if (response.data.success) {
        setOptions(response.data.data);
      } else {
        // 设置默认选项
        setOptions({
          material_categories: [],
          units: [],
          calculation_schemes: [],
          inspection_types: [
            { value: 'exempt', label: '免检' },
            { value: 'spot_check', label: '抽检' },
            { value: 'full_check', label: '全检' }
          ],
          security_codes: [],
          subjects: []
        });
      }
    } catch (error) {
      console.error('加载选项数据失败：', error);
      // 设置默认选项
      setOptions({
        material_categories: [],
        units: [],
        calculation_schemes: [],
        inspection_types: [
          { value: 'exempt', label: '免检' },
          { value: 'spot_check', label: '抽检' },
          { value: 'full_check', label: '全检' }
        ],
        security_codes: [],
        subjects: []
      });
    }
  };

  useEffect(() => {
    loadData();
    loadOptions();
  }, []);

  // 处理分页变化
  const handleTableChange = (paginationConfig) => {
    const newPagination = {
      ...pagination,
      current: paginationConfig.current,
      pageSize: paginationConfig.pageSize
    };
    setPagination(newPagination);
    loadData({
      page: paginationConfig.current,
      page_size: paginationConfig.pageSize
    });
  };

  // 搜索处理
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setMaterialCategoryFilter('');
    setInspectionTypeFilter('');
    setEnabledFilter('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ 
      page: 1,
      search: '',
      material_category_id: '',
      inspection_type: '',
      is_enabled: ''
    });
  };

  // 新增
  const handleAdd = () => {
    setCurrentRecord(null);
    setModalType('add');
    form.resetFields();
    setModalVisible(true);
  };

  // 编辑
  const handleEdit = (record) => {
    setCurrentRecord(record);
    setModalType('edit');
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  // 复制新建
  const handleCopy = (record) => {
    setCurrentRecord(null);
    setModalType('add');
    
    // 复制所有字段数据，但排除ID和编号字段
    const copyData = { ...record };
    delete copyData.id;
    delete copyData.material_code; // 编号需要重新生成
    delete copyData.created_at;
    delete copyData.updated_at;
    delete copyData.created_by;
    delete copyData.updated_by;
    
    // 修改材料名称，添加"复制"标识
    if (copyData.material_name) {
      copyData.material_name = `${copyData.material_name} - 复制`;
    }
    
    form.setFieldsValue(copyData);
    setModalVisible(true);
    message.info('已复制材料信息，请修改后保存');
  };



  // 删除
  const handleDelete = async (id) => {
    try {
      const response = await materialManagementApi.deleteMaterial(id);
      if (response.data.success) {
        message.success('删除成功');
        loadData();
      }
    } catch (error) {
      message.error('删除失败：' + error.message);
    }
  };

  // 处理材料分类变化（自动填入）
  const handleMaterialCategoryChange = async (categoryId) => {
    if (!categoryId) return;
    
    try {
      const response = await materialManagementApi.getMaterialCategoryDetails(categoryId);
      if (response.data.success) {
        const details = response.data.data;
        // 自动填入相关字段
        form.setFieldsValue({
          material_attribute: details.material_type,
          unit_id: details.base_unit_id,
          auxiliary_unit_id: details.auxiliary_unit_id,
          sales_unit_id: details.sales_unit_id,
          density: details.density,
          shelf_life_days: details.shelf_life,
          warning_days: details.warning_days,
          is_surface_printing_ink: details.is_ink,
          is_paper_core: details.is_accessory
        });
      }
    } catch (error) {
      console.error('获取材料分类详情失败：', error);
    }
  };

  // 保存
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      let response;
      if (modalType === 'add') {
        response = await materialManagementApi.createMaterial(values);
      } else {
        response = await materialManagementApi.updateMaterial(currentRecord.id, values);
      }

      if (response.data.success) {
        message.success(modalType === 'add' ? '创建成功' : '更新成功');
        setModalVisible(false);
        loadData();
      } else {
        message.error(response.data.message || '操作失败');
      }
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查表单数据');
      } else {
        message.error('操作失败：' + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  // 取消
  const handleCancel = () => {
    setModalVisible(false);
    setCurrentRecord(null);
    form.resetFields();
  };

  return (
    <div>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row gutter={[16, 16]}>
            <Col span={6}>
              <Input
                placeholder="搜索材料名称、编号、规格型号"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onPressEnter={handleSearch}
                prefix={<SearchOutlined />}
                allowClear
              />
            </Col>
            <Col span={4}>
              <Select
                placeholder="材料分类"
                value={materialCategoryFilter}
                onChange={setMaterialCategoryFilter}
                allowClear
                style={{ width: '100%' }}
              >
                {options.material_categories?.filter(cat => cat && cat.id).map(cat => (
                  <Option key={cat.id} value={cat.id}>{cat.material_name || cat.name}</Option>
                ))}
              </Select>
            </Col>
            <Col span={4}>
              <Select
                placeholder="检验类型"
                value={inspectionTypeFilter}
                onChange={setInspectionTypeFilter}
                allowClear
                style={{ width: '100%' }}
              >
                {options.inspection_types?.filter(type => type && type.value).map(type => (
                  <Option key={type.value} value={type.value}>{type.label}</Option>
                ))}
              </Select>
            </Col>
            <Col span={4}>
              <Select
                placeholder="启用状态"
                value={enabledFilter}
                onChange={setEnabledFilter}
                allowClear
                style={{ width: '100%' }}
              >
                <Option value="true">启用</Option>
                <Option value="false">禁用</Option>
              </Select>
            </Col>
            <Col span={6}>
              <Space wrap>
                <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                  搜索
                </Button>
                <Button icon={<ClearOutlined />} onClick={handleReset}>
                  重置
                </Button>
                <Button icon={<ReloadOutlined />} onClick={() => loadData()}>
                  刷新
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                  新增材料
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 1500, y: 600 }}
          size="small"
        />
      </Card>

      {/* 新增/编辑模态框 */}
      <Modal
        title={modalType === 'add' ? '新增材料' : '编辑材料'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={handleCancel}
        width={1400}
        destroyOnClose
        confirmLoading={loading}
        okText="保存"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            conversion_factor: 1,
            warning_days: 0,
            standard_m_per_roll: 0,
            wind_tolerance_mm: 0,
            tongue_mm: 0,
            purchase_price: 0,
            latest_purchase_price: 0,
            inspection_type: 'spot_check',
            is_enabled: true
          }}
        >
          <Tabs defaultActiveKey="basic">
            <TabPane tab="基本信息" key="basic">
              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="材料编号"
                    name="material_code"
                    tooltip="留空则自动生成"
                  >
                    <Input placeholder="自动生成" />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="材料名称"
                    name="material_name"
                    rules={[{ required: true, message: '请输入材料名称' }]}
                  >
                    <Input placeholder="请输入材料名称" />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="材料分类"
                    name="material_category_id"
                    rules={[{ required: true, message: '请选择材料分类' }]}
                  >
                    <Select 
                      placeholder="请选择材料分类"
                      onChange={handleMaterialCategoryChange}
                      allowClear
                    >
                      {options.material_categories?.filter(cat => cat && cat.id).map(cat => (
                        <Option key={cat.id} value={cat.id}>{cat.material_name || cat.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="材料属性"
                    name="material_attribute"
                  >
                    <Input placeholder="自动填入" disabled />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="单位"
                    name="unit_id"
                    rules={[{ required: true, message: '请选择单位' }]}
                  >
                    <Select placeholder="请选择单位" allowClear>
                      {options.units?.filter(unit => unit && unit.id).map(unit => (
                        <Option key={unit.id} value={unit.id}>{unit.unit_name || unit.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="辅助单位"
                    name="auxiliary_unit_id"
                  >
                    <Select placeholder="自动填入" allowClear>
                      {options.units?.filter(unit => unit && unit.id).map(unit => (
                        <Option key={unit.id} value={unit.id}>{unit.unit_name || unit.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="销售单位"
                    name="sales_unit_id"
                  >
                    <Select placeholder="请选择销售单位" allowClear>
                      {options.units?.filter(unit => unit && unit.id).map(unit => (
                        <Option key={unit.id} value={unit.id}>{unit.unit_name || unit.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="检验类型"
                    name="inspection_type"
                  >
                    <Select placeholder="请选择检验类型">
                      {options.inspection_types?.filter(type => type && type.value).map(type => (
                        <Option key={type.value} value={type.value}>{type.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="换算系数"
                    name="conversion_factor"
                  >
                    <InputNumber
                      placeholder="默认1"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="密度"
                    name="density"
                  >
                    <InputNumber
                      placeholder="自动填入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                      addonAfter="g/cm³"
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="规格型号"
                    name="specification_model"
                  >
                    <Input placeholder="自动填入" />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="保质期(天)"
                    name="shelf_life_days"
                  >
                    <InputNumber
                      placeholder="自动填入"
                      min={0}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="预警天数"
                    name="warning_days"
                  >
                    <InputNumber
                      placeholder="默认0"
                      min={0}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="标准m/卷"
                    name="standard_m_per_roll"
                  >
                    <InputNumber
                      placeholder="默认0"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="风差(mm)"
                    name="wind_tolerance_mm"
                  >
                    <InputNumber
                      placeholder="默认0"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="舌头(mm)"
                    name="tongue_mm"
                  >
                    <InputNumber
                      placeholder="默认0"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            <TabPane tab="尺寸规格" key="dimensions">
              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="宽(mm)"
                    name="width_mm"
                  >
                    <InputNumber
                      placeholder="自动填入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="厚(μm)"
                    name="thickness_um"
                  >
                    <InputNumber
                      placeholder="自动填入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="长(mm)"
                    name="length_mm"
                  >
                    <InputNumber
                      placeholder="自动填入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="高(mm)"
                    name="height_mm"
                  >
                    <InputNumber
                      placeholder="自动填入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="纸箱规格体积"
                    name="carton_spec_volume"
                  >
                    <InputNumber
                      placeholder="请输入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="材料位置"
                    name="material_position"
                  >
                    <Input placeholder="请输入材料位置" />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="扫码批次"
                    name="scan_batch"
                  >
                    <Input placeholder="请输入扫码批次" />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="用友编码"
                    name="uf_code"
                  >
                    <Input placeholder="请输入用友编码" />
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            <TabPane tab="价格库存" key="price_stock">
              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="采购价"
                    name="purchase_price"
                  >
                    <InputNumber
                      placeholder="默认0"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                      addonBefore="¥"
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="最近采购价"
                    name="latest_purchase_price"
                  >
                    <InputNumber
                      placeholder="默认0"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                      addonBefore="¥"
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="最近含税单价"
                    name="latest_tax_included_price"
                  >
                    <InputNumber
                      placeholder="请输入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                      addonBefore="¥"
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="销售价"
                    name="sales_price"
                  >
                    <InputNumber
                      placeholder="请输入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                      addonBefore="¥"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="最小库存(起)"
                    name="min_stock_start"
                  >
                    <InputNumber
                      placeholder="请输入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="最小库存(止)"
                    name="min_stock_end"
                  >
                    <InputNumber
                      placeholder="请输入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="最大库存"
                    name="max_stock"
                  >
                    <InputNumber
                      placeholder="请输入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="损耗1"
                    name="loss_1"
                  >
                    <InputNumber
                      placeholder="请输入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="损耗2"
                    name="loss_2"
                  >
                    <InputNumber
                      placeholder="请输入"
                      min={0}
                      step={0.01}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="正算公式"
                    name="forward_formula"
                  >
                    <Select placeholder="请选择正算公式" allowClear>
                      {options.calculation_schemes?.filter(scheme => scheme && scheme.id).map(scheme => (
                        <Option key={scheme.id} value={scheme.id}>{scheme.scheme_name || scheme.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="反算公式"
                    name="reverse_formula"
                  >
                    <Select placeholder="请选择反算公式" allowClear>
                      {options.calculation_schemes?.filter(scheme => scheme && scheme.id).map(scheme => (
                        <Option key={scheme.id} value={scheme.id}>{scheme.scheme_name || scheme.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="用料公式"
                    name="material_formula_id"
                  >
                    <Select placeholder="请选择用料公式" allowClear>
                      {options.calculation_schemes?.filter(s => s && s.id && s.scheme_category === 'material_usage').map(scheme => (
                        <Option key={scheme.id} value={scheme.id}>{scheme.scheme_name || scheme.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            <TabPane tab="属性设置" key="properties">
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="材料属性" style={{ marginBottom: 16 }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Form.Item name="is_blown_film" valuePropName="checked" noStyle>
                        <Checkbox>是否吹膜</Checkbox>
                      </Form.Item>
                      <Form.Item name="unit_no_conversion" valuePropName="checked" noStyle>
                        <Checkbox>单位不换算</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_paper" valuePropName="checked" noStyle>
                        <Checkbox>是否卷纸</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_surface_printing_ink" valuePropName="checked" noStyle>
                        <Checkbox>表印油墨</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_carton" valuePropName="checked" noStyle>
                        <Checkbox>是否纸箱</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_uv_ink" valuePropName="checked" noStyle>
                        <Checkbox>UV油墨</Checkbox>
                      </Form.Item>
                    </Space>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="特殊属性" style={{ marginBottom: 16 }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Form.Item name="is_paper_core" valuePropName="checked" noStyle>
                        <Checkbox>是否纸芯</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_tube_film" valuePropName="checked" noStyle>
                        <Checkbox>是否筒膜</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_hot_stamping" valuePropName="checked" noStyle>
                        <Checkbox>是否烫金</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_woven_bag" valuePropName="checked" noStyle>
                        <Checkbox>是否编织袋</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_zipper" valuePropName="checked" noStyle>
                        <Checkbox>是否拉链</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_self_made" valuePropName="checked" noStyle>
                        <Checkbox>是否自制</Checkbox>
                      </Form.Item>
                    </Space>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="系统设置" style={{ marginBottom: 16 }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Form.Item name="material_formula_reverse" valuePropName="checked" noStyle>
                        <Checkbox>用料公式反算</Checkbox>
                      </Form.Item>
                      <Form.Item name="no_interface" valuePropName="checked" noStyle>
                        <Checkbox>不对接</Checkbox>
                      </Form.Item>
                      <Form.Item name="cost_object_required" valuePropName="checked" noStyle>
                        <Checkbox>成本对象必填</Checkbox>
                      </Form.Item>
                      <Form.Item name="is_enabled" valuePropName="checked" noStyle>
                        <Checkbox>启用</Checkbox>
                      </Form.Item>
                    </Space>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    label="科目"
                    name="subject_id"
                  >
                    <Select placeholder="请选择科目" allowClear>
                      {options.subjects?.filter(subject => subject && (subject.id || subject.value)).map(subject => (
                        <Option key={subject.id || subject.value} value={subject.id || subject.value}>{subject.name || subject.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="保密编码"
                    name="security_code"
                  >
                    <Select placeholder="请选择保密编码" allowClear>
                      {options.security_codes?.filter(code => code && (code.id || code.value)).map(code => (
                        <Option key={code.id || code.value} value={code.id || code.value}>{code.name || code.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="替代材料分类"
                    name="substitute_material_category_id"
                  >
                    <Select placeholder="请选择替代材料分类" allowClear>
                      {options.material_categories?.filter(cat => cat && cat.id).map(cat => (
                        <Option key={cat.id} value={cat.id}>{cat.material_name || cat.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="显示排序"
                    name="sort_order"
                  >
                    <InputNumber
                      placeholder="默认0"
                      min={0}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item
                    label="备注"
                    name="remarks"
                  >
                    <Input.TextArea
                      placeholder="请输入备注信息"
                      rows={3}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>
          </Tabs>
        </Form>
      </Modal>


    </div>
  );
};

export default MaterialManagement; 