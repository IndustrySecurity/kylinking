import React, { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Tabs,
  Switch,
  Tooltip,
  Tag,
  Divider
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  TeamOutlined,
  UserOutlined,
  SettingOutlined,
  AppstoreOutlined,
  ToolOutlined
} from '@ant-design/icons'
import {
  getTeamGroups,
  getTeamGroup,
  createTeamGroup,
  updateTeamGroup,
  deleteTeamGroup,
  getTeamGroupFormOptions,
  addTeamMember,
  updateTeamMember,
  deleteTeamMember,
  addTeamMachine,
  deleteTeamMachine,
  addTeamProcess,
  deleteTeamProcess
} from '@/api/teamGroup'

const { Title } = Typography
const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs

const TeamGroupManagement = () => {
  const [loading, setLoading] = useState(false)
  const [teamGroups, setTeamGroups] = useState([])
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })
  const [searchParams, setSearchParams] = useState({
    search: '',
    is_enabled: undefined
  })

  // 选项数据
  const [options, setOptions] = useState({
    employees: [],
    machines: [],
    process_categories: []
  })

  // 模态框状态
  const [modalVisible, setModalVisible] = useState(false)
  const [modalType, setModalType] = useState('create') // create | edit | detail
  const [currentRecord, setCurrentRecord] = useState(null)
  const [form] = Form.useForm()

  // 子表相关状态
  const [activeTab, setActiveTab] = useState('basic')
  const [membersData, setMembersData] = useState([])
  const [machinesData, setMachinesData] = useState([])
  const [processesData, setProcessesData] = useState([])

  // 子表编辑状态
  const [memberFormVisible, setMemberFormVisible] = useState(false)
  const [memberForm] = Form.useForm()
  const [editingMember, setEditingMember] = useState(null)

  // 机台和工序对话框状态
  const [machineFormVisible, setMachineFormVisible] = useState(false)
  const [machineForm] = Form.useForm()
  const [processFormVisible, setProcessFormVisible] = useState(false)
  const [processForm] = Form.useForm()

  // 加载选项数据
  const loadOptions = async () => {
    try {
      const response = await getTeamGroupFormOptions()
      if (response?.data?.success) {
        setOptions(response.data.data)
      }
    } catch (error) {
      console.error('加载选项数据失败:', error)
      message.error('加载选项数据失败')
    }
  }

  // 加载班组列表
  const loadTeamGroups = async (params = {}) => {
    try {
      setLoading(true)
      const response = await getTeamGroups({
        page: pagination.current,
        per_page: pagination.pageSize,
        ...searchParams,
        ...params
      })

      if (response?.data?.success) {
        setTeamGroups(response.data.data || [])
        if (response.data.pagination) {
          setPagination(prev => ({
            ...prev,
            current: response.data.pagination.page || 1,
            total: response.data.pagination.total || 0
          }))
        }
      } else {
        message.error(response?.data?.message || '加载班组列表失败')
      }
    } catch (error) {
      message.error('加载班组列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }))
    loadTeamGroups({ page: 1 })
  }

  // 重置搜索
  const handleReset = () => {
    setSearchParams({
      search: '',
      is_enabled: undefined
    })
    setPagination(prev => ({ ...prev, current: 1 }))
    loadTeamGroups({ page: 1, search: '', is_enabled: undefined })
  }

  // 表格分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination)
    loadTeamGroups({
      page: newPagination.current,
      per_page: newPagination.pageSize
    })
  }

  // 新建班组
  const handleCreate = () => {
    setModalType('create')
    setCurrentRecord(null)
    setActiveTab('basic')
    setMembersData([])
    setMachinesData([])
    setProcessesData([])
    form.resetFields()
    form.setFieldsValue({ sort_order: 1 })
    setModalVisible(true)
  }

  // 编辑班组
  const handleEdit = async (record) => {
    try {
      setLoading(true)
      const response = await getTeamGroup(record.id)
      if (response?.data?.success) {
        const teamGroupData = response.data.data
        setModalType('edit')
        setCurrentRecord(teamGroupData)
        setActiveTab('basic')
        
        // 设置表单数据
        form.setFieldsValue({
          team_name: teamGroupData.team_name,
          circulation_card_id: teamGroupData.circulation_card_id,
          day_shift_hours: teamGroupData.day_shift_hours,
          night_shift_hours: teamGroupData.night_shift_hours,
          rotating_shift_hours: teamGroupData.rotating_shift_hours,
          description: teamGroupData.description,
          sort_order: teamGroupData.sort_order,
          is_enabled: teamGroupData.is_enabled
        })

        // 设置子表数据
        setMembersData(teamGroupData.team_members || [])
        setMachinesData(teamGroupData.team_machines || [])
        setProcessesData(teamGroupData.team_processes || [])
        
        setModalVisible(true)
      }
    } catch (error) {
      message.error('获取班组详情失败')
    } finally {
      setLoading(false)
    }
  }



  // 删除班组
  const handleDelete = async (id) => {
    try {
      const response = await deleteTeamGroup(id)
      if (response?.data?.success) {
        message.success('班组删除成功')
        loadTeamGroups()
      } else {
        message.error(response?.data?.message || '删除失败')
      }
    } catch (error) {
      message.error('删除失败')
    }
  }

  // 保存班组
  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      
      const submitData = {
        ...values,
        team_members: membersData.map(member => ({
          employee_id: member.employee_id,
          piece_rate_percentage: member.piece_rate_percentage || 0,
          saving_bonus_percentage: member.saving_bonus_percentage || 0,
          remarks: member.remarks,
          sort_order: member.sort_order || 0
        })),
        team_machines: machinesData.map(machine => ({
          machine_id: machine.machine_id,
          remarks: machine.remarks,
          sort_order: machine.sort_order || 0
        })),
        team_processes: processesData.map(process => ({
          process_category_id: process.process_category_id,
          sort_order: process.sort_order || 0
        }))
      }

      let response
      if (modalType === 'create') {
        response = await createTeamGroup(submitData)
      } else {
        response = await updateTeamGroup(currentRecord.id, submitData)
      }

      if (response?.data?.success) {
        message.success(modalType === 'create' ? '班组创建成功' : '班组更新成功')
        setModalVisible(false)
        loadTeamGroups()
      } else {
        message.error(response?.data?.message || '操作失败')
      }
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查表单填写')
      } else {
        message.error('操作失败')
      }
    }
  }

  // 班组成员管理
  const handleAddMember = () => {
    setEditingMember(null)
    memberForm.resetFields()
    // 设置默认排序号：取当前最大值+1，默认从1开始
    const maxSortOrder = membersData.length > 0 
      ? Math.max(...membersData.map(m => m.sort_order || 0))
      : 0
    memberForm.setFieldsValue({ sort_order: maxSortOrder + 1 })
    setMemberFormVisible(true)
  }

  const handleEditMember = (member) => {
    setEditingMember(member)
    memberForm.setFieldsValue(member)
    setMemberFormVisible(true)
  }

  const handleSaveMember = async () => {
    try {
      const values = await memberForm.validateFields()
      
      if (editingMember) {
        // 更新成员
        const updatedMembers = membersData.map(member => 
          member.id === editingMember.id ? { ...member, ...values } : member
        )
        setMembersData(updatedMembers)
      } else {
        // 添加成员
        const employee = options.employees.find(emp => emp.id === values.employee_id)
        if (employee) {
          // 检查是否已存在
          const exists = membersData.some(member => member.employee_id === values.employee_id)
          if (exists) {
            message.error('该员工已在班组中')
            return
          }
          
          const newMember = {
            id: Date.now(), // 临时ID
            employee_id: values.employee_id,
            employee_name: employee.employee_name,
            employee_code: employee.employee_id,
            position_name: employee.position_name,
            ...values
          }
          setMembersData([...membersData, newMember])
        }
      }
      
      setMemberFormVisible(false)
    } catch (error) {
      message.error('请检查表单填写')
    }
  }

  const handleDeleteMember = (member) => {
    setMembersData(membersData.filter(m => m.id !== member.id))
  }

  // 班组机台管理
  const handleAddMachine = (machineId) => {
    if (!machineId) return
    
    const machine = options.machines.find(m => m.id === machineId)
    if (machine) {
      // 检查是否已存在
      const exists = machinesData.some(m => m.machine_id === machineId)
      if (exists) {
        message.error('该机台已在班组中')
        return
      }
      
      const newMachine = {
        id: Date.now(),
        machine_id: machineId,
        machine_name: machine.machine_name,
        machine_code: machine.machine_code,
        remarks: '',
        sort_order: 0
      }
      setMachinesData([...machinesData, newMachine])
    }
  }

  const handleDeleteMachine = (machine) => {
    setMachinesData(machinesData.filter(m => m.id !== machine.id))
  }

  // 班组工序分类管理
  const handleAddProcess = (processId) => {
    if (!processId) return
    
    const process = options.process_categories.find(p => p.id === processId)
    if (process) {
      // 检查是否已存在
      const exists = processesData.some(p => p.process_category_id === processId)
      if (exists) {
        message.error('该工序分类已在班组中')
        return
      }
      
      const newProcess = {
        id: Date.now(),
        process_category_id: processId,
        process_category_name: process.process_name,
        sort_order: 0
      }
      setProcessesData([...processesData, newProcess])
    }
  }

  const handleDeleteProcess = (process) => {
    setProcessesData(processesData.filter(p => p.id !== process.id))
  }

  // 机台对话框管理
  const handleAddMachineDialog = () => {
    machineForm.resetFields()
    // 设置默认排序号：取当前最大值+1
    const maxSortOrder = machinesData.length > 0 
      ? Math.max(...machinesData.map(m => m.sort_order || 0))
      : 0
    machineForm.setFieldsValue({ sort_order: maxSortOrder + 1 })
    setMachineFormVisible(true)
  }

  const handleSaveMachine = async () => {
    try {
      const values = await machineForm.validateFields()
      const machine = options.machines.find(m => m.id === values.machine_id)
      if (machine) {
        // 检查是否已存在
        const exists = machinesData.some(m => m.machine_id === values.machine_id)
        if (exists) {
          message.error('该机台已在班组中')
          return
        }
        
        const newMachine = {
          id: Date.now(),
          machine_id: values.machine_id,
          machine_name: machine.machine_name,
          machine_code: machine.machine_code,
          remarks: values.remarks || '',
          sort_order: values.sort_order || 0
        }
        setMachinesData([...machinesData, newMachine])
        setMachineFormVisible(false)
      }
    } catch (error) {
      message.error('请检查表单填写')
    }
  }

  // 工序分类对话框管理
  const handleAddProcessDialog = () => {
    processForm.resetFields()
    setProcessFormVisible(true)
  }

  const handleSaveProcess = async () => {
    try {
      const values = await processForm.validateFields()
      const process = options.process_categories.find(p => p.id === values.process_category_id)
      if (process) {
        // 检查是否已存在
        const exists = processesData.some(p => p.process_category_id === values.process_category_id)
        if (exists) {
          message.error('该工序分类已在班组中')
          return
        }
        
        // 自动生成排序号：取当前最大值+1
        const maxSortOrder = processesData.length > 0 
          ? Math.max(...processesData.map(p => p.sort_order || 0))
          : 0
        
        const newProcess = {
          id: Date.now(),
          process_category_id: values.process_category_id,
          process_category_name: process.process_name,
          sort_order: maxSortOrder + 1
        }
        setProcessesData([...processesData, newProcess])
        setProcessFormVisible(false)
      }
    } catch (error) {
      message.error('请检查表单填写')
    }
  }

  useEffect(() => {
    loadOptions()
    loadTeamGroups()
  }, [])

  // 表格列定义
  const columns = [
    {
      title: '班组编号',
      dataIndex: 'team_code',
      key: 'team_code',
      width: 120,
    },
    {
      title: '班组名称',
      dataIndex: 'team_name',
      key: 'team_name',
      width: 150,
    },
    {
      title: '流转卡标识',
      dataIndex: 'circulation_card_id',
      key: 'circulation_card_id',
      width: 120,
    },
    {
      title: '白班(H)',
      dataIndex: 'day_shift_hours',
      key: 'day_shift_hours',
      width: 80,
      render: (text) => text ? `${text}` : '-'
    },
    {
      title: '晚班(H)',
      dataIndex: 'night_shift_hours',
      key: 'night_shift_hours',
      width: 80,
      render: (text) => text ? `${text}` : '-'
    },
    {
      title: '倒班(H)',
      dataIndex: 'rotating_shift_hours',
      key: 'rotating_shift_hours',
      width: 80,
      render: (text) => text ? `${text}` : '-'
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      render: (enabled) => (
        <Tag color={enabled ? 'green' : 'red'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      key: 'created_by_name',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => text ? new Date(text).toLocaleString('zh-CN') : '-'
    },
    {
      title: '修改人',
      dataIndex: 'updated_by_name',
      key: 'updated_by_name',
      width: 100,
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      render: (text) => text ? new Date(text).toLocaleString('zh-CN') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个班组吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              icon={<DeleteOutlined />}
              size="small"
              danger
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // 班组成员表格列
  const memberColumns = [
    {
      title: '员工工号',
      dataIndex: 'employee_code',
      key: 'employee_code',
      width: 120,
    },
    {
      title: '员工姓名',
      dataIndex: 'employee_name',
      key: 'employee_name',
      width: 120,
    },
    {
      title: '职位',
      dataIndex: 'position_name',
      key: 'position_name',
      width: 120,
    },
    {
      title: '计件%',
      dataIndex: 'piece_rate_percentage',
      key: 'piece_rate_percentage',
      width: 100,
      render: (text) => text ? `${text}%` : '0%'
    },
    {
      title: '节约奖%',
      dataIndex: 'saving_bonus_percentage',
      key: 'saving_bonus_percentage',
      width: 100,
      render: (text) => text ? `${text}%` : '0%'
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      ellipsis: true,
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
    },
    ...(modalType !== 'detail' ? [{
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEditMember(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个成员吗？"
            onConfirm={() => handleDeleteMember(record)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              icon={<DeleteOutlined />}
              size="small"
              danger
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    }] : [])
  ]

  // 班组机台表格列
  const machineColumns = [
    {
      title: '机台号',
      dataIndex: 'machine_code',
      key: 'machine_code',
      width: 120,
    },
    {
      title: '机台名称',
      dataIndex: 'machine_name',
      key: 'machine_name',
      width: 150,
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      ellipsis: true,
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
    },
    ...(modalType !== 'detail' ? [{
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record) => (
        <Popconfirm
          title="确定要删除这个机台吗？"
          onConfirm={() => handleDeleteMachine(record)}
          okText="确定"
          cancelText="取消"
        >
          <Button
            icon={<DeleteOutlined />}
            size="small"
            danger
          >
            删除
          </Button>
        </Popconfirm>
      ),
    }] : [])
  ]

  // 班组工序分类表格列
  const processColumns = [
    {
      title: '工序分类',
      dataIndex: 'process_category_name',
      key: 'process_category_name',
      width: 200,
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
    },
    ...(modalType !== 'detail' ? [{
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record) => (
        <Popconfirm
          title="确定要删除这个工序分类吗？"
          onConfirm={() => handleDeleteProcess(record)}
          okText="确定"
          cancelText="取消"
        >
          <Button
            icon={<DeleteOutlined />}
            size="small"
            danger
          >
            删除
          </Button>
        </Popconfirm>
      ),
    }] : [])
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
                <ToolOutlined style={{ marginRight: 8 }} />
                班组管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Input
                  placeholder="搜索班组编号、名称或流转卡标识"
                  value={searchParams.search}
                  onChange={(e) => setSearchParams(prev => ({ ...prev, search: e.target.value }))}
                  onPressEnter={handleSearch}
                  style={{ width: 250 }}
                  prefix={<SearchOutlined />}
                />
                <Select
                  placeholder="启用状态"
                  value={searchParams.is_enabled}
                  onChange={(value) => setSearchParams(prev => ({ ...prev, is_enabled: value }))}
                  style={{ width: 120 }}
                  allowClear
                >
                  <Option value={true}>启用</Option>
                  <Option value={false}>禁用</Option>
                </Select>
                <Button onClick={handleSearch} type="primary">
                  搜索
                </Button>
                <Button onClick={handleReset}>
                  重置
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleCreate}
                >
                  新建班组
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={() => loadTeamGroups()}
                >
                  刷新
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        <Table
          columns={columns}
          dataSource={teamGroups}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 新建/编辑/详情模态框 */}
      <Modal
        title={
          modalType === 'create' ? '新建班组' :
          modalType === 'edit' ? '编辑班组' : '班组详情'
        }
        visible={modalVisible}
        onOk={modalType === 'detail' ? () => setModalVisible(false) : handleSave}
        onCancel={() => setModalVisible(false)}
        width={1000}
        okText={modalType === 'detail' ? '关闭' : '保存'}
        cancelText="取消"
        destroyOnClose
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane 
            tab={
              <span>
                <SettingOutlined />
                基本信息
              </span>
            } 
            key="basic"
          >
            <Form
              form={form}
              layout="vertical"
              disabled={modalType === 'detail'}
            >
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="team_name"
                    label="班组名称"
                    rules={[{ required: true, message: '请输入班组名称' }]}
                  >
                    <Input placeholder="请输入班组名称" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="circulation_card_id"
                    label="流转卡标识"
                  >
                    <Input placeholder="请输入流转卡标识" />
                  </Form.Item>
                </Col>
              </Row>
              
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name="day_shift_hours"
                    label="白班工作标准时间"
                    tooltip="本班组对应的白班工作标准时间，单位H"
                  >
                    <InputNumber
                      placeholder="请输入白班时间"
                      style={{ width: '100%' }}
                      min={0}
                      max={24}
                      precision={2}
                      addonAfter="H"
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="night_shift_hours"
                    label="晚班工作标准时间"
                    tooltip="本班组对应的夜班工作标准时间，单位H"
                  >
                    <InputNumber
                      placeholder="请输入晚班时间"
                      style={{ width: '100%' }}
                      min={0}
                      max={24}
                      precision={2}
                      addonAfter="H"
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="rotating_shift_hours"
                    label="倒班工作标准时间"
                    tooltip="本班组对应的倒班第一天工作标准时间，单位H"
                  >
                    <InputNumber
                      placeholder="请输入倒班时间"
                      style={{ width: '100%' }}
                      min={0}
                      max={24}
                      precision={2}
                      addonAfter="H"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="sort_order"
                    label="排序"
                  >
                    <InputNumber
                      placeholder="请输入排序号"
                      style={{ width: '100%' }}
                      min={0}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="is_enabled"
                    label="启用状态"
                    valuePropName="checked"
                    initialValue={true}
                  >
                    <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="description"
                label="描述"
              >
                <TextArea placeholder="请输入描述" rows={3} />
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <UserOutlined />
                班组人员
              </span>
            } 
            key="members"
          >
            <div style={{ marginBottom: 16 }}>
              {modalType !== 'detail' && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleAddMember}
                >
                  添加成员
                </Button>
              )}
            </div>
            <Table
              columns={memberColumns}
              dataSource={membersData}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </TabPane>

          <TabPane 
            tab={
              <span>
                <AppstoreOutlined />
                班组机台
              </span>
            } 
            key="machines"
          >
            <div style={{ marginBottom: 16 }}>
              {modalType !== 'detail' && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleAddMachineDialog}
                >
                  添加机台
                </Button>
              )}
            </div>
            <Table
              columns={machineColumns}
              dataSource={machinesData}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </TabPane>

          <TabPane 
            tab={
              <span>
                <SettingOutlined />
                工序分类
              </span>
            } 
            key="processes"
          >
            <div style={{ marginBottom: 16 }}>
              {modalType !== 'detail' && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleAddProcessDialog}
                >
                  添加工序分类
                </Button>
              )}
            </div>
            <Table
              columns={processColumns}
              dataSource={processesData}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </TabPane>
        </Tabs>
      </Modal>

      {/* 班组成员编辑模态框 */}
      <Modal
        title={editingMember ? '编辑成员' : '添加成员'}
        visible={memberFormVisible}
        onOk={handleSaveMember}
        onCancel={() => setMemberFormVisible(false)}
        okText="保存"
        cancelText="取消"
        destroyOnClose
      >
        <Form
          form={memberForm}
          layout="vertical"
        >
          <Form.Item
            name="employee_id"
            label="员工"
            rules={[{ required: true, message: '请选择员工' }]}
          >
            <Select
              placeholder="请选择员工"
              disabled={!!editingMember}
              showSearch
              optionFilterProp="children"
              filterOption={(input, option) =>
                option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
            >
              {options.employees?.map(employee => (
                <Option key={employee.id} value={employee.id}>
                  {employee.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="piece_rate_percentage"
                label="计件%"
              >
                <InputNumber
                  placeholder="请输入计件百分比"
                  style={{ width: '100%' }}
                  min={0}
                  max={100}
                  precision={2}
                  addonAfter="%"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="saving_bonus_percentage"
                label="节约奖%"
              >
                <InputNumber
                  placeholder="请输入节约奖百分比"
                  style={{ width: '100%' }}
                  min={0}
                  max={100}
                  precision={2}
                  addonAfter="%"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="sort_order"
            label="排序"
          >
            <InputNumber
              placeholder="请输入排序号"
              style={{ width: '100%' }}
              min={0}
            />
          </Form.Item>

          <Form.Item
            name="remarks"
            label="备注"
          >
            <TextArea placeholder="请输入备注" rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 机台选择模态框 */}
      <Modal
        title="添加机台"
        visible={machineFormVisible}
        onOk={handleSaveMachine}
        onCancel={() => setMachineFormVisible(false)}
        okText="添加"
        cancelText="取消"
        destroyOnClose
      >
        <Form
          form={machineForm}
          layout="vertical"
        >
          <Form.Item
            name="machine_id"
            label="机台"
            rules={[{ required: true, message: '请选择机台' }]}
          >
            <Select
              placeholder="请选择机台"
              showSearch
              optionFilterProp="children"
              filterOption={(input, option) =>
                option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
            >
              {options.machines?.filter(machine => 
                !machinesData.some(m => m.machine_id === machine.id)
              ).map(machine => (
                <Option key={machine.id} value={machine.id}>
                  {machine.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="remarks"
            label="备注"
          >
            <TextArea placeholder="请输入备注" rows={3} />
          </Form.Item>
          
          <Form.Item
            name="sort_order"
            label="排序"
            rules={[{ required: true, message: '请输入排序' }]}
          >
            <InputNumber
              placeholder="请输入排序号"
              style={{ width: '100%' }}
              min={0}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 工序分类选择模态框 */}
      <Modal
        title="添加工序分类"
        visible={processFormVisible}
        onOk={handleSaveProcess}
        onCancel={() => setProcessFormVisible(false)}
        okText="添加"
        cancelText="取消"
        destroyOnClose
      >
        <Form
          form={processForm}
          layout="vertical"
        >
          <Form.Item
            name="process_category_id"
            label="工序分类"
            rules={[{ required: true, message: '请选择工序分类' }]}
          >
            <Select
              placeholder="请选择工序分类"
              showSearch
              optionFilterProp="children"
              filterOption={(input, option) =>
                option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
            >
              {options.process_categories?.filter(process => 
                !processesData.some(p => p.process_category_id === process.id)
              ).map(process => (
                <Option key={process.id} value={process.id}>
                  {process.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default TeamGroupManagement 