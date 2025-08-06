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
  FilterOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import { finishedGoodsInboundService, baseDataService } from '../../../api/business/inventory/finishedGoodsInbound';
import request from '../../../utils/request';

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


const FinishedGoodsInbound = () => {
  // 状态管理
  const [inboundOrders, setInboundOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
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
  const [customers, setCustomers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [employees, setEmployees] = useState([]);
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
  }, [baseDataLoading]);

  // 确保产品数据已加载的函数
  const ensureProductsLoaded = useCallback(async () => {
    if (products.length === 0 && !baseDataLoading) {
      await fetchBaseData();
    }
  }, [products.length, baseDataLoading, fetchBaseData]);

  // 初始化数据 - 只保留一个useEffect
  useEffect(() => {
    fetchInboundOrders();
    fetchBaseData();
  }, []);

  // 监听分页和筛选条件变化
  useEffect(() => {
    fetchInboundOrders();
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

  // 重置搜索
  const handleReset = () => {
    searchForm.resetFields();
    setSearchParams({});
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  // 刷新数据
  const handleRefresh = () => {
    fetchInboundOrders();
    fetchBaseData(); // 同时刷新基础数据
  };

  const fetchInboundOrders = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.current,
        page_size: pagination.pageSize,
        ...filters,
        ...searchParams
      };
      
      const response = await finishedGoodsInboundService.getInboundOrderList(params);
      
      if (response.data?.success) {
        const orderData = response.data.data;
        setInboundOrders(orderData?.items || []);
        setPagination(prev => ({
          ...prev,
          total: orderData?.total || 0
        }));
      } else {
        message.error(response.data?.message || '获取入库单列表失败');
      }
    } catch (error) {
      message.error('获取入库单列表失败');
      setInboundOrders([]);
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
      title: '入库单号',
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
      title: '入库人',
      dataIndex: 'inbound_person',
      key: 'inbound_person',
      width: 100,
      render: (text, record) => {
        // 优先显示后端返回的员工姓名
        if (text) return text;
        // 后备方案：根据ID查找
        if (record.inbound_person_id && employees.length > 0) {
          const employee = employees.find(emp => emp.id === record.inbound_person_id);
          return employee ? (employee.employee_name || employee.name) : '未知员工';
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
      width: 250,
      render: (text) => {
        if (!text) return '-';
        try {
          // 将UTC时间转换为本地时间显示
          const localTime = dayjs.utc(text).local();
          return (
            <div style={{ whiteSpace: 'nowrap' }}>
              <div>{localTime.format('YYYY-MM-DD  HH:mm:ss')}</div>
            </div>
          );
        } catch (error) {
          return text;
        }
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => viewOrder(record)}
            size="small"
          >
            查看
          </Button>
          {record.status === 'draft' && (
            <Button 
              type="link" 
              icon={<EditOutlined />} 
              onClick={() => editOrder(record)}
              size="small"
            >
              编辑
            </Button>
          )}
          {record.status === 'confirmed' && record.approval_status === 'approved' && (
            <Button 
              type="link" 
              icon={<PlayCircleOutlined />} 
              onClick={() => executeOrder(record)}
              size="small"
            >
              执行
            </Button>
          )}
          {(record.approval_status === 'pending' || record.approval_status === 'rejected') && record.status !== 'completed' && record.status !== 'cancelled' && (
            <>
              <Button 
                type="link" 
                icon={<CheckOutlined />} 
                onClick={() => approveOrder(record, 'approved')}
                size="small"
              >
                {record.approval_status === 'rejected' ? '重新审核' : '审核'}
              </Button>
              <Button 
                type="link" 
                danger
                icon={<CloseOutlined />} 
                onClick={() => approveOrder(record, 'rejected')}
                size="small"
              >
                拒绝
              </Button>
            </>
          )}
          {record.status !== 'completed' && record.status !== 'cancelled' && (
            <Popconfirm
              title="确定要取消这个入库单吗？"
              onConfirm={() => cancelOrder(record)}
              okText="确定"
              cancelText="取消"
            >
              <Button 
                type="link" 
                danger
                icon={<DeleteOutlined />}
                size="small"
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
      width: 120
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 150
    },
    {
      title: '产品规格',
      dataIndex: 'product_spec',
      key: 'product_spec',
      width: 120
    },
    {
      title: '入库数',
      dataIndex: 'inbound_quantity',
      key: 'inbound_quantity',
      width: 100,
      render: (text, record) => {
        const unit = units.find(unit => unit.value === record.unit_id);
        return `${text} ${unit?.label || ''}`;
      }
    },
    {
      title: '入库kg数',
      dataIndex: 'inbound_kg_quantity',
      key: 'inbound_kg_quantity',
      width: 100,
      render: (text) => text ? `${text} kg` : '-'
    },
    {
      title: '入库m数',
      dataIndex: 'inbound_m_quantity',
      key: 'inbound_m_quantity',
      width: 100,
      render: (text) => text ? `${text} m` : '-'
    },
    {
      title: '入库卷数',
      dataIndex: 'inbound_roll_quantity',
      key: 'inbound_roll_quantity',
      width: 100,
      render: (text) => text ? `${text} 卷` : '-'
    },
    {
      title: '装箱数',
      dataIndex: 'box_quantity',
      key: 'box_quantity',
      width: 100,
      render: (text) => text ? `${text} 箱` : '-'
    },
    {
      title: '批次号',
      dataIndex: 'batch_number',
      key: 'batch_number',
      width: 120
    },
    {
      title: '建议库位',
      dataIndex: 'location_code',
      key: 'location_code',
      width: 100
    },
    {
      title: '单位成本',
      dataIndex: 'unit_cost',
      key: 'unit_cost',
      width: 100,
      render: (text) => text ? `¥${text}` : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          {!isViewMode && (
            <>
              <Button 
                type="link" 
                icon={<EditOutlined />} 
                onClick={() => editDetail(record)}
                size="small"
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
                  danger
                  icon={<DeleteOutlined />}
                  size="small"
                >
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
          {isViewMode && (
            <span style={{ color: '#999' }}>仅查看</span>
          )}
        </Space>
      )
    }
  ];

  // 事件处理函数
  const handleCreateOrder = () => {
    setCurrentOrder(null);
    setIsViewMode(false); // 设置为编辑模式
    form.resetFields();
    setOrderDetails([]); // 清空明细数据
    // 设置默认值
    form.setFieldsValue({
      order_date: dayjs(), // 默认当前日期
      order_type: 'finished_goods' // 默认成品入库
    });
    setModalVisible(true);
  };

  const viewOrder = async (record) => {
    setCurrentOrder(record);
    setIsViewMode(true); // 设置为查看模式
    try {
      const response = await finishedGoodsInboundService.getInboundOrderDetails(record.id);
      
      // 检查响应格式
      if (response && response.data && response.data.success !== false) {
        const details = response.data?.data || response.data || [];
        setOrderDetails(details);
        if (details.length === 0) {
          message.info('该入库单暂无明细记录');
        }
      } else {
        const errorMsg = response?.data?.error || response?.error || response?.message || '获取入库单明细失败';
        console.error('获取明细失败:', errorMsg);
      }
    } catch (error) {
      console.error('获取入库单明细异常:', error);
      let errorMsg = '获取入库单明细失败';
      if (error.response) {
        console.error('错误响应:', error.response);
        errorMsg = error.response.data?.error || error.response.data?.message || `HTTP ${error.response.status}: ${error.response.statusText}`;
      } else if (error.request) {
        console.error('请求错误:', error.request);
        errorMsg = '网络请求失败，请检查网络连接';
      } else {
        errorMsg = error.message || errorMsg;
      }
    }
    setDetailModalVisible(true);
  };

  const editOrder = async (record) => {
    setCurrentOrder(record);
    setIsViewMode(false); // 设置为编辑模式
    try{
      const response = await finishedGoodsInboundService.getInboundOrderDetails(record.id);
      if (response && response.data && response.data.success !== false) {
        const details = response.data?.data || response.data || [];
        setOrderDetails(details);
        if (details.length === 0) {
          message.info('该入库单暂无明细记录');
        }
      } else {
        const errorMsg = response?.data?.error || response?.error || response?.message || '获取入库单明细失败';
        console.error('获取明细失败:', errorMsg);
      }
    }catch(error){
      console.error('获取入库单明细异常:', error);
    }
    form.setFieldsValue({
      ...record,
      order_date: record.order_date ? dayjs(record.order_date) : null
    });
    setModalVisible(true);
  };

  const executeOrder = async (record) => {
    try {
      const response = await finishedGoodsInboundService.executeInboundOrder(record.id);
      
      // 修复响应数据访问
      if (response.data?.success) {
        message.success('入库单执行成功');
        fetchInboundOrders();
      } else {
        message.error(response.data?.message || response.message || '执行入库单失败');
      }
    } catch (error) {
      console.error('执行入库单失败:', error);
      message.error('执行入库单失败');
    }
  };

  const approveOrder = async (record, status) => {
    try {
      const response = await finishedGoodsInboundService.approveInboundOrder(record.id, {
        approval_status: status,
        approval_notes: status === 'approved' ? '审核通过' : '审核拒绝'
      });
      
      // 修复响应数据访问
      if (response.data?.success || response.success) {
        message.success(status === 'approved' ? '审核通过' : '审核拒绝');
        fetchInboundOrders();
      } else {
        message.error(response.data?.message || response.message || '审核失败');
      }
    } catch (error) {
      console.error('审核失败:', error);
      message.error('审核失败');
    }
  };

  const cancelOrder = async (record) => {
    try {
      const response = await finishedGoodsInboundService.cancelInboundOrder(record.id, {
        cancel_reason: '用户取消'
      });
      
      // 修复响应数据访问
      if (response.data?.success || response.success) {
        message.success('入库单已取消');
        fetchInboundOrders();
      } else {
        message.error(response.data?.message || response.message || '取消入库单失败');
      }
    } catch (error) {
      console.error('取消入库单失败:', error);
      message.error('取消入库单失败');
    }
  };

  const handleSubmit = async (values) => {
    try {
      const formData = {
        ...values,
        order_date: values.order_date ? values.order_date.format('YYYY-MM-DD') : null
      };
      
      let response;
      if (currentOrder) {
        // 更新入库单
        response = await finishedGoodsInboundService.updateInboundOrder(currentOrder.id, formData);
        if (response.data?.success) {
          message.success('入库单更新成功');
        } else {
          message.error(response.data?.message || '更新入库单失败');
          return;
        }
      } else {
        // 创建入库单
        response = await finishedGoodsInboundService.createInboundOrder(formData);
        
        if (response.data?.success) {
          const newOrderId = response.data.data?.id;
          
          // 如果有明细数据，保存明细
          if (orderDetails.length > 0) {
            for (const detail of orderDetails) {
              if (detail.id.toString().startsWith('temp-')) {
                // 只保存临时明细
                const detailData = { ...detail };
                delete detailData.id; // 删除临时ID
                
                try {
                  await finishedGoodsInboundService.createInboundOrderDetail(newOrderId, detailData);
                } catch (detailError) {
                  console.error('保存明细失败:', detailError);
                  // 继续保存其他明细，不中断流程
                }
              }
            }
          }
          
          message.success('入库单创建成功');
          setOrderDetails([]); // 清空明细数据
        } else {
          message.error(response.data?.message || response.message || '创建入库单失败');
          return;
        }
      }
      
      setModalVisible(false);
      fetchInboundOrders();
    } catch (error) {
      console.error('保存失败:', error);
      message.error(`保存失败: ${error.message || error}`);
    }
  };

  const addDetail = async () => {
    setCurrentDetail(null);
    detailForm.resetFields();
    
    // 确保产品数据已加载
    await ensureProductsLoaded();
    
    setDetailModalVisible2(true);
  };

  // 批量选择产品
  const selectProducts = async () => {
    // 确保产品数据已加载
    await ensureProductsLoaded();
    setProductSelectVisible(true);
  };

  // 确认选择产品
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
      inbound_quantity: 1, // 默认数量为1
      unit_id: product.unit_id,
      unit_cost: product.standard_cost || product.unit_cost || 0,
      inbound_kg_quantity: 0,
      inbound_m_quantity: 0,
      inbound_roll_quantity: 0,
      box_quantity: 0,
      batch_number: '',
      location_code: product.default_location || ''
    }));

    setOrderDetails([...orderDetails, ...newDetails]);
    setSelectedProducts([]);
    setProductSelectVisible(false);
    setProductSearchText('');
    message.success(`已添加 ${newDetails.length} 个产品明细`);
  };

  const editDetail = async (record) => {
    setCurrentDetail(record);
    detailForm.setFieldsValue(record);
    
    // 确保产品数据已加载
    await ensureProductsLoaded();
    
    setDetailModalVisible2(true);
  };

  const deleteDetail = async (record) => {
    try {
      if (currentOrder && !record.id.toString().startsWith('temp-')) {
        // 如果有入库单且不是临时记录，调用API删除
        const response = await finishedGoodsInboundService.deleteInboundOrderDetail(
          currentOrder.id, 
          record.id
        );
        
        if (response.data?.success) {
          const newDetails = orderDetails.filter(item => item.id !== record.id);
          setOrderDetails(newDetails);
          message.success('明细删除成功');
        } else {
          message.error(response.message || '删除明细失败');
        }
      } else {
        // 新建模式下或临时记录，直接从本地数据删除
        const newDetails = orderDetails.filter(item => item.id !== record.id);
        setOrderDetails(newDetails);
        message.success('明细删除成功');
      }
    } catch (error) {
      console.error('删除明细失败:', error);
      message.error('删除明细失败');
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

  // 根据计划米数计算入库数量
  const calculateInboundQuantityFromPlannedMeters = (plannedMeters, unitName, productData = null, specification = null) => {
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
      // 根据单位类型计算入库数量
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
      console.error('计算入库数量时出错:', error);
      return undefined;
    }
    
    return undefined;
  };

  // 根据计划重量计算入库数量
  const calculateInboundQuantityFromPlannedWeight = (plannedWeight, unitName, productData = null, specification = null) => {
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
      // 根据单位类型计算入库数量
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
      console.error('计算入库数量时出错:', error);
      return undefined;
    }
    
    return undefined;
  };

  // 更新明细字段的通用函数，实现三个字段的完全同步
  const updateDetailField = (field, value, isUserInput = true) => {
    const currentValues = detailForm.getFieldsValue();
    const productId = currentValues.product_id;
    const unitId = currentValues.unit_id;
    
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
      if (field === 'inbound_quantity') {
        // 用户修改了入库数量，计算kg数和m数
        detailForm.setFieldsValue({ [field]: value });
        
        const plannedValues = calculatePlannedValues(value, unitName, productData, specification);
        
        if (plannedValues.planned_meters !== undefined) {
          detailForm.setFieldsValue({ inbound_m_quantity: plannedValues.planned_meters });
        }
        if (plannedValues.planned_weight !== undefined) {
          detailForm.setFieldsValue({ inbound_kg_quantity: plannedValues.planned_weight });
        }
      }
      else if (field === 'inbound_m_quantity') {
        // 用户修改了m数，计算入库数量和kg数
        detailForm.setFieldsValue({ [field]: value });
        
        const calculatedQuantity = calculateInboundQuantityFromPlannedMeters(value, unitName, productData, specification);
        
        if (calculatedQuantity !== undefined && calculatedQuantity !== null && !isNaN(calculatedQuantity) && isFinite(calculatedQuantity)) {
          detailForm.setFieldsValue({ inbound_quantity: calculatedQuantity });
          
          const plannedValues = calculatePlannedValues(calculatedQuantity, unitName, productData, specification);
          if (plannedValues.planned_weight !== undefined) {
            detailForm.setFieldsValue({ inbound_kg_quantity: plannedValues.planned_weight });
          }
        } else {
          detailForm.setFieldsValue({ 
            inbound_quantity: undefined,
            inbound_kg_quantity: undefined 
          });
        }
      }
      else if (field === 'inbound_kg_quantity') {
        // 用户修改了kg数，计算入库数量和m数
        detailForm.setFieldsValue({ [field]: value });
        
        const calculatedQuantity = calculateInboundQuantityFromPlannedWeight(value, unitName, productData, specification);
        
        if (calculatedQuantity !== undefined && calculatedQuantity !== null && !isNaN(calculatedQuantity) && isFinite(calculatedQuantity)) {
          detailForm.setFieldsValue({ inbound_quantity: calculatedQuantity });
          
          const plannedValues = calculatePlannedValues(calculatedQuantity, unitName, productData, specification);
          if (plannedValues.planned_meters !== undefined) {
            detailForm.setFieldsValue({ inbound_m_quantity: plannedValues.planned_meters });
          }
        } else {
          detailForm.setFieldsValue({ 
            inbound_quantity: undefined,
            inbound_m_quantity: undefined 
          });
        }
      }
      else if (field === 'unit_id') {
        // 用户修改了单位，重新计算所有相关字段
        detailForm.setFieldsValue({ [field]: value });
        
        const quantity = currentValues.inbound_quantity || 0;
        const plannedValues = calculatePlannedValues(quantity, unitName, productData, specification);
        if (plannedValues.planned_meters !== undefined) {
          detailForm.setFieldsValue({ inbound_m_quantity: plannedValues.planned_meters });
        }
        if (plannedValues.planned_weight !== undefined) {
          detailForm.setFieldsValue({ inbound_kg_quantity: plannedValues.planned_weight });
        }
      }
      else {
        // 其他字段，只更新当前字段
        detailForm.setFieldsValue({ [field]: value });
      }
    } else {
      // 程序计算更新，但如果是重新计算转换值，则进行联动
      if (field === 'inbound_quantity') {
        detailForm.setFieldsValue({ [field]: value });
        
        const plannedValues = calculatePlannedValues(value, unitName, productData, specification);
        if (plannedValues.planned_meters !== undefined) {
          detailForm.setFieldsValue({ inbound_m_quantity: plannedValues.planned_meters });
        }
        if (plannedValues.planned_weight !== undefined) {
          detailForm.setFieldsValue({ inbound_kg_quantity: plannedValues.planned_weight });
        }
      } else {
        // 其他字段的程序更新，只更新指定字段，不触发联动
        detailForm.setFieldsValue({ [field]: value });
      }
    }
  };

  const handleDetailSubmit = async (values) => {
    try {
      if (currentDetail) {
        // 更新明细
        if (currentOrder) {
          // 如果有入库单，调用API更新
          const response = await finishedGoodsInboundService.updateInboundOrderDetail(
            currentOrder.id, 
            currentDetail.id, 
            values
          );
          if (response.data?.success) {
            const newDetails = orderDetails.map(item => 
              item.id === currentDetail.id ? { ...item, ...values } : item
            );
            setOrderDetails(newDetails);
            message.success('明细更新成功');
          } else {
            message.error(response.message || '更新明细失败');
            return;
          }
        } else {
          // 新建模式下，直接更新本地数据
          const newDetails = orderDetails.map(item => 
            item.id === currentDetail.id ? { ...item, ...values } : item
          );
          setOrderDetails(newDetails);
            message.success('明细更新成功');
        }
      } else {
        // 添加明细
        if (currentOrder) {
          // 如果有入库单，调用API添加
          const response = await finishedGoodsInboundService.createInboundOrderDetail(
            currentOrder.id, 
            values
          );
          if (response.data?.success) {
            const newDetail = {
              id: response.data.data.id || Date.now().toString(),
              ...values
            };
            setOrderDetails([...orderDetails, newDetail]);
            message.success('明细添加成功');
          } else {
            message.error(response.message || '添加明细失败');
            return;
          }
        } else {
          // 新建模式下，直接添加到本地数据
          const newDetail = {
            id: `temp-${Date.now()}`,
            ...values
          };
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
      {/* 搜索筛选区域 */}
      <StyledCard 
        title={
          <Space>
            <FilterOutlined />
            筛选条件
          </Space>
        }
        size="small"
        style={{ marginBottom: 16 }}
      >
        <Collapse ghost>
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
                      placeholder="输入入库单号、入库人等"
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
                  <Form.Item name="inbound_person_id" label="入库人">
                    <Select placeholder="选择入库人">
                      {employees.map((employee, index) => (
                        <Option key={employee.id || `employee-${index}`} value={employee.id}>
                          {employee.employee_name || employee.name || '未知员工'}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="department_id" label="部门">
                    <Select placeholder="选择部门">
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
      </StyledCard>

      {/* 入库单列表 */}
      <StyledCard 
        title={
          <Space>
            <FileTextOutlined />
            成品入库管理
          </Space>
        }
        extra={
          <Space>
            <ActionButton 
              icon={<ReloadOutlined />} 
              onClick={handleRefresh}
            >
              刷新
            </ActionButton>
            <ActionButton 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={handleCreateOrder}
            >
              新建入库单
            </ActionButton>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={inboundOrders}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              setPagination(prev => ({
                ...prev,
                current: page,
                pageSize: pageSize
              }));
            }
          }}
        />
      </StyledCard>

      {/* 新建/编辑入库单模态框 */}
      <Modal
        title={currentOrder ? '编辑入库单' : '新建入库单'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={1200}
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
                label="仓库"
                rules={[{ required: true, message: '请选择仓库' }]}
              >
                <Select placeholder="请选择仓库">
                  {warehouses.map((warehouse, index) => (
                    <Option key={warehouse.id || `warehouse-${index}`} value={warehouse.id || ''}>
                      {warehouse.warehouse_name || warehouse.name || '未知仓库'}
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
                <DatePicker 
                  style={{ width: '100%' }} 
                  format="YYYY-MM-DD"
                  showTime={false}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="inbound_person_id"
                label="入库人"
              >
                <Select 
                  placeholder="请选择入库人"
                  onChange={(value) => {
                    // 根据选择的员工自动填充部门
                    if (value && employees.length > 0) {
                      const selectedEmployee = employees.find(emp => emp.id === value);
                      if (selectedEmployee && selectedEmployee.department_id) {
                        form.setFieldsValue({
                          department_id: selectedEmployee.department_id
                        });
                      }
                    }
                  }}
                >
                  {employees.map((employee, index) => (
                    <Option key={employee.id || `employee-${index}`} value={employee.id}>
                      {employee.employee_name || employee.name || '未知员工'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="department_id"
                label="部门"
              >
                <Select placeholder="请选择部门">
                  {departments.map((dept, index) => (
                    <Option key={dept.id || `dept-${index}`} value={dept.id}>
                      {dept.department_name || dept.name || '未知部门'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="pallet_barcode"
                label="托盘条码"
              >
                <Input placeholder="请输入托盘条码" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="pallet_count"
                label="托盘套数"
              >
                <InputNumber 
                  placeholder="请输入托盘套数" 
                  style={{ width: '100%' }}
                  min={0}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="notes"
            label="备注"
          >
            <TextArea rows={3} placeholder="请输入备注信息" />
          </Form.Item>

              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit">
                    保存
                  </Button>
                  <Button onClick={() => setModalVisible(false)}>
                    取消
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </TabPane>
          
          <TabPane tab="产品明细" key="2">
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
                  type="default" 
                  icon={<PlusOutlined />} 
                  onClick={selectProducts}
                >
                  批量选择产品
                </Button>
              </Space>
            </div>
            <DetailTable
              columns={detailColumns}
              dataSource={orderDetails}
              rowKey="id"
              scroll={{ x: 1000 }}
              pagination={false}
            />
          </TabPane>
        </Tabs>
      </Modal>

      {/* 查看入库单详情模态框 */}
      <Modal
        title={`入库单详情 - ${currentOrder?.order_number}`}
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setIsViewMode(false); // 重置查看模式状态
        }}
        footer={null}
        width={1200}
      >
        {currentOrder && (
          <Tabs defaultActiveKey="1">
            <TabPane tab="基本信息" key="1">
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>入库单号：</Text>
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
                  <Text strong>入库人：</Text>
                  <Text>
                    {(() => {
                      if (!currentOrder.inbound_person_id) return '-';
                      const employee = employees.find(emp => emp.id === currentOrder.inbound_person_id);
                      return employee ? (employee.employee_name || employee.name) : '未知员工';
                    })()}
                  </Text>
                </Col>
                <Col span={8}>
                  <Text strong>部门：</Text>
                  <Text>
                    {(() => {
                      if (!currentOrder.department_id) return '-';
                      const department = departments.find(dept => dept.id === currentOrder.department_id);
                      return department ? (department.department_name || department.name) : '未知部门';
                    })()}
                  </Text>
                </Col>
                <Col span={8}>
                  <Text strong>托盘套数：</Text>
                  <Text>{currentOrder.pallet_count} 套</Text>
                </Col>
              </Row>
              <Divider />
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>单据状态：</Text>
                  {getStatusTag(currentOrder.status)}
                </Col>
                <Col span={8}>
                  <Text strong>审核状态：</Text>
                  {getApprovalStatusTag(currentOrder.approval_status)}
                </Col>
                <Col span={8}>
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
              </Row>
            </TabPane>
            
            <TabPane tab="入库明细" key="2">
              {!isViewMode && (
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
                      type="default" 
                      icon={<PlusOutlined />} 
                      onClick={selectProducts}
                    >
                      批量选择产品
                    </Button>
                  </Space>
                </div>
              )}
              <DetailTable
                columns={detailColumns}
                dataSource={orderDetails}
                rowKey="id"
                scroll={{ x: 1000 }}
                pagination={false}
              />
            </TabPane>
          </Tabs>
        )}
      </Modal>

      {/* 添加/编辑明细模态框 */}
      <Modal
        title={currentDetail ? '编辑明细' : '添加明细'}
        open={detailModalVisible2}
        onCancel={() => setDetailModalVisible2(false)}
        footer={null}
        width={800}
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
                  onChange={(value) => {
                    const product = products.find(p => p.id === value);
                    if (product) {
                      // 自动填充产品相关字段
                      detailForm.setFieldsValue({
                        product_code: product.product_code || product.code || product.product_code,
                        product_name: product.product_name || product.name || product.product_name,
                        product_spec: product.specification || product.spec || product.product_spec || product.specifications,
                        unit_id: product.unit_id || detailForm.getFieldValue('unit_id'),
                        unit_cost: product.standard_cost || product.unit_cost || detailForm.getFieldValue('unit_cost') || 0,
                        location_code: product.default_location || detailForm.getFieldValue('location_code') || ''
                      });
                      
                      // 如果有入库数量，重新计算转换值
                      const inboundQuantity = detailForm.getFieldValue('inbound_quantity');
                      if (inboundQuantity) {
                        // 延迟执行，确保单位字段已经更新
                        setTimeout(() => {
                          // 传递产品数据给计算函数
                          const unitId = detailForm.getFieldValue('unit_id');
                          const unit = units.find(u => u.value === unitId);
                          if (unit) {
                            const plannedValues = calculatePlannedValues(inboundQuantity, unit.label, product, product.specification || product.spec || product.product_spec || product.specifications);
                            if (plannedValues.planned_meters !== undefined) {
                              detailForm.setFieldsValue({ inbound_m_quantity: plannedValues.planned_meters });
                            }
                            if (plannedValues.planned_weight !== undefined) {
                              detailForm.setFieldsValue({ inbound_kg_quantity: plannedValues.planned_weight });
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
                name="product_code"
                label="产品编码"
              >
                <Input placeholder="自动填充" disabled />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="product_name"
                label="产品名称"
              >
                <Input placeholder="自动填充" disabled />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="product_spec"
                label="产品规格"
              >
                <Input placeholder="自动填充" disabled />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="inbound_quantity"
                label="入库数"
                rules={[{ required: true, message: '请输入入库数' }]}
              >
                <InputNumber 
                  placeholder="请输入入库数" 
                  style={{ width: '100%' }}
                  min={0}
                  onChange={(value) => updateDetailField('inbound_quantity', value, true)}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="unit_id"
                label="单位"
                rules={[{ required: true, message: '请选择单位' }]}
              >
                <Select 
                  placeholder="请选择单位" 
                  allowClear
                  onChange={(value) => updateDetailField('unit_id', value, true)}
                >
                  {units.map(unit => (
                    <Option key={unit.value} value={unit.value}>{unit.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="unit_cost"
                label="单位成本"
              >
                <InputNumber 
                  placeholder="请输入单位成本" 
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="inbound_kg_quantity"
                label="入库kg数"
              >
                <InputNumber 
                  placeholder="请输入kg数" 
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                  onChange={(value) => updateDetailField('inbound_kg_quantity', value, true)}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="inbound_m_quantity"
                label="入库m数"
              >
                <InputNumber 
                  placeholder="请输入m数" 
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                  onChange={(value) => updateDetailField('inbound_m_quantity', value, true)}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="inbound_roll_quantity"
                label="入库卷数"
              >
                <InputNumber 
                  placeholder="请输入卷数" 
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="box_quantity"
                label="装箱数"
              >
                <InputNumber 
                  placeholder="请输入装箱数" 
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="batch_number"
                label="批次号"
              >
                <Input placeholder="请输入批次号" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="location_code"
                label="建议库位"
              >
                <Input placeholder="请输入建议库位" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="notes"
            label="备注"
          >
            <TextArea rows={2} placeholder="请输入备注信息" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
              <Button onClick={() => setDetailModalVisible2(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 产品选择模态框 */}
      <Modal
        title="选择产品"
        open={productSelectVisible}
        onCancel={() => {
          setProductSelectVisible(false);
          setProductSearchText('');
        }}
        onOk={confirmProductSelection}
        width={1000}
        okText="确认选择"
        cancelText="取消"
      >
        <div style={{ marginBottom: 16 }}>
          <Input.Search
            placeholder="搜索产品编码或产品名称"
            allowClear
            value={productSearchText}
            onChange={(e) => setProductSearchText(e.target.value)}
            style={{ width: 300 }}
          />
        </div>
        <Table
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
        />
        <div style={{ marginTop: 16, textAlign: 'right' }}>
          已选择 {selectedProducts.length} 个产品
        </div>
      </Modal>
    </PageContainer>
  );
};

export default FinishedGoodsInbound; 