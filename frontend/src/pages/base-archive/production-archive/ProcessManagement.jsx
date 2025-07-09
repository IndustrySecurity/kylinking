import React, { useState, useEffect, useRef } from 'react';
import { 
  Table, Button, Space, Input, Typography, Card, Form, 
  Modal, message, Popconfirm, Switch, Select, InputNumber, 
  Tabs, Row, Col, Checkbox
} from 'antd';
import { 
  PlusOutlined, EditOutlined, DeleteOutlined, 
  ReloadOutlined, SearchOutlined, SettingOutlined,
  ToolOutlined
} from '@ant-design/icons';
import { processApi } from '../../../api/base-archive/production-archive/processApi';
import { machineApi } from '../../../api/base-archive/production-archive/machineApi';
import { processCategoryApi } from '../../../api/base-archive/base-category/processCategoryApi';
import { unitApi } from '../../../api/base-archive/production-archive/unit';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;


const ProcessManagement = () => {
  // 状态管理
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });
  const [searchText, setSearchText] = useState('');
  const [editingRecord, setEditingRecord] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [processCategoryOptions, setProcessCategoryOptions] = useState([]);
  const [machineOptions, setMachineOptions] = useState([]);
  const [schedulingMethodOptions, setSchedulingMethodOptions] = useState([]);
  const [unitOptions, setUnitOptions] = useState([]);
  
  // 表单引用
  const [modalForm] = Form.useForm();
  const searchInput = useRef(null);
  
  // 计算公式选项 - 修改数据结构以支持按分类选择
  const [formulaOptions, setFormulaOptions] = useState({
    process_quote: [], // 工序报价分类
    process_loss: [], // 工序损耗分类
    process_bonus: [], // 工序节约奖分类
    process_piece: [], // 工序计件分类
    process_other: [] // 工序其它分类
  });
  const [formulaLoading, setFormulaLoading] = useState(false);
  
  
  // 初始化数据
  useEffect(() => {
    loadData();
    loadCategoryOptions();
    loadMachineOptions();
    loadSchedulingMethodOptions();
    loadUnitOptions();
    loadFormulaOptions();
  }, []);

  // 获取工序列表
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await processApi.getProcesses({
        page: params.page || pagination.current,
        per_page: params.pageSize || pagination.pageSize,
        search: params.searchText || searchText
      });
      
      if (response.data && response.data.success && response.data.data) {
        // 处理新的API响应格式
        const result = response.data.data;
        const processes = result.processes || [];

        
        // 按 sort_order 升序排序，保证排序字段生效
        processes.sort((a, b) => {
          const aOrder = a.sort_order === null || a.sort_order === undefined ? 0 : Number(a.sort_order);
          const bOrder = b.sort_order === null || b.sort_order === undefined ? 0 : Number(b.sort_order);
          return aOrder - bOrder;
        });
        
        setData(processes.map(item => ({ ...item, key: item.id })));
        setPagination(prev => ({
          ...prev,
          total: result.total || 0,
          current: result.current_page || 1
        }));
      }
    } catch (error) {
      console.warn('获取工序列表失败:', error);
      setData([]);
      // 不显示错误提示，避免影响用户体验
    } finally {
      setLoading(false);
    }
  };

  // 获取工序分类选项
  const loadCategoryOptions = async () => {
    try {
      const res = await processCategoryApi.getProcessCategoryOptions();
      if (res.data && res.data.success) {
        const list = Array.isArray(res.data.data) ? res.data.data : (res.data.data.items || []);
        const opts = list.map(item => ({ value: item.value || item.id, label: item.label || item.process_name || item.category_name }));
        setProcessCategoryOptions(opts);
      } else {
        setProcessCategoryOptions([]);
      }
    } catch (e) {
      console.warn('加载工序分类失败:', e);
      setProcessCategoryOptions([]);
    }
  };

  // 获取机台选项
  const loadMachineOptions = async () => {
    try {
      const res = await machineApi.getEnabledMachines();
      if (res.data && res.data.success) {
        const list = Array.isArray(res.data.data) ? res.data.data : (res.data.data.items || []);
        const opts = list.map(m => ({ value: m.id, label: m.machine_name || m.name || m.label }));
        setMachineOptions(opts);
      } else {
        setMachineOptions([]);
      }
    } catch (e) {
      console.warn('加载机台失败:', e);
      setMachineOptions([]);
    }
  };

  // 获取单位选项
  const loadUnitOptions = async () => {
    try {
      const response = await unitApi.getEnabledUnits();
      if (response.data && response.data.success && response.data.data) {
        const result = response.data.data;
        // 后端返回格式可能为 { units: [...] } 或直接数组，做兼容处理
        const unitsList = Array.isArray(result)
          ? result
          : (result.units || result.items || []);

        const options = unitsList.map(unit => ({
          value: unit.id,
          label: unit.unit_name || unit.name || unit.label || '-',
        }));
        setUnitOptions(options);
      } else {
        setUnitOptions([]);
      }
    } catch (error) {
      console.warn('加载单位选项失败:', error);
      setUnitOptions([]);
    }
  };

  // 获取排程方式选项
  const loadSchedulingMethodOptions = () => {
    // 直接使用本地常量，避免404接口请求
    setSchedulingMethodOptions([
      { value: 'investment_m', label: '投产m' },
      { value: 'investment_kg', label: '投产kg' },
      { value: 'production_piece', label: '投产(个)' },
      { value: 'production_output', label: '产出m' },
      { value: 'production_kg', label: '产出kg' },
      { value: 'production_piece_out', label: '产出(个)' },
      { value: 'production_set', label: '产出(套)' },
      { value: 'production_sheet', label: '产出(张)' }
    ]);
  };

  // 获取计算公式选项
  const loadFormulaOptions = async () => {
    setFormulaLoading(true);
    try {
      const process_quote = await processApi.getCalculationSchemeOptions('process_quote');
      const process_loss = await processApi.getCalculationSchemeOptions('process_loss');
      const process_bonus = await processApi.getCalculationSchemeOptions('process_bonus');
      const process_piece = await processApi.getCalculationSchemeOptions('process_piece');
      const process_other = await processApi.getCalculationSchemeOptions('process_other');

      setFormulaOptions({
        process_quote: process_quote.data.data,
        process_loss: process_loss.data.data,
        process_bonus: process_bonus.data.data,
        process_piece: process_piece.data.data,
        process_other: process_other.data.data
      });

      
    } catch (e) {
      console.warn('加载计算方案失败', e);
    } finally {
      setFormulaLoading(false);
    }
  };

  // 处理表格变更（分页、排序等）
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({ page: newPagination.current, pageSize: newPagination.pageSize });
  };

  // 处理搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, searchText });
  };

  // 处理搜索框按键事件
  const handleSearchInputKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // 处理创建工序
  const handleAdd = () => {
    setEditingRecord(null);
    modalForm.resetFields();
    // 设置默认值
    modalForm.setFieldsValue({
      is_enabled: true,
      sort_order: 0,
      machines: []
    });
    setModalVisible(true);
  };

  // 处理编辑工序
  const handleEdit = (record) => {
    setEditingRecord(record);
    modalForm.setFieldsValue(record);
    setModalVisible(true);
  };

  // 处理删除工序
  const handleDelete = async (id) => {
    try {
      await processApi.deleteProcess(id);
      message.success('删除成功');
      loadData();
    } catch (e) {
      console.warn('删除失败:', e);
      message.error('删除失败');
    }
  };

  // 处理模态框确认
  const handleModalOk = async () => {
    try {
      setConfirmLoading(true);
      const values = await modalForm.validateFields();
      if (editingRecord) {
        await processApi.updateProcess(editingRecord.id, values);
        message.success('更新成功');
      } else {
        await processApi.createProcess(values);
        message.success('新建成功');
      }
      setModalVisible(false);
      loadData();
    } catch (e) {
      console.warn('保存失败:', e);
      message.error('保存失败');
    } finally {
      setConfirmLoading(false);
    }
  };

  // 处理模态框取消
  const handleModalCancel = () => {
    setModalVisible(false);
  };

  // 渲染复选框组
  const renderCheckboxGroup = (fields) => (
    <Row gutter={[16, 8]}>
      {fields.map(field => (
        <Col span={8} key={field.key}>
          <Form.Item name={field.key} valuePropName="checked" initialValue={false}>
            <Checkbox>{field.label}</Checkbox>
          </Form.Item>
        </Col>
      ))}
    </Row>
  );

  // 表格列定义
  const columns = [
    {
      title: '工序名称',
      dataIndex: 'process_name',
      key: 'process_name',
      width: 150,
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: '工序分类',
      dataIndex: 'process_category_name',
      key: 'process_category_name',
      width: 120,
      render: (text, record) => record.process_category_name,
    },
    {
      title: '排程方式',
      dataIndex: 'scheduling_method',
      key: 'scheduling_method',
      width: 120,
      render: (text, record) => {
        // 首先尝试从 scheduling_method 字段获取值
        let value = text;
        
        // 如果 scheduling_method 为空，尝试其他可能的字段
        if (!value && record) {
          value = record.scheduling_method || record.schedule_method || record.method;
        }
        
        // 根据值查找对应的标签
        const option = schedulingMethodOptions.find(opt => opt.value === value);
        if (option) return option.label;

        // 兼容旧代码/别名
        const aliasMap = {
          production_m: '产出m',
          investment_m: '投产m',
          production_piece: '产出(个)',
          production_piece_out: '产出(个)',
        };
        return aliasMap[value] || value || '-';
      },
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 80,
      render: (text, record) => {
        if (record.unit_id) {
          const unitOption = unitOptions.find(opt => String(opt.value) === String(record.unit_id));
          if (unitOption) return unitOption.label;
        }
        return text || '-';
      },
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 80,
      render: (text) => text ? `¥${parseFloat(text).toFixed(2)}` : '-',
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
    },
    {
      title: '外协',
      dataIndex: 'external_processing',
      key: 'external_processing',
      width: 60,
      render: (value) => (
        <Switch checked={value} size="small" disabled />
      ),
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      render: (enabled) => (
        <Switch checked={enabled} size="small" disabled />
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small" 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除此工序吗?"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              type="link" 
              danger 
              size="small" 
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>
        <ToolOutlined /> 工序管理
      </Title>
        </div>
        
        {/* 搜索和操作区域 - 统一按钮样式和位置 */}
        <Row justify="end" gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Input
              placeholder="搜索工序名称"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onKeyDown={handleSearchInputKeyDown}
              ref={searchInput}
              prefix={<SearchOutlined />}
              style={{ width: 200 }}
            />
          </Col>
          <Col>
            <Space>
            <Button type="primary" onClick={handleSearch} icon={<SearchOutlined />}>
              搜索
            </Button>
            <Button onClick={() => loadData()} icon={<ReloadOutlined />}>
              刷新
            </Button>
            <Button type="primary" onClick={handleAdd} icon={<PlusOutlined />}>
              新建工序
            </Button>
          </Space>
          </Col>
        </Row>
        
        <Table
          rowKey="id"
          columns={columns}
          dataSource={data}
          pagination={pagination}
          loading={loading}
          onChange={handleTableChange}
          size="small"
          scroll={{ x: 'max-content' }}
          bordered
        />
      </Card>

      <Modal
        title={editingRecord ? "编辑工序" : "新建工序"}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={1200}
        confirmLoading={confirmLoading}
        destroyOnClose
      >
        <Form
          form={modalForm}
          layout="vertical"
          scrollToFirstError
        >
          <Tabs defaultActiveKey="basic">
            <TabPane tab="基本信息" key="basic">
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="process_name"
                    label="工序名称"
                    rules={[{ required: true, message: '请输入工序名称' }]}
                  >
                    <Input placeholder="请输入工序名称" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="process_category_id"
                    label="工序分类"
                    rules={[{ required: true, message: '请选择工序分类' }]}
                  >
                    <Select placeholder="请选择工序分类" allowClear>
                      {processCategoryOptions.map(option => (
                        <Option key={option.value} value={option.value}>
                          {option.label}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="scheduling_method"
                    label="排程方式"
                    rules={[{ required: true, message: '请选择排程方式' }]}
                  >
                    <Select placeholder="请选择排程方式" allowClear>
                      {schedulingMethodOptions.map(option => (
                        <Option key={option.value} value={option.value}>
                          {option.label}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="unit_id"
                    label="单位"
                    rules={[{ required: true, message: '请选择单位' }]}
                  >
                    <Select placeholder="请选择单位" allowClear>
                      {unitOptions.map(option => (
                        <Option key={option.value} value={option.value}>
                          {option.label}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="unit_price"
                    label="单价"
                  >
                    <InputNumber placeholder="请输入单价" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="sort_order"
                    label="排序"
                    initialValue={0}
                  >
                    <InputNumber placeholder="请输入排序" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="external_processing"
                    valuePropName="checked"
                    initialValue={false}
                  >
                    <Checkbox>外协</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="is_enabled"
                    valuePropName="checked"
                    initialValue={true}
                  >
                    <Checkbox>启用</Checkbox>
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            <TabPane tab="关联机台" key="machines">
              <Form.List name="machines">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...restField }) => (
                      <Row key={key} gutter={16} align="middle" style={{ marginBottom: 8 }}>
                        <Col span={20}>
                          <Form.Item
                            {...restField}
                            name={[name, 'machine_id']}
                            rules={[{ required: true, message: '请选择机台' }]}
                          >
                            <Select placeholder="请选择机台">
                              {machineOptions.map(option => (
                                <Option key={option.value} value={option.value}>
                                  {option.label}
                                </Option>
                              ))}
                            </Select>
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Button type="link" danger onClick={() => remove(name)}>删除</Button>
                        </Col>
                      </Row>
                    ))}
                    <Form.Item>
                      <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                        添加机台
                      </Button>
                    </Form.Item>
                  </>
                )}
              </Form.List>
            </TabPane>

            <TabPane tab="生产控制" key="production">
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="production_allowance" label="投产允许误差%">
                    <InputNumber placeholder="请输入投产允许误差" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="return_allowance_kg" label="下返废品允许kg">
                    <InputNumber placeholder="请输入下返废品允许kg" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="over_production_allowance" label="超产允许误差%">
                    <InputNumber placeholder="请输入超产允许误差" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="self_check_allowance_kg" label="自检废品允许kg">
                    <InputNumber placeholder="请输入自检废品允许kg" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="workshop_worker_difference" label="车间工人偏差%">
                    <InputNumber placeholder="请输入车间工人偏差" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="max_upload_count" label="最大上报数">
                    <InputNumber placeholder="请输入最大上报数" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="standard_weight_difference" label="标准重量差异%">
                    <InputNumber placeholder="请输入标准重量差异" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="workshop_difference" label="工序完工偏差%">
                    <InputNumber placeholder="请输入工序完工偏差" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="return_allowance_upper_kg" label="上返废品允许kg">
                    <InputNumber placeholder="请输入上返废品允许kg" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="over_production_limit" label="超产允许值">
                    <InputNumber placeholder="请输入超产允许值" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="process_with_machine" valuePropName="checked" initialValue={false}>
                    <Checkbox>生产排程多机台生产</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="semi_product_usage" valuePropName="checked" initialValue={false}>
                    <Checkbox>本工序半成品领用</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="material_usage_required" valuePropName="checked" initialValue={false}>
                    <Checkbox>辅材用量必填</Checkbox>
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            <TabPane tab="MES配置" key="mes">
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="mes_condition_code" label="MES条码前缀">
                    <Input placeholder="请输入MES条码前缀" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="mes_report_form_code" label="MES报表号前缀">
                    <Input placeholder="请输入MES报表号前缀" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="mes_verify_quality" valuePropName="checked" initialValue={false}>
                    <Checkbox>MES自检合格开工</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="mes_upload_defect_items" valuePropName="checked" initialValue={false}>
                    <Checkbox>MES上报废品项填</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="mes_scancode_shelf" valuePropName="checked" initialValue={false}>
                    <Checkbox>MES扫码上架</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="mes_verify_spec" valuePropName="checked" initialValue={false}>
                    <Checkbox>MES检验合格领用</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="mes_upload_kg_required" valuePropName="checked" initialValue={false}>
                    <Checkbox>MES上报数kg必填</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="display_data_collection" valuePropName="checked" initialValue={false}>
                    <Checkbox>显示数据采集面板</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="ignore_inspection" valuePropName="checked" initialValue={false}>
                    <Checkbox>MES检验不合格领用</Checkbox>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="free_inspection" valuePropName="checked" initialValue={false}>
                    <Checkbox>免检</Checkbox>
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            <TabPane tab="计算公式" key="formula">
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="pricing_formula_id" label="报价损耗公式">
                    <Select placeholder="选择公式" loading={formulaLoading} allowClear>
                      {formulaOptions.process_loss.map(opt => (
                        <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="worker_formula_id" label="工单损耗%公式">
                    <Select placeholder="选择公式" loading={formulaLoading} allowClear>
                      {formulaOptions.process_loss.map(opt => (
                        <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="material_formula_id" label="工单损耗m公式">
                    <Select placeholder="选择公式" loading={formulaLoading} allowClear>
                      {formulaOptions.process_loss.map(opt => (
                        <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="output_formula_id" label="产量上报损耗%">
                    <Select placeholder="选择公式" loading={formulaLoading} allowClear>
                      {formulaOptions.process_loss.map(opt => (
                        <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="time_formula_id" label="计件工时公式">
                    <Select placeholder="选择公式" loading={formulaLoading} allowClear>
                      {formulaOptions.process_piece.map(opt => (
                        <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="energy_formula_id" label="计件产能公式">
                    <Select placeholder="选择公式" loading={formulaLoading} allowClear>
                      {formulaOptions.process_piece.map(opt => (
                        <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="saving_formula_id" label="节约奖公式">
                    <Select placeholder="选择公式" loading={formulaLoading} allowClear>
                      {formulaOptions.process_bonus.map(opt => (
                        <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="labor_cost_formula_id" label="计件工资公式">
                    <Select placeholder="选择公式" loading={formulaLoading} allowClear>
                      {formulaOptions.process_piece.map(opt => (
                        <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="pricing_order_formula_id" label="报价工序公式">
                    <Select placeholder="选择公式" loading={formulaLoading} allowClear>
                      {formulaOptions.process_quote.map(opt => (
                        <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            <TabPane tab="描述" key="description">
              <Form.Item
                name="description"
                label="工序描述"
              >
                <TextArea rows={6} placeholder="请输入工序描述" />
              </Form.Item>
            </TabPane>
          </Tabs>
        </Form>
      </Modal>
    </div>
  );
};

export default ProcessManagement; 