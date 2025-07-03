import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Select,
  DatePicker,
  Input,
  message,
  Tag,
  Tabs,
  InputNumber,
  Tooltip,
  Popconfirm
} from 'antd';
import { PlusOutlined, EditOutlined, EyeOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  getMaterialCountPlans,
  createMaterialCountPlan,
  getMaterialCountRecords,
  updateMaterialCountRecord,
  startMaterialCountPlan,
  completeMaterialCountPlan,
  adjustMaterialCountInventory,
  getWarehouseMaterialInventory,
  getWarehouses
} from '../../../api/business/materialCount';
import request from '../../../utils/request';

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
    // 对于没有修改的情况，不发送请求
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

const MaterialCount = () => {
  const [loading, setLoading] = useState(false);
  const [plans, setPlans] = useState([]);
  const [records, setRecords] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('plans');
  const [form] = Form.useForm();
  const [createForm] = Form.useForm();
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);

  // 获取盘点计划列表
  const fetchPlans = async () => {
    try {
      setLoading(true);
      const response = await getMaterialCountPlans();
      if (response.data.success) {
        setPlans(response.data.data.plans || []);
      }
    } catch (error) {
      message.error('获取盘点计划失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取仓库列表（只显示材料仓）
  const fetchWarehouses = async () => {
    try {
      const response = await getWarehouses();
      if (response.data.success) {
        const warehouseData = response.data.data;
        
        let warehouses = [];
        if (Array.isArray(warehouseData)) {
          // 处理选项格式数据，只保留材料仓
          warehouses = warehouseData
            .filter(item => {
              const warehouseType = item.warehouse_type || item.type;
              return warehouseType === 'material' || warehouseType === '材料仓';
            })
            .map(item => ({
              id: item.value || item.id,
              name: item.label || item.warehouse_name || item.name,
              code: item.code || item.warehouse_code,
              type: item.warehouse_type || item.type
            }));
        } else if (warehouseData?.warehouses && Array.isArray(warehouseData.warehouses)) {
          // 处理分页格式数据，只保留材料仓
          warehouses = warehouseData.warehouses
            .filter(item => {
              const warehouseType = item.warehouse_type || item.type;
              return warehouseType === 'material' || warehouseType === '材料仓';
            })
            .map(item => ({
              id: item.id,
              name: item.warehouse_name || item.name,
              code: item.warehouse_code || item.code,
              type: item.warehouse_type || item.type
            }));
        }
        
        setWarehouses(warehouses);
      } else {
        message.error('获取仓库列表失败');
      }
    } catch (error) {
      console.error('获取仓库列表错误:', error);
      message.error('获取仓库列表失败');
    }
  };

  // 获取盘点记录
  const fetchRecords = async (planId) => {
    try {
    setLoading(true);
      const response = await getMaterialCountRecords(planId);
      if (response.data.success) {
        setRecords(response.data.data || []);
      }
    } catch (error) {
      message.error('获取盘点记录失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载员工列表
  const loadEmployees = async () => {
    try {
      const response = await request('/tenant/basic-data/employees/options');
      if (response?.data?.success && response.data.data) {
        const employeeData = Array.isArray(response.data.data) ? response.data.data : [];
        setEmployees(employeeData);
      } else {
        setEmployees([]);
      }
    } catch (error) {
      console.error('加载员工列表失败:', error);
      setEmployees([]);
    }
  };

  // 加载部门列表
  const loadDepartments = async () => {
    try {
      const response = await request('/tenant/basic-data/departments/options');
      if (response?.data?.success && response.data.data) {
        const departmentData = Array.isArray(response.data.data) ? response.data.data : [];
        setDepartments(departmentData);
      } else {
        setDepartments([]);
      }
    } catch (error) {
      console.error('加载部门列表失败:', error);
      setDepartments([]);
    }
  };

  useEffect(() => {
    fetchPlans();
    fetchWarehouses();
    loadEmployees();
    loadDepartments();
  }, []);

  // 创建盘点计划
  const handleCreatePlan = async (values) => {
    if (!values.warehouse_id) {
      message.error('请先选择仓库');
      return;
    }
    
    try {
      setLoading(true);
      
      // 先获取选定仓库的材料库存，确保仓库有材料
      const inventoryResponse = await getWarehouseMaterialInventory(values.warehouse_id);
      if (!inventoryResponse.data.success || !inventoryResponse.data.data.length) {
        message.warning('该仓库没有材料库存，无法创建盘点计划');
        setLoading(false);
        return;
      }
      
      const planData = {
        warehouse_id: values.warehouse_id,
        warehouse_name: warehouses.find(w => w.id === values.warehouse_id)?.name || '',
        warehouse_code: warehouses.find(w => w.id === values.warehouse_id)?.code || '',
        count_person_id: values.count_person_id,
        department_id: values.department_id,
        count_date: values.count_date.toISOString(),
        notes: values.notes
      };

      const response = await createMaterialCountPlan(planData);
      
      if (response.data) {
        message.success('盘点计划创建成功');
        setCreateModalVisible(false);
        form.resetFields();
        fetchPlans();
      }
    } catch (error) {
      console.error('创建盘点计划失败:', error);
      message.error(error.response?.data?.message || '创建盘点计划失败');
    } finally {
      setLoading(false);
    }
  };

  // 开始盘点
  const handleStart = async (planId) => {
    try {
      const response = await startMaterialCountPlan(planId);
      if (response.data.success) {
        message.success('盘点已开始');
        fetchPlans();
      } else {
        message.error(response.data.error || '开始盘点失败');
      }
    } catch (error) {
      message.error('开始盘点失败');
    }
  };

  // 完成盘点
  const handleComplete = async (planId) => {
    try {
      const response = await completeMaterialCountPlan(planId);
      if (response.data.success) {
        message.success('盘点已完成');
        fetchPlans();
      } else {
        message.error(response.data.error || '完成盘点失败');
      }
    } catch (error) {
      message.error('完成盘点失败');
    }
  };

  // 调整库存
  const handleAdjust = async (planId) => {
    try {
      const response = await adjustMaterialCountInventory(planId);
      if (response.data.success) {
        message.success(response.data.message || '库存调整完成');
        fetchPlans(); // 刷新计划列表，更新状态
        // 如果当前查看的就是这个计划，同时刷新记录
        if (selectedPlan && selectedPlan.id === planId) {
          fetchRecords(planId);
        }
      } else {
        message.error(response.data.error || '库存调整失败');
      }
    } catch (error) {
      message.error('库存调整失败');
    }
  };

  // 查看盘点详情
  const handleView = (plan) => {
    setSelectedPlan(plan);
    fetchRecords(plan.id);
    setViewModalVisible(true);
  };

  // 保存实盘数量
  const handleSaveActualQuantity = async (recordId, actualQuantity) => {
    try {
      // 确保actualQuantity是数字类型
      const numericQuantity = Number(actualQuantity);
      if (isNaN(numericQuantity)) {
        message.error('请输入有效的数字');
        return;
      }
      
      const response = await updateMaterialCountRecord(
        selectedPlan.id,
        recordId,
        { actual_quantity: numericQuantity }
      );
      
      if (response.data.success) {
        // 更新本地记录
        const updatedRecord = response.data.data;
        setRecords(records.map(record => 
          record.id === recordId ? updatedRecord : record
        ));
        message.success('实盘数量已保存');
      } else {
        message.error(response.data.error || '保存失败');
      }
    } catch (error) {
      console.error('保存实盘数量失败:', error);
      message.error(error.response?.data?.error || '保存实盘数量失败');
    }
  };

  // 状态标签
  const getStatusTag = (status) => {
    const statusMap = {
      draft: { color: 'default', text: '草稿' },
      in_progress: { color: 'processing', text: '进行中' },
      completed: { color: 'success', text: '已完成' },
      adjusted: { color: 'purple', text: '已调整' }
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 计算差异样式
  const getVarianceStyle = (variance) => {
    if (!variance || variance === 0) return {};
    return {
      color: variance > 0 ? '#52c41a' : '#ff4d4f',
      fontWeight: 'bold'
    };
  };

  // 盘点计划表格列
  const planColumns = [
    {
      title: '盘点单号',
      dataIndex: 'count_number',
      key: 'count_number',
      width: 150
    },
    {
      title: '仓库',
      dataIndex: 'warehouse_name',
      key: 'warehouse_name',
      width: 120
    },
    {
      title: '仓库编号',
      dataIndex: 'warehouse_code',
      key: 'warehouse_code',
      width: 100
    },
    {
      title: '盘点人',
      dataIndex: 'count_person',
      key: 'count_person',
      width: 100,
      render: (text, record) => {
        // 优先显示后端返回的员工姓名
        if (text) return text;
        // 后备方案：根据ID查找
        if (record.count_person_id && employees.length > 0) {
          const employee = employees.find(emp => emp.id === record.count_person_id);
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
      title: '发生日期',
      dataIndex: 'count_date',
      key: 'count_date',
      width: 120,
      render: (date) => dayjs(date).format('YYYY-MM-DD')
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
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          {record.status === 'draft' && (
            <Popconfirm
              title="确定开始此盘点吗？"
              onConfirm={() => handleStart(record.id)}
            >
              <Button type="link">开始</Button>
            </Popconfirm>
          )}
          {record.status === 'in_progress' && (
            <Popconfirm
              title="确定完成此盘点吗？"
              onConfirm={() => handleComplete(record.id)}
            >
              <Button type="link">完成</Button>
            </Popconfirm>
          )}
          {record.status === 'completed' && (
            <Popconfirm
              title="确定要调整库存吗？此操作不可撤销！"
              onConfirm={() => handleAdjust(record.id)}
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

  // 盘点记录表格列
  const recordColumns = [
    {
      title: '材料编码',
      dataIndex: 'material_code',
      key: 'material_code',
      width: 120,
      fixed: 'left'
    },
    {
      title: '材料名称',
      dataIndex: 'material_name',
      key: 'material_name',
      width: 200,
      fixed: 'left'
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
      title: '账面数量',
      dataIndex: 'book_quantity',
      key: 'book_quantity',
      width: 120,
      align: 'right',
      render: (value) => value ? Number(value).toFixed(3) : '0.000'
    },
    {
      title: (
        <div>
          实盘数量
        </div>
      ),
      dataIndex: 'actual_quantity',
      key: 'actual_quantity',
      width: 140,
      align: 'right',
      render: (value, record) => (
        <EditableCell
          value={value}
          onSave={handleSaveActualQuantity}
          record={record}
          disabled={selectedPlan?.status !== 'in_progress'}
        />
      )
    },
    {
      title: '差异数量',
      dataIndex: 'variance_quantity',
      key: 'variance_quantity',
      width: 120,
      align: 'right',
      render: (value) => (
        <span style={getVarianceStyle(value)}>
          {value ? Number(value).toFixed(3) : '0.000'}
        </span>
      )
    },
    {
      title: '差异率(%)',
      dataIndex: 'variance_rate',
      key: 'variance_rate',
      width: 100,
      align: 'right',
      render: (value) => (
        <span style={getVarianceStyle(value)}>
          {value ? `${Number(value).toFixed(2)}%` : '0.00%'}
        </span>
      )
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
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const statusMap = {
          pending: { color: 'default', text: '待盘点' },
          counted: { color: 'processing', text: '已盘点' },
          adjusted: { color: 'success', text: '已调整' }
        };
        const config = statusMap[status] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card title="材料盘点管理">
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
              columns={planColumns}
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

      {/* 创建盘点计划Modal */}
      <Modal
        title="新建盘点计划"
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
          onFinish={handleCreatePlan}
        >
          <Form.Item
            name="warehouse_id"
            label="选择仓库"
            rules={[{ required: true, message: '请选择仓库' }]}
          >
            <Select
              placeholder="请选择仓库"
              showSearch
              optionFilterProp="children"
              onChange={(value) => {
                const warehouse = warehouses.find(w => w.id === value);
                if (warehouse) {
                  form.setFieldsValue({
                    warehouse_name: warehouse.name,
                    warehouse_code: warehouse.code
                  });
                }
              }}
            >
              {warehouses.map(warehouse => (
                <Option key={`count-warehouse-${warehouse.id}`} value={warehouse.id}>
                  {warehouse.name} {warehouse.code ? `(${warehouse.code})` : ''}
                </Option>
              ))}
                </Select>
              </Form.Item>

          <Form.Item name="warehouse_name" hidden>
            <Input />
              </Form.Item>

          <Form.Item name="warehouse_code" hidden>
            <Input />
              </Form.Item>

          <Form.Item
            name="count_person_id"
            label="盘点人"
            rules={[{ required: true, message: '请选择盘点人' }]}
          >
            <Select placeholder="请选择盘点人">
              {Array.isArray(employees) && employees.map((employee) => (
                <Option key={`count-employee-${employee.id}`} value={employee.id}>
                  {employee.employee_name || employee.name}
                </Option>
              ))}
                </Select>
              </Form.Item>

          <Form.Item
            name="department_id"
            label="部门"
          >
            <Select placeholder="请选择部门" allowClear>
              {Array.isArray(departments) && departments.map((dept) => (
                <Option key={`count-department-${dept.id}`} value={dept.id}>
                  {dept.dept_name || dept.department_name || dept.name}
                </Option>
              ))}
                </Select>
              </Form.Item>

          <Form.Item
            name="count_date"
            label="发生日期"
            rules={[{ required: true, message: '请选择发生日期' }]}
            initialValue={dayjs()}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="notes"
            label="备注"
          >
            <TextArea rows={3} placeholder="请输入备注" />
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

      {/* 查看盘点详情Modal */}
      <Modal
        title={`盘点详情 - ${selectedPlan?.count_number}`}
        open={viewModalVisible}
        onCancel={() => {
          setViewModalVisible(false);
          setSelectedPlan(null);
          setRecords([]);
        }}
        footer={null}
        width={1400}
      >
        {selectedPlan && (
          <div>
            <div style={{ marginBottom: 16, padding: 16, background: '#f5f5f5', borderRadius: 4 }}>
              <Space size="large">
                <span><strong>仓库：</strong>{selectedPlan.warehouse_name}</span>
                <span><strong>盘点人：</strong>{selectedPlan.count_person}</span>
                <span><strong>部门：</strong>{selectedPlan.department}</span>
                <span><strong>发生日期：</strong>{dayjs(selectedPlan.count_date).format('YYYY-MM-DD')}</span>
                <span><strong>状态：</strong>{getStatusTag(selectedPlan.status)}</span>
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

export default MaterialCount; 