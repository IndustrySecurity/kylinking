import React, { useState, useEffect, useCallback } from 'react';
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
  const [baseDataLoading, setBaseDataLoading] = useState(false);
  // 分页和筛选状态
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [filters, setFilters] = useState({});
  const [searchParams, setSearchParams] = useState({});

  // 统一的基础数据获取函数
  const fetchBaseData = useCallback(async () => {
    if (baseDataLoading) return; // 防止重复请求
    
    setBaseDataLoading(true);
    try {
      const [warehousesRes, productsRes, departmentsRes, employeesRes, customersRes, unitsRes] = await Promise.all([
        baseDataService.getWarehouses({ warehouse_type: 'finished_goods' }),
        baseDataService.getProducts(),
        baseDataService.getDepartments(),
        baseDataService.getEmployees(),
        baseDataService.getCustomers(),
        baseDataService.getUnits()
      ]);

      // 处理仓库数据
      if (warehousesRes.data?.success) {
        const warehouseData = warehousesRes.data.data;
        const warehouses = Array.isArray(warehouseData) ? warehouseData.map(item => ({
          id: item.value || item.id,
          warehouse_name: item.label || item.warehouse_name || item.name,
          warehouse_code: item.code || item.warehouse_code
        })) : [];
        setWarehouses(warehouses);
      } else {
        setWarehouses([]);
      }

      // 处理产品数据
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

      // 处理部门数据
      if (departmentsRes.data?.success) {
        const departmentData = departmentsRes.data.data;
        const departments = Array.isArray(departmentData) ? departmentData.map(item => ({
          id: item.value || item.id,
          department_name: item.label || item.department_name || item.name,
          department_code: item.code || item.department_code
        })) : [];
        setDepartments(departments);
      } else {
        setDepartments([]);
      }

      // 处理员工数据
      if (employeesRes.data?.success) {
        const employeeData = employeesRes.data.data;
        const employees = Array.isArray(employeeData) ? employeeData.map(item => ({
          id: item.id || item.value,
          employee_name: item.employee_name || item.name || item.label,
          employee_code: item.employee_code || item.code,
          department_id: item.department_id || item.department,
          department_name: item.department_name
        })) : [];
        setEmployees(employees);
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
      console.error('获取基础数据失败:', error);
      message.error('获取基础数据失败，请检查网络连接');
      // 设置空数组
      setWarehouses([]);
      setProducts([]);
      setCustomers([]);
      setDepartments([]);
      setEmployees([]);
      setUnits([]);
    } finally {
      setBaseDataLoading(false);
    }
  }, []);

  // 确保产品数据已加载的函数
  const ensureProductsLoaded = useCallback(async () => {
    if (products.length === 0 && !baseDataLoading) {
      await fetchBaseData();
    }
  }, [products.length, baseDataLoading, fetchBaseData]);

  // 初始化数据 - 只保留一个useEffect
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
    fetchBaseData(); // 同时刷新基础数据
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
      title: '出库重量(kg)',
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

  // 解析产品规格，提取宽度、厚度（单位：丝）
  const parseSpecification = (specification) => {
    if (!specification) return null;
    
    // 尝试解析 "宽度*厚度" 格式，厚度单位为丝
    const patterns = [
      /(\d+(?:\.\d+)?)\s*[×xX*]\s*(\d+(?:\.\d+)?)/, // 数字×数字
      /(\d+(?:\.\d+)?)\s*cm\s*[×xX*]\s*(\d+(?:\.\d+)?)\s*丝/, // cm×丝
      /(\d+(?:\.\d+)?)\s*[×xX*]\s*(\d+(?:\.\d+)?)\s*丝/, // 数字×丝
    ];
    
    for (const pattern of patterns) {
      const match = specification.match(pattern);
      if (match) {
        const [, width, thickness] = match;
        return {
          width: parseFloat(width),
          thickness: parseFloat(thickness) // 厚度单位为丝
        };
      }
    }
    
    return null;
  };

  // 从产品数据中提取参数
  const extractProductParams = (productData, specification = null) => {
    if (!productData) return null;
    
    // 优先从规格字符串解析宽度和厚度
    let width = null;
    let thickness = null;
    
    if (specification) {
      const specParams = parseSpecification(specification);
      if (specParams && specParams.width && specParams.thickness) {
        width = specParams.width;
        thickness = specParams.thickness;
      }
    }
    
    // 如果从规格字符串解析到了宽度和厚度，且产品数据中有密度，则优先使用
    if (width && thickness && productData.density) {
      return {
        width: width,
        thickness: thickness, // 厚度单位为丝
        density: productData.density
      };
    }
    
    // 如果没有规格字符串或解析失败，从产品结构表获取
    if (productData.structures && productData.structures.length > 0) {
      const structure = productData.structures[0];
      if (structure.width && structure.thickness && structure.density) {
        return {
          width: structure.width,
          thickness: structure.thickness, // 厚度单位为丝
          density: structure.density
        };
      }
    }
    
    // 从产品基本信息获取（现在所有字段都在products表中）
    if (productData.struct_width && productData.struct_thickness && productData.density) {
      return {
        width: productData.struct_width,
        thickness: productData.struct_thickness, // 厚度单位为丝
        density: productData.density
      };
    }
    
    // 兼容旧格式
    if (productData.width && productData.thickness && productData.density) {
      return {
        width: productData.width,
        thickness: productData.thickness, // 厚度单位为丝
        density: productData.density
      };
    }
    
    return null;
  };

  // 计算重量和长度的相互转换
  const calculateConversion = (quantity, unitName, productParams, specification) => {
    if (!quantity || quantity <= 0) return { planned_meters: undefined, planned_weight: undefined };
    
    const unitLower = unitName.toLowerCase();

    try {
      // 使用从 extractProductParams 获取的参数，需要将厚度从丝转换为mm
      let params = productParams;
      
      if (params) {
        params = {
          width: params.width,
          thickness: params.thickness * 0.01, // 丝转换为mm (1丝 = 0.01mm)
          density: params.density
        };
      }

      if (!params || !params.width || !params.thickness || !params.density) {
        return calculateBasicConversion(quantity, unitName);
      }

      // 重量转长度：重量(kg) / (宽度(cm) * 厚度(mm) * 密度(g/cm³) / 100)
      // 长度转重量：长度(m) * 宽度(cm) * 厚度(mm) * 密度(g/cm³) / 100
      
      // 重量单位：kg/千克/公斤 -> 计算计划重量和计划米数
      if (unitLower.includes('kg') || unitLower.includes('千克') || unitLower.includes('公斤')) {
        const plannedWeight = Number(quantity);
        const plannedMeters = Number(quantity / (params.width * params.thickness * params.density / 100));

        return { 
          planned_meters: isFinite(plannedMeters) ? Math.round(plannedMeters * 100) / 100 : undefined, 
          planned_weight: isFinite(plannedWeight) ? Math.round(plannedWeight * 100) / 100 : undefined 
        };
      }
      // 重量单位：t/吨 -> 转换为kg后计算
      else if (unitLower.includes('t') || unitLower.includes('吨')) {
        const plannedWeight = Number(quantity * 1000);
        const plannedMeters = Number((quantity * 1000) / (params.width * params.thickness * params.density / 100));

        return { 
          planned_meters: isFinite(plannedMeters) ? Math.round(plannedMeters * 100) / 100 : undefined, 
          planned_weight: isFinite(plannedWeight) ? Math.round(plannedWeight * 100) / 100 : undefined 
        };
      }
      // 长度单位：m/米 -> 计算计划米数和计划重量
      else if (unitLower.includes('m') || unitLower.includes('米')) {
        const plannedMeters = Number(quantity);
        const plannedWeight = Number(quantity * params.width * params.thickness * params.density / 100);

        return { 
          planned_meters: isFinite(plannedMeters) ? Math.round(plannedMeters * 100) / 100 : undefined, 
          planned_weight: isFinite(plannedWeight) ? Math.round(plannedWeight * 100) / 100 : undefined 
        };
      }
      // 长度单位：km/公里 -> 转换为米后计算
      else if (unitLower.includes('km') || unitLower.includes('千米')) {
        const plannedMeters = Number(quantity * 1000);
        const plannedWeight = Number((quantity * 1000) * params.width * params.thickness * params.density / 100);

        return { 
          planned_meters: isFinite(plannedMeters) ? Math.round(plannedMeters * 100) / 100 : undefined, 
          planned_weight: isFinite(plannedWeight) ? Math.round(plannedWeight * 100) / 100 : undefined 
        };
      }
      // 长度单位：cm/厘米 -> 转换为米后计算
      else if (unitLower.includes('cm') || unitLower.includes('厘米')) {
        const plannedMeters = Number(quantity / 100);
        const plannedWeight = Number((quantity / 100) * params.width * params.thickness * params.density / 100);

        return { 
          planned_meters: isFinite(plannedMeters) ? Math.round(plannedMeters * 100) / 100 : undefined, 
          planned_weight: isFinite(plannedWeight) ? Math.round(plannedWeight * 100) / 100 : undefined 
        };
      }
      // 长度单位：mm/毫米 -> 转换为米后计算
      else if (unitLower.includes('mm') || unitLower.includes('毫米')) {
        const plannedMeters = Number(quantity / 1000);
        const plannedWeight = Number((quantity / 1000) * params.width * params.thickness * params.density / 100);

        return { 
          planned_meters: isFinite(plannedMeters) ? Math.round(plannedMeters * 100) / 100 : undefined, 
          planned_weight: isFinite(plannedWeight) ? Math.round(plannedWeight * 100) / 100 : undefined 
        };
      }
    } catch (error) {
      console.error('计算转换时出错:', error);
      return { planned_meters: undefined, planned_weight: undefined };
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

  // 计算计划值（米数和重量）
  const calculatePlannedValues = (quantity, unitName, productData = null, specification = null) => {
    if (!quantity || quantity <= 0 || !unitName) {
      return { planned_meters: undefined, planned_weight: undefined };
    }
    
    // 提取产品参数
    const productParams = extractProductParams(productData, specification);
    
    // 使用智能转换
    return calculateConversion(quantity, unitName, productParams, specification);
  };

  // 根据计划米数计算出库数量
  const calculateOutboundQuantityFromPlannedMeters = (plannedMeters, unitName, productData = null, specification = null) => {
    if (!unitName || !plannedMeters || plannedMeters <= 0) return undefined;

    // 提取产品参数
    const productParams = extractProductParams(productData, specification);

    if (!productParams || !productParams.width || !productParams.thickness || !productParams.density) {
      return undefined;
    }

    // 将厚度从丝转换为mm，保持与calculateConversion函数一致
    const params = {
      width: productParams.width,
      thickness: productParams.thickness * 0.01, // 丝转换为mm (1丝 = 0.01mm)
      density: productParams.density
    };

    const unitLower = unitName.toLowerCase();

    try {
      // 根据单位类型计算出库数量
      if (unitLower.includes('m') || unitLower.includes('米')) {
        return Number(plannedMeters);
      }
      else if (unitLower.includes('km') || unitLower.includes('千米')) {
        const result = Number(plannedMeters / 1000);
        return Math.round(result * 100) / 100;
      }
      else if (unitLower.includes('cm') || unitLower.includes('厘米')) {
        const result = Number(plannedMeters * 100);
        return Math.round(result * 100) / 100;
      }
      else if (unitLower.includes('mm') || unitLower.includes('毫米')) {
        const result = Number(plannedMeters * 1000);
        return Math.round(result * 100) / 100;
      }
      else if (unitLower.includes('kg') || unitLower.includes('千克') || unitLower.includes('公斤')) {
        const weight = Number(plannedMeters * params.width * params.thickness * params.density / 100);
        return Math.round(weight * 100) / 100;
      }
      else if (unitLower.includes('t') || unitLower.includes('吨')) {
        const weight = Number(plannedMeters * params.width * params.thickness * params.density / 100);
        const result = Number(weight / 1000);
        return Math.round(result * 100) / 100;
      }
    } catch (error) {
      console.error('计算出库数量时出错:', error);
      return undefined;
    }
    
    return undefined;
  };

  // 根据计划重量计算出库数量
  const calculateOutboundQuantityFromPlannedWeight = (plannedWeight, unitName, productData = null, specification = null) => {
    if (!unitName || !plannedWeight || plannedWeight <= 0) return undefined;

    // 提取产品参数
    const productParams = extractProductParams(productData, specification);

    if (!productParams || !productParams.width || !productParams.thickness || !productParams.density) {
      return undefined;
    }

    // 将厚度从丝转换为mm，保持与calculateConversion函数一致
    const params = {
      width: productParams.width,
      thickness: productParams.thickness * 0.01, // 丝转换为mm (1丝 = 0.01mm)
      density: productParams.density
    };

    const unitLower = unitName.toLowerCase();

    try {
      // 根据单位类型计算出库数量
      if (unitLower.includes('kg') || unitLower.includes('千克') || unitLower.includes('公斤')) {
        return Number(plannedWeight);
      }
      else if (unitLower.includes('t') || unitLower.includes('吨')) {
        return Number(plannedWeight / 1000);
      }
      else if (unitLower.includes('m') || unitLower.includes('米')) {
        const length = Number(plannedWeight / (params.width * params.thickness * params.density / 100));
        return Math.round(length * 100) / 100;
      }
      else if (unitLower.includes('km') || unitLower.includes('千米')) {
        const length = Number(plannedWeight / (params.width * params.thickness * params.density / 100));
        const result = Number(length / 1000);
        return Math.round(result * 100) / 100;
      }
      else if (unitLower.includes('cm') || unitLower.includes('厘米')) {
        const length = Number(plannedWeight / (params.width * params.thickness * params.density / 100));
        const result = Number(length * 100);
        return Math.round(result * 100) / 100;
      }
      else if (unitLower.includes('mm') || unitLower.includes('毫米')) {
        const length = Number(plannedWeight / (params.width * params.thickness * params.density / 100));
        const result = Number(length * 1000);
        return Math.round(result * 100) / 100;
      }
    } catch (error) {
      console.error('计算出库数量时出错:', error);
      return undefined;
    }
    
    return undefined;
  };

  // 更新明细字段的通用函数，实现三个字段的完全同步
  const updateDetailField = (field, value, isUserInput = true) => {
    const currentValues = detailForm.getFieldsValue();
    const productId = currentValues.product_id;
    const unitId = currentValues.unit;
    
    if (!productId || !unitId) {
      // 如果没有选择产品和单位，只更新当前字段
      detailForm.setFieldsValue({ [field]: value });
      return;
    }

    const product = products.find(p => p.id === productId);
    const unit = units.find(u => u.value === unitId);
    
    if (!product || !unit) {
      detailForm.setFieldsValue({ [field]: value });
      return;
    }

    const productData = product;
    const specification = product.specification || product.spec || product.product_spec || product.specifications;
    const unitName = unit.label;

    // 只有用户直接输入时才进行联动计算
    if (isUserInput) {
      if (field === 'outbound_quantity') {
        // 用户修改了出库数量，计算kg数和m数
        detailForm.setFieldsValue({ [field]: value });
        
        const plannedValues = calculatePlannedValues(value, unitName, productData, specification);
        
        if (plannedValues.planned_meters !== undefined) {
          detailForm.setFieldsValue({ outbound_m_quantity: plannedValues.planned_meters });
        }
        if (plannedValues.planned_weight !== undefined) {
          detailForm.setFieldsValue({ outbound_kg_quantity: plannedValues.planned_weight });
        }
      }
      else if (field === 'outbound_m_quantity') {
        // 用户修改了m数，计算出库数量和kg数
        detailForm.setFieldsValue({ [field]: value });
        
        const calculatedQuantity = calculateOutboundQuantityFromPlannedMeters(value, unitName, productData, specification);
        
        if (calculatedQuantity !== undefined && calculatedQuantity !== null && !isNaN(calculatedQuantity) && isFinite(calculatedQuantity)) {
          detailForm.setFieldsValue({ outbound_quantity: calculatedQuantity });
          
          const plannedValues = calculatePlannedValues(calculatedQuantity, unitName, productData, specification);
          if (plannedValues.planned_weight !== undefined) {
            detailForm.setFieldsValue({ outbound_kg_quantity: plannedValues.planned_weight });
          }
        } else {
          detailForm.setFieldsValue({ 
            outbound_quantity: undefined,
            outbound_kg_quantity: undefined 
          });
        }
      }
      else if (field === 'outbound_kg_quantity') {
        // 用户修改了kg数，计算出库数量和m数
        detailForm.setFieldsValue({ [field]: value });
        
        const calculatedQuantity = calculateOutboundQuantityFromPlannedWeight(value, unitName, productData, specification);
        
        if (calculatedQuantity !== undefined && calculatedQuantity !== null && !isNaN(calculatedQuantity) && isFinite(calculatedQuantity)) {
          detailForm.setFieldsValue({ outbound_quantity: calculatedQuantity });
          
          const plannedValues = calculatePlannedValues(calculatedQuantity, unitName, productData, specification);
          if (plannedValues.planned_meters !== undefined) {
            detailForm.setFieldsValue({ outbound_m_quantity: plannedValues.planned_meters });
          }
        } else {
          detailForm.setFieldsValue({ 
            outbound_quantity: undefined,
            outbound_m_quantity: undefined 
          });
        }
      }
      else if (field === 'unit') {
        // 用户修改了单位，重新计算所有相关字段
        detailForm.setFieldsValue({ [field]: value });
        
        const quantity = currentValues.outbound_quantity || 0;
        const plannedValues = calculatePlannedValues(quantity, unitName, productData, specification);
        if (plannedValues.planned_meters !== undefined) {
          detailForm.setFieldsValue({ outbound_m_quantity: plannedValues.planned_meters });
        }
        if (plannedValues.planned_weight !== undefined) {
          detailForm.setFieldsValue({ outbound_kg_quantity: plannedValues.planned_weight });
        }
      }
      else {
        // 其他字段，只更新当前字段
        detailForm.setFieldsValue({ [field]: value });
      }
    } else {
      // 程序计算更新，但如果是重新计算转换值，则进行联动
      if (field === 'outbound_quantity') {
        detailForm.setFieldsValue({ [field]: value });
        
        const plannedValues = calculatePlannedValues(value, unitName, productData, specification);
        if (plannedValues.planned_meters !== undefined) {
          detailForm.setFieldsValue({ outbound_m_quantity: plannedValues.planned_meters });
        }
        if (plannedValues.planned_weight !== undefined) {
          detailForm.setFieldsValue({ outbound_kg_quantity: plannedValues.planned_weight });
        }
      } else {
        // 其他字段的程序更新，只更新指定字段，不触发联动
        detailForm.setFieldsValue({ [field]: value });
      }
    }
  };

  // 添加明细
  const addDetail = async () => {
    setCurrentDetail(null);
    detailForm.resetFields();
    
    // 确保产品数据已加载
    await ensureProductsLoaded();
    
    setDetailModalVisible2(true);
  };

  // 选择产品
  const selectProducts = async () => {
    // 确保产品数据已加载
    await ensureProductsLoaded();
    setSelectedProducts([]);
    setProductSearchText('');
    setProductSelectVisible(true);
  };

  // 确认产品选择
  const confirmProductSelection = () => {
    if (selectedProducts.length === 0) {
      message.warning('请先选择产品');
      return;
    }

    // 为每个选中的产品创建明细行，自动填充产品相关字段
    const newDetails = selectedProducts.map((product, index) => ({
      id: `temp-${Date.now()}-${index}`,
      product_id: product.id,
      product_code: product.product_code || product.code || product.product_code,
      product_name: product.product_name || product.name || product.product_name,
      product_spec: product.specification || product.spec || product.product_spec || product.specifications,
      outbound_quantity: 1, // 默认数量为1
      unit_id: product.unit_id,
      unit: product.unit_id, // 同时设置 unit 字段用于表单显示
      unit_cost: product.standard_cost || product.unit_cost || 0,
      outbound_kg_quantity: 0,
      outbound_m_quantity: 0,
      outbound_roll_quantity: 0,
      box_quantity: 0,
      batch_number: '',
      location_code: product.default_location || '',
      remark: ''
    }));

    setOrderDetails([...orderDetails, ...newDetails]);
    setSelectedProducts([]);
    setProductSelectVisible(false);
    setProductSearchText('');
    message.success(`已添加 ${newDetails.length} 个产品明细`);
  };

  // 编辑明细
  const editDetail = async (record) => {
    setCurrentDetail(record);
    
    // 确保产品数据已加载
    await ensureProductsLoaded();
    
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
                label={`产品 (共${products.length}个)`}
                rules={[{ required: true, message: '请选择产品' }]}
              >
                <Select 
                  showSearch
                  placeholder={products.length > 0 ? "请选择或搜索产品" : "暂无产品数据，请刷新页面"}
                  notFoundContent={products.length === 0 ? "暂无产品数据" : "未找到匹配的产品"}
                  filterOption={(input, option) => {
                    if (!option || !option.children) return false;
                    const text = option.children.toString().toLowerCase();
                    const inputLower = input.toLowerCase();
                    return text.includes(inputLower);
                  }}
                  optionFilterProp="children"
                  onChange={(productId) => {
                    const product = products.find(p => p.id === productId);
                    if (product) {
                      // 自动填充产品相关字段
                      detailForm.setFieldsValue({
                        product_code: product.product_code || product.code || product.product_code,
                        product_name: product.product_name || product.name || product.product_name,
                        product_spec: product.specification || product.spec || product.product_spec || product.specifications,
                        unit: product.unit_id || detailForm.getFieldValue('unit'),
                        unit_cost: product.standard_cost || product.unit_cost || detailForm.getFieldValue('unit_cost') || 0,
                        location_code: product.default_location || detailForm.getFieldValue('location_code') || ''
                      });
                      
                      // 如果有出库数量，重新计算转换值
                      const outboundQuantity = detailForm.getFieldValue('outbound_quantity');
                      if (outboundQuantity) {
                        // 延迟执行，确保单位字段已经更新
                        setTimeout(() => {
                          // 传递产品数据给计算函数
                          const unitId = detailForm.getFieldValue('unit');
                          const unit = units.find(u => u.value === unitId);
                          if (unit) {
                            const plannedValues = calculatePlannedValues(outboundQuantity, unit.label, product, product.specification || product.spec || product.product_spec || product.specifications);
                            if (plannedValues.planned_meters !== undefined) {
                              detailForm.setFieldsValue({ outbound_m_quantity: plannedValues.planned_meters });
                            }
                            if (plannedValues.planned_weight !== undefined) {
                              detailForm.setFieldsValue({ outbound_kg_quantity: plannedValues.planned_weight });
                            }
                          }
                        }, 0);
                      }
                    }
                  }}
                >
                  {products.map((product, index) => (
                    <Option key={product.id || `product-${index}`} value={product.id || ''}>
                      {(product.product_code || product.code || '未知编码')} - {(product.product_name || product.name || '未知产品')}
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
            <Col span={12}>
              <Form.Item
                name="product_code"
                label="产品编码"
              >
                <Input placeholder="自动填充" disabled />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="product_name"
                label="产品名称"
              >
                <Input placeholder="自动填充" disabled />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="product_spec"
                label="产品规格"
              >
                <Input placeholder="自动填充" disabled />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="location_code"
                label="建议库位"
              >
                <Input placeholder="请输入建议库位" />
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
                  onChange={(value) => updateDetailField('outbound_quantity', value, true)}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="unit" label="单位" rules={[{ required: true, message: '请选择单位' }]}>
                <Select 
                  placeholder="请选择单位" 
                  allowClear
                  onChange={(value) => updateDetailField('unit', value, true)}
                >
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
              <Form.Item name="outbound_kg_quantity" label="出库重量(kg)">
                <InputNumber 
                  placeholder="请输入出库重量" 
                  min={0} 
                  precision={2}
                  style={{ width: '100%' }}
                  onChange={(value) => updateDetailField('outbound_kg_quantity', value, true)}
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
                  onChange={(value) => updateDetailField('outbound_m_quantity', value, true)}
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
            onSelect: (record, selected) => {
              if (selected) {
                setSelectedProducts([...selectedProducts, record]);
              } else {
                setSelectedProducts(selectedProducts.filter(p => p.id !== record.id));
              }
            },
            onSelectAll: (selected, selectedRows, changeRows) => {
              if (selected) {
                const newProducts = changeRows.filter(row => 
                  !selectedProducts.some(p => p.id === row.id)
                );
                setSelectedProducts([...selectedProducts, ...newProducts]);
              } else {
                const changeIds = changeRows.map(row => row.id);
                setSelectedProducts(selectedProducts.filter(p => !changeIds.includes(p.id)));
              }
            }
          }}
          columns={[
            {
              title: '产品编码',
              dataIndex: 'product_code',
              key: 'product_code',
              render: (text, record) => text || record.code || '未知编码'
            },
            {
              title: '产品名称',
              dataIndex: 'product_name',
              key: 'product_name',
              render: (text, record) => text || record.name || '未知产品'
            },
            {
              title: '规格',
              dataIndex: 'specification',
              key: 'specification',
              render: (text, record) => text || record.spec || '-'
            },
            {
              title: '单位',
              dataIndex: 'unit',
              key: 'unit',
              render: (text) => text
            }
          ]}
          dataSource={(() => {
            if (!productSearchText.trim()) return products;
            const searchLower = productSearchText.toLowerCase();
            return products.filter(product => {
              const code = (product.product_code || product.code || '').toLowerCase();
              const name = (product.product_name || product.name || '').toLowerCase();
              const spec = (product.specification || product.spec || '').toLowerCase();
              return code.includes(searchLower) || 
                     name.includes(searchLower) || 
                     spec.includes(searchLower);
            });
          })()}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => {
              const displayText = productSearchText.trim() ? 
                `搜索到 ${total} 条记录` : 
                `共 ${total} 条记录`;
              return displayText;
            }
          }}
          size="small"
          scroll={{ y: 400 }}
        />
        <div style={{ marginTop: 16, textAlign: 'right' }}>
          已选择 {selectedProducts.length} 个产品
        </div>
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