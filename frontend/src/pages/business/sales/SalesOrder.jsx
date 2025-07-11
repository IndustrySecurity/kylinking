import React, { useState, useEffect, useCallback } from 'react';
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
  CalculatorOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import dayjs from 'dayjs';
import salesOrderService from '../../../api/business/sales/salesOrder';

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
    pageSize: 20,
    total: 0
  });

  // 选项数据
  const [customerOptions, setCustomerOptions] = useState([]);
  const [productOptions, setProductOptions] = useState([]);
  const [materialOptions, setMaterialOptions] = useState([]);
  const [taxOptions, setTaxOptions] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [contactOptions, setContactOptions] = useState([]);

  // 子表数据
  const [orderDetails, setOrderDetails] = useState([]);
  const [otherFees, setOtherFees] = useState([]);
  const [materials, setMaterials] = useState([]);

  const [activeTab, setActiveTab] = useState('base');

  useEffect(() => {
    fetchData();
    fetchOptions();
  }, []);

  useEffect(() => {
    if (modalVisible) {
      setActiveTab('base');
    }
  }, [modalVisible]);

  const fetchData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await salesOrderService.getSalesOrders({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...params
      });

      if (response.data.success) {
        setData(response.data.data.orders || []);
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
      const [customerRes, productRes, materialRes, taxRes, employeeRes] = await Promise.all([
        salesOrderService.getCustomerOptions(),
        salesOrderService.getProductOptions(),
        salesOrderService.getMaterialOptions(),
        salesOrderService.getTaxOptions(),
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
      order_date: dayjs(),
      delivery_date: dayjs(),
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
    setCurrentRecord(record);
    try {
      const response = await salesOrderService.getSalesOrderById(record.id);
      if (response.data.success) {
        const orderData = response.data.data;
        
        // 先设置基本字段（不包括联系人相关字段）
        const basicFields = {
          ...orderData,
          order_date: orderData.order_date ? dayjs(orderData.order_date) : null,
          delivery_date: orderData.order_date ? dayjs(orderData.order_date) : dayjs(), // 使用order_date作为delivery_date
          internal_delivery_date: orderData.internal_delivery_date ? dayjs(orderData.internal_delivery_date) : null,
          contract_date: orderData.contract_date ? dayjs(orderData.contract_date) : null,
          // 映射税收字段名
          tax_id: orderData.tax_type_id
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
                basicFields.contact_phone = currentContact.mobile || '';
                basicFields.contact_mobile = currentContact.mobile || '';
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

  const handleDelete = async (record) => {
    try {
      const response = await salesOrderService.deleteSalesOrder(record.id);
      if (response.data.success) {
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
      const orderData = {
        ...values,
        order_date: values.order_date ? values.order_date.format('YYYY-MM-DD') : null,
        delivery_date: values.delivery_date ? values.delivery_date.format('YYYY-MM-DD') : null,
        internal_delivery_date: values.internal_delivery_date ? values.internal_delivery_date.format('YYYY-MM-DD') : null,
        contract_date: values.contract_date ? values.contract_date.format('YYYY-MM-DD') : null,
        order_details: orderDetails,
        other_fees: otherFees,
        material_details: materials,
        // 映射税收字段名
        tax_type_id: values.tax_id
      };

      let response;
      if (currentRecord) {
        response = await salesOrderService.updateSalesOrder(currentRecord.id, orderData);
      } else {
        response = await salesOrderService.createSalesOrder(orderData);
      }

      if (response.data.success) {
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

  const handleViewDetail = (record) => {
    setCurrentRecord(record);
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

  // 处理税收选择变化
  const handleTaxChange = (value) => {
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
  };

  // 处理客户选择变化，自动加载客户信息
  const handleCustomerChange = async (customerId) => {
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
              contact_phone: firstContact.mobile,
              contact_mobile: firstContact.mobile,
              contact_method: firstContact.mobile
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
  };

  // 处理交货日期变化，自动设置内部交期为前一天
  const handleDeliveryDateChange = (date) => {
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
  };

  // 处理联系人选择变化，自动填充联系人信息
  const handleContactChange = (contactId) => {
    if (contactId) {
      const selectedContact = contactOptions.find(option => option.value === contactId);
      if (selectedContact) {
        form.setFieldsValue({
          phone: selectedContact.phone,
          mobile: selectedContact.mobile
        });
      }
    } else {
      // 清空联系人相关信息
      form.setFieldsValue({
        phone: '',
        mobile: ''
      });
    }
  };

  const handleTabChange = (key) => {
    if (['details', 'fees', 'materials'].includes(key)) {
      const deliveryDate = form.getFieldValue('delivery_date');
      if (!deliveryDate) {
        message.warning('请先填写交货日期！');
        return;
      }
    }
    setActiveTab(key);
  };

  const addOrderDetail = () => {
    const deliveryDate = form.getFieldValue('delivery_date');
    const internalDeliveryDate = form.getFieldValue('internal_delivery_date');
    setOrderDetails([
      ...orderDetails,
      {
        id: Date.now(),
        product_id: null,
        product_code: '',
        product_name: '',
        order_quantity: 0,
        unit_price: 0,
        amount: 0,
        unit: '',
        negative_deviation_percentage: 0,
        positive_deviation_percentage: 0,
        production_small_quantity: 0,
        production_large_quantity: 0,
        shipping_quantity: 0,
        production_quantity: 0,
        usable_inventory: 0,
        storage_quantity: 0,
        estimated_thickness_m: 0,
        estimated_weight_kg: 0,
        customer_code: '',
        customer_requirements: '',
        material_structure: '',
        printing_requirements: '',
        internal_delivery_date: internalDeliveryDate || null,
        delivery_date: deliveryDate || null
      }
    ]);
  };

  // 删除订单明细
  const removeOrderDetail = (index) => {
    const newDetails = orderDetails.filter((_, i) => i !== index);
    setOrderDetails(newDetails);
  };

  // 更新订单明细
  const updateOrderDetail = async (index, field, value) => {
    const newDetails = [...orderDetails];
    newDetails[index][field] = value;
    
    // 自动计算金额
    if (field === 'order_quantity' || field === 'unit_price') {
      newDetails[index].amount = (newDetails[index].order_quantity || 0) * (newDetails[index].unit_price || 0);
    }
    
    // 根据产品选择自动填充信息
    if (field === 'product_id' && value) {
      try {
        // 从产品详情API获取完整的产品信息
        const response = await salesOrderService.getProductDetails(value);
        if (response.data.success) {
          const productData = response.data.data;
          
          // 自动填充产品相关字段
          newDetails[index] = {
            ...newDetails[index],
            // 基本产品信息
            product_code: productData.product_code,
            product_name: productData.product_name,
            unit: productData.unit,
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
            tax_type_id: productData.tax_type_id
          };
          
          // 重新计算金额
          const quantity = newDetails[index].order_quantity || 0;
          const price = newDetails[index].unit_price || 0;
          newDetails[index].amount = quantity * price;
          
          // 尝试同时获取库存信息，合并到一次状态更新中
          try {
            const inventoryResponse = await salesOrderService.getProductInventory(value);
            if (inventoryResponse.data.success) {
              const inventory = inventoryResponse.data.data;
              newDetails[index].usable_inventory = inventory.available_quantity || 0;
            }
          } catch (error) {
            console.error('获取库存信息失败:', error);
            // 库存获取失败不影响产品信息填充
          }
          
          // 一次性更新所有数据，避免多次渲染
          setOrderDetails([...newDetails]);
          message.success('产品信息已自动填充');
          return; // 提前返回，避免执行后面的setOrderDetails
        }
      } catch (error) {
        console.error('获取产品详情失败:', error);
        message.error('获取产品详情失败');
        
        // 回退到基本的产品选项信息
        const product = productOptions.find(p => p.value === value);
        if (product) {
          newDetails[index].product_name = product.product_name || product.label?.split(' - ')[1];
          newDetails[index].product_code = product.product_code || product.label?.split(' - ')[0];
          newDetails[index].unit = product.unit || product.unit_name;
          
          if (product.specification) {
            newDetails[index].material_structure = product.specification;
          }
          if (product.unit_price) {
            newDetails[index].unit_price = product.unit_price;
          }
        }
      }
      
      // 对于产品选择的错误情况，也尝试加载库存信息
      try {
        const inventoryResponse = await salesOrderService.getProductInventory(value);
        if (inventoryResponse.data.success) {
          const inventory = inventoryResponse.data.data;
          newDetails[index].usable_inventory = inventory.available_quantity || 0;
        }
      } catch (error) {
        console.error('获取库存信息失败:', error);
      }
    }
    
    setOrderDetails(newDetails);
  };

  // 加载产品库存信息
  const loadInventoryForProduct = async (productId, index, existingDetails = null) => {
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
  };

  // 添加其他费用
  const addOtherFee = () => {
    setOtherFees([...otherFees, {
      id: Date.now(),
      fee_type: '',
      product_id: null,
      product_name: '',
      length: 0,
      width: 0,
      price: 0,
      quantity: 1,
      amount: 0,
      customer_order_number: '',
      customer_code: '',
      delivery_date: null,
      internal_delivery_date: null,
      customer_requirements: '',
      notes: ''
    }]);
  };

  // 删除其他费用
  const removeOtherFee = (index) => {
    const newFees = otherFees.filter((_, i) => i !== index);
    setOtherFees(newFees);
  };

  // 更新其他费用
  const updateOtherFee = (index, field, value) => {
    const newFees = [...otherFees];
    newFees[index][field] = value;
    
    if (field === 'price' || field === 'quantity') {
      newFees[index].amount = newFees[index].price * newFees[index].quantity;
    }
    
    setOtherFees(newFees);
  };

  // 添加销售材料
  const addMaterial = () => {
    setMaterials([...materials, {
      id: Date.now(),
      material_id: null,
      negative_deviation_percentage: 0,
      positive_deviation_percentage: 0,
      gift_quantity: 0,
      quantity: 0,
      auxiliary_quantity: 0,
      price: 0,
      amount: 0,
      delivery_date: null,
      internal_delivery_date: null,
      customer_requirements: '',
      notes: ''
    }]);
  };

  // 删除销售材料
  const removeMaterial = (index) => {
    const newMaterials = materials.filter((_, i) => i !== index);
    setMaterials(newMaterials);
  };

  // 更新销售材料
  const updateMaterial = (index, field, value) => {
    const newMaterials = [...materials];
    newMaterials[index][field] = value;
    
    if (field === 'price' || field === 'quantity') {
      newMaterials[index].amount = newMaterials[index].price * newMaterials[index].quantity;
    }
    
    setMaterials(newMaterials);
  };

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

  const columns = [
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
      key: 'customer_name',
      width: 150
    },
    {
      title: '客户订单号',
      dataIndex: 'customer_order_number',
      key: 'customer_order_number',
      width: 120
    },
    {
      title: '联系人',
      dataIndex: 'contact_person',
      key: 'contact_person',
      width: 100
    },
    {
      title: '税收',
      dataIndex: 'tax_name',
      key: 'tax_name',
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
      key: 'deposit_percentage',
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
      title: '交货日期',
      dataIndex: 'delivery_date',
      key: 'delivery_date',
      width: 120,
      render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
    },
    {
      title: '客户简称',
      dataIndex: 'customer_short_name',
      key: 'customer_short_name',
      width: 100
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
      render: (amount) => `¥${amount?.toFixed(2) || '0.00'}`
    },
    {
      title: '版费订金',
      dataIndex: 'plate_deposit',
      key: 'plate_deposit',
      width: 100,
      render: (amount) => `¥${amount?.toFixed(2) || '0.00'}`
    },
    {
      title: '内部交期',
      dataIndex: 'internal_delivery_date',
      key: 'internal_delivery_date',
      width: 140,
      render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
    },
    {
      title: '业务员',
      dataIndex: 'salesperson_name',
      key: 'salesperson_name',
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
      key: 'tracking_person_name',
      width: 100
    },
    {
      title: '归属公司',
      dataIndex: 'company_name',
      key: 'company_name',
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
      title: '送货地址',
      dataIndex: 'delivery_address',
      key: 'delivery_address',
      width: 200
    },
    {
      title: '生产要求',
      dataIndex: 'production_requirements',
      key: 'production_requirements',
      width: 150,
      ellipsis: true
    },
    {
      title: '订单要求',
      dataIndex: 'order_requirements',
      key: 'order_requirements',
      width: 150,
      ellipsis: true
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          {record.status === 'draft' && (
            <>
              <Button 
                type="link" 
                size="small" 
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定要删除这条记录吗？"
                onConfirm={() => handleDelete(record)}
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
            </>
          )}
        </Space>
      )
    }
  ];

  // 订单明细表格列
  const getOrderDetailColumns = () => [
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
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 150,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateOrderDetail(index, 'product_name', e.target.value)}
          placeholder="产品名称"
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
          onChange={(val) => updateOrderDetail(index, 'order_quantity', val)}
        />
      )
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
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 80,
      render: (value, record, index) => (
        <Input
          value={value}
          onChange={(e) => updateOrderDetail(index, 'unit', e.target.value)}
          placeholder="单位"
        />
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
      title: '可用库存',
      dataIndex: 'usable_inventory',
      key: 'usable_inventory',
      width: 100,
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
  ];

  // 其他费用表格列
  const getOtherFeeColumns = () => [
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
  ];

  // 销售材料表格列
  const getMaterialColumns = () => [
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
  ];

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
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增订单
          </Button>
        </Space>
      </StyledCard>

      {/* 表格区域 */}
      <StyledCard>
        <Table
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
              {/* 第一行：基本订单信息 */}
              <Row gutter={16}>
                <Col span={4}>
                  <Form.Item name="order_number" label="销售单号">
                    <Input placeholder="自动生成" disabled />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="customer_id" label="客户名称" rules={[{ required: true, message: '请选择客户' }]}>
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
                <Col span={4}>
                  <Form.Item name="customer_order_number" label="客户订单号">
                    <Input placeholder="客户订单号" />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="contact_person_id" label="联系人">
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
                <Col span={4}>
                  <Form.Item name="tax_id" label="税收">
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
                <Col span={4}>
                  <Form.Item name="tax_rate" label="税率">
                    <InputNumber style={{ width: '100%' }} min={0} step={0.01} placeholder="0" disabled addonAfter="%" />
                  </Form.Item>
                </Col>
              </Row>

              {/* 第二行：订单类型和客户信息 */}
              <Row gutter={16}>
                <Col span={4}>
                  <Form.Item name="order_type" label="订单类型" rules={[{ required: true, message: '请选择订单类型' }]}>
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
                <Col span={4}>
                  <Form.Item name="customer_code" label="客户编号">
                    <Input placeholder="客户编号" />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="payment_method" label="付款方式">
                    <Input placeholder="付款方式" />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="phone" label="电话">
                    <Input placeholder="电话" />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="deposit" label="订金">
                    <InputNumber style={{ width: '100%' }} min={0} max={100} step={0.01} placeholder="0" addonAfter="%" />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="plate_deposit_rate" label="版费订金%">
                    <InputNumber style={{ width: '100%' }} min={0} max={100} step={0.01} placeholder="0" addonAfter="%" />
                  </Form.Item>
                </Col>
              </Row>

              {/* 第三行：日期和送货信息 */}
              <Row gutter={16}>
                <Col span={4}>
                  <Form.Item name="delivery_date" label="交货日期" rules={[{ required: true, message: '请选择交货日期' }]}>
                    <DatePicker 
                      style={{ width: '100%' }} 
                      onChange={handleDeliveryDateChange}
                    />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="customer_short_name" label="客户简称">
                    <Input placeholder="客户简称" />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="delivery_method" label="送货方式">
                    <Input placeholder="送货方式" />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="mobile" label="手机">
                    <Input placeholder="手机" />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="deposit_amount" label="订金">
                    <InputNumber style={{ width: '100%' }} min={0} step={0.01} placeholder="0" />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="plate_deposit" label="版费订金">
                    <InputNumber style={{ width: '100%' }} min={0} step={0.01} placeholder="0" />
                  </Form.Item>
                </Col>
              </Row>

              {/* 第四行：交期和业务信息 */}
              <Row gutter={16}>
                <Col span={4}>
                  <Form.Item name="internal_delivery_date" label="内部交期">
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="salesperson_id" label="业务员">
                  <Select placeholder="请选择业务员" allowClear>
                  {employees.map((employee, index) => (
                    <Option key={employee.id || `sales-employee-${index}`} value={employee.id}>
                      {employee.employee_name || employee.name || employee.label}
                    </Option>
                  ))}
                </Select>
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="contract_date" label="合同日期">
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="contact_method" label="联系方式">
                    <Select placeholder="请选择联系方式" allowClear>
                      <Option value="phone">电话</Option>
                      <Option value="email">邮件</Option>
                      <Option value="fax">传真</Option>
                      <Option value="wechat">微信</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="tracking_person" label="跟单员">
                    <Select placeholder="请选择跟单员" allowClear showSearch optionFilterProp="children">
                    {employees.map((employee, index) => (
                    <Option key={employee.id || `sales-employee-${index}`} value={employee.id}>
                      {employee.employee_name || employee.name || employee.label}
                    </Option>
                  ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item name="company_id" label="归属公司">
                    <Select placeholder="请选择归属公司" allowClear>
                      {/* TODO: 添加公司选项 */}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              {/* 第五行：物流和地址信息 */}
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="logistics_info" label="物流信息">
                    <Select placeholder="请选择物流信息" allowClear>
                      {/* TODO: 添加物流选项 */}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="delivery_contact" label="送货联系人">
                    <Input placeholder="送货联系人" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="status" label="状态">
                    <Select placeholder="请选择状态" defaultValue="draft">
                      <Option value="draft">草稿</Option>
                      <Option value="confirmed">已确认</Option>
                      <Option value="production">生产中</Option>
                      <Option value="shipped">已发货</Option>
                      <Option value="completed">已完成</Option>
                      <Option value="cancelled">已取消</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              {/* 第六行：地址信息 */}
              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item name="delivery_address" label="送货地址">
                    <Input placeholder="请输入送货地址" />
                  </Form.Item>
                </Col>
              </Row>

              {/* 第七行：要求信息 */}
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="production_requirements" label="生产要求">
                    <TextArea rows={2} placeholder="请输入生产要求" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="order_requirements" label="订单要求">
                    <TextArea rows={2} placeholder="请输入订单要求" />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </TabPane>
          
          <TabPane tab="订单明细" key="details">
            <div style={{ marginBottom: 16 }}>
              <Button type="dashed" onClick={addOrderDetail} icon={<PlusOutlined />}>
                添加明细
              </Button>
            </div>
            <Table
              columns={getOrderDetailColumns()}
              dataSource={orderDetails}
              rowKey={(record, index) => record.id || `detail-${index}`}
              pagination={false}
              size="small"
              scroll={{ x: 2400 }}
              components={{
                body: {
                  cell: ({ children, ...restProps }) => (
                    <td {...restProps} style={{ ...restProps.style, verticalAlign: 'top' }}>
                      {children}
                    </td>
                  )
                }
              }}
            />
          </TabPane>

          <TabPane tab="其他费用" key="fees">
            <div style={{ marginBottom: 16 }}>
              <Button type="dashed" onClick={addOtherFee} icon={<PlusOutlined />}>
                添加费用
              </Button>
            </div>
            <Table
              columns={getOtherFeeColumns()}
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
              columns={getMaterialColumns()}
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
        width={900}
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
                <Text>{currentRecord.customer_name}</Text>
              </Col>
              <Col span={12}>
                <Text strong>客户订单号：</Text>
                <Text>{currentRecord.customer_order_number || '-'}</Text>
              </Col>
              <Col span={12}>
                <Text strong>订单日期：</Text>
                <Text>{currentRecord.order_date ? dayjs(currentRecord.order_date).format('YYYY-MM-DD') : '-'}</Text>
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
          </div>
        )}
      </Drawer>
    </PageContainer>
  );
};

export default SalesOrder; 