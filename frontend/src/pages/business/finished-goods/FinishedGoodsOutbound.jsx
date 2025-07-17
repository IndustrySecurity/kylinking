import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Select, 
  DatePicker, 
  InputNumber, 
  Space, 
  Card, 
  Row, 
  Col, 
  Tabs, 
  Tag, 
  Popconfirm, 
  message,
  Divider,
  Typography,
  Checkbox,
  Collapse
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  EyeOutlined,
  CheckOutlined,
  CloseOutlined,
  PlayCircleOutlined,
  FileTextOutlined,
  SearchOutlined,
  ReloadOutlined,
  FilterOutlined,
  ImportOutlined,
  ExportOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import { finishedGoodsOutboundService, baseDataService } from '../../../api/business/inventory/finishedGoodsOutbound';

// 扩展dayjs插件
dayjs.extend(utc);
dayjs.extend(timezone);

const { Option } = Select;
const { TextArea } = Input;
const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Panel } = Collapse;
const { RangePicker } = DatePicker;

// 样式组件
const PageContainer = styled.div`
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;
`;

const StyledCard = styled(Card)`
  margin-bottom: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02);
  
  .ant-card-head {
    background: #fff;
    border-bottom: 1px solid #f0f0f0;
    
    .ant-card-head-title {
      color: #262626;
      font-weight: 500;
      font-size: 16px;
    }
  }
  
  .ant-card-body {
    padding: 24px;
  }
`;

const ActionButton = styled(Button)`
  margin-right: 8px;
  margin-bottom: 8px;
`;

const StatusTag = styled(Tag)`
  margin-right: 8px;
  border-radius: 4px;
`;

const DetailTable = styled(Table)`
  .ant-table-thead > tr > th {
    background: #fafafa;
    font-weight: 500;
    color: #262626;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .ant-table-tbody > tr > td {
    border-bottom: 1px solid #f0f0f0;
  }
  
  .ant-table-tbody > tr:hover > td {
    background: #fafafa;
  }
`;


