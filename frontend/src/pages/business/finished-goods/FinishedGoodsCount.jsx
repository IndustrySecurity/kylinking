import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Form,
  Input,
  Select,
  DatePicker,
  Card,
  Modal,
  message,
  Space,
  Tag,
  Popconfirm,
  InputNumber,
  Row,
  Col,
  Statistic,
  Descriptions,
  Badge,
  Divider,
  Tooltip,
  Tabs
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  BarChartOutlined,
  EyeOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  getProductCountPlans,
  createProductCountPlan,
  getProductCountPlan,
  getProductCountRecords,
  updateProductCountRecord,
  startProductCountPlan,
  completeProductCountPlan,
  adjustProductCountInventory,
  deleteProductCountPlan,
  getProductCountStatistics,
  getWarehouses,
  getEmployees,
  getDepartments
} from '../../../api/business/inventory/productCount';

const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

// 可编辑单元格组件
const EditableCell = ({ value, onSave, record, disabled }) => {
  const [editing, setEditing] = useState(false);
  const [inputValue, setInputValue] = useState(value);
  
  // 如果没有实盘数量，自动填入账面数量作为默认值
  const defaultValue = value !== null && value !== undefined ? value : record.book_quantity;
  const isDefaultValue = value === null || value === undefined || Number(value).toFixed(3) === Number(record.book_quantity || 0).toFixed(3);

  const handleSave = async () => {
    // 将输入值转换为数字进行比较
    const numericInput = Number(inputValue);
    const numericValue = Number(value);
    const bookQuantity = Number(record.book_quantity || 0);
    
    // 如果输入值和当前值不同，才保存
    const hasChanged = !isNaN(numericInput) && (
      isNaN(numericValue) ? numericInput !== bookQuantity : numericInput !== numericValue
    );
    
    if (hasChanged) {
      await onSave(record.id, numericInput);
    }
    setEditing(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSave();
    }
  };

  useEffect(() => {
    // 如果没有实盘数量，自动设置为账面数量
    if ((value === null || value === undefined) && record.book_quantity) {
      setInputValue(Number(record.book_quantity).toFixed(3));
    } else {
      setInputValue(value);
    }
  }, [value, record.book_quantity]);

  if (disabled) {
    return (
      <span style={{
        color: isDefaultValue ? '#1890ff' : '#000',
        fontWeight: isDefaultValue ? 'bold' : 'normal'
      }}>
        {defaultValue !== null && defaultValue !== undefined ? Number(defaultValue).toFixed(3) : '0.000'}
      </span>
    );
  }

  if (editing) {
    return (
      <InputNumber
        value={inputValue}
        onChange={setInputValue}
        onBlur={handleSave}
        onPressEnter={handleKeyPress}
        style={{ width: '100%' }}
        precision={3}
        min={0}
        autoFocus
      />
    );
  }

  const displayValue = defaultValue !== null && defaultValue !== undefined ? Number(defaultValue).toFixed(3) : Number(record.book_quantity || 0).toFixed(3);

  return (
    <div
      onClick={() => setEditing(true)}
      style={{
        cursor: 'pointer',
        padding: '4px 8px',
        borderRadius: '4px',
        minHeight: '32px',
        display: 'flex',
        alignItems: 'center',
        backgroundColor: isDefaultValue ? '#e6f7ff' : '#fff',
        color: isDefaultValue ? '#1890ff' : '#000',
        fontWeight: isDefaultValue ? 'bold' : 'normal',
        border: isDefaultValue ? '1px dashed #1890ff' : '1px dashed #d9d9d9'
      }}
    >
      {displayValue}
    </div>
  );
};

