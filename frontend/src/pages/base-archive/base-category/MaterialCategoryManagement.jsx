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
  Tooltip,
  Modal,
  Tabs,
  Divider,
  Checkbox,
  Drawer,
  Tag,
  Badge
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  SettingOutlined,
  EyeOutlined,
  ClearOutlined,
  MenuOutlined
} from '@ant-design/icons';
import { materialCategoryApi } from '../../../api/base-archive/base-category/materialCategory';
import { columnConfigurationApi } from '../../../api/system/columnConfiguration';
import { authApi } from '../../../api/auth';
import { useAutoScroll } from '../../../hooks/useAutoScroll';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

// 简化的列头组件
const SimpleColumnHeader = ({ children, moveKey, onMove, ...restProps }) => (
  <th {...restProps} style={{ ...restProps.style, userSelect: 'none' }}>
    {children}
  </th>
);

const MaterialCategoryManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [materialTypeFilter, setMaterialTypeFilter] = useState('');
  const [enabledFilter, setEnabledFilter] = useState('');
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
  const [detailForm] = Form.useForm();
  const [options, setOptions] = useState({
    material_types: [],
    units: []
  });

  // 弹窗和抽屉状态
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [activeTab, setActiveTab] = useState('basic');

  // 列配置状态
  const [columnConfig, setColumnConfig] = useState({});
  const [columnOrder, setColumnOrder] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [columnSettingOrder, setColumnSettingOrder] = useState([]);
  const [columnSettingVisible, setColumnSettingVisible] = useState(false);
  const [configLoaded, setConfigLoaded] = useState(false);
  
  // 自动滚动功能
  const { scrollContainerRef, setDropEffect, handleDragStart, handleDragEnd } = useAutoScroll();

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
      fields: ['base_unit_name', 'auxiliary_unit_name', 'sales_unit_name']
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

  // 字段配置
  const fieldConfig = {
    material_name: { title: '材料分类', width: 150, required: true },
    material_type: { title: '材料属性', width: 100 },
    base_unit_name: { title: '基本单位', width: 100 },
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
    code_prefix: { title: '编码前缀', width: 100 },
    warning_days: { title: '预警天数', width: 100 },
    carton_param1: { title: '纸箱参数1', width: 100 },
    carton_param2: { title: '纸箱参数2', width: 100 },
    carton_param3: { title: '纸箱参数3', width: 100 },
    carton_param4: { title: '纸箱参数4', width: 100 },
    enable_batch: { title: '启用批次', width: 100 },
    enable_barcode: { title: '启用条码', width: 100 },
    is_ink: { title: '是否油墨', width: 100 },
    is_accessory: { title: '是否辅料', width: 100 },
    is_consumable: { title: '是否耗材', width: 100 },
    is_recyclable: { title: '是否可回收', width: 100 },
    is_hazardous: { title: '是否危险品', width: 100 },
    is_imported: { title: '是否进口', width: 100 },
    is_customized: { title: '是否定制', width: 100 },
    is_seasonal: { title: '是否季节性', width: 100 },
    is_fragile: { title: '是否易碎', width: 100 },
    is_perishable: { title: '是否易腐', width: 100 },
    is_temperature_sensitive: { title: '是否温度敏感', width: 120 },
    is_moisture_sensitive: { title: '是否湿度敏感', width: 120 },
    is_light_sensitive: { title: '是否光敏感', width: 120 },
    requires_special_storage: { title: '需要特殊存储', width: 120 },
    requires_certification: { title: '需要认证', width: 100 },
    display_order: { title: '排序', width: 80 },
    is_active: { title: '启用', width: 80, required: false },
    action: { title: '操作', width: 120, fixed: 'right' }
  };

  // 获取显示的列
  const getVisibleColumns = () => {
    const defaultVisible = ['material_name', 'material_type', 'base_unit_name', 'action'];
    const defaultColumnOrder = [
      'material_name', 'material_type', 'base_unit_name', 'auxiliary_unit_name', 'sales_unit_name',
      'density', 'square_weight', 'shelf_life', 'inspection_standard', 'quality_grade',
      'latest_purchase_price', 'sales_price', 'product_quote_price', 'cost_price',
      'show_on_kanban', 'account_subject', 'code_prefix', 'warning_days',
      'carton_param1', 'carton_param2', 'carton_param3', 'carton_param4',
      'enable_batch', 'enable_barcode', 'is_ink', 'is_accessory', 'is_consumable', 'is_recyclable',
      'is_hazardous', 'is_imported', 'is_customized', 'is_seasonal', 'is_fragile', 'is_perishable',
      'is_temperature_sensitive', 'is_moisture_sensitive', 'is_light_sensitive',
      'requires_special_storage', 'requires_certification', 'display_order', 'is_active', 'action'
    ];
    
    const allPossibleColumns = Object.keys(fieldConfig);
    let visible;
    
    // 如果配置还没有加载完成，返回默认可见列
    if (!configLoaded) {
      return defaultVisible;
    }
    
    if (Object.keys(columnConfig).length === 0) {
      // 如果配置为空，显示所有字段（除了action）
      visible = allPossibleColumns.filter(key => key !== 'action');
    } else {
      // 根据配置过滤可见字段
      visible = allPossibleColumns.filter(key => !(key in columnConfig) || columnConfig[key] === true);
    }
    
    // 强制显示必填字段和操作列
    defaultVisible.forEach(key => {
      const config = fieldConfig[key];
      if ((config && config.required) || key === 'action') {
        if (!visible.includes(key)) {
          visible.push(key);
        }
      }
    });
    
    let finalOrder = [];
    
    if (columnOrder.length > 0) {
      columnOrder.forEach(key => {
        if (visible.includes(key)) {
          finalOrder.push(key);
        }
      });
      
      visible.forEach(key => {
        if (!finalOrder.includes(key)) {
          finalOrder.push(key);
        }
      });
    } else {
      defaultColumnOrder.forEach(key => {
        if (visible.includes(key)) {
          finalOrder.push(key);
        }
      });
      
      visible.forEach(key => {
        if (!finalOrder.includes(key)) {
          finalOrder.push(key);
        }
      });
    }
    
    if (finalOrder.includes('action')) {
      finalOrder = finalOrder.filter(key => key !== 'action');
      finalOrder.push('action');
    }
    
    return finalOrder.filter(key => fieldConfig[key]);
  };

  // 获取表单中应该显示的字段
  const getVisibleFormFields = () => {
    // 如果配置还没有加载完成，显示所有字段
    if (!configLoaded) {
      return Object.keys(fieldConfig).filter(key => key !== 'action');
    }
    
    // 如果列配置为空，显示所有字段
    if (Object.keys(columnConfig).length === 0) {
      return Object.keys(fieldConfig).filter(key => key !== 'action');
    }
    
    // 根据列配置过滤字段，只显示被勾选的字段
    return Object.keys(fieldConfig).filter(key => {
      if (key === 'action') return false;
      
      // 必填字段始终显示，不能被隐藏
      const config = fieldConfig[key];
      if (config && config.required) {
        return true;
      }
      
      // 如果配置中没有明确设置为false，则显示
      return !(key in columnConfig) || columnConfig[key] === true;
    });
  };

  // 获取默认激活的分页
  const getDefaultActiveTab = () => {
    // 检查基本信息分组是否有可见字段
    const basicFields = fieldGroups.basic.fields;
    const visibleBasicFields = basicFields.filter(field => 
      getVisibleFormFields().includes(field)
    );
    
    // 如果基本信息分组有可见字段，返回 'basic'
    if (visibleBasicFields.length > 0) {
      return 'basic';
    }
    
    // 否则找到第一个有可见字段的分组
    for (const [groupKey, group] of Object.entries(fieldGroups)) {
      const visibleFields = group.fields.filter(field => 
        getVisibleFormFields().includes(field)
      );
      if (visibleFields.length > 0) {
        return groupKey;
      }
    }
    
    // 如果所有分组都没有可见字段，返回 'basic'
    return 'basic';
  };

  // 获取当前激活分页的可见字段数量
  const getActiveTabVisibleFieldCount = () => {
    if (!activeTab || !fieldGroups[activeTab]) {
      return 0;
    }
    
    const groupFields = fieldGroups[activeTab].fields;
    const visibleFields = groupFields.filter(field => 
      getVisibleFormFields().includes(field)
    );
    
    return visibleFields.length;
  };

  // 移动列功能 - 插入到指定位置
  const moveColumn = (dragKey, targetIndex) => {
    const newOrder = [...columnSettingOrder];
    const dragIndex = newOrder.indexOf(dragKey);
    
    if (dragIndex === -1 || dragIndex === targetIndex) return;
    
    // 移除拖拽项
    newOrder.splice(dragIndex, 1);
    
    // 计算插入位置
    let insertIndex = targetIndex;
    if (dragIndex < targetIndex) {
      // 如果从前面拖到后面，插入位置需要减1
      insertIndex = targetIndex - 1;
    }
    
    // 插入到目标位置
    newOrder.splice(insertIndex, 0, dragKey);
    
    setColumnSettingOrder(newOrder);
  };



  // 加载选项数据
  const loadOptions = async () => {
    try {
      const response = await materialCategoryApi.getMaterialCategoryFormOptions();
      if (response.data.success) {
        setOptions(response.data.data);
      }
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
        ...params
      });

      // 正确处理后端响应格式
      if (response.data.success) {
        const { material_categories, total, current_page } = response.data.data;
        
        // 为每行数据添加key
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
      }
    } catch (error) {
      message.error('加载数据失败：' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  // 加载列配置
  const loadColumnConfig = async () => {
    try {
      // 获取列显示配置
      const configResponse = await columnConfigurationApi.getColumnConfig('materialCategory', 'column_config');
      if (configResponse.data.success && configResponse.data.data) {
        setColumnConfig(configResponse.data.data.config_data);
      }
      
      // 获取列顺序配置
      const orderResponse = await columnConfigurationApi.getColumnConfig('materialCategory', 'column_order');
      if (orderResponse.data.success && orderResponse.data.data) {
        const order = orderResponse.data.data.config_data;
        setColumnOrder(order);
        setColumnSettingOrder(order); // 同时设置列设置中的顺序
      }
    } catch (error) {
      // 加载列配置失败，使用默认配置
    }
  };

  // 检查用户权限 - 简化版本
  const checkUserPermission = async () => {
    try {
      // 使用封装的权限检查API
      const adminStatus = await authApi.checkAdminStatus();
      setIsAdmin(adminStatus.isAdmin);

    } catch (error) {
      console.error('检查用户权限失败:', error);
      setIsAdmin(false);
    }
  };

  // 初始加载
  useEffect(() => {
    const initialize = async () => {
      await loadOptions();
      await loadData();
      await loadColumnConfig();
      await checkUserPermission();
      setConfigLoaded(true);
    };
    
    initialize();
  }, []);

  // 监听列配置变化，自动切换分页
  useEffect(() => {
    const newActiveTab = getDefaultActiveTab();
    setActiveTab(newActiveTab);
  }, [columnConfig]);

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
      
      // 获取可见字段
      const visibleFields = getVisibleFormFields();
      
      // 只保留可见字段的数据
      const filteredValues = {};
      visibleFields.forEach(field => {
        if (values.hasOwnProperty(field)) {
          filteredValues[field] = values[field];
        }
      });
      
      if (currentRecord.id && !currentRecord.id.startsWith('temp_')) {
        await materialCategoryApi.updateMaterialCategory(currentRecord.id, filteredValues);
        message.success('更新成功');
      } else {
        await materialCategoryApi.createMaterialCategory(filteredValues);
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
    // 获取可见字段
    const visibleFields = getVisibleFormFields();
    
    // 构建默认值对象
    const defaultValues = {
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
    
    // 只保留可见字段的默认值
    const newRecord = {};
    visibleFields.forEach(field => {
      if (defaultValues.hasOwnProperty(field)) {
        newRecord[field] = defaultValues[field];
      }
    });
    
    setCurrentRecord(newRecord);
    form.setFieldsValue(newRecord);
    setEditModalVisible(true);
  };

  // 保存列配置
  const saveColumnConfig = async (config) => {
    try {
      if (!isAdmin) {
        message.error('只有管理员可以保存列配置');
        return;
      }

      const allFields = Object.keys(fieldConfig);
      const completeConfig = {};
      
      allFields.forEach(field => {
        const fieldConfigItem = fieldConfig[field];
        // 必填字段始终设置为可见
        if (fieldConfigItem && fieldConfigItem.required) {
          completeConfig[field] = true;
        } else {
          completeConfig[field] = field in config ? config[field] : true;
        }
      });

      let newColumnOrder = [];
      
      if (columnSettingOrder.length > 0) {
        columnSettingOrder.forEach(key => {
          if (completeConfig[key] === true) {
            newColumnOrder.push(key);
          }
        });
      } else if (columnOrder.length > 0) {
        columnOrder.forEach(key => {
          if (completeConfig[key] === true) {
            newColumnOrder.push(key);
          }
        });
      }
      
      allFields.forEach(field => {
        if (completeConfig[field] === true && !newColumnOrder.includes(field)) {
          newColumnOrder.push(field);
        }
      });

      await columnConfigurationApi.saveColumnConfig('materialCategory', 'column_config', completeConfig);
      await columnConfigurationApi.saveColumnConfig('materialCategory', 'column_order', newColumnOrder);
      
      setColumnConfig(completeConfig);
      setColumnOrder(newColumnOrder);
      setColumnSettingOrder(newColumnOrder);
      setColumnSettingVisible(false);
      message.success('列配置已保存');
    } catch (error) {
      const errorMessage = error.response?.data?.message || error.response?.data?.error || error.message;
      if (errorMessage && errorMessage.includes('只有管理员')) {
        message.error('只有管理员可以保存列配置');
      } else {
        message.error('保存列配置失败: ' + errorMessage);
      }
    }
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
          fixed: config.fixed,
          render: (_, record) => {
            return (
              <div style={{ display: 'flex', gap: '2px', flexWrap: 'nowrap', justifyContent: 'center' }}>
                <Tooltip title="详情">
                  <Button
                    icon={<EyeOutlined />}
                    type="link"
                    size="small"
                    style={{ padding: '4px', minWidth: 'auto' }}
                    onClick={() => handleViewDetail(record)}
                  />
                </Tooltip>
                <Tooltip title="编辑">
                  <Button
                    icon={<EditOutlined />}
                    type="link"
                    size="small"
                    style={{ padding: '4px', minWidth: 'auto' }}
                    onClick={() => edit(record)}
                  />
                </Tooltip>
                <Popconfirm
                  title="确定删除吗?"
                  onConfirm={() => handleDelete(record.key)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Tooltip title="删除">
                    <Button
                      icon={<DeleteOutlined />}
                      type="link"
                      size="small"
                      danger
                      style={{ padding: '4px', minWidth: 'auto' }}
                    />
                  </Tooltip>
                </Popconfirm>
              </div>
            );
          },
        };
      }

      // 处理特殊字段的渲染和编辑
      let render;
      
      // 布尔字段 - 显示为开关
      const booleanFields = [
        'is_active', 'show_on_kanban', 'enable_batch', 'enable_barcode',
        'is_ink', 'is_accessory', 'is_consumable', 'is_recyclable', 'is_hazardous',
        'is_imported', 'is_customized', 'is_seasonal', 'is_fragile', 'is_perishable',
        'is_temperature_sensitive', 'is_moisture_sensitive', 'is_light_sensitive',
        'requires_special_storage', 'requires_certification'
      ];
      
      if (booleanFields.includes(key)) {
        render = (value) => <Switch checked={value} disabled />;
      } else if (key === 'material_type') {
        render = (value) => <Tag color={value === '主材' ? 'blue' : 'green'}>{value}</Tag>;
      } else if (['base_unit_name', 'auxiliary_unit_name', 'sales_unit_name'].includes(key)) {
        render = (value) => value || '-';
      } else if (['density', 'square_weight', 'latest_purchase_price', 'sales_price', 'product_quote_price', 'cost_price', 'carton_param1', 'carton_param2', 'carton_param3', 'carton_param4'].includes(key)) {
        render = (value) => value ? Number(value).toFixed(2) : '-';
      } else if (['shelf_life', 'warning_days', 'display_order'].includes(key)) {
        render = (value) => value || '-';
      } else {
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

  // 渲染简化的列设置界面
  const renderColumnSettings = () => {
    // 获取所有字段，按当前顺序排列
    const allFields = Object.keys(fieldConfig).filter(key => key !== 'action');
    
    // 构建完整的字段列表：包含所有字段，按当前顺序排列
    let displayFields = [];
    
    if (columnSettingOrder.length > 0) {
      // 首先添加当前顺序中的字段
      columnSettingOrder.forEach(field => {
        if (allFields.includes(field)) {
          displayFields.push(field);
        }
      });
      
      // 然后添加不在当前顺序中的字段（新字段或被取消勾选的字段）
      allFields.forEach(field => {
        if (!displayFields.includes(field)) {
          displayFields.push(field);
        }
      });
    } else {
      // 如果没有保存的顺序，使用默认顺序
      const defaultOrder = [
        // 基本信息
        'material_name', 'material_type',
        // 单位信息
        'base_unit_name', 'auxiliary_unit_name', 'sales_unit_name',
        // 物理属性
        'density', 'square_weight', 'shelf_life',
        // 检验质量
        'inspection_standard', 'quality_grade',
        // 价格信息
        'latest_purchase_price', 'sales_price', 'product_quote_price', 'cost_price',
        // 业务配置
        'show_on_kanban', 'account_subject', 'code_prefix', 'warning_days',
        // 纸箱参数
        'carton_param1', 'carton_param2', 'carton_param3', 'carton_param4',
        // 材料属性标识
        'enable_batch', 'enable_barcode', 'is_ink', 'is_accessory',
        'is_consumable', 'is_recyclable', 'is_hazardous', 'is_imported', 'is_customized',
        'is_seasonal', 'is_fragile', 'is_perishable', 'is_temperature_sensitive',
        'is_moisture_sensitive', 'is_light_sensitive', 'requires_special_storage', 'requires_certification',
        // 通用字段
        'display_order', 'is_active'
      ];
      
      // 按默认顺序排列
      defaultOrder.forEach(field => {
        if (allFields.includes(field)) {
          displayFields.push(field);
        }
      });
      
      // 添加不在默认顺序中的字段
      allFields.forEach(field => {
        if (!displayFields.includes(field)) {
          displayFields.push(field);
        }
      });
    }
    
    return (
      <div>
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">
            选择需要的字段，支持拖拽调整列顺序
          </Text>
        </div>
        
        {/* 简化的字段列表 */}
        <div 
          ref={scrollContainerRef}
          data-draggable="true"
          style={{ 
            maxHeight: '70vh',
            overflowY: 'auto',
            border: '1px solid #f0f0f0',
            borderRadius: '4px',
            padding: '8px',
            position: 'relative',
            background: 'linear-gradient(to bottom, rgba(24, 144, 255, 0.05) 0%, transparent 150px, transparent calc(100% - 150px), rgba(24, 144, 255, 0.05) 100%)'
          }}
          onDragOver={(e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // 强制设置拖拽效果
            setDropEffect(e);
          }}
          onDragEnter={(e) => {
            e.preventDefault();
            e.stopPropagation();
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            e.stopPropagation();
          }}
          onDrop={(e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // 如果拖拽到容器空白区域，添加到末尾
            const draggedField = e.dataTransfer.getData('text/plain');
            if (draggedField) {
              moveColumn(draggedField, displayFields.length);
            }
          }}
        >
          {displayFields.map((field) => {
            const config = fieldConfig[field];
            if (!config) return null;
            
            // 找到字段所属的分组，用于显示分组信息
            let groupInfo = null;
            Object.entries(fieldGroups).forEach(([groupKey, group]) => {
              if (group.fields.includes(field)) {
                groupInfo = { key: groupKey, ...group };
              }
            });
            
            const isVisible = columnConfig[field] !== false;
            
            return (
              <div
                key={field}
                data-draggable="true"
                style={{
                  padding: '12px',
                  border: '1px solid #d9d9d9',
                  borderRadius: '6px',
                  marginBottom: '4px', // 减少间距
                  backgroundColor: isVisible ? '#fff' : '#f5f5f5',
                  cursor: 'grab',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  transition: 'all 0.2s',
                  opacity: isVisible ? 1 : 0.7,
                  position: 'relative', // 为拖拽区域定位
                  userSelect: 'none' // 防止文本选择
                }}
                draggable
                onDragStart={(e) => handleDragStart(e, field)}
                onDragEnd={(e) => handleDragEnd(e, isVisible)}
                onDragOver={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  
                  // 强制设置拖拽效果
                  setDropEffect(e);
                  
                  const rect = e.currentTarget.getBoundingClientRect();
                  const mouseY = e.clientY;
                  const itemCenterY = rect.top + rect.height / 2;
                  
                  // 根据鼠标位置决定插入位置
                  if (mouseY < itemCenterY) {
                    // 插入到当前项之前
                    e.currentTarget.style.borderTop = '2px solid #1890ff';
                    e.currentTarget.style.borderBottom = '1px solid #d9d9d9';
                  } else {
                    // 插入到当前项之后
                    e.currentTarget.style.borderTop = '1px solid #d9d9d9';
                    e.currentTarget.style.borderBottom = '2px solid #1890ff';
                  }
                }}
                onDragEnter={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                }}
                onDragLeave={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  e.currentTarget.style.borderTop = '1px solid #d9d9d9';
                  e.currentTarget.style.borderBottom = '1px solid #d9d9d9';
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  // 重置边框样式
                  e.currentTarget.style.borderTop = '1px solid #d9d9d9';
                  e.currentTarget.style.borderBottom = '1px solid #d9d9d9';
                  
                  const draggedField = e.dataTransfer.getData('text/plain');
                  
                  if (draggedField !== field) {
                    const rect = e.currentTarget.getBoundingClientRect();
                    const mouseY = e.clientY;
                    const itemCenterY = rect.top + rect.height / 2;
                    
                    // 找到目标字段在当前顺序中的索引
                    let targetIndex = displayFields.indexOf(field);
                    
                    // 根据鼠标位置决定插入位置
                    if (mouseY >= itemCenterY) {
                      // 插入到当前项之后
                      targetIndex += 1;
                    }
                    // 如果鼠标在上半部分，就插入到当前项之前（targetIndex 保持不变）
                    
                    if (targetIndex !== -1) {
                      moveColumn(draggedField, targetIndex);
                    }
                  }
                }}
              >
                {/* 拖拽区域指示器 - 在项目上方 */}
                <div
                  style={{
                    position: 'absolute',
                    top: '-2px',
                    left: 0,
                    right: 0,
                    height: '4px',
                    backgroundColor: 'transparent',
                    cursor: 'grab',
                    zIndex: 1
                  }}
                  onDragOver={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // 强制设置拖拽效果
                    setDropEffect(e);
                    
                    e.currentTarget.style.backgroundColor = '#1890ff';
                  }}
                  onDragEnter={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                  }}
                  onDragLeave={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                  onDrop={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    e.currentTarget.style.backgroundColor = 'transparent';
                    
                    const draggedField = e.dataTransfer.getData('text/plain');
                    if (draggedField !== field) {
                      const targetIndex = displayFields.indexOf(field);
                      if (targetIndex !== -1) {
                        moveColumn(draggedField, targetIndex);
                      }
                    }
                  }}
                />
                
                <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                  <MenuOutlined style={{ marginRight: 8, color: '#999', cursor: 'grab' }} />
                  <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
                    <div style={{ 
                      fontWeight: 'bold', 
                      color: isVisible ? '#000' : '#999',
                      display: 'flex',
                      alignItems: 'center'
                    }}>
                      {config.title}
                      {config.required && (
                        <span style={{ color: '#ff4d4f', marginLeft: '4px' }}>*</span>
                      )}
                    </div>
                    {groupInfo && (
                      <div style={{ fontSize: '12px', color: '#666', marginLeft: '8px', display: 'flex', alignItems: 'center' }}>
                        <span>{groupInfo.icon} {groupInfo.title}</span>
                        <Badge 
                          count={groupInfo.fields.filter(f => getVisibleFormFields().includes(f)).length} 
                          size="small" 
                          style={{ 
                            backgroundColor: '#52c41a', 
                            marginLeft: '4px',
                            fontSize: '10px'
                          }} 
                        />
                      </div>
                    )}
                  </div>
                </div>
                
                <Checkbox
                  checked={isVisible}
                  disabled={config.required} // 必填字段禁用复选框
                  onChange={(e) => {
                    const newConfig = {
                      ...columnConfig,
                      [field]: e.target.checked
                    };
                    setColumnConfig(newConfig);
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
      <div style={{ padding: '24px' }}>
        <style>
          {`
            [draggable="true"] {
              cursor: grab !important;
              user-select: none;
            }
            [draggable="true"]:active {
              cursor: grabbing !important;
            }
            * {
              -webkit-user-drag: none;
              user-drag: none;
            }
            [data-draggable="true"][draggable="true"] {
              -webkit-user-drag: element;
              user-drag: element;
            }
            input, textarea {
              user-select: text;
            }
          `}
        </style>
        <Card>
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div>
                <Title level={4} style={{ margin: 0 }}>
                  材料分类管理
                  <Badge count={getVisibleFormFields().length} style={{ marginLeft: 8 }} />
                </Title>
              </div>
              
              <Space>
                {isAdmin && configLoaded && (
                  <Button 
                    icon={<SettingOutlined />} 
                    onClick={() => setColumnSettingVisible(true)}
                  >
                    字段设置
                  </Button>
                )}
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
                cell: SimpleColumnHeader,
              },
            }}
            bordered
            dataSource={data}
            columns={configLoaded ? generateColumns() : []}
            pagination={pagination}
            loading={loading || !configLoaded}
            onChange={handleTableChange}
            scroll={{ x: 2000, y: 600 }}
            size="middle"
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
              <Tabs activeKey={activeTab} onChange={setActiveTab}>
                {Object.entries(fieldGroups).map(([groupKey, group]) => {
                  // 过滤出当前分组中可见的字段
                  const visibleFields = group.fields.filter(field => 
                    getVisibleFormFields().includes(field)
                  );
                  
                  // 如果分组中没有可见字段，不显示该分组
                  if (visibleFields.length === 0) return null;
                  
                  return (
                    <TabPane 
                      tab={
                        <Space>
                          <span>{group.icon}</span>
                          <span>{group.title}</span>
                          <Badge count={visibleFields.length} size="small" style={{ backgroundColor: '#52c41a' }} />
                        </Space>
                      } 
                      key={groupKey}
                    >
                      <Row gutter={16}>
                        {visibleFields.map(field => {
                          const config = fieldConfig[field];
                          if (!config) return null;
                          
                          let formItem;
                          if (field === 'material_type') {
                            formItem = <Input disabled />;
                          } else if (['base_unit_id', 'auxiliary_unit_id', 'sales_unit_id'].includes(field)) {
                            formItem = <Input disabled />;
                          } else if (field === 'is_active') {
                            formItem = <Switch disabled />;
                          } else if (field === 'show_on_kanban') {
                            formItem = <Switch disabled />;
                          } else if (field.startsWith('is_') || field.includes('enable')) {
                            formItem = <Switch disabled />;
                          } else if (['density', 'square_weight', 'latest_purchase_price', 'sales_price', 'product_quote_price', 'cost_price', 'carton_param1', 'carton_param2', 'carton_param3', 'carton_param4'].includes(field)) {
                            formItem = <InputNumber style={{ width: '100%' }} disabled />;
                          } else if (['shelf_life', 'warning_days', 'display_order'].includes(field)) {
                            formItem = <InputNumber style={{ width: '100%' }} disabled />;
                          } else {
                            formItem = <Input disabled />;
                          }
                          
                          return (
                            <Col span={8} key={field}>
                              <Form.Item label={config.title} name={field}>
                                {formItem}
                              </Form.Item>
                            </Col>
                          );
                        })}
                      </Row>
                    </TabPane>
                  );
                })}
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
              <Tabs activeKey={activeTab} onChange={setActiveTab}>
                {Object.entries(fieldGroups).map(([groupKey, group]) => {
                  // 过滤出当前分组中可见的字段
                  const visibleFields = group.fields.filter(field => 
                    getVisibleFormFields().includes(field)
                  );
                  
                  // 如果分组中没有可见字段，不显示该分组
                  if (visibleFields.length === 0) return null;
                  
                  return (
                    <TabPane 
                      tab={
                        <Space>
                          <span>{group.icon}</span>
                          <span>{group.title}</span>
                          <Badge count={visibleFields.length} size="small" style={{ backgroundColor: '#52c41a' }} />
                        </Space>
                      } 
                      key={groupKey}
                    >
                      <Row gutter={16}>
                        {visibleFields.map(field => {
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
                          } else if (field === 'is_active') {
                            formItem = <Switch />;
                          } else if (field === 'show_on_kanban') {
                            formItem = <Switch />;
                          } else if (field.startsWith('is_') || field.includes('enable')) {
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
                  );
                })}
              </Tabs>
            </Form>
          </Modal>

          {/* 列设置抽屉 - 只有管理员可见 */}
          {isAdmin && configLoaded && (
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
              width="30%"
            >
              <div>
               
                {renderColumnSettings()}
                
                <Divider />
                
                <Space style={{ width: '100%', justifyContent: 'center' }}>
                  <Button 
                    type="primary" 
                    onClick={() => saveColumnConfig(columnConfig)}
                  >
                    保存设置
                  </Button>
                  <Button 
                    onClick={async () => {
                      try {
                        if (!isAdmin) {
                          message.error('只有管理员可以重置列配置');
                          return;
                        }

                        // 删除后端配置
                        await columnConfigurationApi.deleteColumnConfig('materialCategory', 'column_config');
                        await columnConfigurationApi.deleteColumnConfig('materialCategory', 'column_order');
                        
                        // 重置为默认配置
                        setColumnConfig({});
                        setColumnOrder([]);
                        setColumnSettingOrder([]);
                        message.success('已重置为默认设置');
                      } catch (error) {
                        // 检查是否是权限错误
                        const errorMessage = error.response?.data?.message || error.response?.data?.error || error.message;
                        if (errorMessage && errorMessage.includes('只有管理员')) {
                          message.error('只有管理员可以重置列配置');
                        } else {
                          message.error('重置列配置失败: ' + errorMessage);
                        }
                      }
                    }}
                  >
                    重置默认
                  </Button>
                </Space>
              </div>
            </Drawer>
          )}
        </Card>
      </div>
  );
};

export default MaterialCategoryManagement; 