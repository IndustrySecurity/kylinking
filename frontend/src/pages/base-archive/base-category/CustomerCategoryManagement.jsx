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
  Drawer,
  Badge,
  DatePicker,
  Select
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  UserOutlined,
  SettingOutlined,
  EyeOutlined,
  ClearOutlined,
  MenuOutlined
} from '@ant-design/icons';
import { customerCategoryApi } from '../../../api/base-archive/base-category/customerCategory';
import { columnConfigurationApi } from '../../../api/system/columnConfiguration';
import dynamicFieldsApi from '../../../api/system/dynamicFields';
import { authApi } from '../../../api/auth';
import FieldManager from '../../../components/common/FieldManager';
import DynamicForm from '../../../components/common/DynamicForm';
import PageFieldManager from '../../../components/common/PageFieldManager';
import PageDynamicForm from '../../../components/common/PageDynamicForm';
import ColumnSettings from '../../../components/common/ColumnSettings';
import DynamicFormModal from '../../../components/common/DynamicFormModal';


const { Title, Text } = Typography;

// 简化的列头组件
const SimpleColumnHeader = ({ children, moveKey, onMove, ...restProps }) => (
  <th {...restProps} style={{ ...restProps.style, userSelect: 'none' }}>
    {children}
  </th>
);

const CustomerCategoryManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false); // 添加初始化状态
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });
  
  const [form] = Form.useForm();
  const [detailForm] = Form.useForm();
  const searchInputRef = useRef(null);

  // 弹窗和抽屉状态
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);

  // 列配置状态
  const [columnConfig, setColumnConfig] = useState({});
  const [columnOrder, setColumnOrder] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [columnSettingOrder, setColumnSettingOrder] = useState([]);
  const [columnSettingVisible, setColumnSettingVisible] = useState(false);

  // 动态字段状态
  const [dynamicFields, setDynamicFields] = useState([]);
  const [dynamicFieldValues, setDynamicFieldValues] = useState({});
  const [fieldManagerVisible, setFieldManagerVisible] = useState(false);
  const [tableKey, setTableKey] = useState(0); // 用于强制表格重新渲染
  


  // 字段分组定义
  const [fieldGroups, setFieldGroups] = useState({
    basic: {
      title: '基本信息',
      icon: '👥',
      fields: ['category_name', 'category_code', 'description', 'sort_order', 'is_enabled']
    },
    audit: {
      title: '审计信息',
      icon: '📝',
      fields: ['created_by_name', 'created_at', 'updated_by_name', 'updated_at']
    }
    // 动态字段分组将在运行时动态添加
  });

  // 字段配置
  const [fieldConfig, setFieldConfig] = useState({
    category_name: { title: '分类名称', width: 150, required: true, display_order: 1 },
    is_enabled: { title: '是否启用', width: 100, display_order: 2 },
    category_code: { title: '分类编码', width: 120, display_order: 3 },
    description: { title: '描述', width: 200, display_order: 4 },
    sort_order: { title: '显示排序', width: 100, display_order: 5 },
    created_by_name: { title: '创建人', width: 100, display_order: 6 },
    created_at: { title: '创建时间', width: 150, display_order: 7 },
    updated_by_name: { title: '修改人', width: 100, display_order: 8 },
    updated_at: { title: '修改时间', width: 150, display_order: 9 },
    action: { title: '操作', width: 120, fixed: 'right', display_order: 999 }
  });



  // 获取表单中应该显示的字段
  // 全局防御 .filter/.map/.forEach 报错
  // 1. getVisibleFormFields
  const getVisibleFormFields = () => {
    if (!fieldConfig) return [];
    
    // 获取基础字段
    const baseFields = Object.keys(fieldConfig || {}).filter(key => key !== 'action');
    
    // 获取动态字段
    const dynamicFieldNames = Array.isArray(dynamicFields) ? dynamicFields.map(field => field.field_name) : [];
    
    // 合并所有字段
    const allFields = [...baseFields, ...dynamicFieldNames];
    
    // 如果列配置为空，显示所有字段
    if (Object.keys(columnConfig || {}).length === 0) {
      return allFields;
    }
    
    // 根据列配置过滤字段，只显示被勾选的字段
    return allFields.filter(key => {
      // 动态字段始终显示（除非明确隐藏）
      if (dynamicFieldNames.includes(key)) {
        return !(key in (columnConfig || {})) || columnConfig[key] === true;
      }
      
      // 基础字段的处理
      if (key === 'action') return false;
      
      // 必填字段始终显示，不能被隐藏
      const config = fieldConfig[key];
      if (config && config.required) {
        return true;
      }
      
      // 如果配置中没有明确设置为false，则显示
      return !(key in (columnConfig || {})) || columnConfig[key] === true;
    });
  };





  // 获取显示的列
  const getVisibleColumns = () => {
    const defaultVisible = ['category_name', 'category_code', 'action'];
    const defaultColumnOrder = [
      'category_name', 'category_code', 'description', 'sort_order', 'is_enabled',
      'created_by_name', 'created_at', 'updated_by_name', 'updated_at', 'action'
    ].sort((a, b) => {
      const configA = fieldConfig[a];
      const configB = fieldConfig[b];
      const orderA = configA?.display_order || 0;
      const orderB = configB?.display_order || 0;
      return orderA - orderB;
    });
    
    const baseFields = Object.keys(fieldConfig || {});
    const dynamicFieldNames = Array.isArray(dynamicFields) ? dynamicFields.map(field => field.field_name) : [];
    const allPossibleColumns = [...baseFields];
    

    
    let visible;
    
    if (Object.keys(columnConfig || {}).length === 0) {
      // 如果配置为空，显示所有字段（除了action）
      visible = allPossibleColumns.filter(key => key !== 'action');
    } else {
      // 根据配置过滤可见字段
      visible = allPossibleColumns.filter(key => !(key in (columnConfig || {})) || columnConfig[key] === true);
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
    
    // 强制显示必填的动态字段（只处理在fieldConfig中存在的字段）
    if (Array.isArray(dynamicFields)) {
      dynamicFields.forEach(field => {
        if (field.is_required && fieldConfig[field.field_name] && !visible.includes(field.field_name)) {
          visible.push(field.field_name);
        }
      });
    }
    
    let finalOrder = [];
    
    if (Array.isArray(columnOrder) && columnOrder.length > 0) {
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
      
      // 添加动态字段到默认顺序（只处理在fieldConfig中存在的字段）
      dynamicFieldNames.forEach(key => {
        if (visible.includes(key) && fieldConfig[key] && !finalOrder.includes(key)) {
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
    
    return finalOrder.filter(key => (fieldConfig || {})[key]);
  };





  // 加载数据
  const loadData = async (params = {}) => {
    // 只有在非初始化状态下才设置loading
    if (initialized) {
    setLoading(true);
    }
    
    try {
      const response = await customerCategoryApi.getCustomerCategories(params);
      if (response.data && response.data.success) {
        // 确保数据是数组格式
        let data = [];

        // 处理不同的响应格式
        if (response.data.data) {
          if (Array.isArray(response.data.data)) {
            data = response.data.data;
          } else if (response.data.data.customer_categories && Array.isArray(response.data.data.customer_categories)) {
            data = response.data.data.customer_categories;
          } else {
            console.warn('响应数据格式异常:', response.data.data);
            data = [];
          }
        }
        
        // 确保每个记录都有key
        data = data.map((item, index) => ({
          ...item,
          key: item.id || `temp_${index}`
        }));
        
        // 如果有计算字段，计算字段值
        if (Array.isArray(dynamicFields) && dynamicFields.length > 0) {
          const calculatedFields = dynamicFields.filter(field => field.is_calculated);
          if (calculatedFields.length > 0) {
            // 这里可以调用后端API来计算字段值，或者在前端计算
            // 为了简单起见，我们先在前端计算
            for (const record of data) {
              for (const field of calculatedFields) {
                if (field.calculation_formula) {
                  try {
                    // 简单的公式计算（实际项目中应该在后端计算）
                    const result = calculateFieldValue(field.calculation_formula, record);
                    record[field.field_name] = result;
                  } catch (error) {
                    console.error(`计算字段 ${field.field_name} 时出错:`, error);
                    record[field.field_name] = null;
                  }
                }
              }
            }
          }
        }
        
        setData(data);
        setPagination(prev => ({
          ...prev,
          total: response.data.total || data.length,
          current: params.page || 1
        }));
      } else {
        console.warn('API响应格式异常:', response);
        setData([]);
      }
    } catch (error) {
      console.error('加载数据失败:', error);
      message.error('加载数据失败');
      setData([]); // 确保出错时设置为空数组
    } finally {
      if (initialized) {
      setLoading(false);
    }
    }
  };

  // 简单的字段值计算函数（实际项目中应该在后端实现）
  const calculateFieldValue = (formula, record) => {
    try {
      // 创建安全的计算环境，避免使用 JavaScript 关键字
      const safeGlobals = {
        abs: Math.abs,
        round: Math.round,
        min: Math.min,
        max: Math.max,
        pow: Math.pow,
        sqrt: Math.sqrt,
        if_condition: (condition, trueVal, falseVal) => condition ? trueVal : falseVal,
        concat: (...args) => args.join(''),
        format_number: (num, precision = 2) => Number(num).toFixed(precision)
      };
      
      // 将记录数据作为局部变量
      const localVars = { ...record };
      
      // 预处理公式，将 if 替换为 if_condition
      let processedFormula = formula.replace(/\bif\s*\(/g, 'if_condition(');
      
      // 使用 Function 构造函数，但将变量作为参数传递
      const paramNames = [
        ...Object.keys(safeGlobals),
        ...Object.keys(localVars)
      ];
      
      const paramValues = [
        ...Object.values(safeGlobals),
        ...Object.values(localVars)
      ];
      
      // 创建函数体，确保所有变量都在作用域内
      const functionBody = `return ${processedFormula};`;
      
      // 创建并执行函数
      const calculateFunction = new Function(...paramNames, functionBody);
      const result = calculateFunction(...paramValues);
      
      return result;
    } catch (error) {
      console.error('公式计算错误:', error);
      return null;
    }
  };
  

  const loadColumnConfig = async () => {
    try {
      // 获取列显示配置
      const configResponse = await columnConfigurationApi.getColumnConfig('customerCategory', 'column_config');
      if (configResponse.data.success && configResponse.data.data) {
        const configData = configResponse.data.data.config_data;
        setColumnConfig(configData);
      }
      
      // 获取列顺序配置
      const orderResponse = await columnConfigurationApi.getColumnConfig('customerCategory', 'column_order');
      if (orderResponse.data.success && orderResponse.data.data) {
        const order = orderResponse.data.data.config_data;
        setColumnOrder(order);
        setColumnSettingOrder(order);
      }
    } catch (error) {
      console.error('加载列配置失败:', error);
      // 列配置加载失败不影响基础功能
    }
  };

  // 加载动态字段
  const loadDynamicFields = async () => {
    try {
      const response = await dynamicFieldsApi.getModelFields('customer_category');
      if (response.data && response.data.success) {
        const fields = response.data.data || [];
        setDynamicFields(fields);
        
        // 更新字段配置，添加动态字段
        const newFieldConfig = { ...fieldConfig };
        
        // 清理已不存在的动态字段
        Object.keys(newFieldConfig).forEach(key => {
          if (key !== 'action' && !['category_name', 'category_code', 'description', 'sort_order', 'is_enabled', 'created_by_name', 'created_at', 'updated_by_name', 'updated_at'].includes(key)) {
            // 检查这个字段是否还在动态字段列表中
            const fieldExists = fields.some(field => field.field_name === key);
            if (!fieldExists) {
              delete newFieldConfig[key];
            }
          }
        });
        
        // 添加新的动态字段
        fields.forEach(field => {
          if (!newFieldConfig[field.field_name]) {
            newFieldConfig[field.field_name] = {
              title: field.field_label,
              width: 150,
              display_order: field.display_order || 999,
              required: field.is_required || false,
              readonly: field.is_readonly || false,
              visible: field.is_visible !== false
            };
          }
        });
        
        setFieldConfig(newFieldConfig);
      }
    } catch (error) {
      console.error('加载动态字段失败:', error);
      // 动态字段加载失败不影响基础功能
    }
  };
    
  // 加载记录的动态字段值
  const loadRecordDynamicValues = async (recordId) => {
    try {
      const response = await dynamicFieldsApi.getRecordDynamicValues('customer_category', recordId);
      if (response.data && response.data.success) {
        return response.data.data || {};
      }
      return {};
    } catch (error) {
      return {};
    }
  };

  // 移动列功能 - 现在由通用组件处理
  const handleColumnOrderChange = (newOrder) => {
    setColumnSettingOrder(newOrder);
  };

  // 检查用户权限
  const checkUserPermission = async () => {
    try {
      // 使用封装的权限检查API
      const adminStatus = await authApi.checkAdminStatus();
      setIsAdmin(adminStatus.isAdmin);
    } catch (error) {
      setIsAdmin(false);
    }
  };

  // 初始加载
  useEffect(() => {
    const initialize = async () => {
      setLoading(true); // 设置加载状态
      try {
        // 先加载动态字段，再加载数据
        await loadDynamicFields();
        await Promise.all([
          loadData(),
          loadColumnConfig(),
          checkUserPermission()
        ]);
        setInitialized(true); // 标记初始化完成
      } catch (error) {
        // 初始化失败不影响基础功能
      } finally {
        setLoading(false); // 清除加载状态
      }
    };
    
    initialize();
  }, []);



  // 动态更新字段分组中的动态字段
  useEffect(() => {
    if (Array.isArray(dynamicFields)) {
      setFieldGroups(prev => {
        const newGroups = { ...prev };
        // 1. 清除旧的动态字段分组（只保留内置分组）
        Object.keys(newGroups).forEach(key => {
          if (key.startsWith('dynamic_')) {
            delete newGroups[key];
          }
        });
        
        // 2. 创建已有分组的title映射
        const titleToKeyMap = {};
        Object.entries(newGroups).forEach(([key, group]) => {
          titleToKeyMap[group.title] = key;
        });
        
        // 3. 记录哪些自定义字段未能合并到已有分组
        const orphanCustomTabs = {};
        
        // 4. 合并自定义字段到已有分组
        dynamicFields.forEach(field => {
          const pageName = (field.page_name || 'default').trim() || 'default';
          // 通过title匹配已有分组
          const matchedKey = titleToKeyMap[pageName];
          if (matchedKey) {
            if (!newGroups[matchedKey].fields.includes(field.field_name)) {
              newGroups[matchedKey].fields.push(field.field_name);
            }
          } else {
            // 否则记录为孤立自定义tab
            if (!orphanCustomTabs[pageName]) {
              orphanCustomTabs[pageName] = [];
            }
            orphanCustomTabs[pageName].push(field.field_name);
          }
        });
        
        // 5. 为没有分组的自定义字段新建tab
        Object.entries(orphanCustomTabs).forEach(([pageName, fields]) => {
          const groupKey = `dynamic_${pageName}`;
          newGroups[groupKey] = {
            title: pageName,
            icon: '🔧',
            fields: fields
          };
        });
        
        return newGroups;
      });
      
      // 6. 自动将新字段添加到列设置中
      const dynamicFieldNames = dynamicFields.map(field => field.field_name);
      setColumnSettingOrder(prevOrder => {
        const newOrder = Array.isArray(prevOrder) ? [...prevOrder] : [];
        
        // 添加新的动态字段到列设置中
        dynamicFieldNames.forEach(fieldName => {
          if (!newOrder.includes(fieldName)) {
            newOrder.push(fieldName);
          }
        });
        
        return newOrder;
      });
      
      // 7. 为动态字段添加配置
      const newFieldConfig = { ...fieldConfig };
      
      // 先清除所有动态字段的配置（通过检查字段是否在dynamicFields中存在）
      Object.keys(newFieldConfig).forEach(key => {
        const isDynamicField = dynamicFields.some(field => field.field_name === key);
        if (isDynamicField) {
          delete newFieldConfig[key];
        }
      });
      
      // 重新添加当前存在的动态字段配置
      dynamicFields.forEach(field => {
        newFieldConfig[field.field_name] = {
          title: field.field_label,
          width: 120,
          required: field.is_required,
          readonly: field.is_readonly,
          type: field.field_type,
          options: field.field_options,
          help_text: field.help_text,
          default_value: field.default_value, // 添加默认值
          display_order: field.display_order || 4.5 // 添加显示顺序，默认在描述(4)和显示排序(5)之间
        };
      });
      setFieldConfig(newFieldConfig);
    }
  }, [dynamicFields]);

  // 当动态字段加载完成后，重新加载数据以包含动态字段值
  useEffect(() => {
    if (Array.isArray(dynamicFields) && dynamicFields.length > 0 && initialized) {
      loadData();
    }
  }, [dynamicFields, initialized]);

  // 当动态字段变化时，清理已删除字段的配置
  useEffect(() => {
    if (initialized && Array.isArray(dynamicFields)) {
      // 清理已删除字段的列配置（只清理动态字段，不清理基础字段）
      setColumnConfig(prevConfig => {
        const newConfig = { ...prevConfig };
        Object.keys(newConfig).forEach(key => {
          // 检查是否为动态字段且已不存在
          const isDynamicField = dynamicFields.some(field => field.field_name === key);
          if (isDynamicField && !fieldConfig[key]) {
            delete newConfig[key];
          }
        });
        return newConfig;
      });
      
      // 清理已删除字段的列顺序配置（只清理动态字段，不清理基础字段）
      setColumnOrder(prevOrder => {
        if (Array.isArray(prevOrder)) {
          return prevOrder.filter(key => {
            // 保留基础字段，只清理不存在的动态字段
            if (fieldConfig[key]) return true;
            const isDynamicField = dynamicFields.some(field => field.field_name === key);
            return isDynamicField;
          });
        }
        return prevOrder;
      });
      
      setColumnSettingOrder(prevOrder => {
        if (Array.isArray(prevOrder)) {
          return prevOrder.filter(key => {
            // 保留基础字段，只清理不存在的动态字段
            if (fieldConfig[key]) return true;
            const isDynamicField = dynamicFields.some(field => field.field_name === key);
            return isDynamicField;
          });
        }
        return prevOrder;
      });
    }
  }, [dynamicFields, fieldConfig, initialized]);



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

  // 查看详情
  const handleViewDetail = (record) => {
    setCurrentRecord(record);
    detailForm.setFieldsValue(record);
    setDetailModalVisible(true);
  };



  // 开始编辑 - 使用Modal
  const edit = async (record) => {
    setCurrentRecord(record);
    
    // 设置基础字段值
    const formValues = { ...record };
    
    // 加载动态字段值
    if (Array.isArray(dynamicFields) && dynamicFields.length > 0) {
      try {
        // 获取所有页面的动态字段值
        const pageNames = [...new Set(dynamicFields.map(field => {
          const pageName = field.page_name || 'default';
          return pageName.trim() || 'default';
        }))];
        
        for (const pageName of pageNames) {
          const response = await dynamicFieldsApi.getRecordPageValues('customer_category', pageName, record.id);
          if (response.data && response.data.success) {
            const pageValues = response.data.data || {};
            Object.assign(formValues, pageValues);
          }
        }
        
        // 为没有值的动态字段设置默认值
        dynamicFields.forEach(field => {
          if (!(field.field_name in formValues) && field.default_value) {
            // 根据字段类型转换默认值
            let convertedValue = field.default_value;
            if (field.field_type === 'number' || field.field_type === 'integer' || field.field_type === 'float') {
              convertedValue = parseFloat(field.default_value);
            } else if (field.field_type === 'checkbox' || field.field_type === 'boolean') {
              convertedValue = field.default_value === 'true' || field.default_value === true;
            }
            formValues[field.field_name] = convertedValue;
          }
        });
      } catch (error) {
        console.error('加载动态字段值失败:', error);
      }
    }
    
    form.setFieldsValue(formValues);
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
      
      // 分离基础字段和动态字段
      const basicFields = ['category_name', 'category_code', 'description', 'sort_order', 'is_enabled'];
      const basicValues = {};
      const dynamicValuesByPage = {};
      
      Object.keys(values).forEach(key => {
        if (basicFields.includes(key)) {
          basicValues[key] = values[key];
        } else {
          // 动态字段 - 按页面分组
          const dynamicField = Array.isArray(dynamicFields) ? dynamicFields.find(df => df.field_name === key) : null;
          if (dynamicField) {
            const pageName = (dynamicField.page_name || 'default').trim() || 'default';
            if (!dynamicValuesByPage[pageName]) {
              dynamicValuesByPage[pageName] = {};
            }
            dynamicValuesByPage[pageName][key] = values[key];
          }
        }
      });
      
      let response;
      if (currentRecord && currentRecord.id) {
        // 更新现有记录
        response = await customerCategoryApi.updateCustomerCategory(currentRecord.id, basicValues);
        
        // 保存动态字段值（按页面）
        for (const [pageName, pageValues] of Object.entries(dynamicValuesByPage)) {
          if (Object.keys(pageValues).length > 0) {
            await dynamicFieldsApi.saveRecordPageValues('customer_category', pageName, currentRecord.id, pageValues);
          }
        }
        
        
        message.success('更新成功');
      } else {
        // 创建新记录
        response = await customerCategoryApi.createCustomerCategory(basicValues);
        
        // 保存动态字段值（按页面）
        if (response.data.success) {
          const newRecordId = response.data.data.id;
          for (const [pageName, pageValues] of Object.entries(dynamicValuesByPage)) {
            if (Object.keys(pageValues).length > 0) {
              await dynamicFieldsApi.saveRecordPageValues('customer_category', pageName, newRecordId, pageValues);
            }
          }
        }
        
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
        // 删除所有页面的动态字段值
        try {
          const pageNames = [...new Set(dynamicFields.map(field => {
            const pageName = field.page_name || 'default';
            return pageName.trim() || 'default';
          }))].filter(page => page && page.trim());
          
          // 删除每个页面的动态字段值
          for (const pageName of pageNames) {
            await dynamicFieldsApi.deleteRecordPageValues('customer_category', pageName, record.id);
          }
        } catch (error) {
          // 动态字段值删除失败不影响主记录删除
          console.warn('删除动态字段值失败:', error);
        }
        
        // 删除服务器记录
        const response = await customerCategoryApi.deleteCustomerCategory(record.id);
        if (response.data.success) {
          message.success('删除成功');
        }
      }
      
      // 删除本地记录
      const newData = Array.isArray(data) ? data.filter(item => item.key !== key) : [];
      setData(newData);
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.error || error.message));
    }
  };

  // 添加新行
  const handleAdd = () => {
    setCurrentRecord(null);
    
    // 设置基础字段的默认值
    const defaultValues = {
      category_name: '',
      category_code: '',
      description: '',
      sort_order: 0,
      is_enabled: true,
    };
    
    // 为动态字段设置默认值
    if (Array.isArray(dynamicFields)) {
      dynamicFields.forEach(field => {
        if (field.default_value) {
          // 根据字段类型转换默认值
          let convertedValue = field.default_value;
          if (field.field_type === 'number' || field.field_type === 'integer' || field.field_type === 'float') {
            convertedValue = parseFloat(field.default_value);
          } else if (field.field_type === 'checkbox' || field.field_type === 'boolean') {
            convertedValue = field.default_value === 'true' || field.default_value === true;
          }
          defaultValues[field.field_name] = convertedValue;
        }
      });
    }
    
    form.setFieldsValue(defaultValues);
    setEditModalVisible(true);
  };

  // 保存列配置
  const saveColumnConfig = async (config) => {
    try {
      if (!isAdmin) {
        message.error('只有管理员可以保存列配置');
        return;
      }

      const baseFields = Object.keys(fieldConfig || {});
      const dynamicFieldNames = Array.isArray(dynamicFields) ? dynamicFields.map(field => field.field_name) : [];
      const allFields = [...baseFields, ...dynamicFieldNames];
      const completeConfig = {};
      
      // 处理基础字段
      baseFields.forEach(field => {
        const fieldConfigItem = fieldConfig[field];
        // 必填字段始终设置为可见
        if (fieldConfigItem && fieldConfigItem.required) {
          completeConfig[field] = true;
        } else {
          completeConfig[field] = field in config ? config[field] : true;
        }
      });
      
      // 处理动态字段
      dynamicFieldNames.forEach(field => {
        const dynamicField = dynamicFields.find(df => df.field_name === field);
        // 必填的动态字段始终设置为可见
        if (dynamicField && dynamicField.is_required) {
          completeConfig[field] = true;
        } else {
          completeConfig[field] = field in config ? config[field] : true;
        }
      });

      let newColumnOrder = [];
      
      if (Array.isArray(columnSettingOrder) && columnSettingOrder.length > 0) {
        columnSettingOrder.forEach(key => {
          if (completeConfig[key] === true) {
            newColumnOrder.push(key);
          }
        });
      } else if (Array.isArray(columnOrder) && columnOrder.length > 0) {
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

      await columnConfigurationApi.saveColumnConfig('customerCategory', 'column_config', completeConfig);
      await columnConfigurationApi.saveColumnConfig('customerCategory', 'column_order', newColumnOrder);
      
      setColumnConfig(completeConfig);
      setColumnOrder(newColumnOrder);
      setColumnSettingOrder(newColumnOrder);
      setColumnSettingVisible(false);
      message.success('列配置已保存');
      
      // 重新加载列配置以确保数据同步
      setTimeout(() => {
        loadColumnConfig();
      }, 100);
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
    // 如果还没有初始化完成，返回基础列配置
    if (!initialized) {
      return [
        {
          title: '分类名称',
          dataIndex: 'category_name',
          width: 150,
          render: (value) => <span style={{ fontWeight: 500 }}>{value || '-'}</span>,
        },
        {
          title: '分类编码',
          dataIndex: 'category_code',
          width: 120,
          render: (value) => value || '-',
        },
        {
          title: '操作',
          dataIndex: 'action',
          width: 120,
          fixed: 'right',
          render: () => null, // 初始化期间不显示操作按钮
        }
      ];
    }

    const visibleColumns = getVisibleColumns();
    
    // 确保 visibleColumns 是数组且不为空
    if (!Array.isArray(visibleColumns) || visibleColumns.length === 0) {
      console.warn('visibleColumns 不是数组或为空:', visibleColumns);
      return [
        {
          title: '分类名称',
          dataIndex: 'category_name',
          width: 150,
          render: (value) => <span style={{ fontWeight: 500 }}>{value || '-'}</span>,
        },
        {
          title: '操作',
          dataIndex: 'action',
          width: 120,
          fixed: 'right',
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
        }
      ];
    }
    
    const allColumns = visibleColumns.map(key => {
      // 基础字段
      const config = (fieldConfig || {})[key];
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
      // 其它基础字段渲染逻辑
      let render;
      if (key === 'is_enabled') {
        render = (value) => <Switch checked={value} disabled />;
      } else if (["created_at", "updated_at"].includes(key)) {
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
      return {
        title: config.title,
        dataIndex: key,
        width: config.width,
        render,
      };
    }).filter(Boolean);

    return allColumns;
  };





  // 列设置组件 - 现在使用通用组件
  const renderColumnSettings = () => {
    return (
      <ColumnSettings
        fieldConfig={fieldConfig}
        dynamicFields={dynamicFields}
        fieldGroups={fieldGroups}
        columnConfig={columnConfig}
        columnSettingOrder={columnSettingOrder}
        isAdmin={isAdmin}
        onConfigChange={setColumnConfig}
        onOrderChange={handleColumnOrderChange}
        onSave={saveColumnConfig}
        onReset={async () => {
          try {
            // 删除列配置和列顺序配置
            await columnConfigurationApi.deleteColumnConfig('customerCategory', 'column_config');
            await columnConfigurationApi.deleteColumnConfig('customerCategory', 'column_order');
            setColumnConfig({});
            setColumnSettingOrder([]);
            message.success('列配置已重置为默认值');
          } catch (error) {
            message.error('重置列配置失败');
          }
        }}
        title="列显示设置"
      />
    );
  };



  return (
    <div style={{ padding: '24px' }}>

      <Card>
        <div style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <Title level={4} style={{ margin: 0 }}>
                客户分类管理
                <Badge count={Array.isArray(getVisibleFormFields()) ? getVisibleFormFields().length : 0} style={{ marginLeft: 8 }} />
              </Title>
            </div>
            
            <Space direction="vertical" size="small">
              {isAdmin && initialized && (
                <>
                <Button 
                  icon={<SettingOutlined />} 
                  onClick={() => setColumnSettingVisible(true)}
                >
                  字段设置
                </Button>
                  <Button 
                    icon={<SettingOutlined />} 
                    onClick={() => setFieldManagerVisible(true)}
                  >
                    自定义字段
                  </Button>
                </>
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
                disabled={!initialized}
              />
            </Col>
            <Col span={16}>
              <Space>
                <Button 
                  type="primary" 
                  icon={<SearchOutlined />} 
                  onClick={handleSearch}
                  disabled={!initialized}
                >
                  搜索
                </Button>
                <Button 
                  icon={<ClearOutlined />} 
                  onClick={handleReset}
                  disabled={!initialized}
                >
                  重置
                </Button>
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />} 
                  onClick={handleAdd}
                  disabled={!initialized}
                >
                  新增
                </Button>
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={() => loadData()}
                  disabled={!initialized}
                >
                  刷新
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        <Table
          key={tableKey} // 强制表格重新渲染
          components={{
            header: {
              cell: SimpleColumnHeader,
            },
          }}
          bordered
          dataSource={Array.isArray(data) ? data : []}
          columns={generateColumns()}
          pagination={pagination}
          loading={loading || !initialized} // 在初始化期间也显示loading
          onChange={handleTableChange}
          scroll={{ x: 1200, y: 600 }}
          size="middle"
        />

        {/* 详情弹窗 */}
        <DynamicFormModal
          visible={detailModalVisible}
          title="客户分类详情"
          fieldConfig={fieldConfig}
          dynamicFields={dynamicFields}
          fieldGroups={fieldGroups}
          columnSettingOrder={columnSettingOrder}
          form={detailForm}
          onCancel={() => setDetailModalVisible(false)}
          onOk={() => setDetailModalVisible(false)}
          okText="关闭"
          cancelText="取消"
          width={800}
          layout="vertical"
        />

        {/* 编辑弹窗 */}
        <DynamicFormModal
          visible={editModalVisible}
          title={currentRecord?.id ? '编辑客户分类' : '新增客户分类'}
          fieldConfig={fieldConfig}
          dynamicFields={dynamicFields}
          fieldGroups={fieldGroups}
          columnSettingOrder={columnSettingOrder}
          form={form}
          loading={loading}
          onOk={saveModal}
          onCancel={cancel}
          okText="保存"
          cancelText="取消"
          width={800}
          layout="vertical"
        />



        {/* 列设置抽屉 - 只有管理员可见 */}
        {isAdmin && (
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
              {renderColumnSettings()}
          </Drawer>
        )}

        {/* 字段管理组件 */}
        <FieldManager
          modelName="customer_category"
          visible={fieldManagerVisible}
          onCancel={() => setFieldManagerVisible(false)}
          onSuccess={async () => {
            // 重置所有相关状态
                      setColumnConfig({});
                      setColumnOrder([]);
                      setColumnSettingOrder([]);
            
            // 重新加载所有数据
            await loadDynamicFields();
            await loadData();
            await loadColumnConfig();
            
            // 强制表格重新渲染
            setTableKey(prev => prev + 1);
          }}
          title="客户分类自定义字段管理"
          predefinedPages={Object.values(fieldGroups).filter(group => group.title === '基本信息').map(group => group.title)}
        />
      </Card>
    </div>
  );
};

export default CustomerCategoryManagement; 