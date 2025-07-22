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
  Checkbox,
  Modal,
  Tabs,
  Drawer,
  Badge,
  Divider
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
  BankOutlined,
  SettingOutlined,
  EyeOutlined,
  MenuOutlined,
  ClearOutlined
} from '@ant-design/icons';
import { supplierCategoryApi } from '../../../api/base-archive/base-category/supplierCategory';
import { columnConfigurationApi } from '../../../api/system/columnConfiguration';
import { authApi } from '../../../api/auth';
import { useAutoScroll } from '../../../hooks/useAutoScroll';

const { Title } = Typography;
const { TabPane } = Tabs;
const { Text } = Typography;

// 简化的列头组件，避免React警告
const SimpleColumnHeader = ({ children, moveKey, onMove, ...restProps }) => {
  const { onMove: _, ...props } = restProps;
  return <th {...props}>{children}</th>;
};

const SupplierCategoryManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingKey, setEditingKey] = useState('');
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });
  
  // 新增状态变量
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [columnConfig, setColumnConfig] = useState({});
  const [columnOrder, setColumnOrder] = useState([]);
  const [columnSettingOrder, setColumnSettingOrder] = useState([]);
  const [columnSettingVisible, setColumnSettingVisible] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [configLoaded, setConfigLoaded] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');
  const [forceUpdate, setForceUpdate] = useState(0);
  
  const [form] = Form.useForm();
  const [detailForm] = Form.useForm();
  const searchInputRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const { setDropEffect } = useAutoScroll(scrollContainerRef);

  // 字段配置
  const fieldConfig = {
    category_name: { title: '供应商分类名称', width: 150, required: true },
    category_code: { title: '分类编码', width: 120 },
    description: { title: '描述', width: 200 },
    is_plate_making: { title: '制版', width: 80 },
    is_outsourcing: { title: '外发', width: 80 },
    is_knife_plate: { title: '刀板', width: 80 },
    sort_order: { title: '显示排序', width: 100 },
    is_enabled: { title: '是否启用', width: 100 },
    created_by_name: { title: '创建人', width: 100 },
    created_at: { title: '创建时间', width: 150 },
    updated_by_name: { title: '修改人', width: 100 },
    updated_at: { title: '修改时间', width: 150 },
    action: { title: '操作', width: 120, fixed: 'right' }
  };

  // 字段分组
  const fieldGroups = {
    basic: {
      title: '基本信息',
      icon: '📋',
      fields: ['category_name', 'category_code', 'description', 'is_plate_making', 'is_outsourcing', 'is_knife_plate', 'sort_order', 'is_enabled']
    },
    audit: {
      title: '审计信息',
      icon: '📝',
      fields: ['created_by_name', 'created_at', 'updated_by_name', 'updated_at']
    }
  };

  // 判断是否在编辑状态
  const isEditing = (record) => record.key === editingKey;

  // 获取表单中应该显示的字段
  const getVisibleFormFields = () => {
    const allPossibleFields = Object.keys(fieldConfig);
    let visible = [];

    // 确定默认可见性基于columnConfig是否为空
    const isColumnConfigEmpty = Object.keys(columnConfig).length === 0;

    allPossibleFields.forEach(key => {
      // 如果columnConfig为空，所有字段默认可见
      // 如果columnConfig不为空，字段只有在columnConfig[key]为true时才可见
      if (isColumnConfigEmpty || columnConfig[key] === true) {
        visible.push(key);
      }
    });

    // 确保必填字段始终可见
    Object.keys(fieldConfig).forEach(key => {
      const config = fieldConfig[key];
      if (config && config.required && !visible.includes(key)) {
        visible.push(key);
      }
    });

    // 过滤掉'action'，因为它不是表单字段
    visible = visible.filter(field => field !== 'action');

    // 根据columnOrder排序（如果可用），否则使用默认顺序
    let finalOrder = [];
    if (columnOrder.length > 0) {
      finalOrder = columnOrder.filter(field => visible.includes(field));
    } else {
      const defaultColumnOrder = [
        'category_name', 'category_code', 'description', 'is_plate_making', 'is_outsourcing', 'is_knife_plate',
        'sort_order', 'is_enabled', 'created_by_name', 'created_at', 'updated_by_name', 'updated_at'
      ];
      finalOrder = defaultColumnOrder.filter(field => visible.includes(field));
    }

    return finalOrder;
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

  // 获取可见列
  const getVisibleColumns = () => {
    const defaultVisible = ['category_name', 'category_code', 'action'];
    const defaultColumnOrder = [
      'category_name', 'category_code', 'description', 'is_plate_making', 'is_outsourcing', 'is_knife_plate',
      'sort_order', 'is_enabled', 'created_by_name', 'created_at', 'updated_by_name', 'updated_at', 'action'
    ];
    
    const allPossibleColumns = Object.keys(fieldConfig);
    let visible;
    
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

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await supplierCategoryApi.getSupplierCategories({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      // 正确处理后端响应格式
      if (response.data.success) {
        const { supplier_categories, total, current_page } = response.data.data;
        
        // 为每行数据添加key
        const dataWithKeys = supplier_categories.map((item, index) => ({
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
      const configResponse = await columnConfigurationApi.getColumnConfig('supplierCategory', 'column_config');
      if (configResponse.data.success && configResponse.data.data) {
        setColumnConfig(configResponse.data.data.config_data);
      }
      
      // 获取列顺序配置
      const orderResponse = await columnConfigurationApi.getColumnConfig('supplierCategory', 'column_order');
      if (orderResponse.data.success && orderResponse.data.data) {
        const order = orderResponse.data.data.config_data;
        setColumnOrder(order);
        setColumnSettingOrder(order);
      }
    } catch (error) {
      console.error('加载列配置失败:', error);
    }
  };

  // 移动列功能
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

  // 初始加载
  useEffect(() => {
    const initialize = async () => {
      await loadData();
      await loadColumnConfig();
      await checkUserPermission();
      setConfigLoaded(true);
    };
    
    initialize();
  }, []);

  // 监听列配置变化，自动切换分页和更新数字
  useEffect(() => {
    const newActiveTab = getDefaultActiveTab();
    setActiveTab(newActiveTab);
  }, [columnConfig, columnSettingOrder]);

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '' });
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize
    });
  };

  // 开始编辑
  const edit = (record) => {
    setCurrentRecord(record);
    form.setFieldsValue({
      category_name: '',
      category_code: '',
      description: '',
      is_plate_making: false,
      is_outsourcing: false,
      is_knife_plate: false,
      sort_order: 0,
      is_enabled: true,
      ...record,
    });
    setEditModalVisible(true);
  };

  // 取消编辑
  const cancel = () => {
    setEditModalVisible(false);
    form.resetFields();
  };

  // 保存编辑
  const saveModal = async () => {
    try {
      const values = await form.validateFields();

        let response;
      if (currentRecord && currentRecord.id) {
          // 更新现有记录
        response = await supplierCategoryApi.updateSupplierCategory(currentRecord.id, values);
        message.success('更新成功');
        } else {
          // 创建新记录
        response = await supplierCategoryApi.createSupplierCategory(values);
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

  // 查看详情
  const handleViewDetail = (record) => {
    setCurrentRecord(record);
    detailForm.setFieldsValue(record);
    setDetailModalVisible(true);
  };

  // 删除记录
  const handleDelete = async (key) => {
    try {
      const record = data.find(item => item.key === key);
      
      if (record.id && !record.id.startsWith('temp_')) {
        // 删除服务器记录
        const response = await supplierCategoryApi.deleteSupplierCategory(record.id);
        if (response.data.success) {
          message.success('删除成功');
        }
      }
      
      // 删除本地记录
      const newData = data.filter(item => item.key !== key);
      setData(newData);
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.error || error.message));
    }
  };

  // 添加新行
  const handleAdd = () => {
    setCurrentRecord(null);
    form.setFieldsValue({
      category_name: '',
      category_code: '',
      description: '',
      is_plate_making: false,
      is_outsourcing: false,
      is_knife_plate: false,
      sort_order: 0,
      is_enabled: true,
    });
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

      await columnConfigurationApi.saveColumnConfig('supplierCategory', 'column_config', completeConfig);
      await columnConfigurationApi.saveColumnConfig('supplierCategory', 'column_order', newColumnOrder);
      
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
      if (!isAdmin) {
        message.error('只有管理员可以重置列配置');
        return;
      }

      await columnConfigurationApi.deleteColumnConfig('supplierCategory', 'column_config');
      await columnConfigurationApi.deleteColumnConfig('supplierCategory', 'column_order');
      
      setColumnConfig({});
      setColumnOrder([]);
      setColumnSettingOrder([]);
      setColumnSettingVisible(false);
      message.success('列配置已重置为默认');
    } catch (error) {
      message.error('重置列配置失败: ' + (error.response?.data?.error || error.message));
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

      // 处理特殊字段的渲染
      let render;
      
      if (['is_plate_making', 'is_outsourcing', 'is_knife_plate'].includes(key)) {
        render = (value) => <Checkbox checked={value} disabled />;
      } else if (key === 'is_enabled') {
        render = (value) => <Switch checked={value} disabled />;
      } else if (['created_at', 'updated_at'].includes(key)) {
        render = (value) => value ? new Date(value).toLocaleString() : '';
      } else if (key === 'description') {
        render = (value) => (
          <Tooltip placement="topLeft" title={value}>
            {value || '-'}
          </Tooltip>
        );
      } else if (key === 'category_name') {
        render = (value) => <span style={{ fontWeight: 500 }}>{value || '-'}</span>;
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

  // 渲染列设置界面
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
        'category_name', 'category_code', 'description', 'is_plate_making', 'is_outsourcing', 'is_knife_plate', 'sort_order', 'is_enabled',
        // 审计信息
        'created_by_name', 'created_at', 'updated_by_name', 'updated_at'
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
                  e.dataTransfer.setData('text/plain', field);
                  e.dataTransfer.effectAllowed = 'move';
                }}
                onDragEnd={(e) => {
                  e.currentTarget.style.backgroundColor = isVisible ? '#fff' : '#f5f5f5';
                }}
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
                    
                    if (targetIndex !== -1) {
                      moveColumn(draggedField, targetIndex);
                    }
                  }
                }}
              >
                {/* 拖拽区域指示器 */}
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
                供应商分类管理
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
                })()} style={{ marginLeft: 8 }} />
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
            <Col span={8}>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索分类名称、编码或描述"
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
                <Button icon={<ReloadOutlined />} onClick={() => loadData()}>
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
            bordered
            dataSource={data}
          columns={configLoaded ? generateColumns() : []}
            pagination={pagination}
          loading={loading || !configLoaded}
            onChange={handleTableChange}
          scroll={{ x: 1200, y: 600 }}
          size="middle"
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
                onClick={() => saveColumnConfig(columnConfig)}
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
      </Card>

        {/* 编辑弹窗 */}
        <Modal
          title={currentRecord?.id ? '编辑供应商分类' : '新增供应商分类'}
          open={editModalVisible}
          onCancel={cancel}
          onOk={saveModal}
          okText="保存"
          cancelText="取消"
          width={800}
          confirmLoading={loading}
        >
          <Form form={form} layout="vertical">
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              {Object.entries(fieldGroups).map(([groupKey, group]) => {
                // 过滤出当前分组中可见且可编辑的字段
                const visibleFields = group.fields.filter(field => 
                  getVisibleFormFields().includes(field) && 
                  !['created_at', 'updated_at', 'created_by_name', 'updated_by_name'].includes(field)
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
          title="供应商分类详情"
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
                        } else if (['created_at', 'updated_at'].includes(field)) {
                          formItem = <Input disabled />;
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
    </div>
  );
};

export default SupplierCategoryManagement; 