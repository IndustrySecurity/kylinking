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
import { materialOutboundService, baseDataService } from '../../../api/business/materialOutbound';

// 扩展dayjs插件
dayjs.extend(utc);
dayjs.extend(timezone);

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { Search } = Input;
const { Step } = Steps;
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

const MaterialOutbound = ({ onBack }) => {
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
    submitted: { color: 'processing', text: '已提交' },
    approved: { color: 'success', text: '已审核' },
    rejected: { color: 'error', text: '已拒绝' },
    executed: { color: 'purple', text: '已执行' },
    cancelled: { color: 'warning', text: '已取消' }
  };

  const auditStatusConfig = {
    pending: { color: 'default', text: '待审核' },
    approved: { color: 'success', text: '审核通过' },
    rejected: { color: 'error', text: '审核拒绝' }
  };

  useEffect(() => {
    const initializeData = async () => {
      // 先获取基础数据
      await Promise.all([
        fetchWarehouses(),
        fetchMaterials(), 
        fetchEmployees(),
        fetchDepartments()
      ]);
      // 等待一点时间确保state更新
      setTimeout(() => {
        fetchData();
      }, 100);
    };
    
    initializeData();
  }, [pagination.current, pagination.pageSize]);



  // 获取出库单列表
  const fetchData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await materialOutboundService.getOutboundOrderList({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...params
      });
      
      console.log('材料出库API响应:', response.data);
      
      if (response.data.success || response.data.code === 200) {
        const responseData = response.data.data;
        let orders = [];
        
        // 处理不同的数据格式
        if (Array.isArray(responseData)) {
          orders = responseData;
        } else if (responseData?.items && Array.isArray(responseData.items)) {
          orders = responseData.items;
        } else if (responseData?.orders && Array.isArray(responseData.orders)) {
          orders = responseData.orders;
        } else {
          orders = [];
        }
        
        console.log('解析出的订单数据:', orders);
        
        setData(orders);
        
        setPagination(prev => ({
          ...prev,
          total: responseData?.total || orders.length
        }));
      } else {
        console.error('API返回失败:', response.data);
        setData([]);
      }
    } catch (error) {
      console.error('获取数据失败:', error);
      message.error('获取数据失败: ' + (error.response?.data?.error || error.message));
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  // 获取仓库列表（只获取材料仓库）
  const fetchWarehouses = async () => {
    try {
      const response = await baseDataService.getWarehouses();
      console.log('仓库API响应:', response.data);
      if (response.data.success) {
        setWarehouses(response.data.data || []);
        console.log('仓库数据设置完成:', response.data.data);
      }
    } catch (error) {
      console.error('获取仓库列表失败', error);
      // 使用备用API
      try {
        const response = await request.get('/tenant/base-archive/production/production-archive/warehouses/options', {
          params: { warehouse_type: 'material' }
        });
        if (response.data?.success) {
          setWarehouses(response.data.data);
        }
      } catch (backupError) {
        console.error('备用仓库API也失败', backupError);
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
      const response = await baseDataService.getMaterials({
        page_size: 1000, // 获取更多数据
        is_enabled: true // 只获取启用的材料
      });
      console.log('材料API响应:', response.data);
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
        console.log('材料数据设置完成:', materials);
      }
    } catch (error) {
      console.error('获取材料列表失败', error);
      message.error('获取材料列表失败: ' + (error.response?.data?.error || error.message));
    }
  };

  // 获取员工列表
  const fetchEmployees = async () => {
    try {
      const response = await request.get('/tenant/base-archive/base-data/employees/options');
      console.log('员工API响应:', response.data);
      
      if (response.data?.success) {
        setEmployees(response.data.data || []);
      } else {
        console.warn('员工API返回失败:', response.data);
        setEmployees([]);
      }
    } catch (error) {
      console.error('获取员工列表失败:', error);
      setEmployees([]);
    }
  };

  // 获取部门列表
  const fetchDepartments = async () => {
    try {
      const response = await request.get('/tenant/base-archive/base-data/departments/options');
      console.log('部门API响应:', response.data);
      
      if (response.data?.success) {
        setDepartments(response.data.data || []);
      } else {
        console.warn('部门API返回失败:', response.data);
        setDepartments([]);
      }
    } catch (error) {
      console.error('获取部门列表失败:', error);
      setDepartments([]);
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
        order_type: 'production'
      });
      setDetails([]);
    }
  };

  // 获取出库单详情
  const fetchOrderDetails = async (orderId) => {
    try {
      const response = await materialOutboundService.getOutboundOrderById(orderId);
      if (response.data.success || response.data.code === 200) {
        setDetails(response.data.data.details || []);
      } else {
        message.error(response.data.message || '获取详情失败');
      }
    } catch (error) {
      console.error('获取详情失败:', error);
      message.error('获取详情失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // 保存
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      // 构建订单数据，确保字段格式正确
      const orderData = {
        warehouse_id: values.warehouse_id,
        order_date: values.order_date ? values.order_date.format('YYYY-MM-DD') : null,
        order_type: values.order_type,
        outbound_person_id: values.outbound_person_id,
        department_id: values.department_id,
        source_order_type: values.source_order_type,
        source_order_number: values.source_order_number,
        remarks: values.remarks,
        details: details.map(detail => ({
          material_id: detail.material_id,
          material_name: detail.material_name,
          material_code: detail.material_code,
          specification: detail.specification,
          outbound_quantity: detail.outbound_quantity,
          unit: detail.unit,
          batch_number: detail.batch_number,
          location_code: detail.location_code,
          remarks: detail.remarks
        }))
      };

      console.log('发送的订单数据:', orderData);

      let response;
      if (currentRecord) {
        response = await materialOutboundService.updateOutboundOrder(currentRecord.id, orderData);
      } else {
        response = await materialOutboundService.createOutboundOrder(orderData);
      }

      if (response.data.code === 200 || response.data.success) {
        message.success(currentRecord ? '更新成功' : '创建成功');
        setModalVisible(false);
        form.resetFields();
        setDetails([]);
        setCurrentRecord(null);
        fetchData();
      } else {
        message.error(response.data.message || '保存失败');
      }
    } catch (error) {
      console.error('保存失败:', error);
      message.error('保存失败: ' + (error.response?.data?.error || error.message));
    }
  };

  // 删除
  const handleDelete = async (record) => {
    try {
      const response = await request.delete(`/tenant/inventory/material-outbound-orders/${record.id}`);
      if (response.data.code === 200 || response.data.success) {
        message.success('删除成功');
        fetchData();
      } else {
        message.error(response.data.message || '删除失败');
      }
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // 提交
  const handleSubmit = async (record) => {
    try {
      const response = await request.post(`/tenant/inventory/material-outbound-orders/${record.id}/submit`);
      if (response.data.code === 200 || response.data.success) {
        message.success('提交成功');
        fetchData();
      } else {
        message.error(response.data.message || '提交失败');
      }
    } catch (error) {
      console.error('提交失败:', error);
      message.error('提交失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // 审核
  const handleAudit = async (values) => {
    try {
      const response = await request.post(`/tenant/inventory/material-outbound-orders/${currentRecord.id}/approve`, values);
      if (response.data.code === 200 || response.data.success) {
        message.success('审核成功');
        setAuditModalVisible(false);
        fetchData();
      } else {
        message.error(response.data.message || '审核失败');
      }
    } catch (error) {
      console.error('审核失败:', error);
      message.error('审核失败: ' + (error.response?.data?.message || error.message));
    }
  };

  // 执行
  const handleExecute = async (record) => {
    try {
      const response = await request.post(`/tenant/inventory/material-outbound-orders/${record.id}/execute`);
      if (response.data.code === 200 || response.data.success) {
        message.success('执行成功');
        fetchData();
      } else {
        message.error(response.data.message || '执行失败');
      }
    } catch (error) {
      console.error('执行失败:', error);
      message.error('执行失败: ' + (error.response?.data?.message || error.message));
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
        material_name: materials.find(m => m.id === values.material_id)?.material_name || materials.find(m => m.id === values.material_id)?.name || '',
        material_code: materials.find(m => m.id === values.material_id)?.material_code || materials.find(m => m.id === values.material_id)?.code || '',
        specification: materials.find(m => m.id === values.material_id)?.specification_model || materials.find(m => m.id === values.material_id)?.specification || ''
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

  // 删除明细
  const deleteDetail = (record) => {
    setDetails(prev => prev.filter(item => item.key !== record.key));
  };

  // 明细提交
  const handleDetailSubmit = (values) => {
    if (currentDetail) {
      // 编辑模式
      const material = materials.find(m => m.id === values.material_id);
      const updatedDetail = {
        ...currentDetail,
        ...values,
        material_name: material?.material_name || material?.name || values.material_name || '',
        material_code: material?.material_code || material?.code || values.material_code || '',
        specification: material?.specification_model || material?.specification || values.specification || '',
        unit: material?.unit_name || material?.unit || values.unit || ''
      };
      setDetails(prev => prev.map(item => 
        item.key === currentDetail.key ? updatedDetail : item
      ));
    } else {
      // 新增模式
      const material = materials.find(m => m.id === values.material_id);
      const newDetail = {
        ...values,
        key: Date.now(),
        material_id: values.material_id,
        material_name: material?.material_name || material?.name || values.material_name || '',
        material_code: material?.material_code || material?.code || values.material_code || '',
        specification: material?.specification_model || material?.specification || values.specification || '',
        unit: material?.unit_name || material?.unit || values.unit || ''
      };
      setDetails(prev => [...prev, newDetail]);
    }
    setDetailModalVisible2(false);
    detailForm.resetFields();
    setCurrentDetail(null);
  };

  // 表格列定义
  const columns = [
    {
      title: '出库单号',
      dataIndex: 'order_number',
      key: 'order_number',
      width: 150,
      fixed: 'left'
    },
    {
      title: '出库日期',
      dataIndex: 'order_date',
      key: 'order_date',
      width: 120,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD') : '-'
    },
    {
      title: '仓库名称',
      dataIndex: 'warehouse_name',
      key: 'warehouse_name',
      width: 120
    },
    {
      title: '出库类型',
      dataIndex: 'order_type',
      key: 'order_type',
      width: 100,
      render: (text) => {
        const typeMap = {
          production: '生产出库',
          sale: '销售出库',
          transfer: '调拨出库',
          other: '其他出库'
        };
        return typeMap[text] || text;
      }
    },
    {
      title: '出库人',
      dataIndex: 'outbound_person',
      key: 'outbound_person',
      width: 100
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      width: 100,
      render: (departmentId) => {
        if (!departmentId) return '-';
        
        // 如果是UUID格式，尝试映射为部门名称
        const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(departmentId);
        if (isUUID && departments.length > 0) {
          const dept = departments.find(d => d.value === departmentId);
          return dept ? dept.label : departmentId;
        }
        
        return departmentId;
      }
    },
    {
      title: '单据状态',
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
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      width: 150,
      ellipsis: true
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
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => handleViewDetail(record)}
            size="small"
          >
            详情
          </Button>
          {record.status === 'draft' && (
            <Button 
              type="link" 
              icon={<EditOutlined />} 
              onClick={() => handleModalOpen(record)}
              size="small"
            >
            编辑
          </Button>
          )}
          {record.status === 'draft' && (
            <Button 
              type="link" 
              icon={<SendOutlined />} 
              onClick={() => handleSubmit(record)}
              size="small"
            >
              提交
            </Button>
          )}
          {record.status === 'submitted' && record.approval_status === 'pending' && (
            <Button 
              type="link" 
              icon={<CheckOutlined />} 
              onClick={() => {
                setCurrentRecord(record);
                setAuditModalVisible(true);
              }}
              size="small"
            >
                审核
              </Button>
          )}
          {record.status === 'approved' && record.approval_status === 'approved' && (
            <Button 
              type="link" 
              icon={<PlayCircleOutlined />} 
              onClick={() => handleExecute(record)}
              size="small"
            >
              执行
            </Button>
          )}
          {record.status === 'draft' && (
            <Popconfirm
              title="确定要删除这条记录吗？"
              onConfirm={() => handleDelete(record)}
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
      width: 150
    },
    {
      title: '规格型号',
      dataIndex: 'specification',
      key: 'specification',
      width: 120
    },
    {
      title: '出库数量',
      dataIndex: 'outbound_quantity',
      key: 'outbound_quantity',
      width: 100
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 80
    },
    {
      title: '批次号',
      dataIndex: 'batch_number',
      key: 'batch_number',
      width: 120
    },
    {
      title: '库位编码',
      dataIndex: 'location_code',
      key: 'location_code',
      width: 100
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      width: 150,
      ellipsis: true
    },
    ...(!isViewMode ? [{
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => editDetail(record)}
            size="small"
          >
            编辑
          </Button>
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => deleteDetail(record)}
            size="small"
          >
            删除
          </Button>
        </Space>
      )
    }] : [])
  ];

  return (
    <PageContainer>
      {/* 搜索表单 */}
      <StyledCard>
        <Collapse defaultActiveKey={[]}>
          <Panel header="搜索条件" key="1" extra={<FilterOutlined />}>
            <Form
              form={searchForm}
              layout="vertical"
              onFinish={handleSearch}
            >
              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item name="search" label="关键字搜索">
                    <Input 
                      placeholder="输入出库单号、仓库等"
              allowClear
                      prefix={<SearchOutlined />}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="warehouse_id" label="仓库">
                    <Select placeholder="选择仓库" allowClear>
                      {warehouses.map(warehouse => (
                        <Option key={`search-outbound-warehouse-${warehouse.value || warehouse.id}`} value={warehouse.value || warehouse.id}>
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
                        <Option key={`search-outbound-status-${value}`} value={value}>
                          {config.text}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="order_type" label="出库类型">
                    <Select placeholder="选择出库类型" allowClear>
                      <Option key="search-outbound-production" value="production">生产出库</Option>
                      <Option key="search-outbound-sale" value="sale">销售出库</Option>
                      <Option key="search-outbound-transfer" value="transfer">调拨出库</Option>
                      <Option key="search-outbound-other" value="other">其他出库</Option>
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

      {/* 材料出库单列表 */}
      <StyledCard 
        title={
          <Space>
            <FileTextOutlined />
            材料出库管理
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
              新建出库单
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
        title={currentRecord ? '编辑出库单' : '新增出库单'}
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
                            warehouse_name: warehouse.label || warehouse.name || warehouse.warehouse_name
                          });
                        }
                      }}
                    >
                      {warehouses.map(warehouse => (
                        <Option key={`form-outbound-warehouse-${warehouse.value || warehouse.id}`} value={warehouse.value || warehouse.id}>
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
                    label="出库日期"
                    rules={[{ required: true, message: '请选择出库日期' }]}
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
                    label="出库类型"
                    rules={[{ required: true, message: '请选择出库类型' }]}
                  >
                    <Select placeholder="请选择出库类型">
                      <Option key="form-outbound-production" value="production">生产出库</Option>
                      <Option key="form-outbound-sale" value="sale">销售出库</Option>
                      <Option key="form-outbound-transfer" value="transfer">调拨出库</Option>
                      <Option key="form-outbound-other" value="other">其他出库</Option>
                    </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
                  <Form.Item
                name="outbound_person_id"
                    label="出库人"
                    rules={[{ required: true, message: '请选择出库人' }]}
                  >
                    <Select
                      showSearch
                      placeholder="请选择出库人"
                  allowClear
                      filterOption={(input, option) => {
                        return option?.children?.toLowerCase().includes(input.toLowerCase());
                      }}
                    >
                      {employees.map(emp => (
                        <Option key={`form-outbound-employee-${emp.id}`} value={emp.id}>
                          {emp.employee_name || emp.name}
                        </Option>
                      ))}
                    </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
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
                        <Option key={`form-outbound-department-${dept.value || dept.id}`} value={dept.id}>
                          {dept.label || dept.dept_name || dept.department_name || dept.name}
                        </Option>
                      ))}
                    </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
                  <Form.Item label="来源单据类型" name="source_order_type">
                    <Input placeholder="如：生产订单" />
              </Form.Item>
            </Col>
            <Col span={12}>
                  <Form.Item label="来源单据号" name="source_order_number">
                    <Input placeholder="请输入来源单据号" />
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

      {/* 查看出库单详情弹窗 */}
      <Modal
        title={`出库单详情 - ${currentRecord?.order_number}`}
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
                  <Text strong>出库单号：</Text>
                  <Text>{currentRecord.order_number}</Text>
              </Col>
              <Col span={8}>
                  <Text strong>出库日期：</Text>
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
                  <Text strong>出库人：</Text>
                  <Text>{currentRecord.outbound_person}</Text>
              </Col>
              <Col span={8}>
                  <Text strong>部门：</Text>
                  <Text>{currentRecord.department}</Text>
              </Col>
              <Col span={8}>
                  <Text strong>出库类型：</Text>
                  <Text>{currentRecord.order_type}</Text>
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
            </Row>
            </TabPane>
            
            <TabPane tab="出库明细" key="2">
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
                        material_name: material.material_name || material.name,
                        material_code: material.material_code || material.code,
                        specification: material.specification_model || material.specification,
                        unit: material.unit_name || material.unit || ''
                      });
                    }
                  }}
                >
                  {materials.map(material => (
                    <Option key={`detail-outbound-material-${material.id}`} value={material.id}>
                      {material.material_code || material.code} - {material.material_name || material.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
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
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="unit" label="单位">
                <Input placeholder="单位" disabled />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="batch_number" label="批次号">
                <Input placeholder="请输入批次号" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="location_code" label="库位编码">
                <Input placeholder="请输入库位编码" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="remarks" label="备注">
            <TextArea rows={3} placeholder="请输入备注信息" />
          </Form.Item>

          {/* 隐藏字段 */}
          <Form.Item name="material_name" hidden>
            <Input />
          </Form.Item>
          <Form.Item name="material_code" hidden>
            <Input />
          </Form.Item>
          <Form.Item name="specification" hidden>
            <Input />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                确定
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
        title="审核出库单"
        open={auditModalVisible}
        onCancel={() => setAuditModalVisible(false)}
        footer={null}
      >
        <Form
          layout="vertical"
          onFinish={handleAudit}
        >
          <Form.Item
            name="approval_status"
            label="审核结果"
            rules={[{ required: true, message: '请选择审核结果' }]}
          >
            <Select placeholder="请选择审核结果">
              <Option key="audit-outbound-approved" value="approved">通过</Option>
              <Option key="audit-outbound-rejected" value="rejected">拒绝</Option>
            </Select>
          </Form.Item>

          <Form.Item name="approval_remarks" label="审核意见">
            <TextArea rows={3} placeholder="请输入审核意见" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                确定
              </Button>
              <Button onClick={() => setAuditModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default MaterialOutbound; 