import React, { useState, useEffect } from 'react';
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
  getMaterialTransferOrders,
  createMaterialTransferOrder,
  getMaterialTransferOrder,
  updateMaterialTransferOrder,
  getMaterialTransferOrderDetails,
  addMaterialTransferOrderDetail,
  updateMaterialTransferOrderDetail,
  deleteMaterialTransferOrderDetail,
  confirmMaterialTransferOrder,
  executeMaterialTransferOrder,
  receiveMaterialTransferOrder,
  cancelMaterialTransferOrder,
  getWarehouseTransferMaterials
} from '../../../api/business/materialTransfer';
import { warehouseApi } from '../../../api/production/production-archive/warehouse';
import { getEmployeeOptions } from '../../../api/base-data/employee';
import { getDepartmentOptions } from '../../../api/base-data/department';
import request from '../../../utils/request';

const { Option } = Select;
const { TextArea } = Input;
const { Title } = Typography;

const MaterialTransfer = () => {
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
  const [materialModalVisible, setMaterialModalVisible] = useState(false);
  
  // 表单和数据
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const [materialForm] = Form.useForm();
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [orderDetails, setOrderDetails] = useState([]);
  const [availableMaterials, setAvailableMaterials] = useState([]);
  const [editingDetail, setEditingDetail] = useState(null);
  
  // 基础数据
  const [warehouses, setWarehouses] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);

  // 页面加载
  useEffect(() => {
    console.log('MaterialTransfer组件初始化，开始加载数据...');
    fetchOrders();
    fetchWarehouses();
    fetchEmployees();
    fetchDepartments();
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
      
      const response = await getMaterialTransferOrders(queryParams);
      if (response.data.success) {
        setOrders(response.data.data.orders);
        setPagination({
          ...pagination,
          total: response.data.data.pagination.total,
          current: response.data.data.pagination.page
        });
      }
    } catch (error) {
      message.error('获取调拨单列表失败');
    }
    setLoading(false);
  };

  // 获取仓库列表（只获取材料仓库）
  const fetchWarehouses = async () => {
    try {
      // 优先使用材料仓库专用API，确保只获取材料仓库
      let response;
      try {
        // 直接使用正确的仓库基础档案API
        response = await request.get('/tenant/base-archive/base-data/warehouses/options');
        console.log('仓库基础档案API响应:', response.data);
      } catch (warehouseApiError) {
        console.warn('仓库基础档案API失败，尝试通用仓库API:', warehouseApiError);
        // 备用方案：使用通用仓库API
        const generalResponse = await warehouseApi.getWarehouseOptions();
        response = generalResponse;
        console.log('通用仓库API响应:', response.data);
      }
      
      if (response.data && (response.data.success || response.data.code === 200)) {
        // 处理返回的数据格式
        let warehouseList = response.data.data;
        
        if (Array.isArray(warehouseList)) {
          // 转换为标准格式并过滤，确保只显示材料仓库
          const formattedWarehouses = warehouseList
            .filter(warehouse => {
              // 过滤条件：仓库类型为材料仓库或名称包含"材料"
              const warehouseType = warehouse.warehouse_type || warehouse.type || '';
              const warehouseName = warehouse.label || warehouse.warehouse_name || warehouse.name || '';
              return warehouseType === 'material' || 
                     warehouseType === '材料' || 
                     warehouseType === '材料仓库' ||
                     warehouseName.includes('材料') ||
                     warehouseName.includes('原材料');
            })
            .map(warehouse => ({
              id: warehouse.value || warehouse.id,
              warehouse_name: warehouse.label || warehouse.warehouse_name || warehouse.name,
              warehouse_code: warehouse.code || warehouse.warehouse_code,
              warehouse_type: warehouse.warehouse_type || warehouse.type
            }));
          
          setWarehouses(formattedWarehouses);
          console.log('设置材料仓库数据:', formattedWarehouses);
          
          if (formattedWarehouses.length === 0) {
            message.warning('未找到材料仓库，请先在基础档案中创建材料类型的仓库');
          }
        } else {
          console.warn('仓库数据格式不正确:', warehouseList);
          setWarehouses([]);
        }
      } else {
        console.warn('仓库API返回失败:', response.data);
        setWarehouses([]);
      }
    } catch (error) {
      console.error('获取材料仓库列表失败:', error);
      message.error('获取材料仓库列表失败');
      setWarehouses([]);
    }
  };

  // 获取员工列表
  const fetchEmployees = async () => {
    try {
      const response = await getEmployeeOptions();
      if (response.data.success) {
        setEmployees(response.data.data);
      }
    } catch (error) {
      message.error('获取员工列表失败');
    }
  };

  // 获取部门列表
  const fetchDepartments = async () => {
    try {
      const response = await getDepartmentOptions();
      if (response.data.success) {
        setDepartments(response.data.data);
      }
    } catch (error) {
      message.error('获取部门列表失败');
    }
  };

  // 获取调拨单详情
  const fetchOrderDetails = async (orderId) => {
    try {
      const response = await getMaterialTransferOrderDetails(orderId);
      if (response.data.success) {
        setOrderDetails(response.data.data);
      }
    } catch (error) {
      message.error('获取调拨单详情失败');
    }
  };

  // 获取可调拨材料
  const fetchAvailableMaterials = async (warehouseId) => {
    if (!warehouseId) return;
    try {
      const response = await getWarehouseTransferMaterials(warehouseId);
      if (response.data.success) {
        setAvailableMaterials(response.data.data);
      }
    } catch (error) {
      message.error('获取可调拨材料失败');
    }
  };

  // 创建调拨单
  const handleCreate = async (values) => {
    try {
      // 业务逻辑验证
      if (values.from_warehouse_id === values.to_warehouse_id) {
        message.error('调出仓库和调入仓库不能相同');
        return;
      }

      // 验证是否都是材料仓库
      const fromWarehouse = warehouses.find(w => w.id === values.from_warehouse_id);
      const toWarehouse = warehouses.find(w => w.id === values.to_warehouse_id);
      
      if (!fromWarehouse || !toWarehouse) {
        message.error('请选择有效的材料仓库');
        return;
      }

      const response = await createMaterialTransferOrder(values);
      if (response.data.success) {
        message.success('材料调拨单创建成功');
        setCreateModalVisible(false);
        form.resetFields();
        fetchOrders();
      } else {
        message.error(response.data.error || '创建失败');
      }
    } catch (error) {
      console.error('创建调拨单失败:', error);
      message.error('创建材料调拨单失败');
    }
  };

  // 查看详情
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
      const response = await updateMaterialTransferOrder(selectedOrder.id, values);
      if (response.data.success) {
        message.success('调拨单更新成功');
        setEditModalVisible(false);
        editForm.resetFields();
        fetchOrders();
      } else {
        message.error(response.data.error || '更新失败');
      }
    } catch (error) {
      message.error('更新调拨单失败');
    }
  };

  // 添加材料
  const handleAddMaterial = async () => {
    if (!selectedOrder) return;
    await fetchAvailableMaterials(selectedOrder.from_warehouse_id);
    materialForm.resetFields();
    setEditingDetail(null);
    setMaterialModalVisible(true);
  };

  // 编辑材料
  const handleEditMaterial = async (detail) => {
    await fetchAvailableMaterials(selectedOrder.from_warehouse_id);
    setEditingDetail(detail);
    materialForm.setFieldsValue(detail);
    setMaterialModalVisible(true);
  };

  // 保存材料
  const handleSaveMaterial = async (values) => {
    try {
      let response;
      if (editingDetail) {
        response = await updateMaterialTransferOrderDetail(selectedOrder.id, editingDetail.id, values);
      } else {
        response = await addMaterialTransferOrderDetail(selectedOrder.id, values);
      }
      
      if (response.data.success) {
        message.success(`材料${editingDetail ? '更新' : '添加'}成功`);
        setMaterialModalVisible(false);
        materialForm.resetFields();
        await fetchOrderDetails(selectedOrder.id);
      } else {
        message.error(response.data.error || `${editingDetail ? '更新' : '添加'}失败`);
      }
    } catch (error) {
      message.error(`${editingDetail ? '更新' : '添加'}材料失败`);
    }
  };

  // 删除材料
  const handleDeleteMaterial = async (detailId) => {
    try {
      const response = await deleteMaterialTransferOrderDetail(selectedOrder.id, detailId);
      if (response.data.success) {
        message.success('材料删除成功');
        await fetchOrderDetails(selectedOrder.id);
      } else {
        message.error(response.data.error || '删除失败');
      }
    } catch (error) {
      message.error('删除材料失败');
    }
  };

  // 确认调拨单
  const handleConfirm = async (orderId) => {
    try {
      const response = await confirmMaterialTransferOrder(orderId);
      if (response.data.success) {
        message.success('调拨单确认成功');
        fetchOrders();
      } else {
        message.error(response.data.error || '确认失败');
      }
    } catch (error) {
      message.error('确认调拨单失败');
    }
  };

  // 执行调拨单（出库）
  const handleExecute = async (orderId) => {
    try {
      const response = await executeMaterialTransferOrder(orderId);
      if (response.data.success) {
        message.success('调拨单执行成功，材料已出库');
        fetchOrders();
      } else {
        message.error(response.data.error || '执行失败');
      }
    } catch (error) {
      message.error('执行调拨单失败');
    }
  };

  // 接收调拨单（入库）
  const handleReceive = async (orderId) => {
    try {
      const response = await receiveMaterialTransferOrder(orderId);
      if (response.data.success) {
        message.success('调拨单接收成功，材料已入库');
        fetchOrders();
      } else {
        message.error(response.data.error || '接收失败');
      }
    } catch (error) {
      message.error('接收调拨单失败');
    }
  };

  // 取消调拨单
  const handleCancel = async (orderId) => {
    try {
      const response = await cancelMaterialTransferOrder(orderId);
      if (response.data.success) {
        message.success('调拨单取消成功');
        fetchOrders();
      } else {
        message.error(response.data.error || '取消失败');
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
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 调拨类型标签
  const getTransferTypeTag = (type) => {
    const typeMap = {
      warehouse: { color: 'blue', text: '仓库调拨' },
      department: { color: 'green', text: '部门调拨' },
      project: { color: 'orange', text: '项目调拨' },
      emergency: { color: 'red', text: '紧急调拨' }
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 表格列定义
  const columns = [
    {
      title: '调拨单号',
      dataIndex: 'transfer_number',
      key: 'transfer_number',
      width: 150
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
      title: '发生日期',
      dataIndex: 'transfer_date',
      key: 'transfer_date',
      width: 120,
      render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
    },
    {
      title: '总数量',
      dataIndex: 'total_quantity',
      key: 'total_quantity',
      width: 100,
      align: 'right',
      render: (value) => value ? Number(value).toFixed(3) : '0.000'
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 100,
      align: 'right',
      render: (value) => value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status)
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            查看
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
                title="确定确认此调拨单吗？"
                onConfirm={() => handleConfirm(record.id)}
              >
                <Button type="link" icon={<CheckOutlined />}>
                  确认
                </Button>
              </Popconfirm>
            </>
          )}
          {record.status === 'confirmed' && (
            <Popconfirm
              title="确定执行此调拨单吗？材料将会出库。"
              onConfirm={() => handleExecute(record.id)}
            >
              <Button type="link" icon={<SendOutlined />}>
                执行
              </Button>
            </Popconfirm>
          )}
          {record.status === 'in_transit' && (
            <Popconfirm
              title="确定接收此调拨单吗？材料将会入库。"
              onConfirm={() => handleReceive(record.id)}
            >
              <Button type="link" icon={<InboxOutlined />}>
                接收
              </Button>
            </Popconfirm>
          )}
          {['draft', 'confirmed'].includes(record.status) && (
            <Popconfirm
              title="确定取消此调拨单吗？"
              onConfirm={() => handleCancel(record.id)}
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
      title: '材料编码',
      dataIndex: 'material_code',
      key: 'material_code',
      width: 120
    },
    {
      title: '材料名称',
      dataIndex: 'material_name',
      key: 'material_name',
      width: 200
    },
    {
      title: '规格',
      dataIndex: 'material_spec',
      key: 'material_spec',
      width: 150
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 80,
      align: 'center'
    },
    {
      title: '库存数量',
      dataIndex: 'current_stock',
      key: 'current_stock',
      width: 100,
      align: 'right',
      render: (value) => value ? Number(value).toFixed(3) : '0.000'
    },
    {
      title: '调拨数量',
      dataIndex: 'transfer_quantity',
      key: 'transfer_quantity',
      width: 100,
      align: 'right',
      render: (value) => Number(value).toFixed(3)
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 100,
      align: 'right',
      render: (value) => value ? `¥${Number(value).toFixed(2)}` : '-'
    },
    {
      title: '金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 100,
      align: 'right',
      render: (value) => value ? `¥${Number(value).toFixed(2)}` : '-'
    },
    {
      title: '批次号',
      dataIndex: 'batch_number',
      key: 'batch_number',
      width: 120
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        selectedOrder?.status === 'draft' ? (
          <Space>
            <Button
              type="link"
              size="small"
              onClick={() => handleEditMaterial(record)}
            >
              编辑
            </Button>
            <Popconfirm
              title="确定删除此材料吗？"
              onConfirm={() => handleDeleteMaterial(record.id)}
            >
              <Button type="link" size="small" danger>
                删除
              </Button>
            </Popconfirm>
          </Space>
        ) : '-'
      )
    }
  ];

  return (
    <div>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={4} style={{ margin: 0 }}>材料调拨管理</Title>
            <div style={{ color: '#666', fontSize: '14px', marginTop: '4px' }}>
              管理材料仓库之间的材料调拨，支持仓库间库存转移
            </div>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalVisible(true)}
          >
            新增调拨单
          </Button>
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
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条/共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPagination({ ...pagination, current: page, pageSize });
              fetchOrders({ page, per_page: pageSize });
            }
          }}
          scroll={{ x: 1400 }}
        />
      </Card>

      {/* 创建调拨单模态框 */}
      <Modal
        title="新增调拨单"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{
            transfer_date: dayjs(),
            transfer_type: 'warehouse'
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="transfer_type"
                label="调拨类型"
                rules={[{ required: true, message: '请选择调拨类型' }]}
              >
                <Select placeholder="请选择调拨类型">
                  <Option value="warehouse">仓库调拨</Option>
                  <Option value="department">部门调拨</Option>
                  <Option value="project">项目调拨</Option>
                  <Option value="emergency">紧急调拨</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="transfer_date"
                label="调拨日期"
                rules={[{ required: true, message: '请选择调拨日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="from_warehouse_id"
                label="调出仓库"
                rules={[
                  { required: true, message: '请选择调出仓库' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || value !== getFieldValue('to_warehouse_id')) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('调出仓库和调入仓库不能相同'));
                    },
                  })
                ]}
              >
                <Select 
                  placeholder="请选择调出仓库"
                  onChange={() => {
                    // 当调出仓库改变时，验证调入仓库
                    form.validateFields(['to_warehouse_id']);
                  }}
                >
                  {Array.isArray(warehouses) && warehouses.length > 0 ? warehouses.map(warehouse => (
                    <Option key={`from-warehouse-${warehouse.id}`} value={warehouse.id}>
                      {warehouse.warehouse_name}（{warehouse.warehouse_code}）
                    </Option>
                  )) : (
                    <Option key="no-from-warehouses" disabled value="">暂无材料仓库数据</Option>
                  )}
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
                      if (!value || value !== getFieldValue('from_warehouse_id')) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('调入仓库和调出仓库不能相同'));
                    },
                  })
                ]}
              >
                <Select 
                  placeholder="请选择调入仓库"
                  onChange={() => {
                    // 当调入仓库改变时，验证调出仓库
                    form.validateFields(['from_warehouse_id']);
                  }}
                >
                  {Array.isArray(warehouses) && warehouses.length > 0 ? warehouses.map(warehouse => (
                    <Option key={`to-warehouse-${warehouse.id}`} value={warehouse.id}>
                      {warehouse.warehouse_name}（{warehouse.warehouse_code}）
                    </Option>
                  )) : (
                    <Option key="no-to-warehouses" disabled value="">暂无材料仓库数据</Option>
                  )}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="transfer_person_id" label="调拨人">
                <Select placeholder="请选择调拨人" allowClear>
                  {Array.isArray(employees) && employees.map(emp => (
                    <Option key={`transfer-employee-${emp.id}`} value={emp.id}>
                      {emp.employee_name || emp.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="department_id" label="部门">
                <Select placeholder="请选择部门" allowClear>
                  {Array.isArray(departments) && departments.map(dept => (
                    <Option key={`transfer-department-${dept.id}`} value={dept.id}>
                      {dept.department_name || dept.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="transporter" label="承运人">
                <Input placeholder="请输入承运人" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="transport_method" label="运输方式">
                <Select placeholder="请选择运输方式" allowClear>
                  <Option value="manual">人工搬运</Option>
                  <Option value="vehicle">车辆运输</Option>
                  <Option value="logistics">物流配送</Option>
                  <Option value="pipeline">管道输送</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="expected_arrival_date" label="预计到达时间">
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="notes" label="备注">
            <TextArea rows={4} placeholder="请输入备注" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                创建
              </Button>
              <Button onClick={() => {
                setCreateModalVisible(false);
                form.resetFields();
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑调拨单模态框 */}
      <Modal
        title="编辑调拨单"
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          editForm.resetFields();
        }}
        footer={null}
        width={800}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={handleUpdate}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="transfer_type"
                label="调拨类型"
                rules={[{ required: true, message: '请选择调拨类型' }]}
              >
                <Select placeholder="请选择调拨类型">
                  <Option value="warehouse">仓库调拨</Option>
                  <Option value="department">部门调拨</Option>
                  <Option value="project">项目调拨</Option>
                  <Option value="emergency">紧急调拨</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="transfer_date"
                label="调拨日期"
                rules={[{ required: true, message: '请选择调拨日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="transfer_person_id" label="调拨人">
                <Select placeholder="请选择调拨人" allowClear>
                  {Array.isArray(employees) && employees.map(emp => (
                    <Option key={`edit-employee-${emp.id}`} value={emp.id}>
                      {emp.employee_name || emp.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="department_id" label="部门">
                <Select placeholder="请选择部门" allowClear>
                  {Array.isArray(departments) && departments.map(dept => (
                    <Option key={`edit-department-${dept.id}`} value={dept.id}>
                      {dept.department_name || dept.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="transporter" label="承运人">
                <Input placeholder="请输入承运人" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="transport_method" label="运输方式">
                <Select placeholder="请选择运输方式" allowClear>
                  <Option key="edit-transport-manual" value="manual">人工搬运</Option>
                  <Option key="edit-transport-vehicle" value="vehicle">车辆运输</Option>
                  <Option key="edit-transport-logistics" value="logistics">物流配送</Option>
                  <Option key="edit-transport-pipeline" value="pipeline">管道输送</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="expected_arrival_date" label="预计到达时间">
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="notes" label="备注">
            <TextArea rows={4} placeholder="请输入备注" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                更新
              </Button>
              <Button onClick={() => {
                setEditModalVisible(false);
                editForm.resetFields();
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 查看详情模态框 */}
      <Modal
        title="调拨单详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={1200}
      >
        {selectedOrder && (
          <>
            <Descriptions bordered column={3} size="small">
              <Descriptions.Item label="调拨单号">
                {selectedOrder.transfer_number}
              </Descriptions.Item>
              <Descriptions.Item label="调拨类型">
                {getTransferTypeTag(selectedOrder.transfer_type)}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                {getStatusTag(selectedOrder.status)}
              </Descriptions.Item>
              <Descriptions.Item label="调出仓库">
                {selectedOrder.from_warehouse_name}
              </Descriptions.Item>
              <Descriptions.Item label="调入仓库">
                {selectedOrder.to_warehouse_name}
              </Descriptions.Item>
              <Descriptions.Item label="调拨日期">
                {selectedOrder.transfer_date ? dayjs(selectedOrder.transfer_date).format('YYYY-MM-DD') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="调拨人">
                {selectedOrder.transfer_person || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="部门">
                {selectedOrder.department || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="承运人">
                {selectedOrder.transporter || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="总数量">
                {selectedOrder.total_quantity ? Number(selectedOrder.total_quantity).toFixed(3) : '0.000'}
              </Descriptions.Item>
              <Descriptions.Item label="总金额">
                {selectedOrder.total_amount ? `¥${Number(selectedOrder.total_amount).toFixed(2)}` : '¥0.00'}
              </Descriptions.Item>
              <Descriptions.Item label="备注" span={3}>
                {selectedOrder.notes || '-'}
              </Descriptions.Item>
            </Descriptions>

            <Divider>调拨明细</Divider>

            <div style={{ marginBottom: 16 }}>
              {selectedOrder.status === 'draft' && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleAddMaterial}
                >
                  添加材料
                </Button>
              )}
            </div>

            <Table
              columns={detailColumns}
              dataSource={orderDetails}
              rowKey="id"
              pagination={false}
              scroll={{ x: 1200 }}
            />
          </>
        )}
      </Modal>

      {/* 添加/编辑材料模态框 */}
      <Modal
        title={editingDetail ? '编辑材料' : '添加材料'}
        open={materialModalVisible}
        onCancel={() => {
          setMaterialModalVisible(false);
          materialForm.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={materialForm}
          layout="vertical"
          onFinish={handleSaveMaterial}
        >
          <Form.Item
            name="material_id"
            label="材料"
            rules={[{ required: true, message: '请选择材料' }]}
          >
            <Select 
              placeholder="请选择材料"
              showSearch
              optionFilterProp="children"
              disabled={!!editingDetail}
              onChange={(materialId) => {
                const material = Array.isArray(availableMaterials) ? availableMaterials.find(m => m.material_id === materialId) : null;
                if (material) {
                  materialForm.setFieldsValue({
                    current_stock: material.current_quantity,
                    available_quantity: material.available_quantity,
                    unit_price: material.unit_cost
                  });
                }
              }}
            >
              {Array.isArray(availableMaterials) && availableMaterials.map(material => (
                <Option key={`material-${material.material_id}`} value={material.material_id}>
                  {material.material_code} - {material.material_name}
                  {material.material_spec && ` (${material.material_spec})`}
                  - 库存: {Number(material.current_quantity).toFixed(3)}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="current_stock" label="当前库存">
                <InputNumber
                  style={{ width: '100%' }}
                  precision={3}
                  disabled
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="available_quantity" label="可用库存">
                <InputNumber
                  style={{ width: '100%' }}
                  precision={3}
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
                  precision={3}
                  min={0.001}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="unit_price" label="单价">
                <InputNumber
                  style={{ width: '100%' }}
                  precision={4}
                  min={0}
                />
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
                setMaterialModalVisible(false);
                materialForm.resetFields();
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

export default MaterialTransfer; 