const FinishedGoodsOutbound = () => {
  // 状态管理
  const [outboundOrders, setOutboundOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false); // 查看出库单详情模态框
  const [currentOrder, setCurrentOrder] = useState(null);
  const [orderDetails, setOrderDetails] = useState([]);
  const [detailModalVisible2, setDetailModalVisible2] = useState(false);
  const [currentDetail, setCurrentDetail] = useState(null);
  const [productSelectVisible, setProductSelectVisible] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [productSearchText, setProductSearchText] = useState('');
  const [isViewMode, setIsViewMode] = useState(false); // 标识是否为查看模式
  const [form] = Form.useForm();
  const [detailForm] = Form.useForm();
  const [searchForm] = Form.useForm();

  // 基础数据状态
  const [warehouses, setWarehouses] = useState([]);
  const [products, setProducts] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [units, setUnits] = useState([]);
  // 分页和筛选状态
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [filters, setFilters] = useState({});
  const [searchParams, setSearchParams] = useState({});

  // 初始化数据
  useEffect(() => {
    fetchOutboundOrders();
    fetchBaseData();
  }, []);

  // 监听分页和筛选条件变化
  useEffect(() => {
    fetchOutboundOrders();
  }, [pagination.current, pagination.pageSize, filters, searchParams]);

  // 搜索功能
  const handleSearch = (values) => {
    const params = {
      ...values,
      start_date: values.date_range?.[0]?.format('YYYY-MM-DD'),
      end_date: values.date_range?.[1]?.format('YYYY-MM-DD')
    };
    delete params.date_range;
    setSearchParams(params);
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleReset = () => {
    searchForm.resetFields();
    setSearchParams({});
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleRefresh = () => {
    fetchOutboundOrders();
  };

  // 获取基础数据
  const fetchBaseData = async () => {
    try {
      const [warehousesRes, productsRes, departmentsRes, employeesRes, customersRes, unitsRes] = await Promise.all([
        baseDataService.getWarehouses(),
        baseDataService.getProducts(),
        baseDataService.getDepartments(),
        baseDataService.getEmployees(),
        baseDataService.getCustomers(),
        baseDataService.getUnits()
      ]);

      // 处理仓库数据 - 选项API返回格式 {value, label, code}
      if (warehousesRes.data?.success) {
        const warehouseData = warehousesRes.data.data;
        const warehouses = Array.isArray(warehouseData) ? warehouseData.map(item => ({
          id: item.value,
          warehouse_name: item.label,
          warehouse_code: item.code
        })) : [];
        setWarehouses(warehouses);
      } else {
        setWarehouses([]);
      }

      // 处理产品数据 - 列表API返回格式
      if (productsRes.data?.success) {
        const productData = productsRes.data.data;
        let products = [];
        if (Array.isArray(productData)) {
          products = productData;
        } else if (productData?.products && Array.isArray(productData.products)) {
          products = productData.products;
        } else if (productData?.items && Array.isArray(productData.items)) {
          products = productData.items;
        } else if (productData?.data && Array.isArray(productData.data)) {
          products = productData.data;
        }
        setProducts(products);
      } else {
        setProducts([]);
      }

      // 处理部门数据 - 选项API返回格式 {value, label, code}
      if (departmentsRes.data?.success) {
        const departmentData = departmentsRes.data.data;
        const departments = Array.isArray(departmentData) ? departmentData.map(item => ({
          id: item.value,
          department_name: item.label,
          department_code: item.code
        })) : [];
        setDepartments(departments);
      } else {
        setDepartments([]);
      }

      // 处理员工数据 - 特殊格式 {success: true, data: [{id, employee_name, ...}]}
      if (employeesRes.data?.success) {
        const employeeData = employeesRes.data.data;
        setEmployees(Array.isArray(employeeData) ? employeeData : []);
      } else {
        setEmployees([]);
      }

      // 处理客户数据
      if (customersRes.data?.success) {
        const customerData = customersRes.data.data;
        let customers = [];
        if (Array.isArray(customerData)) {
          customers = customerData;
        } else if (customerData?.customers && Array.isArray(customerData.customers)) {
          customers = customerData.customers;
        } else if (customerData?.items && Array.isArray(customerData.items)) {
          customers = customerData.items;
        } else if (customerData?.data && Array.isArray(customerData.data)) {
          customers = customerData.data;
        }
        setCustomers(customers);
      } else {
        console.error('客户数据加载失败:', customersRes.data);
        setCustomers([]);
      }

      // 处理单位数据
      if (unitsRes.data?.success) {
        const unitData = unitsRes.data.data;
        setUnits(unitData);
      } else {
        setUnits([]);
      }
    } catch (error) {
      message.error('获取基础数据失败，请检查网络连接');
      // 设置空数组，不使用模拟数据
      setWarehouses([]);
      setProducts([]);
      setDepartments([]);
      setEmployees([]);
      setCustomers([]);
      setUnits([]);
    }
  };

  const fetchOutboundOrders = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.current,
        page_size: pagination.pageSize,
        ...filters,
        ...searchParams
      };
      
      const response = await finishedGoodsOutboundService.getOutboundOrderList(params);
      
      if (response.data?.success) {
        const orderData = response.data.data;
        setOutboundOrders(orderData?.items || []);
        setPagination(prev => ({
          ...prev,
          total: orderData?.total || 0
        }));
      } else {
        message.error(response.data?.message || '获取出库单列表失败');
      }
    } catch (error) {
      message.error('获取出库单列表失败');
      
      // 设置空数组，不使用模拟数据
      setOutboundOrders([]);
      setPagination(prev => ({
        ...prev,
        total: 0
      }));
    } finally {
      setLoading(false);
    }
  };

  // 获取状态标签
  const getStatusTag = (status) => {
    const statusMap = {
      draft: { color: '#d9d9d9', text: '草稿' },
      confirmed: { color: '#1890ff', text: '已确认' },
      in_progress: { color: '#faad14', text: '执行中' },
      completed: { color: '#52c41a', text: '已完成' },
      cancelled: { color: '#ff4d4f', text: '已取消' }
    };
    const config = statusMap[status] || { color: '#d9d9d9', text: status };
    return <StatusTag color={config.color}>{config.text}</StatusTag>;
  };

  const getApprovalStatusTag = (status) => {
    const statusMap = {
      pending: { color: '#faad14', text: '待审核' },
      approved: { color: '#52c41a', text: '已审核' },
      rejected: { color: '#ff4d4f', text: '已拒绝' }
    };
    const config = statusMap[status] || { color: '#d9d9d9', text: status };
    return <StatusTag color={config.color}>{config.text}</StatusTag>;
  };

  // 表格列定义
  const columns = [
    {
      title: '出库单号',
      dataIndex: 'order_number',
      key: 'order_number',
      width: 180,
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '发生日期',
      dataIndex: 'order_date',
      key: 'order_date',
      width: 120,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD') : '-'
    },
    {
      title: '仓库名称',
      dataIndex: 'warehouse_name',
      key: 'warehouse_name',
      width: 120,
      render: (text, record) => {
        // 如果有仓库名称直接显示，否则根据仓库ID查找
        if (text) return text;
        if (record.warehouse_id && warehouses.length > 0) {
          const warehouse = warehouses.find(w => w.id === record.warehouse_id);
          return warehouse ? warehouse.warehouse_name : '未知仓库';
        }
        return '未知仓库';
      }
    },
    {
      title: '出库人',
      dataIndex: 'outbound_person',
      key: 'outbound_person',
      width: 100,
      render: (text, record) => {
        // 优先显示后端返回的员工姓名
        if (text) return text;
        // 后备方案：根据ID查找
        if (record.outbound_person_id && employees.length > 0) {
          const employee = employees.find(emp => emp.id === record.outbound_person_id);
          return employee ? (employee.label || employee.name) : '未知员工';
        }
        return '-';
      }
    },
    {
      title: '客户',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 120,
      render: (text, record) => {
        if (text) return text;
        if (record.customer_id && customers.length > 0) {
          const customer = customers.find(c => c.id === record.customer_id);
          return customer ? customer.customer_name : '未知客户';
        }
        return '-';
      }
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      width: 100,
      render: (text, record) => {
        // 优先显示后端返回的部门名称
        if (text) return text;
        // 后备方案：根据ID查找
        if (record.department_id && departments.length > 0) {
          const department = departments.find(dept => dept.id === record.department_id);
          return department ? (department.department_name || department.name) : '未知部门';
        }
        return '-';
      }
    },
    {
      title: '托盘套数',
      dataIndex: 'pallet_count',
      key: 'pallet_count',
      width: 100,
      render: (text) => `${text || 0} 套`
    },
    {
      title: '单据状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: getStatusTag
    },
    {
      title: '审核状态',
      dataIndex: 'approval_status',
      key: 'approval_status',
      width: 100,
      render: getApprovalStatusTag
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD HH:mm') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small" wrap>
          <Button 
            type="link" 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => viewOrder(record)}
          >
            查看
          </Button>
          {record.status === 'draft' && (
            <Button 
              type="link" 
              size="small" 
              icon={<EditOutlined />}
              onClick={() => editOrder(record)}
            >
              编辑
            </Button>
          )}
          {record.status === 'confirmed' && record.approval_status === 'approved' && (
            <Button 
              type="link" 
              size="small" 
              icon={<PlayCircleOutlined />}
              onClick={() => executeOrder(record)}
            >
              执行
            </Button>
          )}
          {(record.status === 'draft' || record.status === 'confirmed') && record.approval_status === 'pending' && (
            <>
              <Button 
                type="link" 
                size="small" 
                icon={<CheckOutlined />}
                onClick={() => approveOrder(record, 'approved')}
                style={{ color: '#52c41a' }}
              >
                审核
              </Button>
              <Button 
                type="link" 
                size="small" 
                icon={<CloseOutlined />}
                onClick={() => approveOrder(record, 'rejected')}
                danger
              >
                拒绝
              </Button>
            </>
          )}
          {record.status !== 'completed' && record.status !== 'cancelled' && (
            <Popconfirm
              title="确定要取消这个出库单吗？"
              onConfirm={() => cancelOrder(record)}
              okText="确定"
              cancelText="取消"
            >
              <Button 
                type="link" 
                size="small" 
                danger
                icon={<CloseOutlined />}
              >
                取消
              </Button>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  // 明细表格列定义
  const detailColumns = [
    {
      title: '行号',
      dataIndex: 'line_number',
      key: 'line_number',
      width: 60,
      render: (_, __, index) => index + 1
    },
    {
      title: '产品编码',
      dataIndex: 'product_code',
      key: 'product_code',
      width: 120,
      render: (text) => text || '-'
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 150,
      render: (text) => text || '-'
    },
    {
      title: '规格',
      dataIndex: 'product_spec',
      key: 'product_spec',
      width: 120,
      render: (text) => text || '-'
    },
    {
      title: '出库数量',
      dataIndex: 'outbound_quantity',
      key: 'outbound_quantity',
      width: 100,
      render: (text, record) => {
        if (!text && text !== 0) return '-';
        // 优先使用record.unit_name，如果没有则从units数组中查找
        const unitName = record.unit_name || (record.unit_id ? units.find(unit => unit.value === record.unit_id)?.label : '');
        return `${text} ${unitName || ''}`;
      }
    },
    {
      title: '单价',
      dataIndex: 'unit_cost',
      key: 'unit_cost',
      width: 100,
      render: (text) => text ? `¥${text.toFixed(2)}` : '-'
    },
    {
      title: '出库公斤数',
      dataIndex: 'outbound_kg_quantity',
      key: 'outbound_kg_quantity',
      width: 100,
      render: (text) => text ? `${text} kg` : '-'
    },
    {
      title: '出库米数',
      dataIndex: 'outbound_m_quantity',
      key: 'outbound_m_quantity',
      width: 100,
      render: (text) => text ? `${text} m` : '-'
    },
    {
      title: '出库卷数',
      dataIndex: 'outbound_roll_quantity',
      key: 'outbound_roll_quantity',
      width: 100,
      render: (text) => text ? `${text} 卷` : '-'
    },
    {
      title: '箱数',
      dataIndex: 'box_quantity',
      key: 'box_quantity',
      width: 80,
      render: (text) => text ? `${text} 箱` : '-'
    },
    {
      title: '批次号',
      dataIndex: 'batch_number',
      key: 'batch_number',
      width: 120,
      render: (text) => text || '-'
    },
    {
      title: '库位码',
      dataIndex: 'location_code',
      key: 'location_code',
      width: 100,
      render: (text) => text || '-'
    },
    {
      title: '备注',
      dataIndex: 'remark',
      key: 'remark',
      width: 120,
      render: (text) => text || '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small" 
            icon={<EditOutlined />}
            onClick={() => editDetail(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这条明细吗？"
            onConfirm={() => deleteDetail(record)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              type="link" 
              size="small" 
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 查看详情用的明细表格列定义（不包含操作列）
  const viewDetailColumns = detailColumns.filter(col => col.key !== 'action');

  // 新增出库单
  const handleCreateOrder = () => {
    setCurrentOrder(null);
    setIsViewMode(false);
    setOrderDetails([]);
    form.resetFields();
    // 设置默认发生日期为当前日期
    form.setFieldsValue({
      order_date: dayjs()
    });
    setModalVisible(true);
  };

  // 查看出库单
  const viewOrder = async (record) => {
    try {
      // 设置当前订单
      setCurrentOrder(record);
      
      // 获取出库单明细
      const { data: detailResponse } = await finishedGoodsOutboundService.getOutboundOrderDetails(record.id);
      
      // 处理明细数据（成功或失败场景）
      setOrderDetails(
        detailResponse?.success ? (detailResponse.data || []) : []
      );
      
      // 显示查看模态框
      setViewModalVisible(true);
    } catch (error) {
      console.error('查看订单失败:', error);
      message.error('获取出库单详情失败');
    }
  };

  // 编辑出库单
  const editOrder = async (record) => {
    setCurrentOrder(record);
    setIsViewMode(false);
    form.setFieldsValue({
      ...record,
      order_date: record.order_date ? dayjs(record.order_date) : null
    });
    
    // 加载出库单明细
    try {
      const detailResponse = await finishedGoodsOutboundService.getOutboundOrderDetails(record.id);
      if (detailResponse.data?.success) {
        setOrderDetails(detailResponse.data.data || []);
      }
    } catch (error) {
      console.error('加载明细失败:', error);
    }
    
    setModalVisible(true);
  };

  // 执行出库单
  const executeOrder = async (record) => {
    try {
      const response = await finishedGoodsOutboundService.executeOutboundOrder(record.id);
      if (response.data?.success) {
        message.success('出库单执行成功');
        fetchOutboundOrders();
      } else {
        message.error(response.data?.message || '出库单执行失败');
      }
    } catch (error) {
      message.error('出库单执行失败');
    }
  };

  // 审核出库单
  const approveOrder = async (record, status) => {
    try {
      const response = await finishedGoodsOutboundService.approveOutboundOrder(record.id, {
        approval_status: status,
        approval_comment: status === 'rejected' ? '不符合出库要求' : '审核通过'
      });
      if (response.data?.success) {
        message.success(status === 'approved' ? '审核通过' : '已拒绝');
        fetchOutboundOrders();
      } else {
        message.error(response.data?.message || '审核失败');
      }
    } catch (error) {
      message.error('审核失败');
    }
  };

  // 取消出库单
  const cancelOrder = async (record) => {
    try {
      const response = await finishedGoodsOutboundService.cancelOutboundOrder(record.id, {
        cancel_reason: '用户取消'
      });
      if (response.data?.success) {
        message.success('出库单已取消');
        fetchOutboundOrders();
      } else {
        message.error(response.data?.message || '取消失败');
      }
    } catch (error) {
      message.error('取消失败');
    }
  };

  // 提交出库单
  const handleSubmit = async (values) => {
    try {
      // 清理明细数据，去掉临时ID和多余字段，确保单位字段正确传递
      const cleanDetails = orderDetails.map(detail => {
        const cleanDetail = { ...detail };
        // 如果是临时ID，去掉ID字段让后端生成
        if (cleanDetail.id && cleanDetail.id.toString().startsWith('temp-')) {
          delete cleanDetail.id;
        }
        
        // 确保单位字段正确传递：优先使用unit_id，如果没有则使用unit
        if (cleanDetail.unit_id) {
          cleanDetail.unit = cleanDetail.unit_id; // 后端期望unit字段
        } else if (cleanDetail.unit) {
          cleanDetail.unit_id = cleanDetail.unit; // 同时设置unit_id
        }
        
        return cleanDetail;
      });

      const formData = {
        ...values,
        order_date: values.order_date ? values.order_date.format('YYYY-MM-DD') : null,
        status: 'draft',
        details: cleanDetails  // 包含清理后的明细数据
      };

      if (currentOrder) {
        // 更新
        const response = await finishedGoodsOutboundService.updateOutboundOrder(currentOrder.id, formData);
        if (response.data?.success) {
          message.success('出库单更新成功');
          setModalVisible(false);
          fetchOutboundOrders();
        } else {
          message.error(response.data?.message || '更新失败');
        }
      } else {
        // 新增
        const response = await finishedGoodsOutboundService.createOutboundOrder(formData);
        if (response.data?.success) {
          message.success('出库单创建成功');
          setModalVisible(false);
          fetchOutboundOrders();
        } else {
          message.error(response.data?.message || '创建失败');
        }
      }
    } catch (error) {
      message.error(currentOrder ? '更新失败' : '创建失败');
    }
  };

  // 添加明细
  const addDetail = async () => {
    setCurrentDetail(null);
    detailForm.resetFields();
    setDetailModalVisible2(true);
  };

  // 选择产品
  const selectProducts = async () => {
    setSelectedProducts([]);
    setProductSearchText('');
    setProductSelectVisible(true);
  };

  // 确认产品选择
  const confirmProductSelection = () => {
    const newDetails = selectedProducts.map(product => ({
      id: `temp-${Date.now()}-${product.id}`,
      product_id: product.id,
      product_code: product.product_code,
      product_name: product.product_name,
      product_spec: product.product_spec,
      outbound_quantity: 1,
      unit_id: product.unit_id, // 使用 unit_id
      unit: product.unit_id, // 同时设置 unit 字段用于表单显示
      unit_name: product.unit_name, // 保存单位名称用于显示
      unit_cost: 0,
      outbound_kg_quantity: 0,
      outbound_m_quantity: 0,
      outbound_roll_quantity: 0,
      box_quantity: 0,
      batch_number: '',
      location_code: '',
      remark: ''
    }));

    setOrderDetails([...orderDetails, ...newDetails]);
    setProductSelectVisible(false);
    message.success(`已添加 ${selectedProducts.length} 个产品明细`);
  };

  // 编辑明细
  const editDetail = async (record) => {
    setCurrentDetail(record);
    
    // 处理表单数据，确保字段映射正确
    const formData = { ...record };
    
    // 处理单位字段映射：unit_id -> unit
    if (record.unit_id && units.length > 0) {
      const unit = units.find(u => u.value === record.unit_id);
      if (unit) {
        formData.unit = unit.value;
      }
    }
    
    detailForm.setFieldsValue(formData);
    setDetailModalVisible2(true);
  };

  // 删除明细
  const deleteDetail = async (record) => {
    if (currentOrder && record.id && !record.id.toString().startsWith('temp-')) {
      // 如果是编辑模式且明细已保存，调用API删除
      try {
        const response = await finishedGoodsOutboundService.deleteOutboundOrderDetail(currentOrder.id, record.id);
        if (response.data?.success) {
          setOrderDetails(orderDetails.filter(item => item.id !== record.id));
          message.success('明细删除成功');
        } else {
          message.error(response.data?.message || '删除明细失败');
        }
      } catch (error) {
        console.error('删除明细失败:', error);
        message.error('删除失败');
      }
    } else {
      // 新建模式或临时明细，直接从本地数据中删除
      setOrderDetails(orderDetails.filter(item => item.id !== record.id));
      message.success('明细删除成功');
    }
  };

  // 提交明细表单
  const handleDetailSubmit = async (values) => {
    try {
      // 从产品数据中获取产品详细信息
      const selectedProduct = products.find(p => p.id === values.product_id);
      const productInfo = {
        product_code: selectedProduct?.product_code || '',
        product_name: selectedProduct?.product_name || '',
        product_spec: selectedProduct?.specification || selectedProduct?.spec || ''
      };

      // 处理单位字段映射：unit -> unit_id
      const submitData = { ...values };
      if (values.unit) {
        submitData.unit_id = values.unit;
        delete submitData.unit; // 删除unit字段，避免后端混淆
      }

      if (currentDetail) {
        // 编辑明细
        if (currentOrder && currentDetail.id && !currentDetail.id.toString().startsWith('temp-')) {
          // 如果是编辑模式且明细已保存，调用API更新
          const response = await finishedGoodsOutboundService.updateOutboundOrderDetail(currentOrder.id, currentDetail.id, submitData);
          if (response.data?.success) {
            const updatedDetail = response.data.data || { ...currentDetail, ...values, ...productInfo };
            setOrderDetails(orderDetails.map(item => 
              item.id === currentDetail.id ? updatedDetail : item
            ));
            message.success('明细更新成功');
          } else {
            message.error(response.data?.message || '更新明细失败');
            return;
          }
                  } else {
            // 新建模式或临时明细，直接更新本地数据
            const updatedDetail = { 
              ...currentDetail, 
              ...values,
              ...productInfo,
              unit_id: values.unit // 确保本地数据也包含unit_id
            };
          
          // 确保单位字段正确设置
          if (values.unit) {
            updatedDetail.unit_id = values.unit;
          }
          
          setOrderDetails(orderDetails.map(item => 
            item.id === currentDetail.id ? updatedDetail : item
          ));
          message.success('明细更新成功');
        }
              } else {
          // 新增明细
          if (currentOrder) {
            // 如果是编辑模式，调用API添加明细
            const response = await finishedGoodsOutboundService.createOutboundOrderDetail(currentOrder.id, submitData);
          if (response.data?.success) {
            const newDetail = {
              ...response.data.data,
              ...productInfo
            };
            setOrderDetails([...orderDetails, newDetail]);
            message.success('明细添加成功');
          } else {
            message.error(response.data?.message || '添加明细失败');
            return;
          }
                  } else {
            // 新建模式下，直接添加到本地数据
            const newDetail = {
              id: `temp-${Date.now()}`,
              ...values,
              ...productInfo,
              unit_id: values.unit // 确保本地数据也包含unit_id
            };
          
          // 确保单位字段正确设置
          if (values.unit) {
            newDetail.unit_id = values.unit;
          }
          
          setOrderDetails([...orderDetails, newDetail]);
          message.success('明细添加成功');
        }
      }
      
      setDetailModalVisible2(false);
    } catch (error) {
      console.error('保存明细失败:', error);
      message.error('保存失败');
    }
  };

  return (
    <PageContainer>
      <StyledCard>
        <div style={{ marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0, display: 'inline-block' }}>
            成品出库管理
          </Title>
        </div>

        {/* 搜索表单 */}
        <Collapse style={{ marginBottom: 16 }} ghost>
          <Panel header="展开筛选" key="1">
            <Form
              form={searchForm}
              layout="vertical"
              onFinish={handleSearch}
            >
              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item name="search" label="关键字搜索">
                    <Input 
                      placeholder="输入出库单号、出库人等"
                      allowClear
                      prefix={<SearchOutlined />}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="warehouse_id" label="仓库">
                    <Select placeholder="选择仓库" allowClear>
                      {warehouses.map((warehouse, index) => (
                        <Option key={warehouse.id || `warehouse-${index}`} value={warehouse.id || ''}>
                          {warehouse.warehouse_name || warehouse.name || '未知仓库'}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="status" label="单据状态">
                    <Select placeholder="选择状态" allowClear>
                      <Option value="draft">草稿</Option>
                      <Option value="confirmed">已确认</Option>
                      <Option value="in_progress">执行中</Option>
                      <Option value="completed">已完成</Option>
                      <Option value="cancelled">已取消</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="approval_status" label="审核状态">
                    <Select placeholder="选择审核状态" allowClear>
                      <Option value="pending">待审核</Option>
                      <Option value="approved">已审核</Option>
                      <Option value="rejected">已拒绝</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="date_range" label="发生日期">
                    <RangePicker 
                      style={{ width: '100%' }}
                      format="YYYY-MM-DD"
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="outbound_person_id" label="出库人">
                    <Select placeholder="选择出库人" allowClear>
                      {employees.map((employee, index) => (
                        <Option key={employee.value || `employee-${index}`} value={employee.value}>
                          {employee.label || employee.name || '未知员工'}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="department_id" label="部门">
                    <Select placeholder="选择部门" allowClear>
                      {departments.map((dept, index) => (
                        <Option key={dept.id || `dept-${index}`} value={dept.id}>
                          {dept.department_name || dept.name || '未知部门'}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item label=" " style={{ marginTop: 8 }}>
                    <Space>
                      <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                        搜索
                      </Button>
                      <Button onClick={handleReset} icon={<ReloadOutlined />}>
                        重置
                      </Button>
                    </Space>
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Panel>
        </Collapse>

        {/* 操作按钮 */}
        <div style={{ marginBottom: 16 }}>
          <Space wrap>
            <ActionButton type="primary" icon={<PlusOutlined />} onClick={handleCreateOrder}>
              新增出库单
            </ActionButton>
            <ActionButton icon={<ImportOutlined />}>
              导入
            </ActionButton>
            <ActionButton icon={<ExportOutlined />}>
              导出
            </ActionButton>
            <ActionButton icon={<ReloadOutlined />} onClick={handleRefresh}>
              刷新
            </ActionButton>
          </Space>
        </div>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={outboundOrders}
          loading={loading}
          rowKey="id"
          pagination={{
            ...pagination,
            onChange: (page, pageSize) => {
              setPagination(prev => ({
                ...prev,
                current: page,
                pageSize: pageSize
              }));
            },
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
          }}
          scroll={{ x: 1500 }}
        />
      </StyledCard>

      {/* 新增/编辑出库单弹窗 */}
      <Modal
        title={currentOrder ? '编辑出库单' : '新增出库单'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setModalVisible(false)}>
            取消
          </Button>,
          <Button key="submit" type="primary" onClick={() => form.submit()}>
            确定
          </Button>
        ]}
        width={1200}
        destroyOnClose
      >
        <Tabs defaultActiveKey="1">
          <TabPane tab="基本信息" key="1">
            <Form 
              form={form} 
              layout="vertical" 
              onFinish={handleSubmit}
            >
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item 
                    name="warehouse_id" 
                    label="出库仓库" 
                    rules={[{ required: true, message: '请选择出库仓库' }]}
                  >
                    <Select placeholder="请选择出库仓库">
                      {warehouses.map(warehouse => (
                        <Option key={warehouse.id} value={warehouse.id}>
                          {warehouse.warehouse_name}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item 
                    name="order_date" 
                    label="发生日期" 
                    rules={[{ required: true, message: '请选择发生日期' }]}
                  >
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>
              
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item 
                    name="customer_id" 
                    label="客户"
                  >
                    <Select placeholder="请选择客户" allowClear>
                      {customers.map(customer => (
                        <Option key={customer.id} value={customer.id}>
                          {customer.customer_name}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="outbound_person_id" label="出库人">
                    <Select placeholder="请选择出库人" 
                    onChange={(value) => {
                      // 根据选择的员工自动填充部门
                      if (value && employees.length > 0) {
                        const selectedEmployee = employees.find(emp => emp.value === value);
                        if (selectedEmployee && selectedEmployee.department_id) {
                          form.setFieldsValue({
                            department_id: selectedEmployee.department_id,
                            department_name: selectedEmployee.department_name
                          });
                        }
                      }
                    }}>
                      {employees.map((employee, index) => (
                        <Option key={employee.value || `employee-${index}`} value={employee.value}>
                          {employee.label || employee.name || '未知员工'}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="department_id" label="部门">
                    <Select placeholder="请选择部门" allowClear>
                      {departments.map((dept, index) => (
                        <Option key={dept.id || `dept-${index}`} value={dept.id}>
                          {dept.department_name || dept.name || '未知部门'}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="pallet_count" label="托盘套数">
                    <InputNumber 
                      placeholder="请输入托盘套数" 
                      min={0} 
                      style={{ width: '100%' }} 
                    />
                  </Form.Item>
                </Col>
              </Row>
              
              <Form.Item name="remark" label="备注">
                <TextArea rows={3} placeholder="请输入备注信息" />
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="出库明细" key="2">
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />} 
                  onClick={addDetail}
                >
                  添加明细
                </Button>
                <Button 
                  icon={<PlusOutlined />} 
                  onClick={selectProducts}
                >
                  选择产品
                </Button>
                <Text type="secondary">共 {orderDetails.length} 条明细</Text>
              </Space>
            </div>

            <DetailTable
              columns={detailColumns}
              dataSource={orderDetails}
              rowKey="id"
              pagination={false}
              size="small"
              scroll={{ x: 1200 }}
            />
          </TabPane>
        </Tabs>
      </Modal>

      {/* 产品明细弹窗 */}
      <Modal
        title={currentDetail ? '编辑明细' : '添加明细'}
        open={detailModalVisible2}
        onCancel={() => setDetailModalVisible2(false)}
        footer={[
          <Button key="cancel" onClick={() => setDetailModalVisible2(false)}>
            取消
          </Button>,
          <Button 
            key="submit" 
            type="primary" 
            onClick={() => detailForm.submit()}
          >
            确定
          </Button>
        ]}
        width={800}
        destroyOnClose
      >
        <Form
          form={detailForm}
          layout="vertical"
          onFinish={handleDetailSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                name="product_id" 
                label="产品" 
                rules={[{ required: true, message: '请选择产品' }]}
              >
                <Select 
                  placeholder="请选择产品" 
                  showSearch
                  filterOption={(input, option) =>
                    option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                  }
                  onChange={(productId) => {
                    // 当选择产品时，自动填入单位
                    const product = products.find(p => p.id === productId);
                    if (product && product.unit_id && units.length > 0) {
                      const unit = units.find(u => u.value === product.unit_id);
                      if (unit) {
                        detailForm.setFieldsValue({
                          unit: unit.value
                        });
                      }
                    }
                  }}
                >
                  {products.map(product => (
                    <Option key={product.id} value={product.id}>
                      {product.product_name} ({product.product_code})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                name="batch_number" 
                label="批次号"
              >
                <Input placeholder="请输入批次号" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item 
                name="outbound_quantity" 
                label="出库数量" 
                rules={[{ required: true, message: '请输入出库数量' }]}
              >
                <InputNumber 
                  placeholder="请输入出库数量" 
                  min={0} 
                  precision={2}
                  style={{ width: '100%' }} 
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="unit" label="单位" rules={[{ required: true, message: '请选择单位' }]}>
                <Select placeholder="请选择单位" allowClear>
                  {units.map(unit => (
                    <Option key={unit.value} value={unit.value}>{unit.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="unit_cost" label="单价">
                <InputNumber 
                  placeholder="请输入单价" 
                  min={0} 
                  precision={2}
                  style={{ width: '100%' }} 
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="outbound_kg_quantity" label="出库公斤数">
                <InputNumber 
                  placeholder="请输入出库公斤数" 
                  min={0} 
                  precision={2}
                  style={{ width: '100%' }} 
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="outbound_m_quantity" label="出库米数">
                <InputNumber 
                  placeholder="请输入出库米数" 
                  min={0} 
                  precision={2}
                  style={{ width: '100%' }} 
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="outbound_roll_quantity" label="出库卷数">
                <InputNumber 
                  placeholder="请输入出库卷数" 
                  min={0} 
                  precision={0}
                  style={{ width: '100%' }} 
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="box_quantity" label="箱数">
                <InputNumber 
                  placeholder="请输入箱数" 
                  min={0} 
                  precision={0}
                  style={{ width: '100%' }} 
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="location_code" label="库位码">
                <Input placeholder="请输入库位码" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="remark" label="备注">
            <TextArea rows={2} placeholder="请输入备注信息" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 产品选择弹窗 */}
      <Modal
        title="选择产品"
        open={productSelectVisible}
        onCancel={() => setProductSelectVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setProductSelectVisible(false)}>
            取消
          </Button>,
          <Button 
            key="submit" 
            type="primary" 
            onClick={confirmProductSelection}
            disabled={selectedProducts.length === 0}
          >
            确定选择 ({selectedProducts.length})
          </Button>
        ]}
        width={800}
      >
        <div style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索产品名称或编码"
            value={productSearchText}
            onChange={(e) => setProductSearchText(e.target.value)}
            prefix={<SearchOutlined />}
            allowClear
          />
        </div>
        
        <Table
          rowSelection={{
            selectedRowKeys: selectedProducts.map(p => p.id),
            onChange: (selectedRowKeys, selectedRows) => {
              setSelectedProducts(selectedRows);
            },
          }}
          columns={[
            {
              title: '产品编码',
              dataIndex: 'product_code',
              key: 'product_code',
            },
            {
              title: '产品名称',
              dataIndex: 'product_name',
              key: 'product_name',
            },
            {
              title: '规格',
              dataIndex: 'product_spec',
              key: 'product_spec',
            },
            {
              title: '单位',
              dataIndex: 'unit_name',
              key: 'unit_name',
            },
          ]}
          dataSource={products.filter(product => 
            !productSearchText || 
            product.product_name?.toLowerCase().includes(productSearchText.toLowerCase()) ||
            product.product_code?.toLowerCase().includes(productSearchText.toLowerCase())
          )}
          rowKey="id"
          pagination={false}
          size="small"
          scroll={{ y: 400 }}
        />
      </Modal>

      {/* 查看出库单详情模态框 */}
      <Modal
        title={`出库单详情 - ${currentOrder?.order_number}`}
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={null}
        width={1200}
      >
        {currentOrder && (
          <Tabs defaultActiveKey="1">
            <TabPane tab="基本信息" key="1">
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>出库单号：</Text>
                  <Text>{currentOrder.order_number}</Text>
                </Col>
                <Col span={8}>
                  <Text strong>发生日期：</Text>
                  <Text>{currentOrder.order_date ? dayjs(currentOrder.order_date).format('YYYY-MM-DD') : '-'}</Text>
                </Col>
                <Col span={8}>
                  <Text strong>仓库名称：</Text>
                  <Text>
                    {(() => {
                      // 如果有仓库名称直接显示，否则根据仓库ID查找
                      if (currentOrder.warehouse_name) return currentOrder.warehouse_name;
                      if (currentOrder.warehouse_id && warehouses.length > 0) {
                        const warehouse = warehouses.find(w => w.id === currentOrder.warehouse_id);
                        return warehouse ? warehouse.warehouse_name : '未知仓库';
                      }
                      return '未知仓库';
                    })()}
                  </Text>
                </Col>
              </Row>
              <Divider />
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>出库人：</Text>
                  <Text>
                    {(() => {
                      if (currentOrder.outbound_person) return currentOrder.outbound_person;
                      if (currentOrder.outbound_person_id && employees.length > 0) {
                        const employee = employees.find(emp => emp.id === currentOrder.outbound_person_id);
                        return employee ? (employee.label || employee.name) : '未知员工';
                      }
                      return '-';
                    })()}
                  </Text>
                </Col>
                <Col span={8}>
                  <Text strong>客户：</Text>
                  <Text>
                    {(() => {
                      if (currentOrder.customer_name) return currentOrder.customer_name;
                      if (currentOrder.customer_id && customers.length > 0) {
                        const customer = customers.find(c => c.id === currentOrder.customer_id);
                        return customer ? customer.customer_name : '未知客户';
                      }
                      return '-';
                    })()}
                  </Text>
                </Col>
                <Col span={8}>
                  <Text strong>部门：</Text>
                  <Text>
                    {(() => {
                      if (currentOrder.department) return currentOrder.department;
                      if (currentOrder.department_id && departments.length > 0) {
                        const department = departments.find(dept => dept.id === currentOrder.department_id);
                        return department ? (department.department_name || department.name) : '未知部门';
                      }
                      return '-';
                    })()}
                  </Text>
                </Col>
              </Row>
              <Divider />
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>托盘套数：</Text>
                  <Text>{currentOrder.pallet_count || 0} 套</Text>
                </Col>
                <Col span={8}>
                  <Text strong>单据状态：</Text>
                  {getStatusTag(currentOrder.status)}
                </Col>
                <Col span={8}>
                  <Text strong>审核状态：</Text>
                  {getApprovalStatusTag(currentOrder.approval_status)}
                </Col>
              </Row>
              <Divider />
              <Row gutter={16}>
                <Col span={12}>
                  <Text strong>创建时间：</Text>
                  <Text>
                    {currentOrder.created_at ? 
                      (() => {
                        try {
                          const localTime = dayjs.utc(currentOrder.created_at).local();
                          return `${localTime.format('YYYY-MM-DD')} ${localTime.format('HH:mm:ss')}`;
                        } catch (error) {
                          return currentOrder.created_at;
                        }
                      })()
                      : '-'
                    }
                  </Text>
                </Col>
                <Col span={12}>
                  <Text strong>备注：</Text>
                  <Text>{currentOrder.remark || '-'}</Text>
                </Col>
              </Row>
            </TabPane>
            
            <TabPane tab="出库明细" key="2">
              <DetailTable
                columns={viewDetailColumns}
                dataSource={orderDetails}
                rowKey="id"
                scroll={{ x: 1000 }}
                pagination={false}
              />
            </TabPane>
          </Tabs>
        )}
      </Modal>
    </PageContainer>
  );
};

export default FinishedGoodsOutbound; 