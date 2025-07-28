import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Popconfirm,
  message,
  Tag,
  Drawer,
  Row,
  Col,
  Typography,
  Divider,
  Tabs,
  InputNumber,
  Tooltip
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined,
  ReloadOutlined,
  CheckOutlined,
  CloseOutlined,
  SettingOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import dayjs from 'dayjs';
import salesOrderService from '../../../api/business/sales/salesOrder';
import dynamicFieldsApi from '../../../api/system/dynamicFields';
import FieldManager from '../../../components/common/FieldManager';
import ColumnSettings from '../../../components/common/ColumnSettings';
import DynamicFormModal from '../../../components/common/DynamicFormModal';
import request from '../../../utils/request';
import { columnConfigurationApi } from '../../../api/system/columnConfiguration';
import { authApi } from '../../../api/auth';

const { Option } = Select;
const { TextArea } = Input;
const { Text, Title } = Typography;
const { TabPane } = Tabs;

// 样式组件
const PageContainer = styled.div`
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
`;

const StyledCard = styled(Card)`
  margin-bottom: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const SalesOrder = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  // 选项数据
  const [customerOptions, setCustomerOptions] = useState([]);
  const [productOptions, setProductOptions] = useState([]);
  const [materialOptions, setMaterialOptions] = useState([]);
  const [taxOptions, setTaxOptions] = useState([]);
  const [unitOptions, setUnitOptions] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [contactOptions, setContactOptions] = useState([]);

  // 子表数据
  const [orderDetails, setOrderDetails] = useState([]);
  const [otherFees, setOtherFees] = useState([]);
  const [materials, setMaterials] = useState([]);

  const [activeTab, setActiveTab] = useState('base');

  // 动态字段相关状态
  const [initialized, setInitialized] = useState(false);
  const [dynamicFields, setDynamicFields] = useState([]);
  const [dynamicFieldValues, setDynamicFieldValues] = useState({});
  const [fieldManagerVisible, setFieldManagerVisible] = useState(false);
  const [columnSettingVisible, setColumnSettingVisible] = useState(false);
  const [tableKey, setTableKey] = useState(0);
  const [columnConfig, setColumnConfig] = useState({});
  const [columnOrder, setColumnOrder] = useState([]);
  const [columnSettingOrder, setColumnSettingOrder] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [configLoaded, setConfigLoaded] = useState(false);

  // 字段配置 - 从常量改为状态，支持动态更新
  const [fieldConfig, setFieldConfig] = useState({
    order_number: { title: '销售单号', type: 'text', required: true, readonly: true, display_order: 1 },
    customer_id: { title: '客户名称', type: 'select', required: true, display_order: 2 },
    customer_order_number: { title: '客户订单号', type: 'text', display_order: 3 },
    contact_person_id: { title: '联系人', type: 'select', display_order: 4 },
    tax_id: { title: '税收', type: 'select', display_order: 5 },
    tax_rate: { title: '税率', type: 'number', readonly: true, display_order: 6 },
    order_type: { title: '订单类型', type: 'select', required: true, display_order: 7 },
    customer_code: { title: '客户编号', type: 'text', display_order: 8 },
    payment_method: { title: '付款方式', type: 'text', display_order: 9 },
    phone: { title: '电话', type: 'text', display_order: 10 },
    deposit: { title: '订金', type: 'number', display_order: 11 },
    plate_deposit_rate: { title: '版费订金%', type: 'number', display_order: 12 },
    delivery_date: { title: '交货日期', type: 'date', required: true, display_order: 13 },
    customer_short_name: { title: '客户简称', type: 'text', display_order: 14 },
    delivery_method: { title: '送货方式', type: 'text', display_order: 15 },
    mobile: { title: '手机', type: 'text', display_order: 16 },
    deposit_amount: { title: '订金', type: 'number', display_order: 17 },
    plate_deposit: { title: '版费订金', type: 'number', display_order: 18 },
    internal_delivery_date: { title: '内部交期', type: 'date', display_order: 19 },
    salesperson_id: { title: '业务员', type: 'select', display_order: 20 },
    contract_date: { title: '合同日期', type: 'date', display_order: 21 },
    contact_method: { title: '联系方式', type: 'select', display_order: 22 },
    tracking_person: { title: '跟单员', type: 'select', display_order: 23 },
    company_id: { title: '归属公司', type: 'select', display_order: 24 },
    logistics_info: { title: '物流信息', type: 'select', display_order: 25 },
    delivery_contact: { title: '送货联系人', type: 'text', display_order: 26 },
    status: { title: '状态', type: 'select', display_order: 27 },
    delivery_address: { title: '送货地址', type: 'textarea', display_order: 28 },
    production_requirements: { title: '生产要求', type: 'textarea', display_order: 29 },
    order_requirements: { title: '订单要求', type: 'textarea', display_order: 30 }
  });

  // 字段分组
  const [fieldGroups, setFieldGroups] = useState({
    '基本信息': ['order_number', 'customer_id', 'customer_order_number', 'contact_person_id', 'tax_id', 'tax_rate'],
    '订单信息': ['order_type', 'delivery_date', 'internal_delivery_date', 'contract_date', 'status'],
    '客户信息': ['customer_code', 'customer_short_name', 'phone', 'mobile', 'contact_method'],
    '业务信息': ['salesperson_id', 'tracking_person', 'company_id'],
    '付款信息': ['payment_method', 'deposit', 'deposit_amount', 'plate_deposit_rate', 'plate_deposit'],
    '物流信息': ['delivery_method', 'logistics_info', 'delivery_contact', 'delivery_address'],
    '要求信息': ['production_requirements', 'order_requirements']
  });

  useEffect(() => {
    fetchData();
    fetchOptions();
  }, []);

  useEffect(() => {
    if (modalVisible) {
      setActiveTab('base');
    }
  }, [modalVisible]);

  // 动态字段相关函数
  const calculateFieldValue = (formula, record) => {
    try {
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
      
      const localVars = { ...record };
      
      let processedFormula = formula.replace(/\bif\s*\(/g, 'if_condition(');
      
      const paramNames = [
        ...Object.keys(safeGlobals),
        ...Object.keys(localVars)
      ];
      
      const paramValues = [
        ...Object.values(safeGlobals),
        ...Object.values(localVars)
      ];
      
      const functionBody = `return ${processedFormula};`;
      
      const calculateFunction = new Function(...paramNames, functionBody);
      const result = calculateFunction(...paramValues);
      
      return result;
    } catch (error) {
      console.error('公式计算错误:', error);
      return null;
    }
  };

  const loadDynamicFields = async () => {
    try {
      const response = await dynamicFieldsApi.getModelFields('sales_order');
      if (response.data.success) {
        setDynamicFields(response.data.data || []);
        setInitialized(true);
      }
    } catch (error) {
      console.error('加载动态字段失败:', error);
    }
  };

  const loadRecordDynamicValues = async (recordId) => {
    try {
      const response = await dynamicFieldsApi.getRecordDynamicValues('salesOrder', recordId);
      if (response.data.success) {
        setDynamicFieldValues(response.data.data || {});
      }
    } catch (error) {
      console.error('加载动态字段值失败:', error);
    }
  };

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


      
      await columnConfigurationApi.saveColumnConfig('salesOrder', 'column_config', completeConfig);
      await columnConfigurationApi.saveColumnConfig('salesOrder', 'column_order', newColumnOrder);
      
      setColumnConfig(completeConfig);
      setColumnOrder(newColumnOrder);
      setColumnSettingOrder(newColumnOrder);
      setTableKey(prev => prev + 1);
      message.success('列配置已保存');
      
      // 关闭字段设置面板
      setColumnSettingVisible(false);
      
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

  const handleColumnOrderChange = (newOrder) => {
    setColumnSettingOrder(newOrder);
  };

  // 初始化列顺序
  const initializeColumnOrder = () => {
    // 只有在没有保存的列顺序且没有从后端加载的列顺序时才设置默认顺序
    if (columnSettingOrder.length === 0) {
      const defaultOrder = [
        'order_number', 'customer_id', 'customer_order_number', 'contact_person_id',
        'tax_id', 'tax_rate', 'order_type', 'customer_code', 'payment_method',
        'phone', 'deposit', 'plate_deposit_rate', 'delivery_date', 'customer_short_name',
        'delivery_method', 'mobile', 'deposit_amount', 'plate_deposit', 'internal_delivery_date',
        'salesperson_id', 'contract_date', 'contact_method', 'tracking_person', 'company_id',
        'logistics_info', 'delivery_contact', 'status', 'delivery_address',
        'production_requirements', 'order_requirements'
      ];
      setColumnSettingOrder(defaultOrder);
    }
  };

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

  // 根据列配置获取可见的表单字段
  const getVisibleFormFields = () => {
    // 如果配置还没有加载完成，显示所有字段
    if (!configLoaded) {
      return Object.keys(fieldConfig);
    }
    
    // 如果列配置为空，显示所有字段
    if (Object.keys(columnConfig).length === 0) {
      return Object.keys(fieldConfig);
    }
    
    // 根据列配置过滤字段，只显示被勾选的字段
    return Object.keys(fieldConfig).filter(field => {
      // 必填字段始终显示，不能被隐藏
      const config = fieldConfig[field];
      if (config && config.required) {
        return true;
      }
      
      // 如果配置中没有明确设置为false，则显示
      return !(field in columnConfig) || columnConfig[field] === true;
    });
  };

  // 获取按列设置顺序排列的可见表单字段
  const getOrderedVisibleFormFields = () => {
    const visibleFields = getVisibleFormFields();
    
    // 如果有保存的列顺序，按该顺序排列
    if (columnSettingOrder.length > 0) {
      const orderedFields = [];
      
      // 首先添加列设置顺序中的可见字段
      columnSettingOrder.forEach(field => {
        if (visibleFields.includes(field)) {
          orderedFields.push(field);
        }
      });
      
      // 然后添加不在列设置顺序中的可见字段
      visibleFields.forEach(field => {
        if (!orderedFields.includes(field)) {
          orderedFields.push(field);
        }
      });
      
      return orderedFields;
    }
    
    // 如果没有保存的顺序，按字段配置的display_order排序
    return visibleFields.sort((a, b) => {
      const configA = fieldConfig[a];
      const configB = fieldConfig[b];
      return (configA?.display_order || 0) - (configB?.display_order || 0);
    });
  };

  // 渲染表单字段
  const renderFormField = (fieldName) => {
    const config = fieldConfig[fieldName];
    if (!config) return null;

    const commonProps = {
      name: fieldName,
      label: config.title,
      rules: config.required ? [{ required: true, message: `请输入${config.title}` }] : []
    };

    switch (fieldName) {
      case 'order_number':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="自动生成" disabled />
            </Form.Item>
          </Col>
        );
      
      case 'customer_id':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select 
                placeholder="请选择客户" 
                showSearch 
                optionFilterProp="children"
                onChange={handleCustomerChange}
              >
                {customerOptions.map(option => (
                  <Option key={option.value} value={option.value}>{option.label}</Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'customer_order_number':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="客户订单号" />
            </Form.Item>
          </Col>
        );
      
      case 'contact_person_id':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select 
                placeholder="请选择联系人" 
                allowClear
                showSearch
                optionFilterProp="children"
                onChange={handleContactChange}
              >
                {contactOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'tax_id':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select 
                placeholder="请选择税收" 
                allowClear 
                showSearch 
                optionFilterProp="children"
                onChange={handleTaxChange}
              >
                {taxOptions.map(option => (
                  <Option key={option.value} value={option.value} data-rate={option.rate}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'tax_rate':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <InputNumber style={{ width: '100%' }} min={0} step={0.01} placeholder="0" disabled addonAfter="%" />
            </Form.Item>
          </Col>
        );
      
      case 'order_type':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select placeholder="正常订单">
                <Option value="normal">正常订单</Option>
                <Option value="sample">打样订单</Option>
                <Option value="stock_check">查库订单</Option>
                <Option value="plate_fee">版费订单</Option>
                <Option value="urgent">加急订单</Option>
                <Option value="stock">备货订单</Option>
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'customer_code':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="客户编号" />
            </Form.Item>
          </Col>
        );
      
      case 'payment_method':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="付款方式" />
            </Form.Item>
          </Col>
        );
      
      case 'phone':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="电话" />
            </Form.Item>
          </Col>
        );
      
      case 'deposit':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <InputNumber style={{ width: '100%' }} min={0} max={100} step={0.01} placeholder="0" addonAfter="%" />
            </Form.Item>
          </Col>
        );
      
      case 'plate_deposit_rate':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <InputNumber style={{ width: '100%' }} min={0} max={100} step={0.01} placeholder="0" addonAfter="%" />
            </Form.Item>
          </Col>
        );
      
      case 'delivery_date':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <DatePicker 
                style={{ width: '100%' }} 
                onChange={handleDeliveryDateChange}
              />
            </Form.Item>
          </Col>
        );
      
      case 'customer_short_name':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="客户简称" />
            </Form.Item>
          </Col>
        );
      
      case 'delivery_method':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="送货方式" />
            </Form.Item>
          </Col>
        );
      
      case 'mobile':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="手机" />
            </Form.Item>
          </Col>
        );
      
      case 'deposit_amount':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <InputNumber style={{ width: '100%' }} min={0} step={0.01} placeholder="0" />
            </Form.Item>
          </Col>
        );
      
      case 'plate_deposit':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <InputNumber style={{ width: '100%' }} min={0} step={0.01} placeholder="0" />
            </Form.Item>
          </Col>
        );
      
      case 'internal_delivery_date':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        );
      
      case 'salesperson_id':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select placeholder="请选择业务员" allowClear>
                {employees.map((employee, index) => (
                  <Option key={employee.value || `sales-employee-${index}`} value={employee.value}>
                    {employee.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'contract_date':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        );
      
      case 'contact_method':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select placeholder="请选择联系方式" allowClear>
                <Option value="phone">电话</Option>
                <Option value="email">邮件</Option>
                <Option value="fax">传真</Option>
                <Option value="wechat">微信</Option>
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'tracking_person':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select placeholder="请选择跟单员" allowClear showSearch optionFilterProp="children">
                {employees.map((employee, index) => (
                  <Option key={employee.value || `tracking-employee-${index}`} value={employee.value}>
                    {employee.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'company_id':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select placeholder="请选择归属公司" allowClear>
                {/* TODO: 添加公司选项 */}
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'logistics_info':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select placeholder="请选择物流信息" allowClear>
                {/* TODO: 添加物流选项 */}
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'delivery_contact':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="送货联系人" />
            </Form.Item>
          </Col>
        );
      
      case 'status':
        return (
          <Col span={4} key={fieldName}>
            <Form.Item {...commonProps}>
              <Select placeholder="草稿" defaultValue="draft" disabled>
                <Option value="draft">草稿</Option>
                <Option value="confirmed">已确认</Option>
                <Option value="production">生产中</Option>
                <Option value="shipped">已发货</Option>
                <Option value="completed">已完成</Option>
                <Option value="cancelled">已取消</Option>
              </Select>
            </Form.Item>
          </Col>
        );
      
      case 'delivery_address':
        return (
          <Col span={24} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="请输入送货地址" />
            </Form.Item>
          </Col>
        );
      
      case 'production_requirements':
        return (
          <Col span={12} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="请输入生产要求" />
            </Form.Item>
          </Col>
        );
      
      case 'order_requirements':
        return (
          <Col span={12} key={fieldName}>
            <Form.Item {...commonProps}>
              <Input placeholder="请输入订单要求" />
            </Form.Item>
          </Col>
        );
      
      default:
        return null;
    }
  };

  // 动态字段相关的useEffect
  useEffect(() => {
    const initialize = async () => {
      try {
        await loadDynamicFields();
        await loadColumnConfig();
        await checkUserPermission();
        setInitialized(true);
        setConfigLoaded(true);
      } catch (error) {
        console.error('初始化失败:', error);
        setInitialized(true);
      }
    };
    
    initialize();
  }, []);

  useEffect(() => {
    if (initialized && dynamicFields.length > 0) {
      // 更新字段配置，添加动态字段
      const newFieldConfig = { ...fieldConfig };
      const newFieldGroups = { ...fieldGroups };
      
      dynamicFields.forEach(field => {
        if (!newFieldConfig[field.field_name]) {
          newFieldConfig[field.field_name] = {
            title: field.field_label,
            type: field.field_type,
            required: field.is_required,
            readonly: field.is_readonly,
            display_order: field.display_order || 999,
            help_text: field.help_text,
            field_options: field.field_options,
            is_calculated: field.is_calculated,
            calculation_formula: field.calculation_formula
          };
        }
      });
      
      setFieldConfig(newFieldConfig);
      
      // 将动态字段添加到默认分组
      if (!newFieldGroups['自定义字段']) {
        newFieldGroups['自定义字段'] = [];
      }
      dynamicFields.forEach(field => {
        if (!newFieldGroups['自定义字段'].includes(field.field_name)) {
          newFieldGroups['自定义字段'].push(field.field_name);
        }
      });
      
      setFieldGroups(newFieldGroups);
      
      // 只有在没有列顺序时才初始化
      if (columnSettingOrder.length === 0) {
        initializeColumnOrder();
      } else {
        // 如果有保存的列顺序，确保动态字段也在其中
        const currentOrder = [...columnSettingOrder];
        let hasChanges = false;
        
        dynamicFields.forEach(field => {
          if (!currentOrder.includes(field.field_name)) {
            currentOrder.push(field.field_name);
            hasChanges = true;
          }
        });
        
        if (hasChanges) {
          setColumnSettingOrder(currentOrder);
        }
      }
    }
  }, [initialized, dynamicFields.length]); // 只依赖长度，避免无限循环

  useEffect(() => {
    if (initialized) {
      fetchData();
    }
  }, [initialized]); // 移除dynamicFields依赖，避免无限循环

  // 监听列顺序变化，强制表格重新渲染
  useEffect(() => {
    if (columnSettingOrder.length > 0) {
      setTableKey(prev => prev + 1);
    }
  }, [columnSettingOrder]);

  // 点击外部关闭列设置面板
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (columnSettingVisible) {
        const columnSettingPanel = document.querySelector('.column-setting-panel');
        const columnSettingButton = document.querySelector('.column-setting-button');
        
        if (columnSettingPanel && 
            !columnSettingPanel.contains(event.target) && 
            columnSettingButton && 
            !columnSettingButton.contains(event.target)) {
          setColumnSettingVisible(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [columnSettingVisible]);

  const fetchData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await salesOrderService.getSalesOrders({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...params
      });

      if (response.data.success) {
        let orders = response.data.data.orders || [];
        
        // 计算动态字段值
        if (initialized && dynamicFields.length > 0) {
          orders = orders.map(order => {
            const calculatedFields = {};
            dynamicFields.forEach(field => {
              if (field.is_calculated && field.calculation_formula) {
                const calculatedValue = calculateFieldValue(field.calculation_formula, order);
                calculatedFields[field.field_name] = calculatedValue;
              }
            });
            return { ...order, ...calculatedFields };
          });
        }
        
        setData(orders);
        setPagination(prev => ({
          ...prev,
          total: response.data.data.total
        }));
      }
    } catch (error) {
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchOptions = async () => {
    try {
      const [customerRes, productRes, materialRes, taxRes, unitRes, employeeRes] = await Promise.all([
        salesOrderService.getCustomerOptions(),
        salesOrderService.getProductOptions(),
        salesOrderService.getMaterialOptions(),
        salesOrderService.getTaxOptions(),
        salesOrderService.getUnitOptions(),
        salesOrderService.getEmployeeOptions()
      ]);

      if (customerRes.data.success) {
        setCustomerOptions(customerRes.data.data);
      }
      if (productRes.data.success) {
        setProductOptions(productRes.data.data);
      }
      if (materialRes.data.success) {
        setMaterialOptions(materialRes.data.data);
      }
      if (taxRes.data.success) {
        setTaxOptions(taxRes.data.data);
      }
      if (unitRes.data.success) {
        setUnitOptions(unitRes.data.data);
      }
      if (employeeRes?.data?.success) {
        setEmployees(employeeRes.data.data);
      }
    } catch (error) {
      console.error('获取选项数据失败:', error);
    }
  };

  const handleSearch = async () => {
    const values = await searchForm.validateFields();
    await fetchData(values);
  };

  const handleReset = () => {
    searchForm.resetFields();
    fetchData();
  };

  const handleAdd = () => {
    setCurrentRecord(null);
    form.resetFields();
    form.setFieldsValue({
      delivery_date: dayjs(),
      internal_delivery_date: dayjs().subtract(1, 'day'), // 设置为当前日期的前一天
      status: 'draft',
      order_type: 'normal',
      tax_id: null,
      tax_rate: 0,
      deposit: 0,
      plate_deposit_rate: 0,
      deposit_amount: 0,
      plate_deposit: 0
    });
    setOrderDetails([]);
    setOtherFees([]);
    setMaterials([]);
    setContactOptions([]);
    setModalVisible(true);
  };

  const handleEdit = async (record) => {
    try {
      const response = await salesOrderService.getSalesOrderById(record.id);
      if (response.data.success) {
        const orderData = response.data.data;
        setCurrentRecord(orderData); // 设置完整的订单数据
        
        // 加载动态字段值
        await loadRecordDynamicValues(record.id);
        
        // 先设置基本字段（不包括联系人相关字段）
        const basicFields = {
          ...orderData,
          delivery_date: orderData.delivery_date ? dayjs(orderData.delivery_date) : null,
          internal_delivery_date: orderData.internal_delivery_date ? dayjs(orderData.internal_delivery_date) : null,
          contract_date: orderData.contract_date ? dayjs(orderData.contract_date) : null,
          // 映射税收字段名
          tax_id: orderData.tax_rate_id,
          // 添加动态字段值
          ...dynamicFieldValues
        };
        
        // 如果订单有客户ID，先获取联系人列表
        if (orderData.customer_id) {
          try {
            const contactsResponse = await salesOrderService.getCustomerContacts(orderData.customer_id);
            if (contactsResponse.data.success) {
              const formattedContacts = contactsResponse.data.data.map(c => ({
                value: c.id,
                label: c.contact_name,
                ...c
              }));
              setContactOptions(formattedContacts);
              
              // 查找当前订单对应的联系人
              const currentContact = formattedContacts.find(c => c.value === orderData.contact_person_id);
              if (currentContact) {
                // 使用当前订单的联系人信息
                basicFields.contact_person_id = currentContact.value;
                basicFields.phone = currentContact.mobile || '';
                basicFields.mobile = currentContact.mobile || '';
                basicFields.contact_method = currentContact.mobile || '';
              }
            }
          } catch (error) {
            console.error('加载联系人信息失败:', error);
            setContactOptions([]);
          }
        }
        
        // 设置表单值
        form.setFieldsValue(basicFields);
        setOrderDetails(orderData.order_details || []);
        setOtherFees(orderData.other_fees || []);
        setMaterials(orderData.material_details || []);
        setModalVisible(true);
      }
    } catch (error) {
      message.error('获取订单详情失败');
    }
  };

  const handleFinish = async (record) => {
    try {
      const response = await salesOrderService.finishSalesOrder(record.id);
      if (response.data?.success) {
        message.success('订单已完成');
        fetchData(); // 刷新数据
      } else {
        message.error(response.data?.message || '完成失败');
      }
    } catch (error) {
      message.error('完成失败');
    }
  };

  const handleDelete = async (record) => {
    try {
      const response = await salesOrderService.deleteSalesOrder(record.id);
      if (response.data.success) {
        // 删除动态字段值
        await dynamicFieldsApi.deleteRecordPageValues('sales_order', 'sales_order', record.id);
        message.success('删除成功');
        fetchData();
      }
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      // 过滤无效的销售订单明细（未选产品的行）
      const filteredOrderDetails = orderDetails.filter(item => !!item.product_id);

      // 过滤无效的销售材料（未选材料的行）
      const filteredMaterials = materials.filter(item => !!item.material_id);

      // 过滤无效的其他费用（未选费用类型的行）
      const filteredOtherFees = otherFees.filter(item => !!item.fee_type);

      // 判断销售订单明细中每一项的订单数量是否为0或为空，如果为空或0，则提示用户填写产品数量
      for (let i = 0; i < filteredOrderDetails.length; i++) {
        const item = filteredOrderDetails[i];
        if (!item.order_quantity || item.order_quantity === 0 || item.order_quantity === null) {
          message.error('请填写订单明细中的数量：' + item.product_name);
          return; // 直接终止整个handleSave函数，后续代码不再执行
        }
      };

      // 判断销售材料中每一项的数量是否为0或为空，如果为空或0，则提示用户填写材料数量
      for (let i = 0; i < filteredMaterials.length; i++) {

        const item = filteredMaterials[i];
        if (!item.quantity || item.quantity === 0 || item.quantity === null) {

          message.error('请填写材料明细中的数量：' + item.material.material_name);
          return; // 直接终止整个handleSave函数
        }
      };

      const orderData = {
        ...values,
        delivery_date: values.delivery_date ? values.delivery_date.format('YYYY-MM-DD') : null,
        internal_delivery_date: values.internal_delivery_date ? values.internal_delivery_date.format('YYYY-MM-DD') : null,
        contract_date: values.contract_date ? values.contract_date.format('YYYY-MM-DD') : null,
        order_details: filteredOrderDetails,
        other_fees: filteredOtherFees,
        material_details: filteredMaterials,
        // 映射税收字段名
        tax_rate_id: values.tax_id
      };

      let response;
      let newRecordId;
      if (currentRecord) {
        response = await salesOrderService.updateSalesOrder(currentRecord.id, orderData);
        newRecordId = currentRecord.id;
      } else {
        response = await salesOrderService.createSalesOrder(orderData);
        newRecordId = response.data.data?.id;
      }

      if (response.data.success) {
        // 保存动态字段值
        if (newRecordId) {
          const pageValues = {};
          dynamicFields.forEach(field => {
            const fieldValue = values[field.field_name];
            if (fieldValue !== undefined && fieldValue !== null && fieldValue !== '') {
              pageValues[field.field_name] = fieldValue;
            }
          });
          
          if (Object.keys(pageValues).length > 0) {
            await dynamicFieldsApi.saveRecordPageValues('sales_order', 'sales_order', newRecordId, pageValues);
          }
        }
        
        message.success(currentRecord ? '更新成功' : '创建成功');
        setModalVisible(false);
        fetchData();
      }
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleApprove = async (record) => {
    try {
      const response = await request.post(`/tenant/business/sales/sales-orders/${record.id}/approve`);
      if (response.data.success) {
        message.success('审批成功');
        fetchData();
      }
    } catch (error) {
      message.error('审批失败');
    }
  };

  const handleCancel = async (record) => {
    try {
      const response = await request.post(`/tenant/business/sales/sales-orders/${record.id}/cancel`);
      if (response.data.success) {
        message.success('取消成功');
        fetchData();
      }
    } catch (error) {
      message.error('取消失败');
    }
  };

  const handleViewDetail = async (record) => {
    try {
      // 获取完整的订单详情，包括订单明细
      const response = await salesOrderService.getSalesOrderById(record.id);
      if (response.data.success) {
        const orderData = response.data.data;
        setCurrentRecord(orderData);
      } else {
        message.error('获取订单详情失败');
        return;
      }
    } catch (error) {
      console.error('获取订单详情失败:', error);
      message.error('获取订单详情失败');
      return;
    }
    setDetailDrawerVisible(true);
  };

  const handleTableChange = (newPagination) => {
    setPagination(prev => ({
      ...prev,
      current: newPagination.current,
      pageSize: newPagination.pageSize
    }));
    fetchData();
  };

  // 缓存 handleTaxChange 函数
  const handleTaxChange = useCallback((value) => {
    if (value) {
      const selectedTax = taxOptions.find(option => option.value === value);
      if (selectedTax) {
        form.setFieldsValue({
          tax_rate: selectedTax.rate
        });
      }
    } else {
      form.setFieldsValue({
        tax_rate: 0
      });
    }
  }, [taxOptions, form]);

  // 缓存 handleCustomerChange 函数
  const handleCustomerChange = useCallback(async (customerId) => {
    if (customerId) {
      try {
        // 并行加载客户详情和联系人列表
        const [detailResponse, contactsResponse] = await Promise.all([
          salesOrderService.getCustomerDetails(customerId),
          salesOrderService.getCustomerContacts(customerId)
        ]);

        if (detailResponse.data.success) {
          const customerDetails = detailResponse.data.data;
          // 自动填充客户相关字段
          form.setFieldsValue({
            customer_code: customerDetails.customer_code,
            payment_method_id: customerDetails.payment_method_id,
            salesperson_id: customerDetails.salesperson_id,
            company_id: customerDetails.company_id,
            tax_id: customerDetails.tax_rate_id,
            tax_rate: customerDetails.tax_rate
          });
        }
        if (contactsResponse.data.success) {
          const formattedContacts = contactsResponse.data.data.map(c => ({
            value: c.id,
            label: c.contact_name,
            ...c
          }));
          setContactOptions(formattedContacts);

          if (formattedContacts.length > 0) {
            const firstContact = formattedContacts[0];
            form.setFieldsValue({
              contact_person_id: firstContact.value,
              phone: firstContact.mobile,
              mobile: firstContact.mobile,
            });
          }else{
            form.setFieldsValue({
              contact_person_id: undefined,
              phone: '',
              mobile: '',
              contact_method: null
            });
          }
          message.success('已自动加载客户信息');
        } else {
          message.error(contactsResponse.data.error || '加载联系人失败');
          setContactOptions([]);
        }
      } catch (error) {
        console.error('加载客户信息失败:', error);
        message.warning('加载客户信息失败，请手动填写');
        setContactOptions([]);
      }
    } else {
      // 清空相关字段和联系人选项
      form.setFieldsValue({
        customer_code: '',
        contact_person_id: null,
        phone: '',
        mobile: '',
        payment_method: null,
        delivery_method: null,
        contact_method: null,
        salesperson_id: null,
        company_id: null,
        tax_id: null,
        tax_rate: 0,
        deposit: 0
      });
      setContactOptions([]);
    }
  }, [form, setContactOptions]);

  // 缓存 handleDeliveryDateChange 函数
  const handleDeliveryDateChange = useCallback((date) => {
    if (date) {
      // 设置内部交期为交货日期的前一天
      const internalDeliveryDate = date.subtract(1, 'day');
      form.setFieldsValue({
        internal_delivery_date: internalDeliveryDate
      });
    } else {
      // 清空内部交期
      form.setFieldsValue({
        internal_delivery_date: null
      });
    }
  }, [form]);

  // 缓存 handleContactChange 函数
  const handleContactChange = useCallback((contactId) => {
    if (contactId) {
      const selectedContact = contactOptions.find(option => option.value === contactId);
      if (selectedContact) {
        form.setFieldsValue({
          phone: selectedContact.mobile,
          mobile: selectedContact.mobile,
        });
      }
    } else {
      // 清空联系人相关信息
      form.setFieldsValue({
        phone: '',
        mobile: ''
      });
    }
  }, [contactOptions, form]);

  // 缓存 handleTabChange 函数
  const handleTabChange = useCallback((key) => {
    if (['details', 'fees', 'materials'].includes(key)) {
      const deliveryDate = form.getFieldValue('delivery_date');
      if (!deliveryDate) {
        message.warning('请先填写交货日期！');
        return;
      }
    }
    setActiveTab(key);
  }, [form]);

  // 缓存 addOrderDetail 函数
  const addOrderDetail = useCallback(() => {
    const deliveryDate = form.getFieldValue('delivery_date');
    const internalDeliveryDate = form.getFieldValue('internal_delivery_date');
    const newDetail = {
      id: `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, // 使用更稳定的唯一ID
      product_id: null,
      product_code: '',
      product_name: '',
      product_specification: '',
      planned_meters: undefined,
      planned_weight: undefined,
      corona: '',
      order_quantity: undefined,
      unit_price: undefined,
      amount: 0,
      unit: '',
      unit_id: null,
      negative_deviation_percentage: undefined,
      positive_deviation_percentage: undefined,
      production_small_quantity: undefined,
      production_large_quantity: undefined,
      shipping_quantity: undefined,
      production_quantity: undefined,
      usable_inventory: undefined,
      storage_quantity: undefined,
      estimated_thickness_m: undefined,
      estimated_weight_kg: undefined,
      customer_code: '',
      customer_requirements: '',
      material_structure: '',
      printing_requirements: '',
      internal_delivery_date: internalDeliveryDate || null,
      delivery_date: deliveryDate || null
    };
    setOrderDetails(prev => [...prev, newDetail]);
  }, [form]);

  // 缓存 removeOrderDetail 函数
  const removeOrderDetail = useCallback((index) => {
    setOrderDetails(prev => prev.filter((_, i) => i !== index));
  }, []);

  // 缓存 updateOrderDetail 函数
  const updateOrderDetail = useCallback(async (index, field, value) => {
    setOrderDetails(prev => {
      const newDetails = [...prev];

      newDetails[index] = { ...newDetails[index], [field]: value };
      
      // 自动计算金额
      if (field === 'order_quantity' || field === 'unit_price') {
        newDetails[index].amount = (newDetails[index].order_quantity || 0) * (newDetails[index].unit_price || 0);
      }
      
      // 自动填充计划米数和计划重量
      if (field === 'order_quantity' || field === 'unit_id') {

        const detail = newDetails[index];
        const quantity = detail.order_quantity || 0;
        
        // 正确获取单位名称
        let unitName = detail.unit_name || detail.unit;
        if (!unitName && detail.unit_id) {
          const unitOption = unitOptions.find(opt => opt.value === detail.unit_id);
          unitName = unitOption ? unitOption.label : '';
        }
        
        
        
        // 获取产品数据和规格信息
        const productData = detail.productData || null;
        const specification = detail.product_specification || null;
        
        const plannedValues = calculatePlannedValues(quantity, unitName, productData, specification);
        
        
        newDetails[index].planned_meters = plannedValues.planned_meters;
        newDetails[index].planned_weight = plannedValues.planned_weight;
      }
      
      return newDetails;
    });
    
    // 根据产品选择自动填充信息
    if (field === 'product_id' && value) {
      try {
        // 从产品详情API获取完整的产品信息
        const response = await salesOrderService.getProductDetails(value);
        if (response.data.success) {
          const productData = response.data.data;
          
          // 使用函数式更新，确保状态更新的一致性
          setOrderDetails(prev => {
            const updatedDetails = [...prev];
            updatedDetails[index] = {
              ...updatedDetails[index],
              // 基本产品信息
              product_code: productData.product_code,
              product_name: productData.product_name,
              product_specification: productData.specification || '',
              planned_meters: productData.planned_meters || undefined,
              planned_weight: productData.planned_weight || undefined,
              corona: productData.corona || '',
              unit: productData.unit,
              unit_id: productData.unit_id || productData.sales_unit_id,
              sales_unit_id: productData.sales_unit_id,
              
              // 价格信息
              unit_price: productData.unit_price || 0,
              currency_id: productData.currency_id,
              
              // 库存信息
              usable_inventory: productData.usable_inventory || 0,
              
              // 生产信息
              production_small_quantity: productData.production_small_quantity || 0,
              production_large_quantity: productData.production_large_quantity || 0,
              
              // 技术参数
              estimated_thickness_m: productData.thickness,
              estimated_weight_kg: productData.net_weight,
              
              // 业务字段
              material_structure: productData.material_info || productData.specification,
              storage_requirements: productData.storage_condition,
              customer_requirements: productData.quality_standard,
              printing_requirements: productData.inspection_method,
              
              // 袋型信息
              bag_type_id: productData.bag_type_id,
              
              // 其他字段
              color_count: productData.is_compound_needed ? 1 : 0,
              outer_box: productData.is_packaging_needed ? '是' : '否',
              
              // 税收信息 - 如果产品有关联的税收信息
              tax_rate_id: productData.tax_rate_id
            };
            
            // 重新计算金额
            const quantity = updatedDetails[index].order_quantity || 0;
            const price = updatedDetails[index].unit_price || 0;
            updatedDetails[index].amount = quantity * price;
            
            // 自动填充计划米数和计划重量
            let unitName = updatedDetails[index].unit_name || updatedDetails[index].unit;
            if (!unitName && updatedDetails[index].unit_id) {
              const unitOption = unitOptions.find(opt => opt.value === updatedDetails[index].unit_id);
              unitName = unitOption ? unitOption.label : '';
            }
            
            // 保存产品数据用于后续计算
            updatedDetails[index].productData = productData;
            
            const plannedValues = calculatePlannedValues(quantity, unitName, productData, productData.specification);
            updatedDetails[index].planned_meters = plannedValues.planned_meters;
            updatedDetails[index].planned_weight = plannedValues.planned_weight;
            
            return updatedDetails;
          });
          
          // 尝试同时获取库存信息
          try {
            const inventoryResponse = await salesOrderService.getProductInventory(value);
            if (inventoryResponse.data.success) {
              const inventory = inventoryResponse.data.data;
              setOrderDetails(prev => {
                const updatedDetails = [...prev];
                updatedDetails[index].usable_inventory = inventory.available_quantity || 0;
                return updatedDetails;
              });
            }
          } catch (error) {
            console.error('获取库存信息失败:', error);
          }
          
          message.success('产品信息已自动填充');
          return; // 提前返回，避免执行后面的逻辑
        }
      } catch (error) {
        console.error('获取产品详情失败:', error);
        message.error('获取产品详情失败');
        
        // 回退到基本的产品选项信息
        const product = productOptions.find(p => p.value === value);
        if (product) {
          setOrderDetails(prev => {
            const updatedDetails = [...prev];
            updatedDetails[index] = {
              ...updatedDetails[index],
              product_name: product.product_name || product.label?.split(' - ')[1],
              product_code: product.product_code || product.label?.split(' - ')[0],
              product_specification: product.specification || '',
              unit: product.unit || product.unit_name,
              unit_id: product.unit_id,
              material_structure: product.specification || '',
              unit_price: product.unit_price || 0
            };
            return updatedDetails;
          });
        }
      }
      
      // 对于产品选择的错误情况，也尝试加载库存信息
      try {
        const inventoryResponse = await salesOrderService.getProductInventory(value);
        if (inventoryResponse.data.success) {
          const inventory = inventoryResponse.data.data;
          setOrderDetails(prev => {
            const updatedDetails = [...prev];
            updatedDetails[index].usable_inventory = inventory.available_quantity || 0;
            return updatedDetails;
          });
        }
      } catch (error) {
        console.error('获取库存信息失败:', error);
      }
    }
  }, [productOptions]);

  // 单位转换和自动填充函数
  // 解析产品规格字符串，提取宽度、厚度、密度
  const parseSpecification = (specification) => {
    if (!specification) return null;
    

    
    // 尝试解析 "宽度*厚度*密度" 格式
    const patterns = [
      /(\d+(?:\.\d+)?)\s*[×xX*]\s*(\d+(?:\.\d+)?)\s*[×xX*]\s*(\d+(?:\.\d+)?)/, // 数字×数字×数字
      /(\d+(?:\.\d+)?)\s*mm\s*[×xX*]\s*(\d+(?:\.\d+)?)\s*μm\s*[×xX*]\s*(\d+(?:\.\d+)?)\s*g\/cm³/, // mm×μm×g/cm³
      /(\d+(?:\.\d+)?)\s*[×xX*]\s*(\d+(?:\.\d+)?)\s*[×xX*]\s*(\d+(?:\.\d+)?)\s*g\/cm³/, // 数字×数字×数字g/cm³
    ];
    
    for (const pattern of patterns) {
      const match = specification.match(pattern);
      if (match) {
        const [, width, thickness, density] = match;

        return {
          width: parseFloat(width),
          thickness: parseFloat(thickness),
          density: parseFloat(density)
        };
      }
    }
    
    
    return null;
  };

  // 从产品结构数据中提取参数
  const extractProductParams = (productData) => {
    if (!productData) return null;
    
    // 优先从产品结构表获取
    if (productData.structures && productData.structures.length > 0) {
      const structure = productData.structures[0];
              if (structure.width && structure.thickness && structure.density) {
          return {
            width: structure.width,
            thickness: structure.thickness,
            density: structure.density
          };
        }
    }
    
    // 从产品基本信息获取
    if (productData.width && productData.thickness) {

      return {
        width: productData.width,
        thickness: productData.thickness,
        density: productData.density
      };
    }
    
    return null;
  };

  // 计算重量和长度的相互转换
  const calculateConversion = (quantity, unitName, productParams, specification) => {
    if (!quantity || quantity <= 0) return { planned_meters: undefined, planned_weight: undefined };
    
    const unitLower = unitName.toLowerCase();

    
    // 尝试从规格解析参数
    let params = parseSpecification(specification);
    if (!params) {
      // 从产品数据获取参数
      params = productParams;
    }
    
    if (!params || !params.width || !params.thickness || !params.density) {

      return calculateBasicConversion(quantity, unitName);
    }
    

    
    // 重量转长度：重量(kg) / (宽度(mm) * 厚度(μm) * 密度(g/cm³) / 1000000)
    // 长度转重量：长度(m) * 宽度(mm) * 厚度(μm) * 密度(g/cm³) / 1000000
    
         // 重量单位：kg/千克/公斤 -> 计算计划重量和计划米数
     if (unitLower.includes('kg') || unitLower.includes('千克') || unitLower.includes('公斤')) {
       const plannedWeight = quantity;
       const plannedMeters = quantity / (params.width * params.thickness * params.density / 1000000);

       return { planned_meters: plannedMeters, planned_weight: plannedWeight };
     }
     // 重量单位：t/吨 -> 转换为kg后计算
     else if (unitLower.includes('t') || unitLower.includes('吨')) {
       const plannedWeight = quantity * 1000;
       const plannedMeters = (quantity * 1000) / (params.width * params.thickness * params.density / 1000000);

       return { planned_meters: plannedMeters, planned_weight: plannedWeight };
     }
     // 长度单位：m/米 -> 计算计划米数和计划重量
     else if (unitLower.includes('m') || unitLower.includes('米')) {
       const plannedMeters = quantity;
       const plannedWeight = quantity * params.width * params.thickness * params.density / 1000000;

       return { planned_meters: plannedMeters, planned_weight: plannedWeight };
     }
     // 长度单位：km/公里 -> 转换为米后计算
     else if (unitLower.includes('km') || unitLower.includes('千米')) {
       const plannedMeters = quantity * 1000;
       const plannedWeight = (quantity * 1000) * params.width * params.thickness * params.density / 1000000;

       return { planned_meters: plannedMeters, planned_weight: plannedWeight };
     }
     // 长度单位：cm/厘米 -> 转换为米后计算
     else if (unitLower.includes('cm') || unitLower.includes('厘米')) {
       const plannedMeters = quantity / 100;
       const plannedWeight = (quantity / 100) * params.width * params.thickness * params.density / 1000000;

       return { planned_meters: plannedMeters, planned_weight: plannedWeight };
     }
     // 长度单位：mm/毫米 -> 转换为米后计算
     else if (unitLower.includes('mm') || unitLower.includes('毫米')) {
       const plannedMeters = quantity / 1000;
       const plannedWeight = (quantity / 1000) * params.width * params.thickness * params.density / 1000000;

       return { planned_meters: plannedMeters, planned_weight: plannedWeight };
     }
    

    return calculateBasicConversion(quantity, unitName);
  };

  // 基础单位转换（原来的逻辑）
  const calculateBasicConversion = (quantity, unitName) => {
    const unitLower = unitName.toLowerCase();
    
    // 重量单位：kg/千克/公斤 -> 填入计划重量
    if (unitLower.includes('kg') || unitLower.includes('千克') || unitLower.includes('公斤')) {
      return { planned_meters: undefined, planned_weight: quantity };
    }
    // 重量单位：t/吨 -> 转换为kg填入计划重量
    else if (unitLower.includes('t') || unitLower.includes('吨')) {
      return { planned_meters: undefined, planned_weight: quantity * 1000 };
    }
    // 长度单位：m/米 -> 填入计划米数
    else if (unitLower.includes('m') || unitLower.includes('米')) {
      return { planned_meters: quantity, planned_weight: undefined };
    }
    // 长度单位：km/公里 -> 转换为米填入计划米数
    else if (unitLower.includes('km') || unitLower.includes('千米')) {
      return { planned_meters: quantity * 1000, planned_weight: undefined };
    }
    // 长度单位：cm/厘米 -> 转换为米填入计划米数
    else if (unitLower.includes('cm') || unitLower.includes('厘米')) {
      return { planned_meters: quantity / 100, planned_weight: undefined };
    }
    // 长度单位：mm/毫米 -> 转换为米填入计划米数
    else if (unitLower.includes('mm') || unitLower.includes('毫米')) {
      return { planned_meters: quantity / 1000, planned_weight: undefined };
    }
    
    return { planned_meters: undefined, planned_weight: undefined };
  };

  const calculatePlannedValues = (quantity, unitName, productData = null, specification = null) => {

    
    if (!quantity || quantity <= 0 || !unitName) {

      return { planned_meters: undefined, planned_weight: undefined };
    }
    
    // 提取产品参数
    const productParams = extractProductParams(productData);
    
    // 使用智能转换
    return calculateConversion(quantity, unitName, productParams, specification);
  };

  // 缓存 loadInventoryForProduct 函数
  const loadInventoryForProduct = useCallback(async (productId, index, existingDetails = null) => {
    if (!productId) return;
    
    try {
      const response = await salesOrderService.getProductInventory(productId);
      if (response.data.success) {
        const inventory = response.data.data;
        const newDetails = existingDetails ? [...existingDetails] : [...orderDetails];
        newDetails[index].usable_inventory = inventory.available_quantity || 0;
        setOrderDetails(newDetails);
      }
    } catch (error) {
      console.error('获取库存信息失败:', error);
      message.warning('获取库存信息失败');
    }
  }, [orderDetails]);

  // 缓存 addOtherFee 函数
  const addOtherFee = useCallback(() => {
    const deliveryDate = form.getFieldValue('delivery_date');
    const internalDeliveryDate = form.getFieldValue('internal_delivery_date');
    const newFee = {
      id: `temp_fee_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      fee_type: '',
      product_id: null,
      product_name: '',
      length: undefined,
      width: undefined,
      price: undefined,
      quantity: 1,
      amount: 0,
      customer_order_number: '',
      customer_code: '',
      delivery_date: deliveryDate || null,
      internal_delivery_date: internalDeliveryDate || null,
      customer_requirements: '',
      notes: ''
    };
    setOtherFees(prev => [...prev, newFee]);
  }, [form]);

  // 缓存 removeOtherFee 函数
  const removeOtherFee = useCallback((index) => {
    setOtherFees(prev => prev.filter((_, i) => i !== index));
  }, []);

  // 缓存 updateOtherFee 函数
  const updateOtherFee = useCallback((index, field, value) => {
    setOtherFees(prev => {
      const newFees = [...prev];
      newFees[index] = { ...newFees[index], [field]: value };
      
      if (field === 'price' || field === 'quantity') {
        newFees[index].amount = (newFees[index].price || 0) * (newFees[index].quantity || 0);
      }
      
      return newFees;
    });
  }, []);

  // 缓存 addMaterial 函数
  const addMaterial = useCallback(() => {
    const deliveryDate = form.getFieldValue('delivery_date');
    const internalDeliveryDate = form.getFieldValue('internal_delivery_date');
    const newMaterial = {
      id: `temp_material_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      material_id: null,
      negative_deviation_percentage: undefined,
      positive_deviation_percentage: undefined,
      gift_quantity: undefined,
      quantity: undefined,
      auxiliary_quantity: undefined,
      price: undefined,
      amount: 0,
      delivery_date: deliveryDate || null,
      internal_delivery_date: internalDeliveryDate || null,
      customer_requirements: '',
      notes: ''
    };
    setMaterials(prev => [...prev, newMaterial]);
  }, [form]);

  // 缓存 removeMaterial 函数
  const removeMaterial = useCallback((index) => {
    setMaterials(prev => prev.filter((_, i) => i !== index));
  }, []);

  // 缓存 updateMaterial 函数
  const updateMaterial = useCallback((index, field, value) => {
    setMaterials(prev => {
      const newMaterials = [...prev];
      newMaterials[index] = { ...newMaterials[index], [field]: value };
      
      if (field === 'price' || field === 'quantity') {
        newMaterials[index].amount = (newMaterials[index].price || 0) * (newMaterials[index].quantity || 0);
      }
      
      return newMaterials;
    });
  }, []);

  const statusConfig = {
    draft: { color: 'default', text: '草稿' },
    confirmed: { color: 'processing', text: '已确认' },
    production: { color: 'blue', text: '生产中' },
    shipped: { color: 'success', text: '已发货' },
    completed: { color: 'success', text: '已完成' },
    cancelled: { color: 'error', text: '已取消' }
  };

  const orderTypeConfig = {
    normal: '正常订单',
    sample: '打样订单',
    stock_check: '查库订单',
    plate_fee: '版费订单',
    urgent: '加急订单',
    stock: '备货订单'
  };

  // 生成表格列配置
  const generateColumns = () => {
    const baseColumns = [
      {
        title: '销售单号',
        dataIndex: 'order_number',
        key: 'order_number',
        width: 150,
        fixed: 'left'
      },
      {
        title: '客户名称',
        dataIndex: 'customer_name',
        key: 'customer_id',
        width: 150
      },
      {
        title: '客户订单号',
        dataIndex: 'customer_order_number',
        key: 'customer_order_number',
        width: 120
      },
      {
        title: '交货日期',
        dataIndex: 'delivery_date',
        key: 'delivery_date',
        width: 120,
        render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
      },
      {
        title: '内部交期',
        dataIndex: 'internal_delivery_date',
        key: 'internal_delivery_date',
        width: 140,
        render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        width: 80,
        render: (status) => {
          const config = statusConfig[status] || { color: 'default', text: status };
          return <Tag color={config.color}>{config.text}</Tag>;
        }
      },
      {
        title: '联系人',
        dataIndex: 'contact_person',
        key: 'contact_person_id',
        width: 100
      },
      {
        title: '税收',
        dataIndex: 'tax_name',
        key: 'tax_id',
        width: 100
      },
      {
        title: '税率',
        dataIndex: 'tax_rate',
        key: 'tax_rate',
        width: 80,
        render: (rate) => rate ? `${rate}%` : '0%'
      },
      {
        title: '订单类型',
        dataIndex: 'order_type',
        key: 'order_type',
        width: 100,
        render: (type) => orderTypeConfig[type] || type
      },
      {
        title: '客户编号',
        dataIndex: 'customer_code',
        key: 'customer_code',
        width: 150
      },
      {
        title: '付款方式',
        dataIndex: 'payment_method',
        key: 'payment_method',
        width: 100
      },
      {
        title: '电话',
        dataIndex: 'phone',
        key: 'phone',
        width: 120
      },
      {
        title: '订金%',
        dataIndex: 'deposit_percentage',
        key: 'deposit',
        width: 80,
        render: (rate) => rate ? `${rate}%` : '0%'
      },
      {
        title: '版费订金%',
        dataIndex: 'plate_deposit_rate',
        key: 'plate_deposit_rate',
        width: 100,
        render: (rate) => rate ? `${rate}%` : '0%'
      },
      {
        title: '客户简称',
        dataIndex: 'customer_short_name',
        key: 'customer_short_name',
        width: 120
      },
      {
        title: '送货方式',
        dataIndex: 'delivery_method',
        key: 'delivery_method',
        width: 100
      },
      {
        title: '手机',
        dataIndex: 'mobile',
        key: 'mobile',
        width: 120
      },
      {
        title: '订金',
        dataIndex: 'deposit_amount',
        key: 'deposit_amount',
        width: 100,
        render: (amount) => amount ? `¥${amount}` : '¥0'
      },
      {
        title: '版费订金',
        dataIndex: 'plate_deposit',
        key: 'plate_deposit',
        width: 100,
        render: (amount) => amount ? `¥${amount}` : '¥0'
      },
      {
        title: '业务员',
        dataIndex: 'salesperson_name',
        key: 'salesperson_id',
        width: 100
      },
      {
        title: '合同日期',
        dataIndex: 'contract_date',
        key: 'contract_date',
        width: 120,
        render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
      },
      {
        title: '联系方式',
        dataIndex: 'contact_method',
        key: 'contact_method',
        width: 100
      },
      {
        title: '跟单员',
        dataIndex: 'tracking_person_name',
        key: 'tracking_person',
        width: 100
      },
      {
        title: '归属公司',
        dataIndex: 'company_name',
        key: 'company_id',
        width: 120
      },
      {
        title: '物流信息',
        dataIndex: 'logistics_info',
        key: 'logistics_info',
        width: 120
      },
      {
        title: '送货联系人',
        dataIndex: 'delivery_contact',
        key: 'delivery_contact',
        width: 120
      },
      {
        title: '送货地址',
        dataIndex: 'delivery_address',
        key: 'delivery_address',
        width: 200
      },
      {
        title: '生产要求',
        dataIndex: 'production_requirements',
        key: 'production_requirements',
        width: 200
      },
      {
        title: '订单要求',
        dataIndex: 'order_requirements',
        key: 'order_requirements',
        width: 200
      },
      {
        title: '操作',
        key: 'action',
        fixed: 'right',
        width: 200,
        render: (_, record) => (
          <Space size="small">
            <Button type="link" size="small" onClick={() => handleViewDetail(record)}>
              查看
            </Button>
            {record.status !== 'completed' && (
              <Button type="link" size="small" onClick={() => handleEdit(record)}>
                编辑
              </Button>
            )}
            {record.status === 'draft' && (
              <>
                <Button type="link" size="small" onClick={() => handleApprove(record)}>
                  确认
                </Button>
                <Button type="link" size="small" danger onClick={() => handleDelete(record)}>
                  删除
                </Button>
              </>
            )}
            {record.status === 'confirmed' && (
              <Button type="link" size="small" onClick={() => handleFinish(record)}>
                完成
              </Button>
            )}
            {record.status === 'confirmed' && (
              <Button type="link" size="small" danger onClick={() => handleCancel(record)}>
                取消
              </Button>
            )}
          </Space>
        )
      }
    ];

    // 添加动态字段列
    const dynamicColumns = Array.isArray(dynamicFields) ? dynamicFields.map(field => ({
      title: field.field_label || field.field_Label,
      dataIndex: field.field_name,
      key: field.field_name,
      width: 120,
      render: (value, record) => {
        if (field.is_calculated && field.calculation_formula) {
          try {
            return calculateFieldValue(field.calculation_formula, record);
          } catch (error) {
            console.error('计算字段值失败:', error);
            return value || '-';
          }
        }
        return value || '-';
      }
    })) : [];

    // 合并基础列和动态列
    const allColumns = [...baseColumns, ...dynamicColumns];

    // 根据列配置过滤和排序
    if (Object.keys(columnConfig).length > 0) {
      const visibleColumns = allColumns.filter(col => {
        if (col.key === 'action') return true; // 操作列始终显示
        return columnConfig[col.key] !== false;
      });

      // 根据列顺序排序
      if (Array.isArray(columnSettingOrder) && columnSettingOrder.length > 0) {
        const orderMap = {};
        columnSettingOrder.forEach((key, index) => {
          orderMap[key] = index;
        });

        visibleColumns.sort((a, b) => {
          const orderA = orderMap[a.key] ?? 999;
          const orderB = orderMap[b.key] ?? 999;
          return orderA - orderB;
        });
      }

      return visibleColumns;
    }

    return allColumns;
  };

  const columns = generateColumns();

  // 订单明细表格列
  // 缓存订单明细列定义
  const orderDetailColumns = useMemo(() => [
    {
      title: '产品',
      dataIndex: 'product_id',
      key: 'product_id',
      width: 200,
      fixed: 'left',
      render: (value, record, index) => (
        <Select
          style={{ width: '100%' }}
          placeholder="选择产品"
          value={value}
          onChange={(val) => updateOrderDetail(index, 'product_id', val)}
          showSearch
          optionFilterProp="children"
        >
          {productOptions.map(option => (
            <Option key={option.value} value={option.value}>
              {option.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: '产品编号',
      dataIndex: 'product_code',
      key: 'product_code',
      width: 120,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateOrderDetail(index, 'product_code', e.target.value)}
          placeholder="产品编号"
        />
      )
    },
    {
      title: '产品规格',
      dataIndex: 'product_specification',
      key: 'product_specification',
      width: 150,
      render: (value, record, index) => (
        <Input
          value={value}
          placeholder="产品规格"
        />
      )
    },
    {
      title: '订单数量',
      dataIndex: 'order_quantity',
      key: 'order_quantity',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          placeholder="必填"
          onChange={(val) => updateOrderDetail(index, 'order_quantity', val)}
        />
      )
    },
    {
      title: '单位',
      dataIndex: 'unit_id',
      key: 'unit_id',
      width: 80,
      render: (value, record, index) => {
        // 根据unit_id找到对应的单位名称
        const unitOption = unitOptions.find(opt => opt.value === value);
        const unitName = unitOption ? unitOption.label : record.unit || '';
        
        return (
          <Input
            value={unitName}
            placeholder="选择产品后自动填入"
            readOnly
            style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
          />
        );
      }
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          step={0.01}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'unit_price', val)}
        />
      )
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
      render: (value) => `¥${(value || 0).toLocaleString()}`
    },
    {
      title: '计划米数',
      dataIndex: 'planned_meters',
      key: 'planned_meters',
      width: 120,
       render: (value, record, index) => (
         <InputNumber
           style={{ 
             width: '100%',
             backgroundColor: value ? '#f0f8ff' : '#fff'
           }}
           min={0}
           step={1}
           value={value}
           onChange={(val) => {
             updateOrderDetail(index, 'planned_meters', val);
             // 如果手动修改了计划米数，自动计算计划重量
             if (val && val > 0) {
               const detail = orderDetails[index];
               const productData = detail.productData || null;
               const specification = detail.product_specification || null;
               const productParams = extractProductParams(productData);
               
               if (productParams && productParams.width && productParams.thickness && productParams.density) {
                 const plannedWeight = val * productParams.width * productParams.thickness * productParams.density / 1000000;
                 updateOrderDetail(index, 'planned_weight', plannedWeight);
               }
             }
           }}
           placeholder="自动计算"
         />
       )
     },
         {
       title: '计划重量(kg)',
       dataIndex: 'planned_weight',
       key: 'planned_weight',
       width: 120,
       render: (value, record, index) => (
         <InputNumber
           style={{ 
             width: '100%',
             backgroundColor: value ? '#f0f8ff' : '#fff'
           }}
           min={0}
           step={1}
           value={value}
           onChange={(val) => {
             updateOrderDetail(index, 'planned_weight', val);
             // 如果手动修改了计划重量，自动计算计划米数
             if (val && val > 0) {
               const detail = orderDetails[index];
               const productData = detail.productData || null;
               const specification = detail.product_specification || null;
               const productParams = extractProductParams(productData);
               
               if (productParams && productParams.width && productParams.thickness && productParams.density) {
                 const plannedMeters = val / (productParams.width * productParams.thickness * productParams.density / 1000000);
                 updateOrderDetail(index, 'planned_meters', plannedMeters);
               }
             }
           }}
           placeholder="自动计算"
         />
       )
     },
         {
       title: '电晕',
       dataIndex: 'corona',
       key: 'corona',
       width: 100,
       render: (value, record, index) => (
         <Input
           value={value}
           onChange={(e) => updateOrderDetail(index, 'corona', e.target.value)}
           placeholder="电晕"
         />
       )
     },
    {
      title: '可用库存',
      dataIndex: 'usable_inventory',
      key: 'usable_inventory',
      width: 150,
      render: (value, record, index) => (
        <Tooltip title="点击刷新库存">
          <InputNumber
            style={{ width: '100%' }}
            min={0}
            value={value}
            onChange={(val) => updateOrderDetail(index, 'usable_inventory', val)}
            addonAfter={
              <Button 
                type="link" 
                size="small" 
                icon={<ReloadOutlined />}
                onClick={() => loadInventoryForProduct(record.product_id, index)}
              />
            }
          />
        </Tooltip>
      )
    },
    {
      title: '负偏差%',
      dataIndex: 'negative_deviation_percentage',
      key: 'negative_deviation_percentage',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          max={100}
          step={0.01}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'negative_deviation_percentage', val)}
        />
      )
    },
    {
      title: '正偏差%',
      dataIndex: 'positive_deviation_percentage',
      key: 'positive_deviation_percentage',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          max={100}
          step={0.01}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'positive_deviation_percentage', val)}
        />
      )
    },
    {
      title: '生产最小数',
      dataIndex: 'production_small_quantity',
      key: 'production_small_quantity',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'production_small_quantity', val)}
        />
      )
    },
    {
      title: '生产最大数',
      dataIndex: 'production_large_quantity',
      key: 'production_large_quantity',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'production_large_quantity', val)}
        />
      )
    },
    {
      title: '赠送数',
      dataIndex: 'shipping_quantity',
      key: 'shipping_quantity',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'shipping_quantity', val)}
        />
      )
    },
    {
      title: '生产数',
      dataIndex: 'production_quantity',
      key: 'production_quantity',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'production_quantity', val)}
        />
      )
    },
    {
      title: '存库数',
      dataIndex: 'storage_quantity',
      key: 'storage_quantity',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'storage_quantity', val)}
        />
      )
    },
    {
      title: '预测厚M',
      dataIndex: 'estimated_thickness_m',
      key: 'estimated_thickness_m',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          step={0.01}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'estimated_thickness_m', val)}
        />
      )
    },
    {
      title: '预测厚kg',
      dataIndex: 'estimated_weight_kg',
      key: 'estimated_weight_kg',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          step={0.01}
          value={value}
          onChange={(val) => updateOrderDetail(index, 'estimated_weight_kg', val)}
        />
      )
    },
    {
      title: '客户代号',
      dataIndex: 'customer_code',
      key: 'customer_code',
      width: 120,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateOrderDetail(index, 'customer_code', e.target.value)}
          placeholder="客户代号"
        />
      )
    },
    {
      title: '客户要求',
      dataIndex: 'customer_requirements',
      key: 'customer_requirements',
      width: 150,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateOrderDetail(index, 'customer_requirements', e.target.value)}
          placeholder="客户要求"
        />
      )
    },
    {
      title: '材质结构',
      dataIndex: 'material_structure',
      key: 'material_structure',
      width: 150,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateOrderDetail(index, 'material_structure', e.target.value)}
          placeholder="材质结构"
        />
      )
    },
    {
      title: '印刷要求',
      dataIndex: 'printing_requirements',
      key: 'printing_requirements',
      width: 150,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateOrderDetail(index, 'printing_requirements', e.target.value)}
          placeholder="印刷要求"
        />
      )
    },
    {
      title: '内部交期',
      dataIndex: 'internal_delivery_date',
      key: 'internal_delivery_date',
      width: 140,
      render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
    },
    {
      title: '交货日期',
      dataIndex: 'delivery_date',
      key: 'delivery_date',
      width: 140,
      render: (value, record, index) => (
        <DatePicker
          style={{ width: 125, height: 32, borderRadius: 6, fontSize: 14, paddingLeft: 11, boxSizing: 'border-box' }}
          value={value ? dayjs(value) : null}
          onChange={date => updateOrderDetail(index, 'delivery_date', date ? date.format('YYYY-MM-DD') : null)}
          allowClear
          size="small"
          placeholder="请选择日期"
          inputReadOnly
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      fixed: 'right',
      render: (_, record, index) => (
        <Button 
          type="link" 
          danger 
          size="small"
          icon={<DeleteOutlined />}
          onClick={() => removeOrderDetail(index)}
        >
          删除
        </Button>
      )
    }
  ], [updateOrderDetail, removeOrderDetail, loadInventoryForProduct, productOptions, unitOptions]);

  // 缓存其他费用列定义
  const otherFeeColumns = useMemo(() => [
    {
      title: '费用类型',
      dataIndex: 'fee_type',
      key: 'fee_type',
      width: 120,
      render: (value, record, index) => (
        <Select
          style={{ width: '100%' }}
          placeholder="选择费用类型"
          value={value}
          onChange={(val) => updateOtherFee(index, 'fee_type', val)}
        >
          <Option value="版费">版费</Option>
          <Option value="模具费">模具费</Option>
          <Option value="包装费">包装费</Option>
          <Option value="运费">运费</Option>
          <Option value="其它">其它</Option>
          <Option value="改版费">改版费</Option>
          <Option value="免版费">免版费</Option>
        </Select>
      )
    },
    {
      title: '产品',
      dataIndex: 'product_id',
      key: 'product_id',
      width: 150,
      render: (value, record, index) => (
        <Select
          style={{ width: '100%' }}
          placeholder="选择产品"
          value={value}
          onChange={(val) => updateOtherFee(index, 'product_id', val)}
          allowClear
        >
          {productOptions.map(option => (
            <Option key={option.value} value={option.value}>
              {option.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: '版长',
      dataIndex: 'length',
      key: 'length',
      width: 80,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          step={0.001}
          value={value}
          onChange={(val) => updateOtherFee(index, 'length', val)}
        />
      )
    },
    {
      title: '版周',
      dataIndex: 'width',
      key: 'width',
      width: 80,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          step={0.001}
          value={value}
          onChange={(val) => updateOtherFee(index, 'width', val)}
        />
      )
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          step={0.01}
          value={value}
          onChange={(val) => updateOtherFee(index, 'price', val)}
        />
      )
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          onChange={(val) => updateOtherFee(index, 'quantity', val)}
        />
      )
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
      render: (value) => `¥${(value || 0).toLocaleString()}`
    },
    {
      title: '客户订单号',
      dataIndex: 'customer_order_number',
      key: 'customer_order_number',
      width: 120,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateOtherFee(index, 'customer_order_number', e.target.value)}
          placeholder="客户订单号"
        />
      )
    },
    {
      title: '备注',
      dataIndex: 'notes',
      key: 'notes',
      width: 150,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateOtherFee(index, 'notes', e.target.value)}
          placeholder="备注"
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      fixed: 'right',
      render: (_, record, index) => (
        <Button 
          type="link" 
          danger 
          size="small"
          icon={<DeleteOutlined />}
          onClick={() => removeOtherFee(index)}
        >
          删除
        </Button>
      )
    }
  ], [updateOtherFee, removeOtherFee, productOptions]);

  // 缓存材料列定义
  const materialColumns = useMemo(() => [
    {
      title: '材料',
      dataIndex: 'material_id',
      key: 'material_id',
      width: 200,
      render: (value, record, index) => (
        <Select
          style={{ width: '100%' }}
          placeholder="选择材料"
          value={value}
          onChange={(val) => updateMaterial(index, 'material_id', val)}
          showSearch
          optionFilterProp="children"
        >
          {materialOptions.map(option => (
            <Option key={option.value} value={option.value}>
              {option.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: '负偏差%',
      dataIndex: 'negative_deviation_percentage',
      key: 'negative_deviation_percentage',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          max={100}
          step={0.01}
          value={value}
          onChange={(val) => updateMaterial(index, 'negative_deviation_percentage', val)}
        />
      )
    },
    {
      title: '正偏差%',
      dataIndex: 'positive_deviation_percentage',
      key: 'positive_deviation_percentage',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          max={100}
          step={0.01}
          value={value}
          onChange={(val) => updateMaterial(index, 'positive_deviation_percentage', val)}
        />
      )
    },
    {
      title: '赠送数',
      dataIndex: 'gift_quantity',
      key: 'gift_quantity',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          onChange={(val) => updateMaterial(index, 'gift_quantity', val)}
        />
      )
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          placeholder="必填"
          onChange={(val) => updateMaterial(index, 'quantity', val)}
        />
      )
    },
    {
      title: '辅助数',
      dataIndex: 'auxiliary_quantity',
      key: 'auxiliary_quantity',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          value={value}
          onChange={(val) => updateMaterial(index, 'auxiliary_quantity', val)}
        />
      )
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (value, record, index) => (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          step={0.01}
          value={value}
          onChange={(val) => updateMaterial(index, 'price', val)}
        />
      )
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
      render: (value) => `¥${(value || 0).toLocaleString()}`
    },
    {
      title: '客户要求',
      dataIndex: 'customer_requirements',
      key: 'customer_requirements',
      width: 150,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateMaterial(index, 'customer_requirements', e.target.value)}
          placeholder="客户要求"
        />
      )
    },
    {
      title: '备注',
      dataIndex: 'notes',
      key: 'notes',
      width: 150,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateMaterial(index, 'notes', e.target.value)}
          placeholder="备注"
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      fixed: 'right',
      render: (_, record, index) => (
        <Button 
          type="link" 
          danger 
          size="small"
          icon={<DeleteOutlined />}
          onClick={() => removeMaterial(index)}
        >
          删除
        </Button>
      )
    }
  ], [updateMaterial, removeMaterial, materialOptions]);

  // 详情抽屉中使用的列定义
  const getDetailViewColumns = () => [
         {
       title: '产品名称',
       dataIndex: 'product_name',
       key: 'product_name',
       width: 200,
     },
     {
      title: '产品编号',
      dataIndex: 'product_code',
      key: 'product_code',
      width: 120,
    },
     {
       title: '产品规格',
       dataIndex: 'product_specification',
       key: 'product_specification',
       width: 150,
     },
    {
      title: '订单数量',
      dataIndex: 'order_quantity',
      key: 'order_quantity',
      width: 100,
    },
    {
      title: '单位',
      dataIndex: 'unit_id',
      key: 'unit_id',
      width: 80,
      render: (value, record) => {
        // 根据unit_id找到对应的单位名称
        const unitOption = unitOptions.find(opt => opt.value === value);
        return unitOption ? unitOption.label : record.unit || '-';
      }
    },
    {
      title: '计划米数',
      dataIndex: 'planned_meters',
      key: 'planned_meters',
      width: 120,
    },
    {
      title: '计划重量(kg)',
      dataIndex: 'planned_weight',
      key: 'planned_weight',
      width: 120,
    },
    {
      title: '电晕',
      dataIndex: 'corona',
      key: 'corona',
      width: 100,
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 100,
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
    },
    {
      title: '交货日期',
      dataIndex: 'delivery_date',
      key: 'delivery_date',
      width: 120,
      render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
    }
  ];

  const getFeeViewColumns = () => [
    {
      title: '费用类型',
      dataIndex: 'fee_type',
      key: 'fee_type',
      width: 120,
    },
    {
      title: '产品',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 150,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
    },
    {
      title: '备注',
      dataIndex: 'notes',
      key: 'notes',
      width: 150,
    }
  ];

  const getMaterialViewColumns = () => [
    {
      title: '材料',
      dataIndex: ['material', 'material_name'],
      key: 'material_name',
      width: 200,
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
    },
    {
      title: '备注',
      dataIndex: 'notes',
      key: 'notes',
      width: 150,
    }
  ];

  // 加载列配置
  const loadColumnConfig = async () => {
    try {
      // 加载列配置
      const configResponse = await columnConfigurationApi.getColumnConfig('salesOrder', 'column_config');
      if (configResponse.data.success && configResponse.data.data && configResponse.data.data.config_data) {
        setColumnConfig(configResponse.data.data.config_data);
      }
      
      // 加载列顺序
      const orderResponse = await columnConfigurationApi.getColumnConfig('salesOrder', 'column_order');
      if (orderResponse.data.success && orderResponse.data.data && orderResponse.data.data.config_data) {
        setColumnOrder(orderResponse.data.data.config_data);
        setColumnSettingOrder(orderResponse.data.data.config_data);
      }
    } catch (error) {
      console.error('加载列配置失败:', error);
    }
  };

  return (
    <PageContainer>
      {/* 搜索区域 */}
      <StyledCard>
        <Form form={searchForm} layout="inline">
          <Form.Item name="order_number" label="销售单号">
            <Input placeholder="请输入销售单号" style={{ width: 150 }} />
          </Form.Item>
          <Form.Item name="customer_id" label="客户名称">
            <Select placeholder="请选择客户" style={{ width: 200 }} allowClear>
              {customerOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="order_type" label="订单类型">
            <Select placeholder="请选择订单类型" style={{ width: 120 }} allowClear>
              <Option value="normal">正常订单</Option>
              <Option value="sample">打样订单</Option>
              <Option value="stock_check">查库订单</Option>
              <Option value="plate_fee">版费订单</Option>
              <Option value="urgent">加急订单</Option>
              <Option value="stock">备货订单</Option>
            </Select>
          </Form.Item>
          <Form.Item name="status" label="状态">
            <Select placeholder="请选择状态" style={{ width: 120 }} allowClear>
              <Option value="draft">草稿</Option>
              <Option value="confirmed">已确认</Option>
              <Option value="production">生产中</Option>
              <Option value="shipped">已发货</Option>
              <Option value="completed">已完成</Option>
              <Option value="cancelled">已取消</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
            <Button style={{ marginLeft: 8 }} icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
          </Form.Item>
        </Form>
      </StyledCard>

      {/* 操作区域 */}
      <StyledCard>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增订单
            </Button>
            {checkUserPermission('field_manage') && (
              <Button 
                icon={<SettingOutlined />} 
                onClick={() => setFieldManagerVisible(true)}
              >
                自定义字段
              </Button>
            )}
            <Button 
              icon={<SettingOutlined />} 
              onClick={() => setColumnSettingVisible(true)}
              className="column-setting-button"
            >
              字段设置
            </Button>
          </Space>
          
          {columnSettingVisible && (
            <div 
              className="column-setting-panel"
              style={{ 
                position: 'absolute', 
                top: '100%', 
                right: 0, 
                zIndex: 1000,
                backgroundColor: 'white',
                border: '1px solid #d9d9d9',
                borderRadius: '6px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                padding: '16px',
                minWidth: '400px',
                maxHeight: '80vh',
                overflowY: 'auto'
              }}>
              <ColumnSettings
                fieldConfig={fieldConfig}
                dynamicFields={dynamicFields}
                fieldGroups={fieldGroups}
                columnConfig={columnConfig}
                columnSettingOrder={columnSettingOrder}
                onConfigChange={(config) => {
                  setColumnConfig(config);
                }}
                onSave={saveColumnConfig}
                onReset={() => {
                  setColumnConfig({});
                  setColumnSettingOrder([]);
                  message.success('已重置为默认设置');
                }}
                onOrderChange={handleColumnOrderChange}
                isAdmin={isAdmin}
              />
              <div style={{ textAlign: 'center', marginTop: '16px' }}>
                <Button onClick={() => setColumnSettingVisible(false)}>
                  关闭
                </Button>
              </div>
            </div>
          )}
        </div>
      </StyledCard>

      {/* 表格区域 */}
      <StyledCard>
        <Table
          key={tableKey}
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 3500 }}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
          onChange={handleTableChange}
        />
      </StyledCard>

      {/* 新增/编辑模态框 */}
      <Modal
        title={currentRecord ? '编辑销售订单' : '新增销售订单'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={1400}
        okText="保存"
        cancelText="取消"
        style={{ top: 20 }}
      >
        <Tabs
          activeKey={activeTab}
          onChange={handleTabChange}
        >
          <TabPane tab="基本信息" key="base">
            <Form form={form} layout="vertical">
              {/* 动态渲染表单字段，按列设置顺序排列 */}
              {(() => {
                const orderedFields = getOrderedVisibleFormFields();
                const rows = [];
                let currentRow = [];
                
                orderedFields.forEach((fieldName, index) => {
                  const fieldElement = renderFormField(fieldName);
                  if (fieldElement) {
                    currentRow.push(fieldElement);
                    
                    // 每6个字段换一行，或者遇到特殊字段
                    if (currentRow.length === 6 || fieldName === 'delivery_address' || 
                        fieldName === 'production_requirements' || fieldName === 'order_requirements') {
                      rows.push(
                        <Row gutter={16} key={`row-${rows.length}`}>
                          {currentRow}
                        </Row>
                      );
                      currentRow = [];
                    }
                  }
                });
                
                // 处理最后一行
                if (currentRow.length > 0) {
                  rows.push(
                    <Row gutter={16} key={`row-${rows.length}`}>
                      {currentRow}
                    </Row>
                  );
                }
                
                return rows;
              })()}
            </Form>
          </TabPane>
          
          <TabPane tab="订单明细" key="details">
            <div style={{ marginBottom: 16 }}>
              <Button type="dashed" onClick={addOrderDetail} icon={<PlusOutlined />}>
                添加明细
              </Button>
            </div>
            <Table
              columns={orderDetailColumns}
              dataSource={orderDetails}
              rowKey="id"
              pagination={false}
              size="small"
              scroll={{ x: 2400 }}
            />
          </TabPane>

          <TabPane tab="其他费用" key="fees">
            <div style={{ marginBottom: 16 }}>
              <Button type="dashed" onClick={addOtherFee} icon={<PlusOutlined />}>
                添加费用
              </Button>
            </div>
            <Table
              columns={otherFeeColumns}
              dataSource={otherFees}
              rowKey="id"
              pagination={false}
              size="small"
              scroll={{ x: 1200 }}
            />
          </TabPane>

          <TabPane tab="销售材料" key="materials">
            <div style={{ marginBottom: 16 }}>
              <Button type="dashed" onClick={addMaterial} icon={<PlusOutlined />}>
                添加材料
              </Button>
            </div>
            <Table
              columns={materialColumns}
              dataSource={materials}
              rowKey="id"
              pagination={false}
              size="small"
              scroll={{ x: 1200 }}
            />
          </TabPane>
        </Tabs>
      </Modal>

      {/* 详情抽屉 */}
      <Drawer
        title="销售订单详情"
        placement="right"
        onClose={() => setDetailDrawerVisible(false)}
        open={detailDrawerVisible}
        width={1200}
      >
        {currentRecord && (
          <div>
            <Title level={4}>订单基本信息</Title>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Text strong>订单号：</Text>
                <Text>{currentRecord.order_number}</Text>
              </Col>
              <Col span={12}>
                <Text strong>订单类型：</Text>
                <Text>{orderTypeConfig[currentRecord.order_type] || currentRecord.order_type}</Text>
              </Col>
              <Col span={12}>
                <Text strong>客户名称：</Text>
                <Text>{currentRecord.customer?.customer_name || currentRecord.customer_name || '-'}</Text>
              </Col>
              <Col span={12}>
                <Text strong>客户订单号：</Text>
                <Text>{currentRecord.customer_order_number || '-'}</Text>
              </Col>
              <Col span={12}>
                <Text strong>交货日期：</Text>
                <Text>{currentRecord.delivery_date ? dayjs(currentRecord.delivery_date).format('YYYY-MM-DD') : '-'}</Text>
              </Col>
              <Col span={12}>
                <Text strong>内部交期：</Text>
                <Text>{currentRecord.internal_delivery_date ? dayjs(currentRecord.internal_delivery_date).format('YYYY-MM-DD') : '-'}</Text>
              </Col>
              <Col span={12}>
                <Text strong>订单金额：</Text>
                <Text>¥{currentRecord.order_amount?.toLocaleString() || 0}</Text>
              </Col>
              <Col span={12}>
                <Text strong>状态：</Text>
                <Tag color={statusConfig[currentRecord.status]?.color}>
                  {statusConfig[currentRecord.status]?.text}
                </Tag>
              </Col>
            </Row>
            <Divider />
            <Title level={5}>交货地址</Title>
            <Text>{currentRecord.delivery_address || '-'}</Text>
            {currentRecord.production_requirements && (
              <>
                <Divider />
                <Title level={5}>生产要求</Title>
                <Text>{currentRecord.production_requirements}</Text>
              </>
            )}
            {currentRecord.order_requirements && (
              <>
                <Divider />
                <Title level={5}>订单要求</Title>
                <Text>{currentRecord.order_requirements}</Text>
              </>
            )}

            {/* 订单明细 */}
            {currentRecord.order_details && currentRecord.order_details.length > 0 && (
              <>
                <Divider />
                <Title level={5}>订单明细 ({currentRecord.order_details.length}条)</Title>
                <Table
                  columns={getDetailViewColumns()}
                  dataSource={currentRecord.order_details}
                  rowKey="id"
                  pagination={false}
                  size="small"
                  scroll={{ x: 800 }}
                />
              </>
            )}

            {/* 其他费用 */}
            {currentRecord.other_fees && currentRecord.other_fees.length > 0 && (
              <>
                <Divider />
                <Title level={5}>其他费用 ({currentRecord.other_fees.length}条)</Title>
                <Table
                  columns={getFeeViewColumns()}
                  dataSource={currentRecord.other_fees}
                  rowKey="id"
                  pagination={false}
                  size="small"
                  scroll={{ x: 800 }}
                />
              </>
            )}

            {/* 材料明细 */}
            {currentRecord.material_details && currentRecord.material_details.length > 0 && (
              <>
                <Divider />
                <Title level={5}>材料明细 ({currentRecord.material_details.length}条)</Title>
                <Table
                  columns={getMaterialViewColumns()}
                  dataSource={currentRecord.material_details}
                  rowKey="id"
                  pagination={false}
                  size="small"
                  scroll={{ x: 800 }}
                />
              </>
            )}
          </div>
        )}
      </Drawer>

      {/* 动态字段管理模态框 */}
      <FieldManager
        visible={fieldManagerVisible}
        onCancel={() => setFieldManagerVisible(false)}
        modelName="sales_order"
        pageName="sales_order"
        onSuccess={() => {
          setFieldManagerVisible(false);
          loadDynamicFields();
        }}
      />
    </PageContainer>
  );
};

export default SalesOrder; 