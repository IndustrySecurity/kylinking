import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Switch,
  Row,
  Col,
  Card,
  Space,
  Popconfirm,
  message,
  Tooltip,
  Tag,
  Divider,
  Typography
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import {
  getEmployees,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  getEmploymentStatusOptions,
  getBusinessTypeOptions,
  getGenderOptions,
  getEvaluationLevelOptions,
} from '@/api/base-data/employee'
import { getDepartmentOptions } from '@/api/base-data/department'
import { getPositionOptions } from '@/api/base-data/position'
import dayjs from 'dayjs'

const { Title } = Typography
const { TextArea } = Input
const { Option } = Select

const EmployeeManagement = () => {
  const [loading, setLoading] = useState(false)
  const [employees, setEmployees] = useState([])
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })
  const [searchParams, setSearchParams] = useState({
    search: '',
    department_id: undefined,
    position_id: undefined,
    employment_status: undefined
  })
  
  // 选项数据
  const [options, setOptions] = useState({
    departments: [],
    positions: [],
    employmentStatus: [],
    businessTypes: [],
    genders: [],
    evaluationLevels: []
  })
  
  // 模态框状态
  const [modalVisible, setModalVisible] = useState(false)
  const [modalType, setModalType] = useState('create') // create | edit
  const [currentRecord, setCurrentRecord] = useState(null)
  const [form] = Form.useForm()

  // 加载选项数据
  const loadOptions = async () => {
    try {
      const [
        deptRes,
        posRes,
        statusRes,
        businessTypeRes,
        genderRes,
        evaluationRes
      ] = await Promise.all([
        getDepartmentOptions(),
        getPositionOptions(),
        getEmploymentStatusOptions(),
        getBusinessTypeOptions(),
        getGenderOptions(),
        getEvaluationLevelOptions()
      ])

      // 确保每个响应数据都是数组
      const safeArrayData = (data) => {
        if (Array.isArray(data)) return data
        if (data && typeof data === 'object' && Array.isArray(data.data)) return data.data
        return []
      }

      // 处理职位数据的特殊结构：data.positions
      const getPositionData = (response) => {
        if (response?.data?.data?.positions && Array.isArray(response.data.data.positions)) {
          return response.data.data.positions
        }
        return safeArrayData(response?.data)
      }

      const optionsData = {
        departments: safeArrayData(deptRes?.data),
        positions: getPositionData(posRes),
        employmentStatus: safeArrayData(statusRes?.data),
        businessTypes: safeArrayData(businessTypeRes?.data),
        genders: safeArrayData(genderRes?.data),
        evaluationLevels: safeArrayData(evaluationRes?.data)
      }

      setOptions(optionsData)
    } catch (error) {
      console.error('加载选项数据失败:', error)
      message.error('加载选项数据失败')
      // 设置默认空数组，确保组件不会崩溃
      setOptions({
        departments: [],
        positions: [],
        employmentStatus: [],
        businessTypes: [],
        genders: [],
        evaluationLevels: []
      })
    }
  }

  // 加载员工列表
  const loadEmployees = async (params = {}) => {
    try {
      setLoading(true);
      const response = await getEmployees({
        page: pagination.current,
        per_page: pagination.pageSize,
        ...searchParams,
        ...params
      });
  
      // 标准化响应数据结构处理
      const data = response.data || response;
      if (data.success) {
        // 解构数据并设置默认值防止空指针
        const { employees = [], pagination = {} } = data.data;
        const { total = 0, current_page = 1 } = pagination;
        // 生成唯一key（优先使用id，避免Date.now()重复）
        const processedData = employees.map((item, index) => ({
          ...item,
          key: item.id || `emp_temp_${index}_${Date.now()}`
        }));
  
        setEmployees(processedData);
        setPagination(prev => ({
          ...prev,
          total,
          current: current_page
        }));
      } else {
        message.error(data.message || '加载员工列表失败');
      }
    } catch (error) {
      console.error('员工数据加载异常', error);
      message.error('加载员工列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }))
    loadEmployees({ page: 1 })
  }

  // 重置搜索
  const handleReset = () => {
    setSearchParams({
      search: '',
      department_id: undefined,
      position_id: undefined,
      employment_status: undefined
    })
    setPagination(prev => ({ ...prev, current: 1 }))
    loadEmployees({ page: 1, search: '', department_id: undefined, position_id: undefined, employment_status: undefined })
  }

  // 表格分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination)
    loadEmployees({
      page: newPagination.current,
      per_page: newPagination.pageSize
    })
  }

  // 新建员工
  const handleCreate = async () => {
    setModalType('create')
    setCurrentRecord(null)
    form.resetFields()
    setModalVisible(true)
  }

  // 编辑员工
  const handleEdit = (record) => {
    setModalType('edit')
    setCurrentRecord(record)
    
    const formData = {
      ...record,
      hire_date: record.hire_date ? dayjs(record.hire_date) : null,
      birth_date: record.birth_date ? dayjs(record.birth_date) : null,
      leave_date: record.leave_date ? dayjs(record.leave_date) : null,
      contract_start_date: record.contract_start_date ? dayjs(record.contract_start_date) : null,
      contract_end_date: record.contract_end_date ? dayjs(record.contract_end_date) : null,
      expiry_warning_date: record.expiry_warning_date ? dayjs(record.expiry_warning_date) : null
    }
    
    form.setFieldsValue(formData)
    setModalVisible(true)
  }

  // 删除员工
  const handleDelete = async (id) => {
    try {
      const response = await deleteEmployee(id)
      if (response.success) {
        message.success('删除成功')
        loadEmployees()
      } else {
        message.error(response.message || '删除失败')
      }
    } catch (error) {
      message.error('删除失败')
    }
  }

  // 保存员工
  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      
      // 转换日期格式
      const data = {
        ...values,
        hire_date: values.hire_date?.format('YYYY-MM-DD') || null,
        birth_date: values.birth_date?.format('YYYY-MM-DD') || null,
        leave_date: values.leave_date?.format('YYYY-MM-DD') || null,
        contract_start_date: values.contract_start_date?.format('YYYY-MM-DD') || null,
        contract_end_date: values.contract_end_date?.format('YYYY-MM-DD') || null,
        expiry_warning_date: values.expiry_warning_date?.format('YYYY-MM-DD') || null
      }

      let response
      if (modalType === 'create') {
        response = await createEmployee(data)
      } else {
        response = await updateEmployee(currentRecord.id, data)
      }

      // 正确访问后端响应数据
      const backendResponse = response.data
      
      if (backendResponse && backendResponse.success) {
        message.success(modalType === 'create' ? '创建成功' : '更新成功')
        setModalVisible(false)
        loadEmployees()
      } else {
        const errorMessage = backendResponse?.message || '操作失败'
        console.error('操作失败，后端响应:', backendResponse)
        message.error(errorMessage)
      }
    } catch (error) {
      console.error('保存员工出错:', error)
      if (error.errorFields) {
        message.error('请检查表单填写')
      } else {
        // 检查是否是网络错误导致的假阳性
        if (error.response && error.response.status === 201) {
          // 状态码201表示创建成功，可能是响应格式解析问题
          const backendResponse = error.response.data
          if (backendResponse && backendResponse.success) {
            message.success(modalType === 'create' ? '创建成功' : '更新成功')
            setModalVisible(false)
            loadEmployees()
          } else {
            message.error('创建可能成功，但响应格式异常，请刷新页面查看')
          }
        } else {
          message.error('操作失败: ' + (error.message || '未知错误'))
        }
      }
    }
  }

  // 获取在职状态标签
  const getEmploymentStatusTag = (status) => {
    const statusMap = {
      trial: { color: 'orange', text: '试用' },
      active: { color: 'green', text: '在职' },
      leave: { color: 'red', text: '离职' },
      suspended: { color: 'red', text: '停职' }
    }
    const config = statusMap[status] || { color: 'default', text: status }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  // 根据职位自动填入部门
  const handlePositionChange = (positionId) => {
    if (Array.isArray(options.positions)) {
      const position = options.positions.find(p => p.value === positionId)
      if (position && position.department_id) {
        form.setFieldsValue({ department_id: position.department_id })
      }
    }
  }

  // 表格列定义
  const columns = [
    {
      title: '员工工号',
      dataIndex: 'employee_id',
      key: 'employee_id',
      width: 120,
      fixed: 'left'
    },
    {
      title: '员工姓名',
      dataIndex: 'employee_name',
      key: 'employee_name',
      width: 120,
      fixed: 'left'
    },
    {
      title: '在职状态',
      dataIndex: 'employment_status',
      key: 'employment_status',
      width: 100,
      fixed: 'left',
      render: (status) => getEmploymentStatusTag(status)
    },
    {
      title: '部门',
      dataIndex: ['department', 'dept_name'],
      key: 'department_name',
      width: 120
    },
    {
      title: '职位',
      dataIndex: ['position', 'position_name'],
      key: 'position_name',
      width: 120
    },
    {
      title: '业务类型',
      dataIndex: 'business_type',
      key: 'business_type',
      width: 100,
      render: (type) => {
        const typeMap = {
          salesperson: '业务员',
          purchaser: '采购员',
          comprehensive: '综合',
          delivery_person: '送货员'
        }
        return typeMap[type] || type
      }
    },
    {
      title: '性别',
      dataIndex: 'gender',
      key: 'gender',
      width: 80,
      render: (gender) => {
        const genderMap = {
          male: '男',
          female: '女',
          confidential: '保密'
        }
        return genderMap[gender] || gender
      }
    },
    {
      title: '手机',
      dataIndex: 'mobile_phone',
      key: 'mobile_phone',
      width: 120
    },
    {
      title: '入职日期',
      dataIndex: 'hire_date',
      key: 'hire_date',
      width: 120
    },
    {
      title: '座机',
      dataIndex: 'landline_phone',
      key: 'landline_phone',
      width: 120
    },
    {
      title: '身份证号',
      dataIndex: 'id_number',
      key: 'id_number',
      width: 180
    },
    {
      title: '出生日期',
      dataIndex: 'birth_date',
      key: 'birth_date',
      width: 120
    },
    {
      title: '籍贯',
      dataIndex: 'native_place',
      key: 'native_place',
      width: 120
    },
    {
      title: '民族',
      dataIndex: 'ethnicity',
      key: 'ethnicity',
      width: 80
    },
    {
      title: '省份',
      dataIndex: 'province',
      key: 'province',
      width: 100
    },
    {
      title: '城市',
      dataIndex: 'city',
      key: 'city',
      width: 100
    },
    {
      title: '流转卡标识',
      dataIndex: 'circulation_card_id',
      key: 'circulation_card_id',
      width: 120
    },
    {
      title: '车间工号',
      dataIndex: 'workshop_id',
      key: 'workshop_id',
      width: 100
    },
    {
      title: '评量级别',
      dataIndex: 'evaluation_level',
      key: 'evaluation_level',
      width: 100,
      render: (level) => {
        const levelMap = {
          finance: '财务',
          technology: '工艺',
          supply: '供应',
          marketing: '营销'
        }
        return levelMap[level] || level
      }
    },
    {
      title: '工龄工资',
      dataIndex: 'seniority_wage',
      key: 'seniority_wage',
      width: 100,
      render: (wage) => wage ? `¥${wage}` : '-'
    },
    {
      title: '考核工资',
      dataIndex: 'assessment_wage',
      key: 'assessment_wage',
      width: 100,
      render: (wage) => wage ? `¥${wage}` : '-'
    },
    {
      title: '合同开始',
      dataIndex: 'contract_start_date',
      key: 'contract_start_date',
      width: 120
    },
    {
      title: '合同结束',
      dataIndex: 'contract_end_date',
      key: 'contract_end_date',
      width: 120
    },
    {
      title: '用友编码',
      dataIndex: 'ufida_code',
      key: 'ufida_code',
      width: 120
    },
    {
      title: '金蝶推送',
      dataIndex: 'kingdee_push',
      key: 'kingdee_push',
      width: 100,
      render: (push) => push ? '是' : '否'
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      width: 200,
      ellipsis: {
        showTitle: false,
      },
      render: (remarks) => (
        <Tooltip placement="topLeft" title={remarks}>
          {remarks}
        </Tooltip>
      )
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      key: 'created_by_name',
      width: 100
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
    },
    {
      title: '修改人',
      dataIndex: 'updated_by_name',
      key: 'updated_by_name',
      width: 100
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 160,
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个员工吗？"
            onConfirm={() => handleDelete(record.id)}
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
  ]

  useEffect(() => {
    loadOptions()
    loadEmployees()
  }, [])

  return (
    <div className="employee-management">
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Title level={4}>员工管理</Title>
          
          {/* 搜索区域 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col xs={24} sm={6}>
              <Input
                placeholder="搜索员工工号/姓名/手机/身份证号"
                value={searchParams.search}
                onChange={(e) => setSearchParams(prev => ({ ...prev, search: e.target.value }))}
                onPressEnter={handleSearch}
              />
            </Col>
            <Col xs={24} sm={4}>
              <Select
                placeholder="选择部门"
                value={searchParams.department_id || undefined}
                onChange={(value) => setSearchParams(prev => ({ ...prev, department_id: value }))}
                allowClear
                style={{ width: '100%' }}
              >
                {Array.isArray(options.departments) && options.departments.map(dept => (
                  <Option key={dept.value} value={dept.value}>{dept.label}</Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={4}>
              <Select
                placeholder="选择职位"
                value={searchParams.position_id || undefined}
                onChange={(value) => setSearchParams(prev => ({ ...prev, position_id: value }))}
                allowClear
                style={{ width: '100%' }}
              >
                {Array.isArray(options.positions) && options.positions.map(pos => (
                  <Option key={pos.value} value={pos.value}>{pos.label}</Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={4}>
              <Select
                placeholder="选择在职状态"
                value={searchParams.employment_status || undefined}
                onChange={(value) => setSearchParams(prev => ({ ...prev, employment_status: value }))}
                allowClear
                style={{ width: '100%' }}
              >
                {Array.isArray(options.employmentStatus) && options.employmentStatus.map(status => (
                  <Option key={status.value} value={status.value}>{status.label}</Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={6}>
              <Space>
                <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                  搜索
                </Button>
                <Button icon={<ReloadOutlined />} onClick={handleReset}>
                  重置
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新建员工
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={employees}
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
          onChange={handleTableChange}
          rowKey="key"
          scroll={{ x: 3320 }}
        />
      </Card>

      {/* 编辑/新建模态框 */}
      <Modal
        title={modalType === 'create' ? '新建员工' : '编辑员工'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={1000}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Row gutter={16}>
            {/* 基本信息 */}
            <Col span={24}>
              <Divider orientation="left">基本信息</Divider>
            </Col>
            
            <Col span={8}>
              <Form.Item
                label="员工工号"
                name="employee_id"
                rules={[{ required: false, message: '请输入员工工号' }]}
              >
                <Input placeholder="系统自动生成" disabled />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item
                label="员工姓名"
                name="employee_name"
                rules={[{ required: true, message: '请输入员工姓名' }]}
              >
                <Input placeholder="请输入员工姓名" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item
                label="职位"
                name="position_id"
                rules={[{ required: true, message: '请选择职位' }]}
              >
                <Select
                  placeholder="请选择职位"
                  onChange={handlePositionChange}
                >
                  {Array.isArray(options.positions) && options.positions.map(pos => (
                    <Option key={pos.value} value={pos.value}>{pos.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item
                label="部门"
                name="department_id"
                tooltip="根据职位自动填入，不可修改"
              >
                <Select placeholder="根据职位自动填入" disabled>
                  {Array.isArray(options.departments) && options.departments.map(dept => (
                    <Option key={dept.value} value={dept.value}>{dept.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item
                label="在职状态"
                name="employment_status"
              >
                <Select placeholder="请选择在职状态">
                  {Array.isArray(options.employmentStatus) && options.employmentStatus.map(status => (
                    <Option key={status.value} value={status.value}>{status.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item
                label="业务类型"
                name="business_type"
              >
                <Select placeholder="请选择业务类型">
                  {Array.isArray(options.businessTypes) && options.businessTypes.map(type => (
                    <Option key={type.value} value={type.value}>{type.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item
                label="性别"
                name="gender"
              >
                <Select placeholder="请选择性别">
                  {Array.isArray(options.genders) && options.genders.map(gender => (
                    <Option key={gender.value} value={gender.value}>{gender.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            {/* 联系信息 */}
            <Col span={24}>
              <Divider orientation="left">联系信息</Divider>
            </Col>
            
            <Col span={8}>
              <Form.Item label="手机" name="mobile_phone">
                <Input placeholder="请输入手机号码" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="电话" name="landline_phone">
                <Input placeholder="请输入电话号码" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="紧急电话" name="emergency_phone">
                <Input placeholder="请输入紧急联系电话" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="身份证号" name="id_number">
                <Input placeholder="请输入身份证号" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="入职日期" name="hire_date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="出生日期" name="birth_date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="流转卡标识" name="circulation_card_id">
                <Input placeholder="请输入流转卡标识" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="车间工号" name="workshop_id">
                <Input placeholder="请输入车间工号" />
              </Form.Item>
            </Col>
            
            {/* 地址信息 */}
            <Col span={24}>
              <Divider orientation="left">地址信息</Divider>
            </Col>
            
            <Col span={8}>
              <Form.Item label="籍贯" name="native_place">
                <Input placeholder="请输入籍贯" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="民族" name="ethnicity">
                <Input placeholder="请输入民族" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="省/自治区" name="province">
                <Input placeholder="请输入省/自治区" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="地/市" name="city">
                <Input placeholder="请输入地/市" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="区/县" name="district">
                <Input placeholder="请输入区/县" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="街/乡" name="street">
                <Input placeholder="请输入街/乡" />
              </Form.Item>
            </Col>
            
            {/* 工作信息 */}
            <Col span={24}>
              <Divider orientation="left">工作信息</Divider>
            </Col>
            
            <Col span={8}>
              <Form.Item label="评量流程级别" name="evaluation_level">
                <Select placeholder="请选择评量流程级别">
                  {Array.isArray(options.evaluationLevels) && options.evaluationLevels.map(level => (
                    <Option key={level.value} value={level.value}>{level.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="离职日期" name="leave_date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="工龄工资" name="seniority_wage">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                  placeholder="请输入工龄工资"
                />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="考核工资" name="assessment_wage">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                  placeholder="请输入考核工资"
                />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="合同签订日期" name="contract_start_date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="合同终止日期" name="contract_end_date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="到期预警日期" name="expiry_warning_date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="用友编码" name="ufida_code">
                <Input placeholder="请输入用友编码" />
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item label="金蝶推送" name="kingdee_push" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            
            <Col span={24}>
              <Form.Item label="备注" name="remarks">
                <TextArea rows={3} placeholder="请输入备注信息" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  )
}

export default EmployeeManagement 