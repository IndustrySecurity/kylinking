import React, { useState, useEffect, useRef } from 'react';
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
  Tooltip,
  Modal,
  Tabs,
  Divider,
  Checkbox,
  Drawer,
  Tag,
  Badge,
  Collapse,
  Affix
} from 'antd';
import {
  PlusOutlined,
  SaveOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined,
  SettingOutlined,
  EyeOutlined,
  DragOutlined,
  ExpandOutlined,
  CompressOutlined,
  FilterOutlined,
  ClearOutlined
} from '@ant-design/icons';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { materialCategoryApi } from '../../api/materialCategory';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { Panel } = Collapse;

// 拖拽类型
const DragTypes = {
  COLUMN: 'column'
};

// 可拖拽的列头组件
const DraggableColumnHeader = ({ children, onMove, moveKey, ...restProps }) => {
  const ref = useRef();
  
  const [{ isDragging }, drag] = useDrag({
    type: DragTypes.COLUMN,
    item: { key: moveKey },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const [, drop] = useDrop({
    accept: DragTypes.COLUMN,
    hover: (item) => {
      if (item.key !== moveKey) {
        onMove(item.key, moveKey);
        item.key = moveKey;
      }
    },
  });

  drag(drop(ref));

  return (
    <th
      ref={ref}
      {...restProps}
      style={{
        ...restProps.style,
        opacity: isDragging ? 0.5 : 1,
        cursor: 'move',
        userSelect: 'none'
      }}
    >
      <Space>
        <DragOutlined style={{ color: '#999' }} />
        {children}
      </Space>
    </th>
  );
};

const MaterialCategoryManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [materialTypeFilter, setMaterialTypeFilter] = useState('');
  const [enabledFilter, setEnabledFilter] = useState('');
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
  const [detailForm] = Form.useForm();
  const [options, setOptions] = useState({
    material_types: [],
    units: []
  });

  // 弹窗和抽屉状态
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [columnSettingVisible, setColumnSettingVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [isCompactMode, setIsCompactMode] = useState(false);

  // 列配置状态
  const [columnConfig, setColumnConfig] = useState(() => {
    const saved = localStorage.getItem('materialCategory_columnConfig');
    return saved ? JSON.parse(saved) : {};
  });

  // 列顺序状态
  const [columnOrder, setColumnOrder] = useState(() => {
    const saved = localStorage.getItem('materialCategory_columnOrder');
    return saved ? JSON.parse(saved) : [];
  });

  // 字段分组定义
  const fieldGroups = {
    basic: {
      title: '基本信息',
      icon: '📋',
      fields: ['material_name', 'material_type', 'display_order', 'is_active']
    },
    units: {
      title: '单位信息',
      icon: '📏',
      fields: ['base_unit_id', 'auxiliary_unit_id', 'sales_unit_id']
    },
    physical: {
      title: '物理属性',
      icon: '⚖️',
      fields: ['density', 'square_weight', 'shelf_life']
    },
    quality: {
      title: '检验质量',
      icon: '🔍',
      fields: ['inspection_standard', 'quality_grade']
    },
    price: {
      title: '价格信息',
      icon: '💰',
      fields: ['latest_purchase_price', 'sales_price', 'product_quote_price', 'cost_price']
    },
    business: {
      title: '业务配置',
      icon: '⚙️',
      fields: ['show_on_kanban', 'account_subject', 'code_prefix', 'warning_days']
    },
    carton: {
      title: '纸箱参数',
      icon: '📦',
      fields: ['carton_param1', 'carton_param2', 'carton_param3', 'carton_param4']
    },
    flags: {
      title: '材料属性标识',
      icon: '🏷️',
      fields: [
        'enable_batch', 'enable_barcode', 'is_ink', 'is_accessory',
        'is_consumable', 'is_recyclable', 'is_hazardous', 'is_imported', 'is_customized',
        'is_seasonal', 'is_fragile', 'is_perishable', 'is_temperature_sensitive',
        'is_moisture_sensitive', 'is_light_sensitive', 'requires_special_storage', 'requires_certification'
      ]
    }
  };

  // 字段配置 - 移除固定列设置
  const fieldConfig = {
    material_name: { title: '材料分类', width: 150, required: true },
    material_type: { title: '材料属性', width: 100 },
    base_unit_name: { title: '单位', width: 80 },
    auxiliary_unit_name: { title: '辅助单位', width: 100 },
    sales_unit_name: { title: '销售单位', width: 100 },
    density: { title: '密度', width: 80 },
    square_weight: { title: '平方克重', width: 100 },
    shelf_life: { title: '保质期/天', width: 100 },
    inspection_standard: { title: '检验标准', width: 120 },
    quality_grade: { title: '质量等级', width: 100 },
    latest_purchase_price: { title: '最近采购价', width: 120 },
    sales_price: { title: '销售价', width: 100 },
    product_quote_price: { title: '产品报价', width: 100 },
    cost_price: { title: '成本价格', width: 100 },
    show_on_kanban: { title: '看板显示', width: 100 },
    account_subject: { title: '科目', width: 100 },
    warning_days: { title: '预警天数', width: 100 },
    display_order: { title: '排序', width: 80 },
    is_active: { title: '启用', width: 80 },
    action: { title: '操作', width: 150 }
  };

  // 获取显示的列
  const getVisibleColumns = () => {
    const defaultVisible = ['material_name', 'material_type', 'base_unit_name', 'is_active', 'action'];
    let visible = Object.keys(columnConfig).length > 0 
      ? Object.keys(columnConfig).filter(key => columnConfig[key])
      : defaultVisible;
    
    // 应用列顺序
    if (columnOrder.length > 0) {
      const orderedVisible = [];
      columnOrder.forEach(key => {
        if (visible.includes(key)) {
          orderedVisible.push(key);
        }
      });
      // 添加不在顺序中但可见的列
      visible.forEach(key => {
        if (!orderedVisible.includes(key)) {
          orderedVisible.push(key);
        }
      });
      visible = orderedVisible;
    }
    
    return visible.filter(key => fieldConfig[key]);
  };

  // 移动列
  const moveColumn = (dragKey, hoverKey) => {
    const visibleColumns = getVisibleColumns();
    const dragIndex = visibleColumns.indexOf(dragKey);
    const hoverIndex = visibleColumns.indexOf(hoverKey);
    
    if (dragIndex === -1 || hoverIndex === -1) return;
    
    const newOrder = [...visibleColumns];
    const dragColumn = newOrder[dragIndex];
    newOrder.splice(dragIndex, 1);
    newOrder.splice(hoverIndex, 0, dragColumn);
    
    setColumnOrder(newOrder);
    localStorage.setItem('materialCategory_columnOrder', JSON.stringify(newOrder));
  };

  // 加载选项数据
  const loadOptions = async () => {
    try {
      const response = await materialCategoryApi.getMaterialCategoryOptions();
      setOptions(response);
    } catch (error) {
      message.error('加载选项数据失败：' + (error.response?.data?.error || error.message));
    }
  };

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await materialCategoryApi.getMaterialCategories({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        material_type: materialTypeFilter,
        is_enabled: enabledFilter,
        ...params
      });

      const { material_categories, total, current_page } = response;
      
      const dataWithKeys = material_categories.map((item, index) => ({
        ...item,
        key: item.id || `temp_${index}`
      }));
      
      setData(dataWithKeys);
      setPagination(prev => ({
        ...prev,
        total,
        current: current_page
      }));
    } catch (error) {
      message.error('加载数据失败：' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    loadOptions();
    loadData();
  }, []);

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setMaterialTypeFilter('');
    setEnabledFilter('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '', material_type: '', is_enabled: '' });
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize
    });
  };

  // 查看详情
  const handleViewDetail = (record) => {
    setCurrentRecord(record);
    detailForm.setFieldsValue(record);
    setDetailModalVisible(true);
  };

  // 开始编辑 - 使用Modal
  const edit = (record) => {
    setCurrentRecord(record);
    form.setFieldsValue({
      ...record,
    });
    setEditModalVisible(true);
  };

  // 取消编辑
  const cancel = () => {
    setEditModalVisible(false);
    form.resetFields();
  };

  // 保存编辑 - Modal版本
  const saveModal = async () => {
    try {
      const values = await form.validateFields();
      
      let response;
      if (currentRecord.id && !currentRecord.id.startsWith('temp_')) {
        response = await materialCategoryApi.updateMaterialCategory(currentRecord.id, values);
        message.success('更新成功');
      } else {
        response = await materialCategoryApi.createMaterialCategory(values);
        message.success('创建成功');
      }

      setEditModalVisible(false);
      form.resetFields();
      setCurrentRecord(null);
      loadData(); // 重新加载数据
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        message.error('保存失败：' + (error.response?.data?.error || error.message));
      }
    }
  };

  // 保存编辑 - 内联版本（保留用于兼容）
  const save = async (key) => {
    try {
      const row = await form.validateFields();
      const newData = [...data];
      const index = newData.findIndex((item) => key === item.key);

      if (index > -1) {
        const item = newData[index];
        const updatedItem = { ...item, ...row };
        
        let response;
        if (item.id && !item.id.startsWith('temp_')) {
          response = await materialCategoryApi.updateMaterialCategory(item.id, row);
        } else {
          response = await materialCategoryApi.createMaterialCategory(row);
        }

        newData.splice(index, 1, {
          ...updatedItem,
          ...response,
          key: response.id
        });
        setData(newData);
        message.success('保存成功');
      }
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        message.error('保存失败：' + (error.response?.data?.error || error.message));
      }
    }
  };

  // 删除记录
  const handleDelete = async (key) => {
    try {
      const record = data.find(item => item.key === key);
      
      if (record.id && !record.id.startsWith('temp_')) {
        await materialCategoryApi.deleteMaterialCategory(record.id);
        message.success('删除成功');
      }
      
      const newData = data.filter(item => item.key !== key);
      setData(newData);
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.error || error.message));
    }
  };

  // 添加新行 - 使用Modal
  const handleAdd = () => {
    const newRecord = {
      key: `temp_${Date.now()}`,
      material_name: '',
      material_type: '主材',
      density: null,
      square_weight: null,
      shelf_life: null,
      inspection_standard: '',
      quality_grade: '',
      latest_purchase_price: null,
      sales_price: null,
      product_quote_price: null,
      cost_price: null,
      show_on_kanban: false,
      account_subject: '',
      code_prefix: 'M',
      warning_days: null,
      carton_param1: null,
      carton_param2: null,
      carton_param3: null,
      carton_param4: null,
      enable_batch: false,
      enable_barcode: false,
      is_ink: false,
      is_accessory: false,
      is_consumable: false,
      is_recyclable: false,
      is_hazardous: false,
      is_imported: false,
      is_customized: false,
      is_seasonal: false,
      is_fragile: false,
      is_perishable: false,
      is_temperature_sensitive: false,
      is_moisture_sensitive: false,
      is_light_sensitive: false,
      requires_special_storage: false,
      requires_certification: false,
      display_order: 0,
      is_active: true,
    };
    
    setCurrentRecord(newRecord);
    form.setFieldsValue(newRecord);
    setEditModalVisible(true);
  };

  // 保存列配置
  const saveColumnConfig = (config) => {
    setColumnConfig(config);
    localStorage.setItem('materialCategory_columnConfig', JSON.stringify(config));
    setColumnSettingVisible(false);
    message.success('列配置已保存');
  };

  // 生成表格列
  const generateColumns = () => {
    const visibleColumns = getVisibleColumns();
    
    return visibleColumns.map(key => {
      const config = fieldConfig[key];
      if (!config) return null;

      if (key === 'action') {
        return {
          title: config.title,
          dataIndex: key,
          width: config.width,
          render: (_, record) => {
            return (
              <Space>
                <Button
                  icon={<EyeOutlined />}
                  type="link"
                  size="small"
                  onClick={() => handleViewDetail(record)}
                >
                  详情
                </Button>
                <Button
                  icon={<EditOutlined />}
                  type="link"
                  size="small"
                  onClick={() => edit(record)}
                >
                  编辑
                </Button>
                <Popconfirm
                  title="确定删除吗?"
                  onConfirm={() => handleDelete(record.key)}
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
            );
          },
        };
      }

      // 处理特殊字段的渲染和编辑
      let render;
      
      if (key === 'is_active') {
        render = (value) => <Switch checked={value} disabled />;
      } else if (key === 'show_on_kanban') {
        render = (value) => <Switch checked={value} disabled />;
      } else if (key === 'material_type') {
        render = (value) => <Tag color={value === '主材' ? 'blue' : 'green'}>{value}</Tag>;
      } else if (['base_unit_id', 'auxiliary_unit_id', 'sales_unit_id'].includes(key)) {
        render = (value) => {
          const unit = options.units?.find(u => u.id === value);
          return unit ? unit.name : '-';
        };
      } else if (['density', 'square_weight', 'latest_purchase_price', 'sales_price', 'product_quote_price', 'cost_price', 'carton_param1', 'carton_param2', 'carton_param3', 'carton_param4'].includes(key)) {
        render = (value) => value ? Number(value).toFixed(2) : '-';
      } else if (['shelf_life', 'warning_days', 'display_order'].includes(key)) {
        render = (value) => value || '-';
      }

      const column = {
        title: config.title,
        dataIndex: key,
        width: config.width,
        render,
      };

      // 添加拖拽功能到列头
      if (key !== 'action') {
        column.onHeaderCell = () => ({
          moveKey: key,
          onMove: moveColumn,
        });
      }

      return column;
    }).filter(Boolean);
  };

  // 渲染字段组
  const renderFieldGroup = (groupKey, group) => {
    const groupFields = group.fields.filter(field => fieldConfig[field]);
    
    return (
      <Panel 
        header={
          <Space>
            <span>{group.icon}</span>
            <span>{group.title}</span>
            <Badge count={groupFields.length} size="small" />
          </Space>
        } 
        key={groupKey}
      >
        <Row gutter={[16, 16]}>
          {groupFields.map(field => {
            const config = fieldConfig[field];
            if (!config) return null;
            
            return (
              <Col span={8} key={field}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Text>{config.title}</Text>
                  <Checkbox
                    checked={columnConfig[field] !== false}
                    onChange={(e) => {
                      setColumnConfig(prev => ({
                        ...prev,
                        [field]: e.target.checked
                      }));
                    }}
                  />
                </div>
              </Col>
            );
          })}
        </Row>
      </Panel>
    );
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div style={{ padding: '24px' }}>
        <Card>
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Title level={4} style={{ margin: 0 }}>
                材料分类管理
                <Badge count={data.length} style={{ marginLeft: 8 }} />
              </Title>
              
              <Space>
                <Tooltip title={isCompactMode ? '展开视图' : '紧凑视图'}>
                  <Button
                    icon={isCompactMode ? <ExpandOutlined /> : <CompressOutlined />}
                    onClick={() => setIsCompactMode(!isCompactMode)}
                  />
                </Tooltip>
                <Button 
                  icon={<SettingOutlined />} 
                  onClick={() => setColumnSettingVisible(true)}
                >
                  列设置
                </Button>
              </Space>
            </div>
            
            {/* 搜索和筛选区域 */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={6}>
                <Input
                  placeholder="搜索材料名称、科目等"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={handleSearch}
                  prefix={<SearchOutlined />}
                  allowClear
                />
              </Col>
              <Col span={4}>
                <Select
                  placeholder="材料属性"
                  value={materialTypeFilter}
                  onChange={setMaterialTypeFilter}
                  allowClear
                  style={{ width: '100%' }}
                >
                  {options.material_types?.map(type => (
                    <Option key={type} value={type}>{type}</Option>
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
              <Col span={10}>
                <Space>
                  <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                    搜索
                  </Button>
                  <Button icon={<ClearOutlined />} onClick={handleReset}>
                    重置
                  </Button>
                  <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                    新增
                  </Button>
                  <Button icon={<ReloadOutlined />} onClick={() => loadData()}>
                    刷新
                  </Button>
                </Space>
              </Col>
            </Row>
          </div>

          {/* 表格 */}
          <Table
            components={{
              header: {
                cell: DraggableColumnHeader,
              },
            }}
            bordered
            dataSource={data}
            columns={generateColumns()}
            pagination={pagination}
            loading={loading}
            onChange={handleTableChange}
            scroll={{ x: 1500, y: 600 }}
            size={isCompactMode ? 'small' : 'middle'}
          />

          {/* 详情弹窗 */}
          <Modal
            title={
              <Space>
                <span>材料分类详情</span>
                {currentRecord && (
                  <Tag color={currentRecord.material_type === '主材' ? 'blue' : 'green'}>
                    {currentRecord.material_type}
                  </Tag>
                )}
              </Space>
            }
            open={detailModalVisible}
            onCancel={() => setDetailModalVisible(false)}
            footer={[
              <Button key="close" onClick={() => setDetailModalVisible(false)}>
                关闭
              </Button>
            ]}
            width={1200}
          >
            <Form form={detailForm} layout="vertical">
              <Tabs defaultActiveKey="basic">
                {Object.entries(fieldGroups).map(([groupKey, group]) => (
                  <TabPane 
                    tab={
                      <Space>
                        <span>{group.icon}</span>
                        <span>{group.title}</span>
                      </Space>
                    } 
                    key={groupKey}
                  >
                    <Row gutter={16}>
                      {group.fields.map(field => {
                        const config = fieldConfig[field];
                        if (!config) return null;
                        
                        return (
                          <Col span={8} key={field}>
                            <Form.Item label={config.title} name={field}>
                              {field.startsWith('is_') || field.includes('enable') || field === 'show_on_kanban' ? 
                                <Switch disabled /> : 
                                <Input disabled />
                              }
                            </Form.Item>
                          </Col>
                        );
                      })}
                    </Row>
                  </TabPane>
                ))}
              </Tabs>
            </Form>
          </Modal>

          {/* 编辑弹窗 */}
          <Modal
            title={
              <Space>
                <span>{currentRecord?.id && !currentRecord.id.startsWith('temp_') ? '编辑材料分类' : '新增材料分类'}</span>
                {currentRecord && currentRecord.material_type && (
                  <Tag color={currentRecord.material_type === '主材' ? 'blue' : 'green'}>
                    {currentRecord.material_type}
                  </Tag>
                )}
              </Space>
            }
            open={editModalVisible}
            onCancel={cancel}
            onOk={saveModal}
            okText="保存"
            cancelText="取消"
            width={1200}
            confirmLoading={loading}
          >
            <Form form={form} layout="vertical">
              <Tabs defaultActiveKey="basic">
                {Object.entries(fieldGroups).map(([groupKey, group]) => (
                  <TabPane 
                    tab={
                      <Space>
                        <span>{group.icon}</span>
                        <span>{group.title}</span>
                      </Space>
                    } 
                    key={groupKey}
                  >
                    <Row gutter={16}>
                      {group.fields.map(field => {
                        const config = fieldConfig[field];
                        if (!config) return null;
                        
                        let formItem;
                        if (field === 'material_type') {
                          formItem = (
                            <Select placeholder="请选择材料属性">
                              {options.material_types?.map(type => (
                                <Option key={type} value={type}>{type}</Option>
                              ))}
                            </Select>
                          );
                        } else if (['base_unit_id', 'auxiliary_unit_id', 'sales_unit_id'].includes(field)) {
                          formItem = (
                            <Select placeholder="请选择单位" allowClear>
                              {options.units?.map(unit => (
                                <Option key={unit.id} value={unit.id}>{unit.name}</Option>
                              ))}
                            </Select>
                          );
                        } else if (field.startsWith('is_') || field.includes('enable') || field === 'show_on_kanban') {
                          formItem = <Switch />;
                        } else if (['density', 'square_weight', 'latest_purchase_price', 'sales_price', 'product_quote_price', 'cost_price', 'carton_param1', 'carton_param2', 'carton_param3', 'carton_param4'].includes(field)) {
                          formItem = <InputNumber style={{ width: '100%' }} placeholder={`请输入${config.title}`} />;
                        } else if (['shelf_life', 'warning_days', 'display_order'].includes(field)) {
                          formItem = <InputNumber style={{ width: '100%' }} placeholder={`请输入${config.title}`} />;
                        } else {
                          formItem = <Input placeholder={`请输入${config.title}`} />;
                        }
                        
                        return (
                          <Col span={8} key={field}>
                            <Form.Item 
                              label={config.title} 
                              name={field}
                              rules={config.required ? [{ required: true, message: `请输入${config.title}` }] : []}
                              valuePropName={field.startsWith('is_') || field.includes('enable') || field === 'show_on_kanban' ? 'checked' : 'value'}
                            >
                              {formItem}
                            </Form.Item>
                          </Col>
                        );
                      })}
                    </Row>
                  </TabPane>
                ))}
              </Tabs>
            </Form>
          </Modal>

          {/* 列设置抽屉 */}
          <Drawer
            title={
              <Space>
                <SettingOutlined />
                <span>列显示设置</span>
              </Space>
            }
            placement="right"
            onClose={() => setColumnSettingVisible(false)}
            open={columnSettingVisible}
            width={500}
          >
            <div>
              <div style={{ marginBottom: 16 }}>
                <Text type="secondary">
                  选择要显示的列，支持拖拽调整列顺序
                </Text>
              </div>
              
              <Collapse defaultActiveKey={Object.keys(fieldGroups)}>
                {Object.entries(fieldGroups).map(([groupKey, group]) => 
                  renderFieldGroup(groupKey, group)
                )}
              </Collapse>
              
              <Divider />
              
              <Space style={{ width: '100%', justifyContent: 'center' }}>
                <Button 
                  type="primary" 
                  onClick={() => saveColumnConfig(columnConfig)}
                >
                  保存设置
                </Button>
                <Button 
                  onClick={() => {
                    setColumnConfig({});
                    setColumnOrder([]);
                    localStorage.removeItem('materialCategory_columnConfig');
                    localStorage.removeItem('materialCategory_columnOrder');
                    message.success('已重置为默认设置');
                  }}
                >
                  重置默认
                </Button>
              </Space>
            </div>
          </Drawer>
        </Card>
      </div>
    </DndProvider>
  );
};

export default MaterialCategoryManagement; 