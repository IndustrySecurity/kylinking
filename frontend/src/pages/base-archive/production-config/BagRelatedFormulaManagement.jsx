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
      console.log('加载袋型公式数据，参数:', {
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        bag_type_id: bagTypeFilter,
        is_enabled: enabledFilter,
        ...params
      });

      const response = await bagRelatedFormulaApi.getBagRelatedFormulas({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        bag_type_id: bagTypeFilter,
        is_enabled: enabledFilter,
        ...params
      });

      console.log('袋型公式API响应:', response.data);

      if (response.data.success) {
        // 添加详细的调试信息
        console.log('=== 袋型公式数据解析调试 ===');
        console.log('1. 完整响应:', response);
        console.log('2. response.data:', response.data);
        console.log('3. response.data.data:', response.data.data);
        
        // 修正数据路径：实际数据在 response.data.data.data 中
        const responseWrapper = response.data.data || {};
        const actualData = responseWrapper.data || {};
        console.log('4. 实际数据层 (response.data.data.data):', actualData);
        console.log('5. actualData.formulas:', actualData.formulas);
        console.log('6. formulas是否为数组:', Array.isArray(actualData.formulas));
        
        // 从正确的层级提取字段
        const formulasArray = Array.isArray(actualData.formulas) ? actualData.formulas : [];
        const total = actualData.total || 0;
        const currentPage = actualData.current_page || 1;
        
        console.log('7. 提取结果:', { 
          formulasArray, 
          formulasLength: formulasArray.length,
          total, 
          currentPage,
          firstFormula: formulasArray[0]
        });
        
        // 为每行数据添加key
        const dataWithKeys = formulasArray.map((item, index) => ({
          ...item,
          key: item.id || `temp_${index}`
        }));
        
        console.log('8. 最终处理的数据:', dataWithKeys);
        
        setData(dataWithKeys);
        setPagination(prev => ({
          ...prev,
          total: total,
          current: currentPage
        }));
        
        console.log('9. 数据设置完成，表格应该显示', dataWithKeys.length, '条记录');
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
      console.log('=== 袋型公式选项数据加载调试 ===');
      console.log('开始加载袋型公式选项数据...');
      
      const response = await bagRelatedFormulaApi.getBagRelatedFormulaOptions();
      console.log('1. 选项API完整响应:', response);
      console.log('2. response.data:', response.data);
      console.log('3. response.data.data:', response.data.data);
      
      if (response.data.success) {
        // 修正选项数据路径：根据日志，实际数据可能在 response.data.data.data 中
        const responseWrapper = response.data.data || {};
        const actualOptionsData = responseWrapper.data || responseWrapper; // 备用方案
        console.log('4. 实际选项数据层:', actualOptionsData);
        console.log('5. bag_types:', actualOptionsData.bag_types);
        console.log('6. formulas:', actualOptionsData.formulas);
        
        // 处理袋型选项
        let bagTypeOptions = [];
        if (Array.isArray(actualOptionsData.bag_types)) {
          bagTypeOptions = actualOptionsData.bag_types.map(item => ({
            value: item.id || item.value,
            label: item.name || item.label || item.bag_type_name,
            ...item
          }));
        }
        
        // 处理公式选项
        let formulaOptions = [];
        if (Array.isArray(actualOptionsData.formulas)) {
          formulaOptions = actualOptionsData.formulas.map(item => ({
            value: item.id || item.value,
            label: item.name || item.label || item.scheme_name,
            ...item
          }));
        }
        
        const processedOptions = {
          bag_types: bagTypeOptions,
          formulas: formulaOptions
        };
        
        console.log('7. 处理后的选项:', processedOptions);
        
        setFormOptions(processedOptions);
        console.log('8. 选项数据设置完成');
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
        bag_types: [
          { id: 'flat_bag', value: 'flat_bag', label: '平口袋', name: '平口袋' },
          { id: 'vest_bag', value: 'vest_bag', label: '背心袋', name: '背心袋' },
          { id: 'shopping_bag', value: 'shopping_bag', label: '手提袋', name: '手提袋' },
          { id: 'garbage_bag', value: 'garbage_bag', label: '垃圾袋', name: '垃圾袋' },
          { id: 'food_bag', value: 'food_bag', label: '食品袋', name: '食品袋' }
        ],
        formulas: [
          { id: 'area_formula', value: 'area_formula', label: '面积公式', name: '面积公式' },
          { id: 'weight_formula', value: 'weight_formula', label: '重量公式', name: '重量公式' },
          { id: 'material_formula', value: 'material_formula', label: '材料公式', name: '材料公式' },
          { id: 'loss_formula', value: 'loss_formula', label: '损耗公式', name: '损耗公式' },
          { id: 'cost_formula', value: 'cost_formula', label: '成本公式', name: '成本公式' }
        ]
      };
      console.log('9. 使用默认选项:', defaultOptions);
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
    console.log('=== 数据状态变化监控 ===');
    console.log('表格数据更新:', {
      dataLength: data.length,
      hasData: data.length > 0,
      firstItemId: data[0]?.id,
      firstItemBagType: data[0]?.bag_type_name
    });
  }, [data]);

  useEffect(() => {
    console.log('=== 选项状态变化监控 ===');
    console.log('选项数据更新:', {
      bagTypesLength: formOptions.bag_types?.length || 0,
      formulasLength: formOptions.formulas?.length || 0,
      bagTypesPreview: formOptions.bag_types?.slice(0, 2),
      formulasPreview: formOptions.formulas?.slice(0, 2)
    });
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
      form.setFieldsValue({
        ...record,
        sort_order: record.sort_order || 0
      });
    } else {
      form.resetFields();
      form.setFieldsValue({
        is_enabled: true,
        sort_order: 0
      });
    }
    setModalVisible(true);
  };

  // 保存袋型相关公式
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      let response;
      if (editingFormula) {
        response = await bagRelatedFormulaApi.updateBagRelatedFormula(editingFormula.id, values);
        if (response.data.success) {
          message.success('更新成功');
        }
      } else {
        response = await bagRelatedFormulaApi.createBagRelatedFormula(values);
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
      dataIndex: 'bag_type_name',
      key: 'bag_type_name',
      width: 150,
      render: (text) => <Text>{text || '-'}</Text>
    },
    {
      title: '米数公式',
      dataIndex: 'meter_formula',
      key: 'meter_formula',
      width: 150,
      render: (formula) => (
        <Tooltip title={formula ? formula.formula : ''}>
          <Text>
            {formula ? formula.name : '-'}
          </Text>
        </Tooltip>
      )
    },
    {
      title: '平方公式',
      dataIndex: 'square_formula',
      key: 'square_formula',
      width: 150,
      render: (formula) => (
        <Tooltip title={formula ? formula.formula : ''}>
          <Text>
            {formula ? formula.name : '-'}
          </Text>
        </Tooltip>
      )
    },
    {
      title: '料宽公式',
      dataIndex: 'material_width_formula',
      key: 'material_width_formula',
      width: 150,
      render: (formula) => (
        <Tooltip title={formula ? formula.formula : ''}>
          <Text>
            {formula ? formula.name : '-'}
          </Text>
        </Tooltip>
      )
    },
    {
      title: '元/个公式',
      dataIndex: 'per_piece_formula',
      key: 'per_piece_formula',
      width: 150,
      render: (formula) => (
        <Tooltip title={formula ? formula.formula : ''}>
          <Text>
            {formula ? formula.name : '-'}
          </Text>
        </Tooltip>
      )
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
      {/* 调试信息 - 仅在开发环境显示 */}
      {process.env.NODE_ENV === 'development' && (
        <Card style={{ marginBottom: 16, backgroundColor: '#f0f2f5' }}>
          <Title level={5}>调试信息</Title>
          <p><strong>表格数据:</strong> {data.length} 条记录</p>
          <p><strong>袋型选项:</strong> {formOptions.bag_types?.length || 0} 个</p>
          <p><strong>公式选项:</strong> {formOptions.formulas?.length || 0} 个</p>
          <p><strong>加载状态:</strong> {loading ? '加载中' : '已完成'}</p>
          <p><strong>分页信息:</strong> 总共 {pagination.total} 条，当前第 {pagination.current} 页</p>
          {data.length > 0 && (
            <details>
              <summary>第一条数据预览</summary>
              <pre>{JSON.stringify(data[0], null, 2)}</pre>
            </details>
          )}
          {formOptions.bag_types && formOptions.bag_types.length > 0 && (
            <details>
              <summary>袋型选项预览</summary>
              <pre>{JSON.stringify(formOptions.bag_types, null, 2)}</pre>
            </details>
          )}
        </Card>
      )}
      
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
          destroyOnClose
          key={modalVisible ? (editingFormula?.id || 'new') : 'closed'}
        >
          <Form
            form={form}
            layout="vertical"
            preserve={false}
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
                    {(formOptions.bag_types || []).map(item => (
                      <Option key={item.value} value={item.value}>
                        {item.label}
                      </Option>
                    ))}
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
                      <Option key={item.value} value={item.value} title={item.formula}>
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
                      <Option key={item.value} value={item.value} title={item.formula}>
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
                      <Option key={item.value} value={item.value} title={item.formula}>
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