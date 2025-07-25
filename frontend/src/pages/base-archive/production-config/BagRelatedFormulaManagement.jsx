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
import { bagRelatedFormulaApi } from '../../../api/base-archive/production-config/bagRelatedFormula';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const BagRelatedFormulaManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingFormula, setEditingFormula] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [bagTypeFilter, setBagTypeFilter] = useState('');
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
    bag_types: [],
    formulas: []
  });

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await bagRelatedFormulaApi.getBagRelatedFormulas({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        bag_type_id: bagTypeFilter,
        is_enabled: enabledFilter,
        ...params
      });

      if (response.data.success) {
        
        const responseWrapper = response.data.data || {};

        const formulasArray = responseWrapper.formulas || [];
        const total = responseWrapper.total || 0;
        const currentPage = responseWrapper.page || 1;
          
        // 为每行数据添加key
        const dataWithKeys = formulasArray.map((item, index) => ({
          ...item,
          key: item.id || `temp_${index}`
        }));
        
        
        setData(dataWithKeys);
        setPagination(prev => ({
          ...prev,
          total: total,
          current: currentPage
        }));
        
        
      } else {
        console.error('袋型公式API返回失败:', response.data.message);
        message.error('加载数据失败：' + (response.data.message || '未知错误'));
        setData([]);
      }
    } catch (error) {
      console.error('袋型公式数据加载错误:', error);
      const errorMsg = error.response?.data?.message || error.response?.data?.error || error.message || '网络请求失败';
      message.error('加载数据失败：' + errorMsg);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  // 加载选项数据
  const loadOptions = async () => {
    try {
      const response = await bagRelatedFormulaApi.getBagRelatedFormulaOptions();

      if (response.data.success) {
        // 根据新的API结构，数据在 response.data.data 中
        const optionsData = response.data.data || {};
        
        // 处理袋型选项
        let bagTypeOptions = [];
        if (Array.isArray(optionsData.bag_type_options)) {
          bagTypeOptions = optionsData.bag_type_options.map(item => ({
            value: item.value,
            label: item.label,
            spec_expression: item.spec_expression,
            ...item
          }));
        }
        
        // 处理计算方案选项
        let formulaOptions = [];
        if (Array.isArray(optionsData.calculation_scheme_options)) {
          formulaOptions = optionsData.calculation_scheme_options.map(item => ({
            value: item.value,
            label: item.label,
            formula: item.formula,
            category: item.category,
            description: item.description,
            ...item
          }));
        }
        
        const processedOptions = {
          bag_types: bagTypeOptions,
          formulas: formulaOptions
        };
        setFormOptions(processedOptions);
      } else {
        console.warn('选项API返回失败，使用默认数据');
        const defaultOptions = {
          bag_types: [],
          formulas: []
        };
        setFormOptions(defaultOptions);
      }
    } catch (error) {
      console.error('袋型公式选项数据加载错误:', error);
      // 使用默认选项作为后备
      const defaultOptions = {
        bag_types: [],
        formulas: []
      };
      setFormOptions(defaultOptions);
    }
  };

  // 初始加载
  useEffect(() => {
    const initializeData = async () => {
      await loadOptions(); // 先加载选项数据
      await loadData();     // 再加载列表数据
    };
    initializeData();
  }, []);

  // 监控数据状态变化
  useEffect(() => {

  }, [data]);

  useEffect(() => {

  }, [formOptions]);

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setBagTypeFilter('');
    setEnabledFilter(undefined);
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '', bag_type_id: '', is_enabled: undefined });
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
    setEditingFormula(record);
    
    if (record) {
      // 编辑模式：显示所有袋型选项
      const formData = {
        ...record,
        sort_order: record.sort_order || 0,
        is_enabled: record.is_enabled !== undefined ? record.is_enabled : true
      };
      form.setFieldsValue(formData)
    } else {
      // 新增模式：过滤掉已有公式配置的袋型
      form.resetFields();
      const defaultData = {
        is_enabled: true,
        sort_order: 0
      };

      form.setFieldsValue(defaultData);
    }
    setModalVisible(true);
  };

  // 保存袋型相关公式
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      // 清理数据：移除undefined和null值，设置默认值
      const cleanedValues = {
        bag_type_id: values.bag_type_id,
        meter_formula_id: values.meter_formula_id || null,
        square_formula_id: values.square_formula_id || null,
        material_width_formula_id: values.material_width_formula_id || null,
        per_piece_formula_id: values.per_piece_formula_id || null,
        dimension_description: values.dimension_description || '',
        description: values.description || '',
        sort_order: values.sort_order || 0,
        is_enabled: values.is_enabled !== undefined ? values.is_enabled : true
      };
        
      // 确保bag_type_id存在且有效
      if (!cleanedValues.bag_type_id) {
        message.error('请选择袋型');
        return;
      }
      
      // 验证袋型选项是否存在
      const selectedBagType = formOptions.bag_types.find(b => b.value === cleanedValues.bag_type_id);
      if (!selectedBagType) {
        message.error('选择的袋型无效');
        return;
      }
      
      let response;
      if (editingFormula) {
        response = await bagRelatedFormulaApi.updateBagRelatedFormula(editingFormula.id, cleanedValues);
        if (response.data.success) {
          message.success('更新成功');
        }
      } else {
        response = await bagRelatedFormulaApi.createBagRelatedFormula(cleanedValues);
        if (response.data.success) {
          message.success('创建成功');
        }
      }

      setModalVisible(false);
      loadData();
    } catch (error) {
      console.error('保存错误详情:', error);
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        const errorMessage = error.response?.data?.message || error.response?.data?.error || error.message;
        if (errorMessage.includes('已存在相关公式配置')) {
          message.error('该袋型已存在公式配置，请选择其他袋型或编辑现有配置');
        } else if (errorMessage.includes('袋型不能为空')) {
          message.error('请选择袋型');
        } else if (errorMessage.includes('数据完整性错误')) {
          message.error('数据格式错误，请检查输入内容');
        } else {
          message.error('保存失败：' + errorMessage);
        }
      }
    }
  };

  // 删除袋型相关公式
  const handleDelete = async (id) => {
    try {
      await bagRelatedFormulaApi.deleteBagRelatedFormula(id);
      message.success('删除成功');
      loadData();
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.message || error.message));
    }
  };

  // 状态切换
  const handleStatusChange = async (id, checked) => {
    try {
      await bagRelatedFormulaApi.updateBagRelatedFormula(id, { is_enabled: checked });
      message.success('状态更新成功');
      loadData();
    } catch (error) {
      message.error('状态更新失败：' + (error.response?.data?.message || error.message));
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '袋型',
      dataIndex: 'bag_type_id',
      key: 'bag_type_id',
      width: 150,
      render: (bagTypeId) => {
        const bagType = formOptions.bag_types.find(b => b.value === bagTypeId);
        return (
          <Tooltip title={bagType ? bagType.spec_expression : ''}>
            <Text>
              {bagType ? bagType.label : '-'}
            </Text>
          </Tooltip>
        );
      }
    },
    {
      title: '米数公式',
      dataIndex: 'meter_formula_id',
      key: 'meter_formula_id',
      width: 150,
      render: (formulaId) => {
        const formula = formOptions.formulas.find(f => f.value === formulaId);
        return (
          <Tooltip title={formula ? formula.formula : ''}>
            <Text>
              {formula ? formula.label : '-'}
            </Text>
          </Tooltip>
        );
      }
    },
    {
      title: '平方公式',
      dataIndex: 'square_formula_id',
      key: 'square_formula_id',
      width: 150,
      render: (formulaId) => {
        const formula = formOptions.formulas.find(f => f.value === formulaId);
        return (
          <Tooltip title={formula ? formula.formula : ''}>
            <Text>
              {formula ? formula.label : '-'}
            </Text>
          </Tooltip>
        );
      }
    },
    {
      title: '料宽公式',
      dataIndex: 'material_width_formula_id',
      key: 'material_width_formula_id',
      width: 150,
      render: (formulaId) => {
        const formula = formOptions.formulas.find(f => f.value === formulaId);
        return (
          <Tooltip title={formula ? formula.formula : ''}>
            <Text>
              {formula ? formula.label : '-'}
            </Text>
          </Tooltip>
        );
      }
    },
    {
      title: '元/个公式',
      dataIndex: 'per_piece_formula_id',
      key: 'per_piece_formula_id',
      width: 150,
      render: (formulaId) => {
        const formula = formOptions.formulas.find(f => f.value === formulaId);
        return (
          <Tooltip title={formula ? formula.formula : ''}>
            <Text>
              {formula ? formula.label : '-'}
            </Text>
          </Tooltip>
        );
      }
    },
    {
      title: '尺寸维度',
      dataIndex: 'dimension_description',
      key: 'dimension_description',
      width: 120,
      render: (text) => <Text>{text || '-'}</Text>
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      align: 'center',
      render: (text) => <Text>{text}</Text>
    },
    {
      title: '状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      align: 'center',
      render: (enabled, record) => (
        <Switch
          checked={enabled}
          onChange={(checked) => handleStatusChange(record.id, checked)}
          size="small"
        />
      )
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      key: 'created_by_name',
      width: 100,
      align: 'center',
      render: (text) => <Text>{text || '-'}</Text>
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => text ? new Date(text).toLocaleString('zh-CN') : '-'
    },
    {
      title: '修改人',
      dataIndex: 'updated_by_name',
      key: 'updated_by_name',
      width: 100,
      align: 'center',
      render: (text) => <Text>{text || '-'}</Text>
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      render: (text) => text ? new Date(text).toLocaleString('zh-CN') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => showModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这条记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              icon={<DeleteOutlined />}
              size="small"
              danger
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
          <Title level={4} style={{ margin: 0 }}>袋型相关公式管理</Title>
        </div>

        {/* 搜索栏 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Input
              placeholder="搜索袋型名称、尺寸维度..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
          </Col>
          <Col span={5}>
            <Select
              placeholder="选择袋型"
              value={bagTypeFilter}
              onChange={setBagTypeFilter}
              allowClear
              style={{ width: '100%' }}
            >
              {(formOptions.bag_types || []).map(item => (
                <Option key={item.value} value={item.value}>
                  {item.label}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder="状态"
              value={enabledFilter}
              onChange={setEnabledFilter}
              allowClear
              style={{ width: '100%' }}
            >
              <Option value={true}>启用</Option>
              <Option value={false}>禁用</Option>
            </Select>
          </Col>
          <Col span={9}>
            <Space>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleSearch}
              >
                搜索
              </Button>
              <Button onClick={handleReset}>重置</Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => loadData()}
              >
                刷新
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => showModal()}
              >
                新增
              </Button>
            </Space>
          </Col>
        </Row>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
          size="small"
        />

        {/* 新增/编辑模态框 */}
        <Modal
          title={editingFormula ? '编辑袋型相关公式' : '新增袋型相关公式'}
          open={modalVisible}
          onOk={handleSave}
          onCancel={() => setModalVisible(false)}
          width={800}
          destroyOnClose={false}
        >
          <Form
            form={form}
            layout="vertical"
            preserve={true}
          >
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="袋型"
                  name="bag_type_id"
                  rules={[{ required: true, message: '请选择袋型' }]}
                >
                  <Select
                    placeholder="请选择袋型"
                    showSearch
                    optionFilterProp="children"
                  >
                    {(formOptions.bag_types || []).map(item => {
                      // 在新增模式下，过滤掉已有公式配置的袋型
                      if (!editingFormula) {
                        const existingFormula = data.find(formula => formula.bag_type_id === item.value);
                        if (existingFormula) {
                          return null; // 不显示已有配置的袋型
                        }
                      }
                      return (
                        <Option key={item.value} value={item.value}>
                          {item.label}
                        </Option>
                      );
                    }).filter(Boolean)}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="米数公式"
                  name="meter_formula_id"
                >
                  <Select
                    placeholder="请选择米数公式"
                    allowClear
                    showSearch
                    optionFilterProp="children"
                  >
                    {(formOptions.formulas || []).map(item => (
                      <Option key={item.value} value={item.value} title={`${item.description} - ${item.formula}`}>
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
                  label="平方公式"
                  name="square_formula_id"
                >
                  <Select
                    placeholder="请选择平方公式"
                    allowClear
                    showSearch
                    optionFilterProp="children"
                  >
                    {(formOptions.formulas || []).map(item => (
                      <Option key={item.value} value={item.value} title={item.formula}>
                        {item.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="料宽公式"
                  name="material_width_formula_id"
                >
                  <Select
                    placeholder="请选择料宽公式"
                    allowClear
                    showSearch
                    optionFilterProp="children"
                  >
                    {(formOptions.formulas || []).map(item => (
                      <Option key={item.value} value={item.value} title={`${item.description} - ${item.formula}`}>
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
                  label="元/个公式"
                  name="per_piece_formula_id"
                >
                  <Select
                    placeholder="请选择元/个公式"
                    allowClear
                    showSearch
                    optionFilterProp="children"
                  >
                    {(formOptions.formulas || []).map(item => (
                      <Option key={item.value} value={item.value} title={`${item.description} - ${item.formula}`}>
                        {item.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="尺寸维度"
                  name="dimension_description"
                >
                  <Input placeholder="请输入尺寸维度" />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
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
              <Col span={8}>
                <Form.Item
                  label="状态"
                  name="is_enabled"
                  valuePropName="checked"
                >
                  <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              label="描述"
              name="description"
            >
              <TextArea 
                rows={3} 
                placeholder="请输入描述信息"
                maxLength={500}
                showCount
              />
            </Form.Item>
          </Form>
        </Modal>
      </Card>
    </div>
  );
};

export default BagRelatedFormulaManagement; 