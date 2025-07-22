import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Switch,
  InputNumber,
  Space,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Form,
  Tooltip,
  Select,
  Modal,
  Tabs,
  Checkbox,
  Divider,
  Drawer,
  Badge
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
  ClearOutlined,
  MenuOutlined,
  EyeOutlined
} from '@ant-design/icons';
import processCategoryApi from '../../../api/base-archive/base-category/processCategoryApi';
import { authApi } from '../../../api/auth';
import { useAutoScroll } from '../../../hooks/useAutoScroll';
import { columnConfigurationApi } from '../../../api/system/columnConfiguration';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

// 拖拽列头组件
const SimpleColumnHeader = ({ children, moveKey, onMove, ...restProps }) => {
  return (
    <th {...restProps}>
      <div style={{ cursor: 'move', userSelect: 'none' }}>
        {children}
      </div>
    </th>
  );
};

const ProcessCategoryManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total) => `共 ${total} 条记录`,
  });

  // 选择选项
  const [categoryTypeOptions, setCategoryTypeOptions] = useState([]);
  const [dataCollectionModeOptions, setDataCollectionModeOptions] = useState([]);

  // 新增状态变量
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [columnConfig, setColumnConfig] = useState({});
  const [columnOrder, setColumnOrder] = useState([]);
  const [columnSettingOrder, setColumnSettingOrder] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');
  const [configLoaded, setConfigLoaded] = useState(false);
  const [forceUpdate, setForceUpdate] = useState(0);
  const [columnSettingVisible, setColumnSettingVisible] = useState(false);
  
  const [editForm] = Form.useForm();
  const [detailForm] = Form.useForm();
  const searchInputRef = useRef(null);
  const scrollContainerRef = useRef(null);
  
  // 使用自动滚动钩子
  const { setDropEffect } = useAutoScroll(scrollContainerRef);

  // 字段配置
  const fieldConfig = {
    process_name: { title: '工序分类', required: true },
    category_type: { title: '类型', required: false },
    data_collection_mode: { title: '数据自动采集模式', required: false },
    sort_order: { title: '排序', required: false },
    is_enabled: { title: '是否启用', required: false },
    show_data_collection_interface: { title: '显示数据采集界面', required: false },
    description: { title: '描述', required: false },
    created_by_username: { title: '创建人', required: false },
    created_at: { title: '创建时间', required: false },
    updated_by_username: { title: '修改人', required: false },
    updated_at: { title: '修改时间', required: false },
    // 基础配置字段
    report_quantity: { title: '上报数量', required: false },
    report_personnel: { title: '上报人员', required: false },
    report_data: { title: '上报数据', required: false },
    report_kg: { title: '上报KG', required: false },
    report_number: { title: '报号', required: false },
    report_time: { title: '上报时间', required: false },
    down_report_time: { title: '下报时间', required: false },
    machine_speed: { title: '机速', required: false },
    cutting_specs: { title: '分切规格', required: false },
    aging_room: { title: '熟化室', required: false },
    reserved_char_1: { title: '预留字符1', required: false },
    reserved_char_2: { title: '预留字符2', required: false },
    net_weight: { title: '净重', required: false },
    production_task_display_order: { title: '生产任务显示序号', required: false },
    // 装箱配置字段
    packing_bags_count: { title: '装箱袋数', required: false },
    pallet_barcode: { title: '托盘条码', required: false },
    pallet_bag_loading: { title: '托盘装袋数', required: false },
    box_loading_count: { title: '入托箱数', required: false },
    seed_bag_count: { title: '种袋数', required: false },
    defect_bag_count: { title: '除袋数', required: false },
    report_staff: { title: '上报人员', required: false },
    shortage_count: { title: '缺数', required: false },
    material_specs: { title: '材料规格', required: false },
    color_mixing_count: { title: '合色数', required: false },
    batch_bags: { title: '批袋', required: false },
    production_date: { title: '生产日期', required: false },
    compound: { title: '复合', required: false },
    process_machine_allocation: { title: '工艺分机台', required: false },
    // 持续率配置字段
    continuity_rate: { title: '持续率', required: false },
    strip_head_change_count: { title: '换条头数', required: false },
    plate_support_change_count: { title: '换版支数', required: false },
    plate_change_count: { title: '换版次数', required: false },
    lamination_change_count: { title: '换贴合报', required: false },
    plate_making_multiple: { title: '制版倍送', required: false },
    algorithm_time: { title: '换算时间', required: false },
    timing: { title: '计时', required: false },
    pallet_time: { title: '托盘时间', required: false },
    glue_water_change_count: { title: '换胶水数', required: false },
    glue_drip_bag_change: { title: '换条胶袋', required: false },
    pallet_sub_bag_change: { title: '换压报料', required: false },
    transfer_report_change: { title: '换转报料', required: false },
    auto_print: { title: '自动打印', required: false },
    // 过程管控字段
    process_rate: { title: '过程率', required: false },
    color_set_change_count: { title: '换套色数', required: false },
    mesh_format_change_count: { title: '换网格数', required: false },
    overtime: { title: '加班', required: false },
    team_date: { title: '班组日期', required: false },
    sampling_time: { title: '打样时间', required: false },
    start_reading: { title: '开始读数', required: false },
    count_times: { title: '计次', required: false },
    blade_count: { title: '刀刃数', required: false },
    power_consumption: { title: '用电量', required: false },
    maintenance_time: { title: '维修时间', required: false },
    end_time: { title: '结束时间', required: false },
    malfunction_material_collection: { title: '故障次数领料', required: false },
    is_query_machine: { title: '是否询机', required: false },
    // MES配置字段
    mes_report_kg_manual: { title: 'MES上报kg取用里kg', required: false },
    mes_kg_auto_calculation: { title: 'MES上报kg自动接算', required: false },
    auto_weighing_once: { title: '自动称重一次', required: false },
    mes_process_feedback_clear: { title: 'MES工艺反馈空工艺', required: false },
    mes_consumption_solvent_by_ton: { title: 'MES消耗溶剂用里按吨', required: false },
    single_report_open: { title: '单报装打开', required: false },
    multi_condition_open: { title: '多条件同时开工', required: false },
    mes_line_start_work_order: { title: 'MES线本单开工单', required: false },
    mes_material_kg_consumption: { title: 'MES上报材料kg用里消费kg', required: false },
    mes_report_not_less_than_kg: { title: 'MES上报数不能小于上报kg', required: false },
    mes_water_consumption_by_ton: { title: 'MES耗水用里按吨', required: false },
    // 自检类型字段
    self_check_type_1: { title: '自检1', required: false },
    self_check_type_2: { title: '自检2', required: false },
    self_check_type_3: { title: '自检3', required: false },
    self_check_type_4: { title: '自检4', required: false },
    self_check_type_5: { title: '自检5', required: false },
    self_check_type_6: { title: '自检6', required: false },
    self_check_type_7: { title: '自检7', required: false },
    self_check_type_8: { title: '自检8', required: false },
    self_check_type_9: { title: '自检9', required: false },
    self_check_type_10: { title: '自检10', required: false },
    // 工艺预料字段
    process_material_1: { title: '工艺1', required: false },
    process_material_2: { title: '工艺2', required: false },
    process_material_3: { title: '工艺3', required: false },
    process_material_4: { title: '工艺4', required: false },
    process_material_5: { title: '工艺5', required: false },
    process_material_6: { title: '工艺6', required: false },
    process_material_7: { title: '工艺7', required: false },
    process_material_8: { title: '工艺8', required: false },
    process_material_9: { title: '工艺9', required: false },
    process_material_10: { title: '工艺10', required: false },
    // 预留字段
    reserved_popup_1: { title: '弹出1', required: false },
    reserved_popup_2: { title: '弹出2', required: false },
    reserved_popup_3: { title: '弹出3', required: false },
    reserved_dropdown_1: { title: '下拉1', required: false },
    reserved_dropdown_2: { title: '下拉2', required: false },
    reserved_dropdown_3: { title: '下拉3', required: false },
    // 数字字段
    number_1: { title: '数字1', required: false },
    number_2: { title: '数字2', required: false },
    number_3: { title: '数字3', required: false },
    number_4: { title: '数字4', required: false },
  };

  // 字段分组
  const fieldGroups = {
    basic: {
      title: '基本信息',
      icon: '📋',
      fields: [
        'process_name', 'category_type', 'data_collection_mode', 'sort_order', 
        'is_enabled', 'show_data_collection_interface', 'description'
      ]
    },
    custom: {
      title: '自定义字段',
      icon: '🔧',
      fields: [
        'self_check_type_1', 'self_check_type_2', 'self_check_type_3', 'self_check_type_4', 'self_check_type_5',
        'self_check_type_6', 'self_check_type_7', 'self_check_type_8', 'self_check_type_9', 'self_check_type_10',
        'process_material_1', 'process_material_2', 'process_material_3', 'process_material_4', 'process_material_5',
        'process_material_6', 'process_material_7', 'process_material_8', 'process_material_9', 'process_material_10',
        'reserved_popup_1', 'reserved_popup_2', 'reserved_popup_3', 'reserved_dropdown_1', 'reserved_dropdown_2', 'reserved_dropdown_3',
        'number_1', 'number_2', 'number_3', 'number_4'
      ]
    },
    basicConfig: {
      title: '基础配置',
      icon: '⚙️',
      fields: [
        'report_quantity', 'report_personnel', 'report_data', 'report_kg', 'report_number',
        'report_time', 'down_report_time', 'machine_speed', 'cutting_specs', 'aging_room',
        'reserved_char_1', 'reserved_char_2', 'net_weight', 'production_task_display_order'
      ]
    },
    packingConfig: {
      title: '装箱配置',
      icon: '📦',
      fields: [
        'packing_bags_count', 'pallet_barcode', 'pallet_bag_loading', 'box_loading_count',
        'seed_bag_count', 'defect_bag_count', 'report_staff', 'shortage_count',
        'material_specs', 'color_mixing_count', 'batch_bags', 'production_date',
        'compound', 'process_machine_allocation'
      ]
    },
    continuityConfig: {
      title: '持续率配置',
      icon: '📊',
      fields: [
        'continuity_rate', 'strip_head_change_count', 'plate_support_change_count', 'plate_change_count',
        'lamination_change_count', 'plate_making_multiple', 'algorithm_time', 'timing',
        'pallet_time', 'glue_water_change_count', 'glue_drip_bag_change', 'pallet_sub_bag_change',
        'transfer_report_change', 'auto_print'
      ]
    },
    processControl: {
      title: '过程管控',
      icon: '🎯',
      fields: [
        'process_rate', 'color_set_change_count', 'mesh_format_change_count', 'overtime',
        'team_date', 'sampling_time', 'start_reading', 'count_times', 'blade_count',
        'power_consumption', 'maintenance_time', 'end_time', 'malfunction_material_collection',
        'is_query_machine'
      ]
    },
    mesConfig: {
      title: 'MES配置',
      icon: '🏭',
      fields: [
        'mes_report_kg_manual', 'mes_kg_auto_calculation', 'auto_weighing_once', 'mes_process_feedback_clear',
        'mes_consumption_solvent_by_ton', 'single_report_open', 'multi_condition_open',
        'mes_line_start_work_order', 'mes_material_kg_consumption', 'mes_report_not_less_than_kg',
        'mes_water_consumption_by_ton'
      ]
    },
    audit: {
      title: '审计信息',
      icon: '📝',
      fields: ['created_by_username', 'created_at', 'updated_by_username', 'updated_at']
    }
  };

  // 获取可见表单字段
  const getVisibleFormFields = () => {
    const allFields = Object.keys(fieldConfig).filter(key => key !== 'action');
    return allFields.filter(field => {
      const fieldConfigItem = fieldConfig[field];
      if (fieldConfigItem && fieldConfigItem.required) {
        return true; // 必填字段始终可见
      }
      return columnConfig[field] !== false; // 根据当前配置判断可见性
    });
  };

  // 获取默认激活的分页
  const getDefaultActiveTab = () => {
    const visibleFields = getVisibleFormFields();
    
    // 找到第一个有可见字段的分组
    for (const [groupKey, group] of Object.entries(fieldGroups)) {
      const hasVisibleFields = group.fields.some(field => visibleFields.includes(field));
      if (hasVisibleFields) {
        return groupKey;
      }
    }
    
    return 'basic'; // 默认返回基本信息
  };

  // 获取当前分页的可见字段数量
  const getActiveTabVisibleFieldCount = () => {
    const currentGroup = fieldGroups[activeTab];
    if (!currentGroup) return 0;
    
    const visibleFields = getVisibleFormFields();
    return currentGroup.fields.filter(field => visibleFields.includes(field)).length;
  };

  // 获取可见列
  const getVisibleColumns = () => {
    const visibleFields = getVisibleFormFields();
    return visibleFields.filter(field => {
      const config = fieldConfig[field];
      return config && !['created_at', 'updated_at', 'created_by_name', 'updated_by_name'].includes(field);
    });
  };

  // 移动列
  const moveColumn = (dragKey, targetIndex) => {
    // 获取所有字段
    const allFields = Object.keys(fieldConfig).filter(key => key !== 'action');
    let currentOrder = [...columnOrder];
    
    // 如果当前顺序为空，使用所有字段的默认顺序
    if (currentOrder.length === 0) {
      currentOrder = [...allFields];
    }
    
    // 确保拖拽的字段在当前顺序中
    if (!currentOrder.includes(dragKey)) {
      currentOrder.push(dragKey);
    }
    
    const dragIndex = currentOrder.indexOf(dragKey);
    
    // 如果拖拽字段不在列表中，直接返回
    if (dragIndex === -1) {
      return;
    }
    
    // 移除拖拽字段
    currentOrder.splice(dragIndex, 1);
    
    // 确保目标索引在有效范围内
    const validTargetIndex = Math.max(0, Math.min(targetIndex, currentOrder.length));
    
    // 插入到目标位置
    currentOrder.splice(validTargetIndex, 0, dragKey);
    
    console.log('移动字段:', dragKey, '到位置:', validTargetIndex, '新顺序:', currentOrder);
    
    setColumnOrder(currentOrder);
    setColumnSettingOrder(currentOrder);
    
    // 强制重新渲染
    setForceUpdate(prev => prev + 1);
  };

  // 加载列配置
  const loadColumnConfig = async () => {
    try {
      // 获取列配置和列顺序
      const [configResponse, orderResponse] = await Promise.all([
        columnConfigurationApi.getColumnConfig('processCategory', 'column_config'),
        columnConfigurationApi.getColumnConfig('processCategory', 'column_order')
      ]);
      
      console.log('加载配置响应:', configResponse);
      console.log('加载顺序响应:', orderResponse);
      
      let columnConfigData = {};
      let columnOrderData = [];
      
      if (configResponse && configResponse.data && configResponse.data.success) {
        // 从保存的响应中，数据在 configResponse.data.data.config_data 中
        columnConfigData = configResponse.data.data.config_data || configResponse.data.data || {};
      }
      
      if (orderResponse && orderResponse.data && orderResponse.data.success) {
        // 从保存的响应中，数据在 orderResponse.data.data.config_data 中
        columnOrderData = orderResponse.data.data.config_data || orderResponse.data.data || [];
      }
      
      console.log('解析后的配置数据:', columnConfigData);
      console.log('解析后的顺序数据:', columnOrderData);
      
      // 设置默认配置（如果API没有返回数据）
      if (Object.keys(columnConfigData).length === 0) {
        Object.keys(fieldConfig).forEach(field => {
          columnConfigData[field] = true; // 默认所有字段都可见
        });
      }
      
      setColumnConfig(columnConfigData);
      setColumnOrder(columnOrderData);
      setColumnSettingOrder(columnOrderData);
      setConfigLoaded(true);
    } catch (error) {
      console.error('加载列配置失败:', error);
      // 设置默认配置
      const defaultConfig = {};
      Object.keys(fieldConfig).forEach(field => {
        defaultConfig[field] = true;
      });
      setColumnConfig(defaultConfig);
      setColumnSettingOrder([]);
      setConfigLoaded(true);
    }
  };

  // 检查用户权限
  const checkUserPermission = async () => {
    try {
      // 使用封装的权限检查API
      const adminStatus = await authApi.checkAdminStatus();
      setIsAdmin(adminStatus.isAdmin);
      
      console.log(`用户权限检查: ${adminStatus.user.email}, is_admin=${adminStatus.user.is_admin}, is_superadmin=${adminStatus.user.is_superadmin}`);
    } catch (error) {
      console.error('检查用户权限失败:', error);
      setIsAdmin(false);
    }
  };

  // 初始化
  useEffect(() => {
    const initialize = async () => {
      await Promise.all([
        loadColumnConfig(),
        checkUserPermission()
      ]);
    };
    initialize();
  }, []);

  // 监听列配置变化，自动切换分页和更新数字
  useEffect(() => {
    const newActiveTab = getDefaultActiveTab();
    setActiveTab(newActiveTab);
  }, [columnConfig, columnSettingOrder]);

  useEffect(() => {
    loadData();
    loadOptions();
  }, [pagination.current, pagination.pageSize, searchText]);

  const loadOptions = async () => {
    try {
      // 先设置静态选项测试
      setCategoryTypeOptions([
        { value: 'laminating', label: '淋膜' }
      ]);
      
      setDataCollectionModeOptions([
        { value: 'auto_weighing_scanning', label: '自动称重扫码模式' },
        { value: 'auto_meter_scanning', label: '自动取米扫码模式' },
        { value: 'auto_scanning', label: '自动扫码模式' },
        { value: 'auto_weighing', label: '自动称重模式' },
        { value: 'weighing_only', label: '仅称重模式' },
        { value: 'scanning_summary_weighing', label: '扫码汇总称重模式' }
      ]);

      // 尝试从API获取选项
      const [typeRes, modeRes] = await Promise.all([
        processCategoryApi.getProcessCategoryTypeOptions(),
        processCategoryApi.getDataCollectionModeOptions()
      ]);
      
      // 处理类型选项
      if (isSuccessResp(typeRes)) {
        const options = typeRes.data.data || [];
        // 过滤掉value为空字符串的选项
        setCategoryTypeOptions(options.filter(option => option.value !== ''));
      } else if (typeRes && typeRes.data && Array.isArray(typeRes.data)) {
        setCategoryTypeOptions(typeRes.data.filter(option => option.value !== ''));
      }
      
      // 处理数据采集模式选项
      if (isSuccessResp(modeRes)) {
        const options = modeRes.data.data || [];
        // 过滤掉value为空字符串的选项
        setDataCollectionModeOptions(options.filter(option => option.value !== ''));
      } else if (modeRes && modeRes.data && Array.isArray(modeRes.data)) {
        setDataCollectionModeOptions(modeRes.data.filter(option => option.value !== ''));
      }
    } catch (error) {
      console.error('加载选项失败:', error);
      // 保持静态选项作为后备
    }
  };

  // 新增: 通用成功判断函数
  const isSuccessResp = (resp) => {
    return resp && resp.data && (resp.data.success === true || resp.data.code === 200);
  };

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await processCategoryApi.getProcessCategories({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      if (isSuccessResp(response)) {
        const { process_categories, items, total, current_page } = response.data.data;
        const list = process_categories || items || [];
        
        // 为每行数据添加key
        const dataWithKeys = list.map((item, index) => ({
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
      console.error('加载数据失败:', error);
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理分页变化
  const handleTableChange = (paginationConfig) => {
    setPagination(prev => ({
      ...prev,
      current: paginationConfig.current,
      pageSize: paginationConfig.pageSize,
    }));
  };

  // 处理搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData();
  };

  // 处理重置
  const handleReset = () => {
    setSearchText('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData();
  };

  // 刷新数据
  const handleRefresh = () => {
    setSearchText('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData();
  };



  // 删除记录
  const deleteRecord = async (record) => {
    try {
      await processCategoryApi.deleteProcessCategory(record.id);
      message.success('删除成功');
      loadData();
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  // 编辑记录
  const edit = (record) => {
    setCurrentRecord(record);
    editForm.setFieldsValue(record);
    setEditModalVisible(true);
  };

  // 取消编辑
  const cancel = () => {
    setEditModalVisible(false);
    setCurrentRecord(null);
    editForm.resetFields();
  };

  // 保存编辑
  const saveModal = async () => {
    try {
      const values = await editForm.validateFields();
      
      if (currentRecord?.id) {
        // 更新
        const response = await processCategoryApi.updateProcessCategory(currentRecord.id, values);
        if (isSuccessResp(response)) {
          message.success('更新成功');
          setEditModalVisible(false);
          setCurrentRecord(null);
          editForm.resetFields();
          loadData();
        } else {
          message.error(response?.data?.message || '更新失败');
        }
      } else {
        // 新建
        await createProcessCategory(values);
      }
    } catch (error) {
      console.error('保存失败:', error);
      message.error('保存失败');
    }
  };

  // 查看详情
  const handleViewDetail = (record) => {
    setCurrentRecord(record);
    detailForm.setFieldsValue(record);
    setDetailModalVisible(true);
  };

  // 删除记录
  const handleDelete = async (key) => {
    try {
      await processCategoryApi.deleteProcessCategory(key);
      message.success('删除成功');
      loadData();
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  // 新增记录
  const handleAdd = () => {
    setCurrentRecord(null);
    editForm.resetFields();
    editForm.setFieldsValue({
        sort_order: 0,
        is_enabled: true,
        show_data_collection_interface: false
      });
    setEditModalVisible(true);
  };

  // 创建新记录
  const createProcessCategory = async (values) => {
    try {
        const response = await processCategoryApi.createProcessCategory(values);
        if (isSuccessResp(response)) {
          message.success('创建成功');
        setEditModalVisible(false);
        setCurrentRecord(null);
        editForm.resetFields();
          loadData();
        } else {
          message.error(response?.data?.message || '创建失败');
      }
    } catch (error) {
      console.error('创建失败:', error);
      message.error('创建失败');
    }
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
      
      // 优先使用传递的顺序信息
      if (config._columnOrder && config._columnOrder.length > 0) {
        newColumnOrder = [...config._columnOrder];
        console.log('使用传递的顺序信息:', newColumnOrder);
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

      console.log('保存列配置:', completeConfig);
      console.log('保存列顺序:', newColumnOrder);
      
      const configResponse = await columnConfigurationApi.saveColumnConfig('processCategory', 'column_config', completeConfig);
      const orderResponse = await columnConfigurationApi.saveColumnConfig('processCategory', 'column_order', newColumnOrder);
      
      console.log('配置保存响应:', configResponse);
      console.log('顺序保存响应:', orderResponse);
      
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

  // 重置列配置
  const resetColumnConfig = async () => {
    try {
      // 删除列配置和列顺序
      await Promise.all([
        columnConfigurationApi.deleteColumnConfig('processCategory', 'column_config'),
        columnConfigurationApi.deleteColumnConfig('processCategory', 'column_order')
      ]);
      
      // 设置默认配置
      const defaultConfig = {};
      Object.keys(fieldConfig).forEach(field => {
        defaultConfig[field] = true;
      });
      setColumnConfig(defaultConfig);
      setColumnOrder([]);
      setColumnSettingOrder([]);
      message.success('列配置重置成功');
    } catch (error) {
      console.error('重置列配置失败:', error);
      message.error('列配置重置失败');
    }
  };

  // 生成列配置
  const generateColumns = () => {
    const visibleFields = getVisibleFormFields();
    const columns = [];

    // 按照保存的列顺序来生成列
    let orderedVisibleFields = [];
    
    if (columnOrder.length > 0) {
      // 按照保存的顺序排列可见字段
      columnOrder.forEach(field => {
        if (visibleFields.includes(field)) {
          orderedVisibleFields.push(field);
        }
      });
      
      // 添加不在保存顺序中的可见字段（新字段）
      visibleFields.forEach(field => {
        if (!orderedVisibleFields.includes(field)) {
          orderedVisibleFields.push(field);
        }
      });
    } else {
      // 如果没有保存的顺序，使用默认顺序
      orderedVisibleFields = visibleFields;
    }
    
    // 添加调试日志
    console.log('生成列 - 可见字段:', visibleFields);
    console.log('生成列 - 保存顺序:', columnOrder);
    console.log('生成列 - 最终顺序:', orderedVisibleFields);

    // 添加可见字段列
    orderedVisibleFields.forEach(field => {
      const config = fieldConfig[field];
      if (!config) return;

      let column = {
        title: config.title,
        dataIndex: field,
        key: field,
      width: 120,
        render: (text, record) => {
          if (field === 'is_enabled') {
            return <Switch checked={text} size="small" disabled />;
          } else if (field === 'category_type') {
        const option = categoryTypeOptions.find(opt => opt.value === text);
        return option ? option.label : text || '-';
          } else if (field === 'data_collection_mode') {
            const option = dataCollectionModeOptions.find(opt => opt.value === text);
            return option ? option.label : text || '-';
          } else if (field === 'created_at' || field === 'updated_at') {
            return text ? new Date(text).toLocaleString() : '-';
          } else if (field === 'process_name') {
            return <strong>{text}</strong>;
          } else {
            return text || '-';
          }
        }
      };

      columns.push(column);
    });

    // 添加操作列
    columns.push({
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              size="small"
              onClick={() => handleViewDetail(record)}
              style={{ padding: '4px 8px' }}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              size="small"
              onClick={() => edit(record)}
              style={{ padding: '4px 8px' }}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Popconfirm
              title="确定删除这条记录吗？"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="text"
                icon={<DeleteOutlined />}
                size="small"
                danger
                style={{ padding: '4px 8px' }}
              />
            </Popconfirm>
          </Tooltip>
          </Space>
      ),
    });

    return columns;
  };

  // 渲染列设置
  const renderColumnSettings = () => {
    // 获取所有字段，按当前顺序排列
    const allFields = Object.keys(fieldConfig).filter(key => key !== 'action');
    
    // 构建完整的字段列表：包含所有字段，按当前顺序排列
    let displayFields = [];
    let visibleFields = [];
    let hiddenFields = [];
    
    if (columnOrder.length > 0) {
      // 首先添加当前顺序中的字段（去重）
      const addedFields = new Set();
      columnOrder.forEach(field => {
        if (allFields.includes(field) && !addedFields.has(field)) {
          // 根据可见性分类
          if (columnConfig[field] !== false) {
            visibleFields.push(field);
          } else {
            hiddenFields.push(field);
          }
          addedFields.add(field);
        }
      });
      
      // 然后添加不在当前顺序中的字段（新字段）
      allFields.forEach(field => {
        if (!addedFields.has(field)) {
          // 根据可见性分类
          if (columnConfig[field] !== false) {
            visibleFields.push(field);
          } else {
            hiddenFields.push(field);
          }
          addedFields.add(field);
        }
      });
    } else {
      // 如果没有保存的顺序，使用所有字段的默认顺序
      allFields.forEach(field => {
        if (columnConfig[field] !== false) {
          visibleFields.push(field);
        } else {
          hiddenFields.push(field);
        }
      });
    }
    
    // 先显示可见字段，再显示隐藏字段
    displayFields = [...visibleFields, ...hiddenFields];
    
    console.log('字段设置抽屉 - 当前顺序:', columnOrder);
    console.log('字段设置抽屉 - 显示字段:', displayFields);
    
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
                  marginBottom: '4px',
                  backgroundColor: isVisible ? '#fff' : '#f5f5f5',
                  cursor: 'grab',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  transition: 'all 0.2s',
                  opacity: isVisible ? 1 : 0.7,
                  position: 'relative',
                  userSelect: 'none'
                }}
                draggable
                onDragStart={(e) => {
                  console.log('开始拖拽字段:', field);
                  e.dataTransfer.setData('text/plain', field);
                  e.dataTransfer.effectAllowed = 'move';
                }}
                onDragEnd={(e) => {
                  e.currentTarget.style.backgroundColor = isVisible ? '#fff' : '#f5f5f5';
                }}
                onDragOver={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
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
                  
                  const draggedField = e.dataTransfer.getData('text/plain');
                  console.log('拖拽到字段:', field, '拖拽的字段:', draggedField);
                  
                  if (draggedField !== field) {
                    // 获取当前保存的顺序列表
                    const allFields = Object.keys(fieldConfig).filter(key => key !== 'action');
                    let currentOrder = [...columnOrder];
                    
                    // 如果当前顺序为空，使用所有字段的默认顺序
                    if (currentOrder.length === 0) {
                      currentOrder = [...allFields];
                    }
                    
                    // 找到目标字段在保存顺序中的索引
                    const targetIndex = currentOrder.indexOf(field);
                    console.log('目标字段索引:', targetIndex);
                    
                    if (targetIndex !== -1) {
                      moveColumn(draggedField, targetIndex);
                    }
                  }
                }}
              >

                
                {/* 字段信息 */}
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
                          count={groupInfo.fields.filter(f => {
                            // 直接计算可见性，不依赖 getVisibleFormFields 函数
                            const fieldConfigItem = fieldConfig[f];
                            if (fieldConfigItem && fieldConfigItem.required) {
                              return true; // 必填字段始终可见
                            }
                            return columnConfig[f] !== false; // 根据当前配置判断可见性
                          }).length} 
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
                    
                    // 强制重新渲染以更新数字
                    setForceUpdate(prev => prev + 1);
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>
    );
  };



  // 可编辑单元格组件





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
        <div style={{ marginBottom: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div>
              <Title level={4} style={{ margin: 0 }}>
                工序分类管理
                <Badge count={(() => {
                  // 直接计算可见字段数量，确保实时更新
                  const allFields = Object.keys(fieldConfig).filter(key => key !== 'action');
                  return allFields.filter(field => {
                    const fieldConfigItem = fieldConfig[field];
                    if (fieldConfigItem && fieldConfigItem.required) {
                      return true; // 必填字段始终可见
                    }
                    return columnConfig[field] !== false; // 根据当前配置判断可见性
                  }).length;
                })()} style={{ marginLeft: 8, backgroundColor: '#52c41a' }} />
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
          <Row gutter={16} style={{ marginBottom: 0 }}>
            <Col span={8}>
              <Input
                  ref={searchInputRef}
                placeholder="搜索工序分类名称、类型"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onPressEnter={handleSearch}
                prefix={<SearchOutlined />}
                  allowClear
              />
            </Col>
            <Col span={16}>
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
              <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
                刷新
              </Button>
            </Space>
          </Col>
        </Row>
        </div>

          <Table
            components={{
            header: {
              cell: SimpleColumnHeader,
              },
            }}
            dataSource={data}
          columns={configLoaded ? generateColumns() : []}
          pagination={pagination}
          loading={loading || !configLoaded}
          onChange={handleTableChange}
          scroll={{ x: 1200, y: 600 }}
          size="small"
          />

        {/* 列设置抽屉 */}
        <Drawer
          title={
            <Space>
              <SettingOutlined />
              <span>列显示设置</span>
            </Space>
          }
          placement="right"
          width="30%"
          open={columnSettingVisible}
          onClose={() => setColumnSettingVisible(false)}
        >
          <div>
            {renderColumnSettings()}
            
            <Divider />
            
            <Space style={{ width: '100%', justifyContent: 'center' }}>
              <Button 
                type="primary" 
                onClick={() => {
                  console.log('保存前 - 当前配置:', columnConfig);
                  console.log('保存前 - 当前顺序:', columnOrder);
                  // 传递完整的配置信息，包括顺序
                  saveColumnConfig({
                    ...columnConfig,
                    _columnOrder: columnOrder // 添加顺序信息
                  });
                }}
              >
                保存设置
              </Button>
              <Button 
                onClick={resetColumnConfig}
              >
                重置默认
              </Button>
            </Space>
          </div>
        </Drawer>

        {/* 编辑弹窗 */}
        <Modal
          title={currentRecord?.id ? '编辑工序分类' : '新增工序分类'}
          open={editModalVisible}
          onCancel={cancel}
          onOk={saveModal}
          okText="保存"
          cancelText="取消"
          width={800}
          confirmLoading={loading}
        >
          <Form form={editForm} layout="vertical">
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              {Object.entries(fieldGroups).map(([groupKey, group]) => {
                // 过滤出当前分组中可见且可编辑的字段
                const visibleFields = group.fields.filter(field => 
                  getVisibleFormFields().includes(field) && 
                  !['created_at', 'updated_at', 'created_by_username', 'updated_by_username'].includes(field)
                );
                
                // 如果分组中没有可见字段，不显示该分组
                if (visibleFields.length === 0) return null;
                
                return (
                  <TabPane 
                    tab={
                      <Space>
                        <span>{group.icon}</span>
                        <span>{group.title}</span>
                        <Badge count={visibleFields.filter(field => {
                          // 直接计算可见性，确保实时更新
                          const fieldConfigItem = fieldConfig[field];
                          if (fieldConfigItem && fieldConfigItem.required) {
                            return true; // 必填字段始终可见
                          }
                          return columnConfig[field] !== false; // 根据当前配置判断可见性
                        }).length} size="small" style={{ backgroundColor: '#52c41a' }} />
                      </Space>
                    } 
                    key={groupKey}
                  >
                <Row gutter={16}>
                      {visibleFields.map(field => {
                        const config = fieldConfig[field];
                        if (!config) return null;
                        
                        let formItem;
                        if (['is_plate_making', 'is_outsourcing', 'is_knife_plate'].includes(field)) {
                          formItem = <Checkbox />;
                        } else if (field === 'is_enabled') {
                          formItem = <Switch />;
                        } else if (field === 'sort_order') {
                          formItem = <InputNumber style={{ width: '100%' }} min={0} />;
                        } else if (field === 'category_type') {
                          formItem = (
                      <Select placeholder="请选择类型" allowClear>
                        {categoryTypeOptions.map(option => (
                          <Option key={option.value} value={option.value}>
                            {option.label}
                          </Option>
                        ))}
                      </Select>
                          );
                        } else if (field === 'data_collection_mode') {
                          formItem = (
                      <Select placeholder="请选择数据自动采集模式" allowClear>
                        {dataCollectionModeOptions.map(option => (
                          <Option key={option.value} value={option.value}>
                            {option.label}
                          </Option>
                        ))}
                      </Select>
                          );
                        } else if (field === 'show_data_collection_interface') {
                          formItem = <Checkbox />;
                        } else if (field === 'description') {
                          formItem = <TextArea rows={3} />;
                        } else if (field.startsWith('number_')) {
                          formItem = <InputNumber style={{ width: '100%' }} precision={2} />;
                        } else {
                          formItem = <Input />;
                        }
                        
                        return (
                          <Col span={12} key={field}>
                            <Form.Item 
                              label={config.title} 
                              name={field}
                              rules={[
                                {
                                  required: config.required,
                                  message: `请输入${config.title}!`,
                                },
                              ]}
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

        {/* 详情弹窗 */}
        <Modal
          title="工序分类详情"
          open={detailModalVisible}
          onCancel={() => setDetailModalVisible(false)}
          footer={[
            <Button key="close" onClick={() => setDetailModalVisible(false)}>
              关闭
            </Button>
          ]}
          width={800}
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
                        <Badge count={visibleFields.filter(field => {
                          // 直接计算可见性，确保实时更新
                          const fieldConfigItem = fieldConfig[field];
                          if (fieldConfigItem && fieldConfigItem.required) {
                            return true; // 必填字段始终可见
                          }
                          return columnConfig[field] !== false; // 根据当前配置判断可见性
                        }).length} size="small" style={{ backgroundColor: '#52c41a' }} />
                      </Space>
                    } 
                    key={groupKey}
                  >
                <Row gutter={16}>
                      {visibleFields.map(field => {
                        const config = fieldConfig[field];
                        if (!config) return null;
                        
                        let formItem;
                        if (['is_plate_making', 'is_outsourcing', 'is_knife_plate'].includes(field)) {
                          formItem = <Checkbox disabled />;
                        } else if (field === 'is_enabled') {
                          formItem = <Switch disabled />;
                        } else if (field === 'show_data_collection_interface') {
                          formItem = <Checkbox disabled />;
                        } else if (field === 'category_type') {
                          formItem = (
                            <Select disabled>
                              {categoryTypeOptions.map(option => (
                                <Option key={option.value} value={option.value}>
                                  {option.label}
                                </Option>
                              ))}
                            </Select>
                          );
                        } else if (field === 'data_collection_mode') {
                          formItem = (
                            <Select disabled>
                              {dataCollectionModeOptions.map(option => (
                                <Option key={option.value} value={option.value}>
                                  {option.label}
                                </Option>
                              ))}
                            </Select>
                          );
                        } else if (['created_at', 'updated_at'].includes(field)) {
                          formItem = <Input disabled />;
                        } else if (field.startsWith('number_')) {
                          formItem = <InputNumber style={{ width: '100%' }} disabled />;
                        } else {
                          formItem = <Input disabled />;
                        }
                        
                        return (
                          <Col span={12} key={field}>
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

      </Card>
    </div>
  );
};

export default ProcessCategoryManagement; 