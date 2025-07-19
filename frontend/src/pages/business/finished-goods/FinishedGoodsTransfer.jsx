import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Row,
  Col,
  message,
  Popconfirm,
  Divider,
  Descriptions,
  Typography
} from 'antd';
import {
  PlusOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckOutlined,
  SendOutlined,
  InboxOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  getProductTransferOrders,
  createProductTransferOrder,
  getProductTransferOrder,
  updateProductTransferOrder,
  getProductTransferOrderDetails,
  addProductTransferOrderDetail,
  updateProductTransferOrderDetail,
  deleteProductTransferOrderDetail,
  confirmProductTransferOrder,
  executeProductTransferOrder,
  receiveProductTransferOrder,
  cancelProductTransferOrder,
  getWarehouseProductInventory
} from '../../../api/business/inventory/productTransfer';
import { baseDataService } from '../../../api/business/inventory/finishedGoodsInbound';
import { getProductById } from '../../../api/base-archive/base-data/productManagement';

const { Option } = Select;
const { TextArea } = Input;
const { Title } = Typography;

const FinishedGoodsTransfer = () => {
  // 状态
  const [loading, setLoading] = useState(false);
  const [orders, setOrders] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  });
  
  // 模态框状态
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [productModalVisible, setProductModalVisible] = useState(false);
  
  // 表单和数据
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const [productForm] = Form.useForm();
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [orderDetails, setOrderDetails] = useState([]);
  const [availableProducts, setAvailableProducts] = useState([]);
  const [editingDetail, setEditingDetail] = useState(null);
  
  // 基础数据
  const [warehouses, setWarehouses] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [baseDataLoading, setBaseDataLoading] = useState(false);

  // 页面加载
  useEffect(() => {
    fetchOrders();
    fetchBaseData();
  }, []);

  // 获取调拨单列表
  const fetchOrders = async (params = {}) => {
    setLoading(true);
    try {
      const queryParams = {
        page: pagination.current,
        per_page: pagination.pageSize,
        ...params
      };
      
      const response = await getProductTransferOrders(queryParams);
      if (response.data.success) {
        setOrders(response.data.data.orders);
        setPagination({
          ...pagination,
          total: response.data.data.pagination.total,
          current: response.data.data.pagination.page
        });
      }
    } catch (error) {
      message.error('获取成品调拨单列表失败');
    }
    setLoading(false);
  };

  // 统一的基础数据获取函数
  const fetchBaseData = useCallback(async () => {
    if (baseDataLoading) return; // 防止重复请求
    
    setBaseDataLoading(true);
    try {
      const [warehousesRes, employeesRes, departmentsRes] = await Promise.all([
        baseDataService.getWarehouses({ warehouse_type: 'finished_goods' }),
        baseDataService.getEmployees(),
        baseDataService.getDepartments()
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
    } catch (error) {
      console.error('获取基础数据失败:', error);
      message.error('获取基础数据失败，请检查网络连接');
      // 设置空数组
      setWarehouses([]);
      setEmployees([]);
      setDepartments([]);
    } finally {
      setBaseDataLoading(false);
    }
  }, []);

  // 获取调拨单明细
  const fetchOrderDetails = async (orderId) => {
    try {
      const response = await getProductTransferOrderDetails(orderId);
      if (response.data.success) {
        setOrderDetails(response.data.data);
      }
    } catch (error) {
      message.error('获取调拨单明细失败');
    }
  };


  // 获取可用成品库存
  const fetchAvailableProducts = async (warehouseId) => {
    try {
      const response = await getWarehouseProductInventory(warehouseId);
      if (response.data.success) {
        const rawData = response.data.data;
        
        // 确保数据是数组格式
        let processedData = [];
        if (Array.isArray(rawData)) {
          processedData = rawData;
        } else if (rawData && Array.isArray(rawData.items)) {
          processedData = rawData.items;
        } else if (rawData && Array.isArray(rawData.data)) {
          processedData = rawData.data;
        }
        
        
        if (processedData.length === 0) {
          setAvailableProducts([]);
          return;
        }
        
        // 合并库存数据和产品信息
        const productPromises = processedData.map(async (item) => {
          try {
            const productResponse = await getProductById(item.product_id);
            const product = productResponse.data.success ? productResponse.data.data : {};
            
            return {
              product_id: item.product_id,
              product_code: product.product_code || item.product_code || '',
              product_name: product.product_name || item.product_name || '未知产品',
              product_spec: product.specification || item.product_spec || '',
              current_quantity: item.current_quantity || item.quantity || 0,
              available_quantity: item.available_quantity || item.current_quantity || item.quantity || 0,
              unit: product.base_unit || item.unit || '个',
              unit_cost: item.unit_cost || item.cost || 0,
              warehouse_id: item.warehouse_id || warehouseId,
              warehouse_name: item.warehouse_name,
              // 添加更多产品信息
              customer_name: product.customer_name || '',
              bag_type_name: product.bag_type_name || ''
            };
          } catch (error) {
            console.error(`获取产品 ${item.product_id} 信息失败:`, error);
            // 如果获取产品信息失败，返回基础库存信息
            return {
              product_id: item.product_id,
              product_code: item.product_code || '',
              product_name: item.product_name || '未知产品',
              product_spec: item.product_spec || '',
              current_quantity: item.current_quantity || item.quantity || 0,
              available_quantity: item.available_quantity || item.current_quantity || item.quantity || 0,
              unit: item.unit || '个',
              unit_cost: item.unit_cost || item.cost || 0,
              warehouse_id: item.warehouse_id || warehouseId,
              warehouse_name: item.warehouse_name,
              customer_name: '',
              bag_type_name: ''
            };
          }
        });
        
        // 等待所有异步操作完成
        const mappedData = await Promise.all(productPromises);
        
        setAvailableProducts(mappedData);
      } else {
        console.error('获取仓库成品库存失败:', response.data.message);
        message.error(response.data.message || '获取仓库成品库存失败');
        setAvailableProducts([]);
      }
    } catch (error) {
      console.error('获取仓库成品库存异常:', error);
      message.error('获取仓库成品库存失败');
      setAvailableProducts([]);
    }
  };

  // 创建调拨单
  const handleCreate = async (values) => {
    try {
      // 处理日期格式
      const submitData = {
        ...values,
        transfer_date: values.transfer_date ? values.transfer_date.format('YYYY-MM-DD') : undefined,
        expected_arrival_date: values.expected_arrival_date ? values.expected_arrival_date.format('YYYY-MM-DD') : undefined
      };
      
      const response = await createProductTransferOrder(submitData);
      if (response.data.success) {
        message.success('成品调拨单创建成功');
        setCreateModalVisible(false);
        form.resetFields();
        fetchOrders();
      } else {
        message.error(response.data.message || '创建失败');
      }
    } catch (error) {
      message.error('创建成品调拨单失败');
    }
  };

  // 查看调拨单详情
  const handleViewDetail = async (order) => {
    setSelectedOrder(order);
    await fetchOrderDetails(order.id);
    setDetailModalVisible(true);
  };

  // 编辑调拨单
  const handleEdit = (order) => {
    setSelectedOrder(order);
    editForm.setFieldsValue({
      ...order,
      transfer_date: order.transfer_date ? dayjs(order.transfer_date) : null,
      expected_arrival_date: order.expected_arrival_date ? dayjs(order.expected_arrival_date) : null
    });
    setEditModalVisible(true);
  };

  // 更新调拨单
  const handleUpdate = async (values) => {
    try {
      const submitData = {
        ...values,
        transfer_date: values.transfer_date ? values.transfer_date.format('YYYY-MM-DD') : undefined,
        expected_arrival_date: values.expected_arrival_date ? values.expected_arrival_date.format('YYYY-MM-DD') : undefined
      };
      
      const response = await updateProductTransferOrder(selectedOrder.id, submitData);
      if (response.data.success) {
        message.success('调拨单更新成功');
        setEditModalVisible(false);
        fetchOrders();
      }
    } catch (error) {
      message.error('更新调拨单失败');
    }
  };

  // 添加成品
  const handleAddProduct = async () => {
    if (!selectedOrder) return;
    
    // 获取调出仓库的成品库存
    await fetchAvailableProducts(selectedOrder.from_warehouse_id);
    
    setEditingDetail(null);
    productForm.resetFields();
    setProductModalVisible(true);
  };

  // 编辑成品明细
  const handleEditProduct = async (detail) => {
    setEditingDetail(detail);
    productForm.setFieldsValue(detail);
    await fetchAvailableProducts(selectedOrder.from_warehouse_id);
    setProductModalVisible(true);
  };

  // 保存成品明细
  const handleSaveProduct = async (values) => {
    try {
      if (editingDetail) {
        // 更新明细
        const response = await updateProductTransferOrderDetail(selectedOrder.id, editingDetail.id, values);
        if (response.data.success) {
          message.success('成品明细更新成功');
        }
      } else {
        // 添加明细
        const response = await addProductTransferOrderDetail(selectedOrder.id, values);
        if (response.data.success) {
          message.success('成品明细添加成功');
        }
      }
      
      setProductModalVisible(false);
      // 刷新明细数据
      await fetchOrderDetails(selectedOrder.id);
      // 刷新调拨单列表以更新总数量
      await fetchOrders();
      
    } catch (error) {
      message.error(editingDetail ? '更新成品明细失败' : '添加成品明细失败');
    }
  };

  // 删除成品明细
  const handleDeleteProduct = async (detailId) => {
    try {
      const response = await deleteProductTransferOrderDetail(selectedOrder.id, detailId);
      if (response.data.success) {
        message.success('成品明细删除成功');
        // 刷新明细数据
        await fetchOrderDetails(selectedOrder.id);
        // 刷新调拨单列表以更新总数量
        await fetchOrders();
      }
    } catch (error) {
      message.error('删除成品明细失败');
    }
  };

  // 确认调拨单
  const handleConfirm = async (orderId) => {
    try {
      const response = await confirmProductTransferOrder(orderId);
      if (response.data.success) {
        message.success('调拨单确认成功');
        fetchOrders();
      } else {
        message.error(response.data.message || '确认失败');
      }
    } catch (error) {
      message.error('确认调拨单失败');
    }
  };

  // 执行调拨单
  const handleExecute = async (orderId) => {
    try {
      const response = await executeProductTransferOrder(orderId);
      if (response.data.success) {
        message.success('调拨单执行成功');
        fetchOrders();
      } else {
        message.error(response.data.message || '执行失败');
      }
    } catch (error) {
      message.error('执行调拨单失败');
    }
  };

  // 收货确认
  const handleReceive = async (orderId) => {
    try {
      const response = await receiveProductTransferOrder(orderId);
      if (response.data.success) {
        message.success('收货确认成功');
        fetchOrders();
      } else {
        message.error(response.data.message || '收货确认失败');
      }
    } catch (error) {
      message.error('收货确认失败');
    }
  };

  // 取消调拨单
  const handleCancel = async (orderId) => {
    try {
      const response = await cancelProductTransferOrder(orderId, { reason: '用户取消' });
      if (response.data.success) {
        message.success('调拨单取消成功');
        fetchOrders();
      } else {
        message.error(response.data.message || '取消失败');
      }
    } catch (error) {
      message.error('取消调拨单失败');
    }
  };

  // 状态标签
  const getStatusTag = (status) => {
    const statusMap = {
      draft: { color: 'default', text: '草稿' },
      confirmed: { color: 'processing', text: '已确认' },
      in_transit: { color: 'warning', text: '运输中' },
      completed: { color: 'success', text: '已完成' },
      cancelled: { color: 'error', text: '已取消' }
    };
    const statusInfo = statusMap[status] || { color: 'default', text: status };
    return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
  };

  // 调拨类型标签
  const getTransferTypeTag = (type) => {
    const typeMap = {
      warehouse: { color: 'blue', text: '仓库调拨' },
      department: { color: 'green', text: '部门调拨' },
      project: { color: 'orange', text: '项目调拨' },
      emergency: { color: 'red', text: '紧急调拨' }
    };
    const typeInfo = typeMap[type] || { color: 'default', text: type };
    return <Tag color={typeInfo.color}>{typeInfo.text}</Tag>;
  };

  // 运输方式文本转换
  const getTransportMethodText = (method) => {
    const methodMap = {
      manual: '人工搬运',
      vehicle: '车辆运输',
      logistics: '物流配送',
      forklift: '叉车运输'
    };
    return methodMap[method] || method || '-';
  };

  // 表格列定义
  const columns = [
    {
      title: '调拨单号',
      dataIndex: 'transfer_number',
      key: 'transfer_number',
      width: 150,
      fixed: 'left'
    },
    {
      title: '调拨类型',
      dataIndex: 'transfer_type',
      key: 'transfer_type',
      width: 100,
      render: (type) => getTransferTypeTag(type)
    },
    {
      title: '调出仓库',
      dataIndex: 'from_warehouse_name',
      key: 'from_warehouse_name',
      width: 120
    },
    {
      title: '调入仓库',
      dataIndex: 'to_warehouse_name',
      key: 'to_warehouse_name',
      width: 120
    },
    {
      title: '调拨人',
      dataIndex: 'transfer_person',
      key: 'transfer_person',
      width: 100
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      width: 100
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      render: (status) => getStatusTag(status)
    },
    {
      title: '总数量',
      dataIndex: 'total_quantity',
      key: 'total_quantity',
      width: 100,
      render: (value) => value || 0
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            {record.status === 'draft' ? '添加调拨明细' : '查看'}
          </Button>
          
          {record.status === 'draft' && (
            <>
              <Button
                type="link"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定要确认这个调拨单吗？"
                onConfirm={() => handleConfirm(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button type="link" icon={<CheckOutlined />}>
                  确认
                </Button>
              </Popconfirm>
            </>
          )}
          
          {record.status === 'confirmed' && (
            <Popconfirm
              title="确定要执行这个调拨单吗？"
              onConfirm={() => handleExecute(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button type="link" icon={<SendOutlined />}>
                执行
              </Button>
            </Popconfirm>
          )}
          
          {record.status === 'in_transit' && (
            <Popconfirm
              title="确定要确认收货吗？"
              onConfirm={() => handleReceive(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button type="link" icon={<InboxOutlined />}>
                收货
              </Button>
            </Popconfirm>
          )}
          
          {record.status !== 'completed' && record.status !== 'cancelled' && (
            <Popconfirm
              title="确定要取消这个调拨单吗？"
              onConfirm={() => handleCancel(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button type="link" danger>
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
      title: '规格',
      dataIndex: 'product_spec',
      key: 'product_spec',
      width: 120
    },
    {
      title: '客户',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 100
    },
    {
      title: '袋型',
      dataIndex: 'bag_type_name',
      key: 'bag_type_name',
      width: 100
    },
    {
      title: '调拨数量',
      dataIndex: 'transfer_quantity',
      key: 'transfer_quantity',
      width: 100
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 60
    },
    {
      title: '库存数量',
      dataIndex: 'available_quantity',
      key: 'available_quantity',
      width: 100
    },
    {
      title: '调出库位',
      dataIndex: 'from_location_code',
      key: 'from_location_code',
      width: 100
    },
    {
      title: '调入库位',
      dataIndex: 'to_location_code',
      key: 'to_location_code',
      width: 100
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          {selectedOrder?.status === 'draft' && (
            <>
              <Button
                type="link"
                size="small"
                onClick={() => handleEditProduct(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定要删除这个明细吗？"
                onConfirm={() => handleDeleteProduct(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button type="link" size="small" danger>
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      )
    }
  ];

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24, fontWeight: 600 }}>成品调拨</Title>
      <Card style={{ borderRadius: 8, boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)', border: 'none' }}>
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              新建调拨单
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={orders}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              setPagination({ ...pagination, current: page, pageSize });
              fetchOrders({ page, per_page: pageSize });
            }
          }}
          scroll={{ x: 1500 }}
        />
      </Card>

      {/* 创建调拨单模态框 */}
      <Modal
        title="新建成品调拨单"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{ transfer_type: 'warehouse' }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="from_warehouse_id"
                label="调出仓库"
                rules={[{ required: true, message: '请选择调出仓库' }]}
              >
                <Select placeholder="请选择调出仓库">
                  {warehouses.map((warehouse, index) => (
                    <Option key={warehouse.id || `from-warehouse-${index}`} value={warehouse.id}>
                      {warehouse.warehouse_name || '未知仓库'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="to_warehouse_id"
                label="调入仓库"
                rules={[
                  { required: true, message: '请选择调入仓库' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('from_warehouse_id') !== value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('调入仓库不能与调出仓库相同'));
                    },
                  }),
                ]}
              >
                <Select placeholder="请选择调入仓库">
                  {warehouses.map((warehouse, index) => (
                    <Option key={warehouse.id || `to-warehouse-${index}`} value={warehouse.id}>
                      {warehouse.warehouse_name || '未知仓库'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="transfer_type"
                label="调拨类型"
                rules={[{ required: true, message: '请选择调拨类型' }]}
              >
                <Select>
                  <Option key="create-transfer-type-warehouse" value="warehouse">仓库调拨</Option>
                  <Option key="create-transfer-type-department" value="department">部门调拨</Option>
                  <Option key="create-transfer-type-project" value="project">项目调拨</Option>
                  <Option key="create-transfer-type-emergency" value="emergency">紧急调拨</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="transfer_person_id" label="调拨人">
                <Select placeholder="请选择调拨人" allowClear
                   onChange={(value) => {
                   // 根据选择的员工自动填充部门
                   const selectedEmployee = employees.find(emp => emp.id === value);
                   if (selectedEmployee && selectedEmployee.department_id) {
                     form.setFieldsValue({
                       department_id: selectedEmployee.department_id
                     });
                   }
                 }}
                >
                  {employees.map((employee, index) => (
                    <Option key={employee.id || `create-employee-${index}`} value={employee.id}>
                      {employee.employee_name || employee.name || employee.label || '未知员工'}
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
                    <Option key={dept.id || `create-dept-${index}`} value={dept.id}>
                      {dept.department_name || dept.label || '未知部门'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="transport_method" label="运输方式">
                <Select placeholder="请选择运输方式" allowClear>
                  <Option key="create-transport-manual" value="manual">人工搬运</Option>
                  <Option key="create-transport-vehicle" value="vehicle">车辆运输</Option>
                  <Option key="create-transport-logistics" value="logistics">物流配送</Option>
                  <Option key="create-transport-forklift" value="forklift">叉车运输</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                name="transfer_date" 
                label="调拨日期"
                initialValue={dayjs()}
              >
                <DatePicker 
                  style={{ width: '100%' }}
                  placeholder="请选择调拨日期"
                  format="YYYY-MM-DD"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="expected_arrival_date" label="预计到达时间">
                <DatePicker 
                  style={{ width: '100%' }}
                  placeholder="请选择预计到达时间"
                  format="YYYY-MM-DD"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="transporter" label="承运人">
            <Input placeholder="请输入承运人" />
          </Form.Item>

          <Form.Item name="notes" label="备注">
            <TextArea rows={3} placeholder="请输入备注" />
          </Form.Item>

          <Form.Item>
            <Space style={{ float: 'right' }}>
              <Button onClick={() => {
                setCreateModalVisible(false);
                form.resetFields();
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                创建
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑调拨单模态框 */}
      <Modal
        title="编辑成品调拨单"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={handleUpdate}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="transfer_type" label="调拨类型">
                <Select>
                  <Option key="edit-transfer-type-warehouse" value="warehouse">仓库调拨</Option>
                  <Option key="edit-transfer-type-department" value="department">部门调拨</Option>
                  <Option key="edit-transfer-type-project" value="project">项目调拨</Option>
                  <Option key="edit-transfer-type-emergency" value="emergency">紧急调拨</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="transfer_person_id" label="调拨人">
                <Select placeholder="请选择调拨人" allowClear>
                  {employees.map((employee, index) => (
                    <Option key={employee.id || `edit-employee-${index}`} value={employee.id}>
                      {employee.employee_name || employee.name || employee.label || '未知员工'}
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
                    <Option key={dept.id || `edit-dept-${index}`} value={dept.id}>
                      {dept.department_name || dept.label || '未知部门'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="transport_method" label="运输方式">
                <Select placeholder="请选择运输方式" allowClear>
                  <Option key="edit-transport-manual" value="manual">人工搬运</Option>
                  <Option key="edit-transport-vehicle" value="vehicle">车辆运输</Option>
                  <Option key="edit-transport-logistics" value="logistics">物流配送</Option>
                  <Option key="edit-transport-forklift" value="forklift">叉车运输</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                name="transfer_date" 
                label="调拨日期"
                initialValue={dayjs()}
              >
                <DatePicker 
                  style={{ width: '100%' }}
                  placeholder="请选择调拨日期"
                  format="YYYY-MM-DD"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="expected_arrival_date" label="预计到达时间">
                <DatePicker 
                  style={{ width: '100%' }}
                  placeholder="请选择预计到达时间"
                  format="YYYY-MM-DD"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="transporter" label="承运人">
            <Input placeholder="请输入承运人" />
          </Form.Item>

          <Form.Item name="notes" label="备注">
            <TextArea rows={3} placeholder="请输入备注" />
          </Form.Item>

          <Form.Item>
            <Space style={{ float: 'right' }}>
              <Button onClick={() => setEditModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                更新
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 调拨单详情模态框 */}
      <Modal
        title="成品调拨单详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="detail-modal-close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={1200}
      >
        {selectedOrder && (
          <>
            <Descriptions bordered column={3} size="small">
              <Descriptions.Item label="调拨单号">{selectedOrder.transfer_number}</Descriptions.Item>
              <Descriptions.Item label="调拨类型">{getTransferTypeTag(selectedOrder.transfer_type)}</Descriptions.Item>
              <Descriptions.Item label="状态">{getStatusTag(selectedOrder.status)}</Descriptions.Item>
              <Descriptions.Item label="调出仓库">{selectedOrder.from_warehouse_name}</Descriptions.Item>
              <Descriptions.Item label="调入仓库">{selectedOrder.to_warehouse_name}</Descriptions.Item>
              <Descriptions.Item label="调拨人">{selectedOrder.transfer_person || '-'}</Descriptions.Item>
              <Descriptions.Item label="部门">{selectedOrder.department || '-'}</Descriptions.Item>
              <Descriptions.Item label="承运人">{selectedOrder.transporter || '-'}</Descriptions.Item>
              <Descriptions.Item label="运输方式">{getTransportMethodText(selectedOrder.transport_method)}</Descriptions.Item>
              <Descriptions.Item label="调拨日期">
                {selectedOrder.transfer_date ? dayjs(selectedOrder.transfer_date).format('YYYY-MM-DD') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="预计到达">
                {selectedOrder.expected_arrival_date ? dayjs(selectedOrder.expected_arrival_date).format('YYYY-MM-DD') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="实际到达">
                {selectedOrder.actual_arrival_date ? dayjs(selectedOrder.actual_arrival_date).format('YYYY-MM-DD') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="备注" span={3}>{selectedOrder.notes || '-'}</Descriptions.Item>
            </Descriptions>

            <Divider />

            <div style={{ marginBottom: 16 }}>
              <Space>
                <Title level={5}>调拨明细</Title>
                {selectedOrder.status === 'draft' && (
                  <Button
                    type="primary"
                    size="small"
                    icon={<PlusOutlined />}
                    onClick={handleAddProduct}
                  >
                    添加成品
                  </Button>
                )}
              </Space>
            </div>

            <Table
              columns={detailColumns}
              dataSource={orderDetails}
              rowKey="id"
              pagination={false}
              size="small"
              scroll={{ x: 1000 }}
            />
          </>
        )}
      </Modal>

      {/* 添加/编辑成品模态框 */}
      <Modal
        title={editingDetail ? "编辑成品明细" : "添加成品明细"}
        open={productModalVisible}
        onCancel={() => {
          setProductModalVisible(false);
          productForm.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={productForm}
          layout="vertical"
          onFinish={handleSaveProduct}
        >
          <Form.Item
            name="product_id"
            label="产品"
            rules={[{ required: true, message: '请选择产品' }]}
          >
            <Select
              placeholder="请选择产品"
              showSearch
              optionFilterProp="children"
              disabled={!!editingDetail}
              onChange={(productId) => {
                const product = Array.isArray(availableProducts) ? availableProducts.find(p => p.product_id === productId) : null;
                if (product) {
                  productForm.setFieldsValue({
                    current_stock: product.current_quantity,
                    available_quantity: product.available_quantity,
                    unit: product.unit,
                    unit_cost: product.unit_cost
                  });
                }
              }}
            >
              {Array.isArray(availableProducts) && availableProducts.map((product, index) => (
                <Option key={product.product_id || `product-${index}`} value={product.product_id}>
                  {product.product_code} - {product.product_name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="current_stock" label="当前库存">
                <InputNumber
                  style={{ width: '100%' }}
                  precision={2}
                  disabled
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="available_quantity" label="可用库存">
                <InputNumber
                  style={{ width: '100%' }}
                  precision={2}
                  disabled
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="transfer_quantity"
                label="调拨数量"
                rules={[
                  { required: true, message: '请输入调拨数量' },
                  { type: 'number', min: 0.001, message: '调拨数量必须大于0' }
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  precision={2}
                  min={0.01}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="unit" label="单位">
                <Input disabled />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="batch_number" label="批次号">
            <Input placeholder="请输入批次号" />
          </Form.Item>

          <Form.Item name="notes" label="备注">
            <TextArea rows={3} placeholder="请输入备注" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
              <Button onClick={() => {
                setProductModalVisible(false);
                productForm.resetFields();
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default FinishedGoodsTransfer; 