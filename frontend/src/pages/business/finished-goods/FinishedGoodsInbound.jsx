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
                      console.log(detailForm.getFieldsValue());
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
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="unit_id"
                label="单位"
                rules={[{ required: true, message: '请选择单位' }]}
              >
                <Select placeholder="请选择单位" allowClear>
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
                  precision={3}
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
                  precision={3}
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
                  precision={3}
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
                  precision={3}
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