const FinishedGoodsCount = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });
  const [searchParams, setSearchParams] = useState({});
  
  // Tab状态
  const [activeTab, setActiveTab] = useState('plans');
  
  // 弹窗状态
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  
  // 数据状态
  const [currentPlan, setCurrentPlan] = useState(null);
  const [records, setRecords] = useState([]);
  
  // 基础数据
  const [warehouses, setWarehouses] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  
  // 表单
  const [createForm] = Form.useForm();


  // 状态配置
  const statusConfig = {
    draft: { text: '草稿', color: 'default' },
    in_progress: { text: '进行中', color: 'processing' },
    completed: { text: '已完成', color: 'success' },
    adjusted: { text: '已调整', color: 'purple' }
  };

  const recordStatusConfig = {
    pending: { text: '待盘点', color: 'default' },
    counted: { text: '已盘点', color: 'success' },
    adjusted: { text: '已调整', color: 'purple' }
  };

  // 初始化
  useEffect(() => {
    loadPlans();
    loadBasicData();
  }, []);

  // 加载基础数据
  const loadBasicData = async () => {
    try {
      const [warehousesRes, employeesRes, departmentsRes] = await Promise.all([
        getWarehouses(),
        getEmployees(),
        getDepartments()
      ]);
      
      // 处理仓库数据
      // 处理仓库数据 - Axios响应格式: {data: {success: true, data: [...]}}
      let warehouseData = [];
      if (warehousesRes && warehousesRes.data && warehousesRes.data.data && Array.isArray(warehousesRes.data.data)) {
        warehouseData = warehousesRes.data.data;
      }
      // 过滤出成品仓库
      const productWarehouses = warehouseData.filter(w => 
        w.type === 'finished_goods' || 
        (w.warehouse_name && w.warehouse_name.includes('成品')) ||
        (w.label && w.label.includes('成品'))
      );
      setWarehouses(productWarehouses.length > 0 ? productWarehouses : warehouseData);
      
      // 处理员工数据 - Axios响应格式: {data: {success: true, data: [...]}}
      let employeeData = [];
      if (employeesRes && employeesRes.data && employeesRes.data.data && Array.isArray(employeesRes.data.data)) {
        employeeData = employeesRes.data.data;
      }
      setEmployees(employeeData);
       
       // 处理部门数据 - Axios响应格式: {data: {success: true, data: [...]}}
       let departmentData = [];
       if (departmentsRes && departmentsRes.data && departmentsRes.data.data && Array.isArray(departmentsRes.data.data)) {
         departmentData = departmentsRes.data.data;
       }
      setDepartments(departmentData);
    } catch (error) {
      console.error('加载基础数据失败:', error);
      message.error('加载基础数据失败: ' + error.message);
    }
  };

  // 加载盘点计划列表
  const loadPlans = async (params = {}) => {
    setLoading(true);
    try {
      const queryParams = {
        page: pagination.current,
        page_size: pagination.pageSize,
        ...searchParams,
        ...params
      };
      
      const response = await getProductCountPlans(queryParams);
      
      // 处理响应数据结构
      const result = response.data || response;
      
      if (result.success) {
        const items = result.data?.items || [];
        
        setPlans(items);
        setPagination(prev => ({
          ...prev,
          total: result.data?.total || 0,
          current: result.data?.page || 1
        }));
      } else {
        message.error(result.message || '获取盘点计划失败');
      }
    } catch (error) {
      console.error('获取盘点计划失败:', error);
      message.error('获取盘点计划失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // 创建盘点计划
  const handleCreate = async (values) => {
    
    try {
      // 验证必填字段
      if (!values.warehouse_id) {
        message.error('请选择盘点仓库');
        return;
      }
      
      if (!values.count_person_id) {
        message.error('请选择盘点人');
        return;
      }
      
      if (!values.count_date) {
        message.error('请选择盘点日期');
        return;
      }
      
      // 获取仓库名称
      const selectedWarehouse = warehouses.find(w => 
        (w.value || w.id) === values.warehouse_id
      );
      const warehouse_name = selectedWarehouse ? 
        (selectedWarehouse.label || selectedWarehouse.warehouse_name) : '';

      const data = {
        ...values,
        warehouse_name,
        count_date: values.count_date.toISOString()
      };
      
      
      const response = await createProductCountPlan(data);
      
      // 检查响应结构，可能成功信息在 data 中
      const result = response.data || response;
      
      if (result.success) {
        message.success('创建盘点计划成功');
        setCreateModalVisible(false);
        createForm.resetFields();
        loadPlans();
      } else {
        message.error(result.message || '创建失败');
      }
    } catch (error) {
      console.error('创建盘点计划错误:', error);
      message.error('创建盘点计划失败: ' + error.message);
    }
  };

  // 查看详情


  // 开始盘点
  const handleStart = async (planId) => {
    try {
      const response = await startProductCountPlan(planId);
      const result = response.data || response;
      
      if (result.success) {
        message.success('盘点已开始');
        loadPlans();
      } else {
        message.error(result.message || '开始盘点失败');
      }
    } catch (error) {
      console.error('开始盘点失败:', error);
      message.error(error.response?.data?.message || '开始盘点失败');
    }
  };

  // 完成盘点
  const handleComplete = async (planId) => {
    try {
      const response = await completeProductCountPlan(planId);
      const result = response.data || response;
      
      if (result.success) {
        message.success('盘点已完成');
        loadPlans();
      } else {
        message.error(result.message || '完成盘点失败');
      }
    } catch (error) {
      console.error('完成盘点失败:', error);
      message.error(error.response?.data?.message || '完成盘点失败');
    }
  };

  // 删除盘点计划
  const handleDelete = async (planId) => {
    try {
      const response = await deleteProductCountPlan(planId);
      const result = response.data || response;
      
      if (result.success) {
        message.success('删除盘点计划成功');
        loadPlans();
      } else {
        message.error(result.message || '删除盘点计划失败');
      }
    } catch (error) {
      console.error('删除盘点计划失败:', error);
      message.error(error.response?.data?.message || '删除盘点计划失败');
    }
  };

  // 保存实盘数量
  const handleSaveActualQuantity = async (recordId, actualQuantity) => {
    try {
      const response = await updateProductCountRecord(currentPlan.id, recordId, {
        actual_quantity: actualQuantity,
        status: 'counted'
      });
      
      const result = response.data || response;
      if (result.success) {
        message.success('保存成功');
        // 重新加载记录
        handleView(currentPlan);
      } else {
        message.error(result.message || '保存失败');
      }
    } catch (error) {
      console.error('保存实盘数量失败:', error);
      message.error('保存失败: ' + error.message);
    }
  };

  // 查看盘点记录
  const handleView = async (plan) => {
    try {
      setCurrentPlan(plan);
      
      // 加载盘点记录
      const recordsResponse = await getProductCountRecords(plan.id, {
        page: 1,
        page_size: 50
      });
      
      const recordsResult = recordsResponse.data || recordsResponse;
      
      if (recordsResult.success) {
        const items = recordsResult.data?.items || [];
        setRecords(items);
      }
      

      
      setViewModalVisible(true);
    } catch (error) {
      message.error('获取盘点记录失败: ' + error.message);
    }
  };



  // 调整库存
  const handleAdjustInventory = async (planId) => {
    try {
      const response = await adjustProductCountInventory(planId, {
        record_ids: [] // 后端会自动处理有差异的记录
      });
      
      const result = response.data || response;
      
      if (result.success) {
        message.success(result.message || '库存调整完成');
        loadPlans(); // 刷新计划列表，更新状态
        // 如果当前查看的就是这个计划，同时刷新记录
        if (currentPlan && currentPlan.id === planId) {
          handleView(currentPlan);
        }
      } else {
        message.error(result.message || '库存调整失败');
      }
    } catch (error) {
      console.error('调整库存失败:', error);
      message.error(error.response?.data?.message || '调整库存失败');
    }
  };



  // 表格列定义
  const columns = [
    {
      title: '盘点单号',
      dataIndex: 'count_number',
      key: 'count_number',
      width: 140,
      fixed: 'left'
    },
    {
      title: '仓库',
      dataIndex: 'warehouse_name',
      key: 'warehouse_name',
      width: 120
    },
    {
      title: '盘点人',
      dataIndex: 'count_person_name',
      key: 'count_person_name',
      width: 100
    },
    {
      title: '部门',
      dataIndex: 'department_name',
      key: 'department_name',
      width: 120
    },
    {
      title: '盘点日期',
      dataIndex: 'count_date',
      key: 'count_date',
      width: 120,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD') : '-'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const config = statusConfig[status] || { text: status, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD HH:mm') : '-'
    },
    {
      title: '备注',
      dataIndex: 'notes',
      key: 'notes',
      width: 200,
      ellipsis: { showTitle: false },
      render: (text) => (
        <Tooltip title={text} placement="topLeft">
          {text || '-'}
        </Tooltip>
      )
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
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          
          {record.status === 'draft' && (
            <>
              <Popconfirm
                title="确定开始此盘点吗？"
                onConfirm={() => handleStart(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button type="link">开始</Button>
              </Popconfirm>
              
              <Popconfirm
                title="确定删除这个盘点计划吗？"
                onConfirm={() => handleDelete(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button type="link" danger>
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
          
          {record.status === 'in_progress' && (
            <Popconfirm
              title="确定完成此盘点吗？"
              onConfirm={() => handleComplete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button type="link">完成</Button>
            </Popconfirm>
          )}
          
          {record.status === 'completed' && (
            <Popconfirm
              title="确定要调整库存吗？此操作不可撤销！"
              onConfirm={() => handleAdjustInventory(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button type="link" danger>调整库存</Button>
            </Popconfirm>
          )}
          
          {record.status === 'adjusted' && (
            <span style={{ color: '#8c8c8c' }}>已完成调整</span>
          )}
        </Space>
      )
    }
  ];

  // 盘点记录列定义
  const recordColumns = [
    {
      title: '产品编码',
      dataIndex: 'product_code',
      key: 'product_code',
      width: 120,
      fixed: 'left'
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 150,
      fixed: 'left'
    },
    {
      title: '规格',
      dataIndex: 'product_spec',
      key: 'product_spec',
      width: 120,
      ellipsis: true
    },
    {
      title: '客户',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 120
    },
    {
      title: '袋型',
      dataIndex: 'bag_type_name',
      key: 'bag_type_name',
      width: 100
    },
    {
      title: '批次号',
      dataIndex: 'batch_number',
      key: 'batch_number',
      width: 120
    },
    {
      title: '库位',
      dataIndex: 'location_code',
      key: 'location_code',
      width: 100
    },
    {
      title: '单位',
      dataIndex: 'base_unit',
      key: 'base_unit',
      width: 80
    },
    {
      title: '账面数量',
      dataIndex: 'book_quantity',
      key: 'book_quantity',
      width: 100,
      align: 'right',
      render: (value) => Number(value).toFixed(3)
    },
    {
      title: '实盘数量',
      dataIndex: 'actual_quantity',
      key: 'actual_quantity',
      width: 120,
      align: 'center',
      render: (value, record) => (
        <EditableCell
          value={value}
          record={record}
          onSave={handleSaveActualQuantity}
          disabled={currentPlan?.status !== 'in_progress'}
        />
      )
    },
    {
      title: '差异数量',
      dataIndex: 'variance_quantity',
      key: 'variance_quantity',
      width: 100,
      align: 'right',
      render: (value) => {
        if (value === null) return '-';
        const num = Number(value);
        return (
          <span style={{ color: num > 0 ? '#52c41a' : num < 0 ? '#ff4d4f' : '#000' }}>
            {num > 0 ? '+' : ''}{num.toFixed(3)}
          </span>
        );
      }
    },
    {
      title: '差异率(%)',
      dataIndex: 'variance_rate',
      key: 'variance_rate',
      width: 100,
      align: 'right',
      render: (value) => {
        if (value === null) return '-';
        const num = Number(value);
        return (
          <span style={{ color: num > 0 ? '#52c41a' : num < 0 ? '#ff4d4f' : '#000' }}>
            {num > 0 ? '+' : ''}{num.toFixed(2)}%
          </span>
        );
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const config = recordStatusConfig[status] || { text: status, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '差异原因',
      dataIndex: 'variance_reason',
      key: 'variance_reason',
      width: 150,
      ellipsis: { showTitle: false },
      render: (text) => (
        <Tooltip title={text} placement="topLeft">
          {text || '-'}
        </Tooltip>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card title="成品盘点管理">
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="盘点计划" key="plans">
            <div style={{ marginBottom: 16 }}>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                新建盘点
              </Button>
            </div>

            <Table
              columns={columns}
              dataSource={plans}
              rowKey="id"
              loading={loading}
              scroll={{ x: 1000 }}
              pagination={{
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`
              }}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* 创建盘点计划弹窗 */}
      <Modal
        title="创建成品盘点计划"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
        width={600}
        afterOpenChange={(visible) => {
          if (visible) {
            // 模态框打开时设置默认值
            createForm.setFieldsValue({
              count_date: dayjs() // 设置当前日期为默认值
            });
          }
        }}
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={handleCreate}
          onFinishFailed={(errorInfo) => {
            message.error('请检查表单填写是否完整');
          }}
          initialValues={{
            count_date: dayjs() // 设置初始值为当前日期
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="warehouse_id"
                label="盘点仓库"
                rules={[{ required: true, message: '请选择盘点仓库' }]}
              >
                <Select placeholder="选择成品仓库" showSearch optionFilterProp="children">
                  {warehouses.map((warehouse, index) => (
                    <Option key={warehouse.value || warehouse.id || `warehouse-${index}`} value={warehouse.value || warehouse.id}>
                      {warehouse.label || warehouse.warehouse_name || '未命名仓库'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="count_person_id"
                label="盘点人"
                rules={[{ required: true, message: '请选择盘点人' }]}
              >
                <Select 
                  placeholder="请选择盘点人"
                  onChange={(value) => {
                    // 根据选择的员工自动填充部门
                    if (value && employees.length > 0) {
                      const selectedEmployee = employees.find(emp => emp.value === value);
                      if (selectedEmployee && selectedEmployee.department_id) {
                        createForm.setFieldsValue({
                          department_id: selectedEmployee.department_id
                        });
                      }
                    }
                  }}
                >
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
              <Form.Item
                name="department_id"
                label="所属部门"
              >
                <Select placeholder="选择部门" allowClear showSearch>
                  {departments.map((dept, index) => (
                    <Option key={dept.value || dept.id || `dept-${index}`} value={dept.value || dept.id}>
                      {dept.label || dept.dept_name || dept.name || '未命名部门'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="count_date"
                label="盘点日期"
                rules={[{ required: true, message: '请选择盘点日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item name="notes" label="备注">
            <TextArea rows={3} placeholder="输入备注信息" />
          </Form.Item>
          
          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Space>
              <Button onClick={() => setCreateModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                创建
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 查看盘点详情Modal */}
      <Modal
        title={`盘点详情 - ${currentPlan?.count_number}`}
        open={viewModalVisible}
        onCancel={() => {
          setViewModalVisible(false);
          setCurrentPlan(null);
          setRecords([]);
        }}
        footer={null}
        width={1400}
      >
        {currentPlan && (
          <div>
            <div style={{ marginBottom: 16, padding: 16, background: '#f5f5f5', borderRadius: 4 }}>
              <Space size="large">
                <span><strong>仓库：</strong>{currentPlan.warehouse_name}</span>
                <span><strong>盘点人：</strong>{currentPlan.count_person_name}</span>
                <span><strong>部门：</strong>{currentPlan.department_name || '-'}</span>
                <span><strong>盘点日期：</strong>{dayjs(currentPlan.count_date).format('YYYY-MM-DD')}</span>
                <span><strong>状态：</strong>
                  <Tag color={statusConfig[currentPlan.status]?.color}>
                    {statusConfig[currentPlan.status]?.text}
                  </Tag>
                </span>
              </Space>
            </div>

            <Table
              columns={recordColumns}
              dataSource={records}
              rowKey="id"
              loading={loading}
              scroll={{ x: 1400, y: 400 }}
              pagination={{
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`
              }}
            />
          </div>
        )}
      </Modal>


    </div>
  );
};

export default FinishedGoodsCount;