import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Form,
  Modal,
  Input,
  Select,
  DatePicker,
  Space,
  Tag,
  Popconfirm,
  message,
  Row,
  Col,
  InputNumber,
  Divider,
  Typography,
  Descriptions,
  Steps,
  Tabs,
  Collapse
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CheckOutlined,
  CloseOutlined,
  SendOutlined,
  ArrowLeftOutlined,
  PlayCircleOutlined,
  SearchOutlined,
  ReloadOutlined,
  FilterOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import request from '../../../utils/request';
import { useNavigate } from 'react-router-dom';

// 扩展dayjs插件
dayjs.extend(utc);
dayjs.extend(timezone);

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { Search } = Input;
const { Step } = Steps;
// 注意：以下API在未来版本中将被废弃，但为了代码稳定性暂时保留
// TODO: 后续版本中将 TabPane 替换为 Tabs 的 items 属性
// TODO: 后续版本中将 Panel 替换为 Collapse 的 items 属性
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

const MaterialInbound = ({ onBack }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [detailModalVisible2, setDetailModalVisible2] = useState(false);
  const [auditModalVisible, setAuditModalVisible] = useState(false);
  const [executeModalVisible, setExecuteModalVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [currentDetail, setCurrentDetail] = useState(null);
  const [isViewMode, setIsViewMode] = useState(false);
  const [form] = Form.useForm();
  const [detailForm] = Form.useForm();
  const [searchForm] = Form.useForm();
  const [warehouses, setWarehouses] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [details, setDetails] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  // 状态配置
  const statusConfig = {
    draft: { color: 'default', text: '草稿' },
    confirmed: { color: 'processing', text: '已确认' },
    in_progress: { color: 'processing', text: '执行中' },
    completed: { color: 'success', text: '已完成' },
    cancelled: { color: 'warning', text: '已取消' }
  };

  const auditStatusConfig = {
    pending: { color: 'default', text: '待审核' },
    approved: { color: 'success', text: '审核通过' },
    rejected: { color: 'error', text: '审核拒绝' }
  };

  useEffect(() => {
    fetchData();
    fetchWarehouses();
    fetchMaterials();
    fetchSuppliers();
    fetchEmployees();
    fetchDepartments();
  }, [pagination.current, pagination.pageSize]);

  // 获取入库单列表
  const fetchData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await request.get('/tenant/inventory/material-inbound-orders', {
        params: {
          page: pagination.current,
          page_size: pagination.pageSize,
          ...params
        }
      });
      
      if (response.data.success) {
        setData(response.data.data.items || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.data.total || 0
        }));
      }
    } catch (error) {
      message.error('获取数据失败: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  // 获取仓库列表（只获取材料仓库）
  const fetchWarehouses = async () => {
    try {
      const response = await request.get('/tenant/inventory/warehouses', {
        params: { warehouse_type: 'material' } // 只获取材料仓库
      });
      if (response.data.code === 200) {
        setWarehouses(response.data.data);
      }
          } catch (error) {
        // 使用备用API
        try {
          const response = await request.get('/tenant/basic-data/warehouses/options', {
            params: { warehouse_type: 'material' }
          });
          if (response.data?.success) {
            setWarehouses(response.data.data);
          }
        } catch (backupError) {
          // 使用模拟数据
          setWarehouses([
            { value: '1', label: '原材料一库', code: 'CL001' },
            { value: '2', label: '原材料二库', code: 'CL002' },
            { value: '3', label: '原材料三库', code: 'CL003' },
            { value: '4', label: '材料仓', code: 'CL004' }
          ]);
        }
      }
  };

  // 获取材料列表
  const fetchMaterials = async () => {
    try {
      const response = await request.get('/tenant/basic-data/material-management');
      if (response.data?.success) {
        const materialData = response.data.data;
        let materials = [];
        if (Array.isArray(materialData)) {
          materials = materialData;
        } else if (materialData?.materials && Array.isArray(materialData.materials)) {
          materials = materialData.materials;
        } else if (materialData?.items && Array.isArray(materialData.items)) {
          materials = materialData.items;
        }
        setMaterials(materials);
      }
    } catch (error) {
      message.error('获取材料列表失败');
    }
  };

  // 获取供应商列表
  const fetchSuppliers = async () => {
    try {
      const response = await request.get('/tenant/basic-data/supplier-management');
      if (response.data?.success) {
        const supplierData = response.data.data;
        let suppliers = [];
        if (Array.isArray(supplierData)) {
          suppliers = supplierData;
        } else if (supplierData?.suppliers && Array.isArray(supplierData.suppliers)) {
          suppliers = supplierData.suppliers;
        } else if (supplierData?.items && Array.isArray(supplierData.items)) {
          suppliers = supplierData.items;
        }
        setSuppliers(suppliers);
      }
    } catch (error) {
      message.error('获取供应商列表失败');
    }
  };

  // 获取员工列表
  const fetchEmployees = async () => {
    try {
      const response = await request.get('/tenant/basic-data/employees');
      if (response.data?.success) {
        const employeeData = response.data.data;
        let employees = [];
        if (Array.isArray(employeeData)) {
          employees = employeeData;
        } else if (employeeData?.employees && Array.isArray(employeeData.employees)) {
          employees = employeeData.employees;
        } else if (employeeData?.items && Array.isArray(employeeData.items)) {
          employees = employeeData.items;
        }
        setEmployees(employees);
      }
    } catch (error) {
      // 不显示错误信息，因为员工可能没有单独的API
    }
  };

  // 获取部门列表
  const fetchDepartments = async () => {
    try {
      const response = await request.get('/tenant/inventory/departments/options');
      if (response.data?.success) {
        setDepartments(response.data.data);
      }
    } catch (error) {
      console.error('获取部门列表失败', error);
      // 如果获取失败，尝试使用备用API
      try {
        const response = await request.get('/tenant/basic-data/departments/options');
        if (response.data?.success) {
          setDepartments(response.data.data);
        }
      } catch (backupError) {
        console.error('备用部门API也失败', backupError);
      }
    }
  };

  // 搜索
  const handleSearch = (values) => {
    const params = {};
    Object.keys(values).forEach(key => {
      if (values[key]) {
        params[key] = values[key];
      }
    });
    fetchData(params);
  };

  // 重置搜索
  const handleSearchReset = () => {
    searchForm.resetFields();
    fetchData();
  };

  // 新增/编辑
  const handleModalOpen = (record = null) => {
    setCurrentRecord(record);
    setIsViewMode(false);
    setModalVisible(true);
    if (record) {
      // 编辑模式
      form.setFieldsValue({
        ...record,
        order_date: record.order_date ? dayjs(record.order_date) : dayjs()
      });
      // 获取明细数据
      fetchOrderDetails(record.id);
    } else {
      // 新增模式
      form.resetFields();
      form.setFieldsValue({
        order_date: dayjs(),
        order_type: 'material'
      });
      setDetails([]);
    }
  };

  // 获取入库单详情
  const fetchOrderDetails = async (orderId) => {
    try {
      // 获取明细数据
      const detailResponse = await request.get(`/tenant/inventory/material-inbound-orders/${orderId}/details`);
      if (detailResponse.data.success) {
        console.log('明细数据:', detailResponse.data.data);
        // 清理数据，移除SQLAlchemy内部属性
        const cleanDetails = (detailResponse.data.data || []).map(detail => {
          const cleanDetail = { ...detail };
          // 删除SQLAlchemy的内部属性
          delete cleanDetail._sa_instance_state;
          // 添加React需要的key属性
          cleanDetail.key = cleanDetail.id || Date.now() + Math.random();
          return cleanDetail;
        });
        setDetails(cleanDetails);
      } else {
        console.error('获取明细失败:', detailResponse.data.error);
        setDetails([]);
      }
    } catch (error) {
      console.error('获取详情失败:', error);
      message.error('获取详情失败');
      setDetails([]);
    }
  };

  // 保存
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      // 清理明细数据，移除SQLAlchemy的内部属性
      const cleanDetails = details.map(detail => {
        const cleanDetail = { ...detail };
        // 删除SQLAlchemy和React的内部属性
        delete cleanDetail._sa_instance_state;
        delete cleanDetail.key;
        // 确保必要字段存在
        return {
          material_id: cleanDetail.material_id,
          material_name: cleanDetail.material_name,
          material_code: cleanDetail.material_code,
          specification: cleanDetail.specification || cleanDetail.material_spec,
          inbound_quantity: cleanDetail.inbound_quantity || cleanDetail.quantity,
          inbound_weight: cleanDetail.inbound_weight || cleanDetail.weight,
          inbound_length: cleanDetail.inbound_length || cleanDetail.length,
          inbound_rolls: cleanDetail.inbound_rolls || cleanDetail.roll_count,
          unit: cleanDetail.unit,
          batch_number: cleanDetail.batch_number,
          unit_price: cleanDetail.unit_price,
          notes: cleanDetail.notes
        };
      });
      
      const orderData = {
        ...values,
        order_date: values.order_date ? values.order_date.format('YYYY-MM-DD') : null,
        details: cleanDetails
      };

      let response;
      if (currentRecord) {
        response = await request.put(`/tenant/inventory/material-inbound-orders/${currentRecord.id}`, orderData);
      } else {
        response = await request.post('/tenant/inventory/material-inbound-orders', orderData);
      }

      if (response.data.success) {
        message.success(currentRecord ? '更新成功' : '创建成功');
        setModalVisible(false);
        fetchData();
        form.resetFields();
        setDetails([]);
      }
    } catch (error) {
      message.error('保存失败: ' + (error.response?.data?.error || error.message));
    }
  };

  // 删除
  const handleDelete = async (record) => {
    try {
      const response = await request.delete(`/tenant/inventory/material-inbound-orders/${record.id}`);
      if (response.data.success) {
        message.success('删除成功');
        fetchData();
      }
    } catch (error) {
      message.error('删除失败: ' + (error.response?.data?.error || error.message));
    }
  };

  // 提交
  const handleSubmit = async (record) => {
    try {
      const response = await request.post(`/tenant/inventory/material-inbound-orders/${record.id}/submit`);
      if (response.data.success) {
        message.success('提交成功');
        fetchData();
      }
    } catch (error) {
      message.error('提交失败: ' + (error.response?.data?.error || error.message));
    }
  };

  // 审核
  const handleAudit = async (values) => {
    try {
      const response = await request.post(`/tenant/inventory/material-inbound-orders/${currentRecord.id}/approve`, values);
      if (response.data.success) {
        message.success('审核成功');
        setAuditModalVisible(false);
        fetchData();
      }
    } catch (error) {
      message.error('审核失败: ' + (error.response?.data?.error || error.message));
    }
  };

  // 执行
  const handleExecute = async (record) => {
    try {
      const response = await request.post(`/tenant/inventory/material-inbound-orders/${record.id}/execute`);
      if (response.data.success) {
        message.success('执行成功');
        setExecuteModalVisible(false);
        fetchData();
      }
    } catch (error) {
      message.error('执行失败: ' + (error.response?.data?.error || error.message));
    }
  };

  // 查看详情
  const handleViewDetail = (record) => {
    setCurrentRecord(record);
    setIsViewMode(true);
    fetchOrderDetails(record.id);
    setDetailModalVisible(true);
  };

  // 添加明细
  const handleAddDetail = async () => {
    try {
      const values = await detailForm.validateFields();
      const newDetail = {
        ...values,
        key: Date.now(),
        material_id: values.material_id,
        material_name: materials.find(m => m.id === values.material_id)?.name || '',
        material_code: materials.find(m => m.id === values.material_id)?.code || '',
        specification: materials.find(m => m.id === values.material_id)?.specification || ''
      };
      setDetails([...details, newDetail]);
      detailForm.resetFields();
    } catch (error) {
      // 表单验证失败
    }
  };

  // 删除明细
  const handleRemoveDetail = (index) => {
    const newDetails = details.filter((_, i) => i !== index);
    setDetails(newDetails);
  };

  // 添加单个明细
  const addDetail = () => {
    setCurrentDetail(null);
    detailForm.resetFields();
    setDetailModalVisible2(true);
  };

  // 编辑明细
  const editDetail = (record) => {
    setCurrentDetail(record);
    detailForm.setFieldsValue(record);
    setDetailModalVisible2(true);
  };

  // 删除明细（单个）
  const deleteDetail = (record) => {
    const newDetails = details.filter(item => item.key !== record.key);
    setDetails(newDetails);
    message.success('明细删除成功');
  };

  // 保存明细
  const handleDetailSubmit = (values) => {
    if (currentDetail) {
      // 更新明细
      const newDetails = details.map(item => 
        item.key === currentDetail.key ? { ...item, ...values } : item
      );
      setDetails(newDetails);
      message.success('明细更新成功');
    } else {
      // 添加明细
      const material = materials.find(m => m.id === values.material_id);
      const newDetail = {
        ...values,
        key: Date.now(),
        material_name: material?.material_name || material?.name || '',
        material_code: material?.material_code || material?.code || '',
        specification: material?.specification || material?.spec || ''
      };
      setDetails([...details, newDetail]);
      message.success('明细添加成功');
    }
    setDetailModalVisible2(false);
    detailForm.resetFields();
  };

  // 表格列定义
  const columns = [
    {
      title: '入库单号',
      dataIndex: 'order_number',
      key: 'order_number',
      width: 160,
    },
    {
      title: '入库日期',
      dataIndex: 'order_date',
      key: 'order_date',
      width: 120,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD') : '-'
    },
    {
      title: '入库类型',
      dataIndex: 'order_type',
      key: 'order_type',
      width: 100,
      render: (type) => {
        const typeMap = {
          purchase: '采购入库',
          return: '退货入库',
          transfer: '调拨入库',
          other: '其他入库'
        };
        return typeMap[type] || type;
      }
    },
    {
      title: '仓库',
      dataIndex: 'warehouse_name',
      key: 'warehouse_name',
      width: 120,
    },
    {
      title: '入库人',
      dataIndex: 'inbound_person',
      key: 'inbound_person',
      width: 100,
      render: (personName, record) => {
        // 优先显示后端返回的员工姓名
        if (personName) return personName;
        
        // 后备方案：根据inbound_person_id查找
        if (!record.inbound_person_id) return '-';
        const employee = employees.find(emp => emp.id === record.inbound_person_id);
        return employee ? (employee.employee_name || employee.name) : '未知员工';
      }
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      width: 100,
      render: (deptName, record) => {
        // 优先显示后端返回的部门名称
        if (deptName) return deptName;
        
        // 后备方案：根据department_id查找
        if (!record.department_id) return '-';
        const department = departments.find(dept => dept.id === record.department_id);
        return department ? (department.department_name || department.dept_name || department.name) : '未知部门';
      }
    },
    {
      title: '供应商',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const config = statusConfig[status] || { color: 'default', text: status };
        return <StatusTag color={config.color}>{config.text}</StatusTag>;
      }
    },
    {
      title: '审核状态',
      dataIndex: 'approval_status',
      key: 'approval_status',
      width: 100,
      render: (status) => {
        const config = auditStatusConfig[status] || { color: 'default', text: status };
        return <StatusTag color={config.color}>{config.text}</StatusTag>;
      }
    },
    {
      title: '总数量',
      dataIndex: 'total_quantity',
      key: 'total_quantity',
      width: 100,
      render: (value) => value || 0
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 120,
      render: (value) => value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 180,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
          {record.status === 'draft' && (
            <>
              <Button
                type="link"
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleModalOpen(record)}
              >
                编辑
              </Button>
              <Button
                type="link"
                size="small"
                icon={<SendOutlined />}
                onClick={() => handleSubmit(record)}
              >
                提交
              </Button>
              <Popconfirm
                title="确定删除这条记录吗？"
                onConfirm={() => handleDelete(record)}
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
            </>
          )}
          {(record.status === 'submitted' || record.status === 'confirmed') && record.approval_status === 'approved' && (
            <Button
              type="link"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => handleExecute(record)}
            >
              执行
            </Button>
          )}
        </Space>
      ),
    },
  ];

  // 明细表格列定义
  const detailColumns = [
    {
      title: '材料名称',
      dataIndex: 'material_name',
      key: 'material_name',
    },
    {
      title: '材料编码',
      dataIndex: 'material_code',
      key: 'material_code',
    },
    {
      title: '规格',
      dataIndex: 'specification',
      key: 'specification',
    },
    {
      title: '入库数量',
      dataIndex: 'inbound_quantity',
      key: 'inbound_quantity',
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
    },
    {
      title: '重量(kg)',
      dataIndex: 'weight',
      key: 'weight',
    },
    {
      title: '长度(m)',
      dataIndex: 'length',
      key: 'length',
    },
    {
      title: '卷数',
      dataIndex: 'roll_count',
      key: 'roll_count',
    },
    {
      title: '批次号',
      dataIndex: 'batch_number',
      key: 'batch_number',
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      render: (value) => value ? `¥${Number(value).toFixed(2)}` : ''
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (value) => value ? `¥${Number(value).toFixed(2)}` : ''
    },
    {
      title: '质量状态',
      dataIndex: 'quality_status',
      key: 'quality_status',
      render: (status) => {
        const statusMap = {
          qualified: { color: 'success', text: '合格' },
          unqualified: { color: 'error', text: '不合格' },
          pending: { color: 'warning', text: '待检' }
        };
        const config = statusMap[status] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '建议库位',
      dataIndex: 'suggested_location',
      key: 'suggested_location',
    },
    {
      title: '实际库位',
      dataIndex: 'actual_location',
      key: 'actual_location',
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record, index) => (
        <Space size="small">
          {!isViewMode && (
            <>
              <Button
                type="link"
                icon={<EditOutlined />}
                size="small"
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
      ),
    }
  ];

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
                      placeholder="输入入库单号、仓库、供应商等"
                      allowClear
                      prefix={<SearchOutlined />}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="warehouse_id" label="仓库">
                    <Select placeholder="选择仓库" allowClear>
                      {warehouses.map(warehouse => (
                        <Option key={warehouse.value || warehouse.id} value={warehouse.value || warehouse.id}>
                          {warehouse.label || warehouse.name || warehouse.warehouse_name}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="status" label="单据状态">
                    <Select placeholder="选择状态" allowClear>
                      {Object.entries(statusConfig).map(([value, config]) => (
                        <Option key={value} value={value}>
                          {config.text}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="order_type" label="入库类型">
                    <Select placeholder="选择入库类型" allowClear>
                      <Option value="material">材料入库</Option>
                      <Option value="auxiliary">辅料入库</Option>
                      <Option value="packaging">包装入库</Option>
                      <Option value="other">其他入库</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              <Row>
                <Col span={4}>
                  <Form.Item label=" " style={{ marginTop: 8 }}>
                    <Space>
                      <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                        搜索
                      </Button>
                      <Button onClick={handleSearchReset} icon={<ReloadOutlined />}>
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

      {/* 材料入库单列表 */}
      <StyledCard 
        title={
          <Space>
            <FileTextOutlined />
            材料入库管理
          </Space>
        }
        extra={
          <Space>
            <ActionButton 
              icon={<ReloadOutlined />} 
              onClick={() => fetchData()}
            >
              刷新
            </ActionButton>
            <ActionButton 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={() => handleModalOpen()}
            >
              新建入库单
            </ActionButton>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1800 }}
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

      {/* 新增/编辑弹窗 */}
      <Modal
        title={currentRecord ? '编辑入库单' : '新增入库单'}
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
              onFinish={handleSave}
            >
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="warehouse_id"
                    label="仓库"
                    rules={[{ required: true, message: '请选择仓库' }]}
                  >
                    <Select
                      placeholder="请选择仓库"
                      onChange={(value) => {
                        const warehouse = warehouses.find(w => w.value === value || w.id === value);
                        if (warehouse) {
                          form.setFieldsValue({ 
                            warehouse_name: warehouse.warehouse_name || warehouse.name 
                          });
                        }
                      }}
                    >
                      {warehouses.map(warehouse => (
                        <Option key={warehouse.value || warehouse.id} value={warehouse.value || warehouse.id}>
                          {warehouse.label || warehouse.name || warehouse.warehouse_name}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                  <Form.Item name="warehouse_name" hidden>
                    <Input />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="order_date"
                    label="入库日期"
                    rules={[{ required: true, message: '请选择入库日期' }]}
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
                    name="order_type"
                    label="入库类型"
                    rules={[{ required: true, message: '请选择入库类型' }]}
                  >
                    <Select placeholder="请选择入库类型">
                      <Option value="material">材料入库</Option>
                      <Option value="auxiliary">辅料入库</Option>
                      <Option value="packaging">包装入库</Option>
                      <Option value="other">其他入库</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="supplier_id" label="供应商">
                    <Select
                      placeholder="请选择供应商"
                      allowClear
                      onChange={(value) => {
                        const supplier = suppliers.find(s => s.id === value);
                        if (supplier) {
                          form.setFieldsValue({ 
                            supplier_name: supplier.supplier_name || supplier.company_name || supplier.name
                          });
                        }
                      }}
                    >
                      {suppliers.map(supplier => (
                        <Option key={supplier.id} value={supplier.id}>
                          {supplier.supplier_name || supplier.company_name || supplier.name}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                  <Form.Item name="supplier_name" hidden>
                    <Input />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="inbound_person_id"
                    label="入库人"
                    rules={[{ required: true, message: '请选择入库人' }]}
                  >
                    <Select 
                      showSearch
                      placeholder="请选择入库人"
                      allowClear
                      filterOption={(input, option) => {
                        return option?.children?.toLowerCase().includes(input.toLowerCase());
                      }}
                    >
                      {employees.map(emp => (
                        <Option key={emp.id} value={emp.id}>
                          {emp.employee_name || emp.name}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="department_id"
                    label="部门"
                    rules={[{ required: true, message: '请选择部门' }]}
                  >
                    <Select 
                      showSearch
                      placeholder="请选择部门"
                      allowClear
                      filterOption={(input, option) => {
                        return option?.children?.toLowerCase().includes(input.toLowerCase());
                      }}
                    >
                      {departments.map(dept => (
                        <Option key={dept.id || dept.value} value={dept.id}>
                          {dept.department_name || dept.dept_name || dept.name || dept.label}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="来源单据类型" name="source_order_type">
                    <Input placeholder="如：采购订单" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="来源单据号" name="source_order_number">
                    <Input placeholder="请输入来源单据号" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="托盘条码" name="pallet_barcode">
                    <Input placeholder="请输入托盘条码" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="备注" name="remarks">
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
          
          <TabPane tab="材料明细" key="2">
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />} 
                  onClick={addDetail}
                >
                  添加明细
                </Button>
              </Space>
            </div>
            <DetailTable
              columns={detailColumns}
              dataSource={details}
              rowKey="key"
              scroll={{ x: 1200 }}
              pagination={false}
            />
          </TabPane>
        </Tabs>
      </Modal>

      {/* 查看入库单详情弹窗 */}
      <Modal
        title={`入库单详情 - ${currentRecord?.order_number}`}
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setIsViewMode(false);
        }}
        footer={null}
        width={1200}
      >
        {currentRecord && (
          <Tabs defaultActiveKey="1">
            <TabPane tab="基本信息" key="1">
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>入库单号：</Text>
                  <Text>{currentRecord.order_number}</Text>
                </Col>
                <Col span={8}>
                  <Text strong>入库日期：</Text>
                  <Text>{currentRecord.order_date ? dayjs(currentRecord.order_date).format('YYYY-MM-DD') : '-'}</Text>
                </Col>
                <Col span={8}>
                  <Text strong>仓库名称：</Text>
                  <Text>{currentRecord.warehouse_name}</Text>
                </Col>
              </Row>
              <Divider />
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>入库人：</Text>
                  <Text>
                    {(() => {
                      // 优先显示后端返回的员工姓名
                      if (currentRecord.inbound_person) return currentRecord.inbound_person;
                      
                      // 后备方案：根据inbound_person_id查找
                      if (!currentRecord.inbound_person_id) return '-';
                      const employee = employees.find(emp => emp.id === currentRecord.inbound_person_id);
                      return employee ? (employee.employee_name || employee.name) : '未知员工';
                    })()}
                  </Text>
                </Col>
                <Col span={8}>
                  <Text strong>部门：</Text>
                  <Text>
                    {(() => {
                      // 优先显示后端返回的部门名称
                      if (currentRecord.department) return currentRecord.department;
                      
                      // 后备方案：根据department_id查找
                      if (!currentRecord.department_id) return '-';
                      const department = departments.find(dept => dept.id === currentRecord.department_id);
                      return department ? (department.department_name || department.dept_name || department.name) : '未知部门';
                    })()}
                  </Text>
                </Col>
                <Col span={8}>
                  <Text strong>供应商：</Text>
                  <Text>{currentRecord.supplier_name || '无'}</Text>
                </Col>
              </Row>
              <Divider />
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>单据状态：</Text>
                  <StatusTag color={statusConfig[currentRecord.status]?.color}>
                    {statusConfig[currentRecord.status]?.text}
                  </StatusTag>
                </Col>
                <Col span={8}>
                  <Text strong>审核状态：</Text>
                  <StatusTag color={auditStatusConfig[currentRecord.audit_status]?.color}>
                    {auditStatusConfig[currentRecord.audit_status]?.text}
                  </StatusTag>
                </Col>
                <Col span={8}>
                  <Text strong>托盘条码：</Text>
                  <Text>{currentRecord.pallet_barcode || '无'}</Text>
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
                  </Space>
                </div>
              )}
              <DetailTable
                columns={detailColumns}
                dataSource={details}
                rowKey="key"
                scroll={{ x: 1200 }}
                pagination={false}
              />
            </TabPane>
          </Tabs>
        )}
      </Modal>

      {/* 添加/编辑明细弹窗 */}
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
                name="material_id"
                label="材料"
                rules={[{ required: true, message: '请选择材料' }]}
              >
                <Select 
                  showSearch
                  placeholder="请选择或搜索材料"
                  filterOption={(input, option) => {
                    if (!option || !option.children) return false;
                    const text = option.children.toString().toLowerCase();
                    const inputLower = input.toLowerCase();
                    return text.includes(inputLower);
                  }}
                  onChange={(value) => {
                    const material = materials.find(m => m.id === value);
                    if (material) {
                      detailForm.setFieldsValue({
                        material_code: material.material_code || material.code || '',
                        material_name: material.material_name || material.name || '',
                        specification: material.specification || material.spec || '',
                        unit: material.unit || '个'
                      });
                    }
                  }}
                >
                  {materials.map(material => (
                    <Option key={material.id} value={material.id}>
                      {(material.material_code || material.code)} - {(material.material_name || material.name)}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="material_code"
                label="材料编码"
              >
                <Input placeholder="自动填充" disabled />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="material_name"
                label="材料名称"
              >
                <Input placeholder="自动填充" disabled />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="specification"
                label="规格"
              >
                <Input placeholder="自动填充" disabled />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="inbound_quantity"
                label="入库数量"
                rules={[{ required: true, message: '请输入入库数量' }]}
              >
                <InputNumber 
                  placeholder="请输入数量" 
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="unit"
                label="单位"
                rules={[{ required: true, message: '请输入单位' }]}
              >
                <Input placeholder="请输入单位" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="unit_price"
                label="单价"
              >
                <InputNumber 
                  placeholder="请输入单价" 
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
                name="weight"
                label="重量(kg)"
              >
                <InputNumber 
                  placeholder="请输入重量" 
                  style={{ width: '100%' }}
                  min={0}
                  precision={3}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="length"
                label="长度(m)"
              >
                <InputNumber 
                  placeholder="请输入长度" 
                  style={{ width: '100%' }}
                  min={0}
                  precision={3}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="roll_count"
                label="卷数"
              >
                <InputNumber 
                  placeholder="请输入卷数" 
                  style={{ width: '100%' }}
                  min={0}
                  precision={0}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="batch_number"
                label="批次号"
              >
                <Input placeholder="请输入批次号" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="suggested_location"
                label="建议库位"
              >
                <Input placeholder="请输入建议库位" />
              </Form.Item>
            </Col>
          </Row>

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

      {/* 审核弹窗 */}
      <Modal
        title="审核入库单"
        open={auditModalVisible}
        onCancel={() => setAuditModalVisible(false)}
        onOk={() => {
          const auditForm = Modal.confirm.__form;
          auditForm.validateFields().then(values => {
            handleAudit(values);
          });
        }}
      >
        <Form
          layout="vertical"
          ref={(ref) => { Modal.confirm.__form = ref; }}
        >
          <Form.Item
            label="审核结果"
            name="audit_result"
            rules={[{ required: true, message: '请选择审核结果' }]}
          >
            <Select>
              <Option value="approved">审核通过</Option>
              <Option value="rejected">审核拒绝</Option>
            </Select>
          </Form.Item>
          <Form.Item label="审核意见" name="audit_comments">
            <TextArea rows={3} placeholder="请输入审核意见" />
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default MaterialInbound; 