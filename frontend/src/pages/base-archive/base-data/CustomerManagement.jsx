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
  DatePicker
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  ExportOutlined,
  UserOutlined,
  ContactsOutlined,
  EnvironmentOutlined,
  FileTextOutlined,
  BankOutlined,
  TeamOutlined
} from '@ant-design/icons'
import {
  getCustomerManagementList,
  getCustomerManagementDetail,
  createCustomerManagement,
  updateCustomerManagement,
  deleteCustomerManagement,
  toggleCustomerStatus,
  exportCustomerManagement,
  getCustomerManagementFormOptions
} from '../../../api/base-archive/base-data/customerManagement'
import dayjs from 'dayjs'

const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs

const CustomerManagement = () => {
  const [loading, setLoading] = useState(false)
  const [customers, setCustomers] = useState([])
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })

  // 日期格式化函数
  const formatDate = (dateStr) => {
    if (!dateStr) return '****.**.**';
    const date = new Date(dateStr);
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
  }

  // 日期范围格式化函数
  const formatDateRange = (startDate, endDate) => {
    const start = formatDate(startDate);
    const end = formatDate(endDate);
    return `${start}-${end}`;
  }

  // 解析日期范围字符串 YYYY.MM.DD-YYYY.MM.DD
  const parseDateRange = (dateRangeStr) => {
    if (!dateRangeStr || dateRangeStr === '****.**.**-****.**.**') {
      return [null, null];
    }
    const parts = dateRangeStr.split('-');
    if (parts.length !== 2) {
      return [null, null];
    }
    
    const parseDate = (dateStr) => {
      if (dateStr === '****.**.**') return null;
      const dateParts = dateStr.split('.');
      if (dateParts.length !== 3) return null;
      return new Date(`${dateParts[0]}-${dateParts[1]}-${dateParts[2]}`);
    };
    
    return [parseDate(parts[0]), parseDate(parts[1])];
  }

  // 格式化日期范围为字符串
  const formatDateRangeForSubmit = (dates) => {
    if (!dates || dates.length !== 2) return {};
    const [start, end] = dates;
    return {
      start: start ? start.toISOString().split('T')[0] : null,
      end: end ? end.toISOString().split('T')[0] : null
    };
  }
  const [searchParams, setSearchParams] = useState({
    search: '',
    customer_category_id: undefined,
    is_enabled: undefined
  })

  // 选项数据
  const [options, setOptions] = useState({
    customer_categories: [],
    customers: [],
    package_methods: [],
    business_types: [],
    enterprise_types: [],
    tax_rates: [],
    payment_methods: [],
    currencies: [],
    employees: []
  })

  // 模态框状态
  const [modalVisible, setModalVisible] = useState(false)
  const [modalType, setModalType] = useState('create')
  const [currentRecord, setCurrentRecord] = useState(null)
  const [form] = Form.useForm()

  // 子表相关状态
  const [activeTab, setActiveTab] = useState('basic')
  const [subTableData, setSubTableData] = useState({
    contacts: [],
    delivery_addresses: [],
    invoice_units: [],
    payment_units: [],
    affiliated_companies: []
  })

  // 加载选项数据
  const loadOptions = async () => {
    try {
      const response = await getCustomerManagementFormOptions()
      if (response?.data?.success) {
        setOptions(response.data.data)
      }
    } catch (error) {
      console.error('加载选项数据失败:', error)
      message.error('加载选项数据失败')
    }
  }

  // 加载客户列表
  const loadCustomers = async (params = {}) => {
    try {
      setLoading(true)
      const response = await getCustomerManagementList({
        page: pagination.current,
        per_page: pagination.pageSize,
        ...searchParams,
        ...params
      })

      if (response?.data?.success) {
        const data = response.data.data
        
        // 为数据添加唯一key
        const customersWithKeys = (data.customers || []).map((item, index) => ({
          ...item,
          key: item.id || `customer-${index}-${Date.now()}`, // 使用id作为key，如果没有id则生成唯一key
        }));
        
        setCustomers(customersWithKeys)
        setPagination(prev => ({
          ...prev,
          current: data.current_page || 1,
          total: data.total || 0
        }))
      } else {
        message.error(response?.data?.error || '加载客户列表失败')
      }
    } catch (error) {
      console.error('加载客户列表失败:', error)
      message.error('加载客户列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadOptions()
    loadCustomers()
  }, [])

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }))
    loadCustomers({ page: 1 })
  }

  // 重置搜索
  const handleReset = () => {
    setSearchParams({
      search: '',
      customer_category_id: undefined,
      is_enabled: undefined
    })
    setPagination(prev => ({ ...prev, current: 1 }))
    loadCustomers({ page: 1, search: '', customer_category_id: undefined, is_enabled: undefined })
  }

  // 表格分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination)
    loadCustomers({
      page: newPagination.current,
      per_page: newPagination.pageSize
    })
  }

  // 新建客户
  const handleCreate = () => {
    setModalType('create')
    setCurrentRecord(null)
    setActiveTab('basic')
    resetSubTableData()
    form.resetFields()
    setModalVisible(true)
  }

  // 重置子表数据
  const resetSubTableData = () => {
    setSubTableData({
      contacts: [{}],
      delivery_addresses: [{}],
      invoice_units: [{}],
      payment_units: [{}],
      affiliated_companies: [{}]
    })
  }

  // 编辑客户
  const handleEdit = async (record) => {
    try {
      setLoading(true)
      const response = await getCustomerManagementDetail(record.id)
      if (response?.data?.success) {
        const customerData = response.data.data
        setModalType('edit')
        setCurrentRecord(customerData)
        setActiveTab('basic')
        
        // 处理日期范围数据
        const formData = { ...customerData }
        
        // 处理商标证期间
        if (customerData.trademark_start_date || customerData.trademark_end_date) {
          formData.trademark_period = [
            customerData.trademark_start_date ? dayjs(customerData.trademark_start_date) : null,
            customerData.trademark_end_date ? dayjs(customerData.trademark_end_date) : null
          ]
        }
        
        // 处理条码证期间
        if (customerData.barcode_cert_start_date || customerData.barcode_cert_end_date) {
          formData.barcode_cert_period = [
            customerData.barcode_cert_start_date ? dayjs(customerData.barcode_cert_start_date) : null,
            customerData.barcode_cert_end_date ? dayjs(customerData.barcode_cert_end_date) : null
          ]
        }
        
        // 处理合同期间
        if (customerData.contract_start_date || customerData.contract_end_date) {
          formData.contract_period = [
            customerData.contract_start_date ? dayjs(customerData.contract_start_date) : null,
            customerData.contract_end_date ? dayjs(customerData.contract_end_date) : null
          ]
        }
        
        // 处理经营期间
        if (customerData.business_start_date || customerData.business_end_date) {
          formData.business_period = [
            customerData.business_start_date ? dayjs(customerData.business_start_date) : null,
            customerData.business_end_date ? dayjs(customerData.business_end_date) : null
          ]
        }
        
        // 处理生产许可期间
        if (customerData.production_permit_start_date || customerData.production_permit_end_date) {
          formData.production_permit_period = [
            customerData.production_permit_start_date ? dayjs(customerData.production_permit_start_date) : null,
            customerData.production_permit_end_date ? dayjs(customerData.production_permit_end_date) : null
          ]
        }
        
        // 处理检验报告期间
        if (customerData.inspection_report_start_date || customerData.inspection_report_end_date) {
          formData.inspection_report_period = [
            customerData.inspection_report_start_date ? dayjs(customerData.inspection_report_start_date) : null,
            customerData.inspection_report_end_date ? dayjs(customerData.inspection_report_end_date) : null
          ]
        }

        // 处理单个日期
        if (customerData.reconciliation_date) {
          formData.reconciliation_date = dayjs(customerData.reconciliation_date);
        }
        
        form.setFieldsValue(formData)
        
        // 设置子表数据
        setSubTableData({
          contacts: customerData.contacts?.length > 0 ? customerData.contacts : [{}],
          delivery_addresses: customerData.delivery_addresses?.length > 0 ? customerData.delivery_addresses : [{}],
          invoice_units: customerData.invoice_units?.length > 0 ? customerData.invoice_units : [{}],
          payment_units: customerData.payment_units?.length > 0 ? customerData.payment_units : [{}],
          affiliated_companies: customerData.affiliated_companies?.length > 0 ? customerData.affiliated_companies : [{}]
        })
        
        setModalVisible(true)
      } else {
        message.error(response?.data?.error || '获取客户详情失败')
      }
    } catch (error) {
      console.error('获取客户详情失败:', error)
      message.error('获取客户详情失败')
    } finally {
      setLoading(false)
    }
  }

  // 删除客户
  const handleDelete = async (id) => {
    try {
      setLoading(true)
      const response = await deleteCustomerManagement(id)
      if (response?.data?.success) {
        message.success('删除成功')
        loadCustomers()
      } else {
        message.error(response?.data?.error || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      message.error('删除失败')
    } finally {
      setLoading(false)
    }
  }

  // 切换启用状态
  const handleToggleStatus = async (record) => {
    try {
      setLoading(true)
      const response = await toggleCustomerStatus(record.id)
      if (response?.data?.success) {
        message.success(`客户已${record.is_enabled ? '禁用' : '启用'}`)
        loadCustomers()
      } else {
        message.error(response?.data?.error || '状态切换失败')
      }
    } catch (error) {
      console.error('状态切换失败:', error)
      message.error('状态切换失败')
    } finally {
      setLoading(false)
    }
  }

  // 保存客户
  const handleSave = async () => {
    try {
      await form.validateFields()
      const formData = form.getFieldsValue()

      // 处理日期范围数据
      const processedData = { ...formData }
      
      // 处理商标证期间
      if (formData.trademark_period) {
        const { start, end } = formatDateRangeForSubmit(formData.trademark_period)
        processedData.trademark_start_date = start
        processedData.trademark_end_date = end
        delete processedData.trademark_period
      }
      
      // 处理条码证期间
      if (formData.barcode_cert_period) {
        const { start, end } = formatDateRangeForSubmit(formData.barcode_cert_period)
        processedData.barcode_cert_start_date = start
        processedData.barcode_cert_end_date = end
        delete processedData.barcode_cert_period
      }
      
      // 处理合同期间
      if (formData.contract_period) {
        const { start, end } = formatDateRangeForSubmit(formData.contract_period)
        processedData.contract_start_date = start
        processedData.contract_end_date = end
        delete processedData.contract_period
      }
      
      // 处理经营期间
      if (formData.business_period) {
        const { start, end } = formatDateRangeForSubmit(formData.business_period)
        processedData.business_start_date = start
        processedData.business_end_date = end
        delete processedData.business_period
      }
      
      // 处理生产许可期间
      if (formData.production_permit_period) {
        const { start, end } = formatDateRangeForSubmit(formData.production_permit_period)
        processedData.production_permit_start_date = start
        processedData.production_permit_end_date = end
        delete processedData.production_permit_period
      }
      
      // 处理检验报告期间
      if (formData.inspection_report_period) {
        const { start, end } = formatDateRangeForSubmit(formData.inspection_report_period)
        processedData.inspection_report_start_date = start
        processedData.inspection_report_end_date = end
        delete processedData.inspection_report_period
      }

      // 包含子表数据
      const submitData = {
        ...processedData,
        ...subTableData
      }

      setLoading(true)
      let response
      if (modalType === 'create') {
        response = await createCustomerManagement(submitData)
      } else {
        response = await updateCustomerManagement(currentRecord.id, submitData)
      }

      if (response?.data?.success) {
        message.success(modalType === 'create' ? '创建成功' : '更新成功')
        closeModal()
        loadCustomers()
      } else {
        message.error(response?.data?.error || `${modalType === 'create' ? '创建' : '更新'}失败`)
      }
    } catch (error) {
      console.error('保存失败:', error)
      if (error.errorFields) {
        message.error('请检查表单填写是否正确')
      } else {
        message.error('保存失败')
      }
    } finally {
      setLoading(false)
    }
  }

  // 导出数据
  const handleExport = async () => {
    try {
      setLoading(true)
      const response = await exportCustomerManagement(searchParams)
      if (response?.data?.success) {
        message.success(`导出成功，共${response.data.data.length}条数据`)
        console.log('导出数据:', response.data.data)
      } else {
        message.error(response?.data?.error || '导出失败')
      }
    } catch (error) {
      console.error('导出失败:', error)
      message.error('导出失败')
    } finally {
      setLoading(false)
    }
  }

  // 添加子表行
  const addSubTableRow = (tableType) => {
    setSubTableData(prev => ({
      ...prev,
      [tableType]: [...prev[tableType], {}]
    }))
  }

  // 删除子表行
  const removeSubTableRow = (tableType, index) => {
    setSubTableData(prev => {
      const filtered = prev[tableType].filter((_, i) => i !== index)
      // 如果删除完了，至少保留一个空行
      const newData = filtered.length === 0 ? [{}] : filtered
      return {
        ...prev,
        [tableType]: newData
      }
    })
  }

  // 更新子表数据
  const updateSubTableData = (tableType, index, field, value) => {
    setSubTableData(prev => ({
      ...prev,
      [tableType]: prev[tableType].map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }))
  }

  // 表格列定义
  const columns = [
    {
      title: '序号',
      dataIndex: 'index',
      key: 'index',
      width: 60,
      render: (_, __, index) => (pagination.current - 1) * pagination.pageSize + index + 1,
    },
    {
      title: '客户编号',
      dataIndex: 'customer_code',
      key: 'customer_code',
      width: 120,
    },
    {
      title: '客户名称',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 200,
    },
    {
      title: '客户分类',
      dataIndex: 'customer_category_name',
      key: 'customer_category_name',
      width: 120,
    },
    {
      title: '客户简称',
      dataIndex: 'customer_abbreviation',
      key: 'customer_abbreviation',
      width: 150,
    },
    {
      title: '客户等级',
      dataIndex: 'customer_level',
      key: 'customer_level',
      width: 80,
    },
    {
      title: '企业类型',
      dataIndex: 'enterprise_type',
      key: 'enterprise_type',
      width: 100,
      render: (text, record) => record.enterprise_type_name,
    },
    {
      title: '区域',
      dataIndex: 'region',
      key: 'region',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD HH:mm') : '',
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            size="small"
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这条记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // 渲染联系人表格
  const renderContactTable = () => {
    const contactColumns = [
      {
        title: '联系人',
        dataIndex: 'contact_name',
        width: 120,
        render: (text, record, index) => (
          <Input
            value={text}
            onChange={(e) => updateSubTableData('contacts', index, 'contact_name', e.target.value)}
            disabled={modalType === 'detail'}
            placeholder="请输入联系人"
            size="small"
          />
        )
      },
      {
        title: '职位',
        dataIndex: 'position',
        width: 100,
        render: (text, record, index) => (
          <Input
            value={text}
            onChange={(e) => updateSubTableData('contacts', index, 'position', e.target.value)}
            disabled={modalType === 'detail'}
            placeholder="请输入职位"
            size="small"
          />
        )
      },
      {
        title: '手机',
        dataIndex: 'mobile',
        width: 130,
        render: (text, record, index) => (
          <Input
            value={text}
            onChange={(e) => updateSubTableData('contacts', index, 'mobile', e.target.value)}
            disabled={modalType === 'detail'}
            placeholder="请输入手机号"
            size="small"
          />
        )
      },
      {
        title: '传真',
        dataIndex: 'fax',
        width: 120,
        render: (text, record, index) => (
          <Input
            value={text}
            onChange={(e) => updateSubTableData('contacts', index, 'fax', e.target.value)}
            disabled={modalType === 'detail'}
            placeholder="请输入传真"
            size="small"
          />
        )
      },
      {
        title: 'QQ',
        dataIndex: 'qq',
        width: 120,
        render: (text, record, index) => (
          <Input
            value={text}
            onChange={(e) => updateSubTableData('contacts', index, 'qq', e.target.value)}
            disabled={modalType === 'detail'}
            placeholder="请输入QQ"
            size="small"
          />
        )
      },
      {
        title: '微信',
        dataIndex: 'wechat',
        width: 120,
        render: (text, record, index) => (
          <Input
            value={text}
            onChange={(e) => updateSubTableData('contacts', index, 'wechat', e.target.value)}
            disabled={modalType === 'detail'}
            placeholder="请输入微信"
            size="small"
          />
        )
      },
      {
        title: '邮箱',
        dataIndex: 'email',
        width: 180,
        render: (text, record, index) => (
          <Input
            value={text}
            onChange={(e) => updateSubTableData('contacts', index, 'email', e.target.value)}
            disabled={modalType === 'detail'}
            placeholder="请输入邮箱"
            size="small"
          />
        )
      },
      {
        title: '部门',
        dataIndex: 'department',
        width: 120,
        render: (text, record, index) => (
          <Input
            value={text}
            onChange={(e) => updateSubTableData('contacts', index, 'department', e.target.value)}
            disabled={modalType === 'detail'}
            placeholder="请输入部门"
            size="small"
          />
        )
      },
      {
        title: '操作',
        width: 80,
        render: (text, record, index) => (
          modalType !== 'detail' ? (
            <Button
              type="link"
              danger
              size="small"
              icon={<DeleteOutlined />}
              onClick={() => removeSubTableRow('contacts', index)}
            >
              删除
            </Button>
          ) : null
        )
      }
    ]

    return (
      <Table
        columns={contactColumns}
        dataSource={subTableData.contacts || []}
        rowKey={(record, index) => index}
        pagination={false}
        size="small"
        scroll={{ x: 1000 }}
        bordered
      />
    )
  }

  // 渲染其他子表组件（表格形式）
  const renderSubTable = (tableType, columns, title) => {
    const data = subTableData[tableType] || []
    
    // 构建表格列配置
    const tableColumns = columns.map(col => ({
      title: col.title,
      dataIndex: col.key,
      width: col.width || 150,
      render: (text, record, index) => {
        if (col.type === 'textarea') {
          return (
            <TextArea
              value={text}
              onChange={(e) => updateSubTableData(tableType, index, col.key, e.target.value)}
              disabled={modalType === 'detail'}
              rows={2}
              placeholder={`请输入${col.title}`}
              size="small"
            />
          )
        } else {
          return (
            <Input
              value={text}
              onChange={(e) => updateSubTableData(tableType, index, col.key, e.target.value)}
              disabled={modalType === 'detail'}
              placeholder={`请输入${col.title}`}
              size="small"
            />
          )
        }
      }
    }))

    // 添加操作列
    if (modalType !== 'detail') {
      tableColumns.push({
        title: '操作',
        width: 80,
        render: (text, record, index) => (
          <Button
            type="link"
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => removeSubTableRow(tableType, index)}
          >
            删除
          </Button>
        )
      })
    }

    return (
      <div>
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Button
              type="dashed"
              onClick={() => addSubTableRow(tableType)}
              icon={<PlusOutlined />}
              disabled={modalType === 'detail'}
            >
              添加{title.replace('信息', '')}
            </Button>
            {modalType !== 'detail' && (
              <Button
                onClick={() => setSubTableData(prev => ({ ...prev, [tableType]: [{}] }))}
                icon={<ReloadOutlined />}
              >
                重置{title.replace('信息', '')}
              </Button>
            )}
          </Space>
        </div>
        <Table
          columns={tableColumns}
          dataSource={data}
          rowKey={(record, index) => index}
          pagination={false}
          size="small"
          scroll={{ x: 800 }}
          bordered
        />
      </div>
    )
  }

  // 统一关闭模态框
  const closeModal = () => {
    setModalVisible(false)
    form.resetFields()
    resetSubTableData()
    setCurrentRecord(null)
  }

  return (
    <div style={{ padding: '20px' }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Input
                placeholder="搜索客户名称、电话、税号等"
                value={searchParams.search}
                onChange={(e) => setSearchParams(prev => ({ ...prev, search: e.target.value }))}
                onPressEnter={handleSearch}
                allowClear
              />
            </Col>
            <Col span={5}>
              <Select
                placeholder="选择客户分类"
                value={searchParams.customer_category_id}
                onChange={(value) => setSearchParams(prev => ({ ...prev, customer_category_id: value }))}
                allowClear
                style={{ width: '100%' }}
              >
                {options.customer_categories?.map(item => (
                  <Option key={item.value} value={item.value}>{item.label}</Option>
                )) || []}
              </Select>
            </Col>
            <Col span={4}>
              <Select
                placeholder="启用状态"
                value={searchParams.is_enabled}
                onChange={(value) => setSearchParams(prev => ({ ...prev, is_enabled: value }))}
                allowClear
                style={{ width: '100%' }}
              >
                <Option value={true}>启用</Option>
                <Option value={false}>禁用</Option>
              </Select>
            </Col>
            <Col span={9}>
              <Space>
                <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                  搜索
                </Button>
                <Button icon={<ReloadOutlined />} onClick={handleReset}>
                  重置
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新建客户
                </Button>
                <Button icon={<ExportOutlined />} onClick={handleExport}>
                  导出数据
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        <Table
          columns={columns}
          dataSource={customers}
          rowKey="key"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 客户表单模态框 */}
      <Modal
        title={modalType === 'create' ? '新建客户' : modalType === 'edit' ? '编辑客户' : '查看客户'}
        open={modalVisible}
        onCancel={closeModal}
        footer={modalType === 'detail' ? [
          <Button key="close" onClick={closeModal}>
            关闭
          </Button>
        ] : [
          <Button key="cancel" onClick={closeModal}>
            取消
          </Button>,
          <Button key="submit" type="primary" loading={loading} onClick={handleSave}>
            保存
          </Button>
        ]}
        width={1200}
        destroyOnClose
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab={<span><UserOutlined />基本信息</span>} key="basic">
            <Form form={form} layout="vertical">
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="客户编号"
                    name="customer_code"
                  >
                    <Input disabled placeholder={modalType === 'create' ? '自动生成' : ''} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="客户名称"
                    name="customer_name"
                    rules={[{ required: true, message: '请输入客户名称' }]}
                  >
                    <Input />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="客户分类" name="customer_category_id">
                    <Select
                      placeholder="选择客户分类"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.customer_categories?.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      )) || []}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="税收" name="tax_rate_id">
                    <Select
                      placeholder="选择税收"
                      disabled={modalType === 'detail'}
                      allowClear
                      onChange={(value) => {
                        if (value) {
                          const selectedTax = options.tax_rates?.find(item => item.value === value);
                          if (selectedTax && selectedTax.rate !== undefined) {
                            form.setFieldsValue({ tax_rate: selectedTax.rate });
                          }
                        } else {
                          form.setFieldsValue({ tax_rate: 0 });
                        }
                      }}
                    >
                      {options.tax_rates && options.tax_rates.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="税率%" name="tax_rate">
                    <InputNumber
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      min={0}
                      max={100}
                      step={0.01}
                      placeholder="自动填入"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="客户等级" name="customer_level">
                    <Select
                      placeholder="选择客户等级"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      <Option value="A">A</Option>
                      <Option value="B">B</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="上级客户" name="parent_customer_id">
                    <Select
                      placeholder="选择上级客户"
                      disabled={modalType === 'detail'}
                      allowClear
                      showSearch
                      filterOption={(input, option) =>
                        option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                      }
                    >
                      {options.customers && options.customers.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="区域" name="region">
                    <Select
                      placeholder="选择省份"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      <Option value="北京">北京</Option>
                      <Option value="天津">天津</Option>
                      <Option value="河北">河北</Option>
                      <Option value="山西">山西</Option>
                      <Option value="内蒙古">内蒙古</Option>
                      <Option value="辽宁">辽宁</Option>
                      <Option value="吉林">吉林</Option>
                      <Option value="黑龙江">黑龙江</Option>
                      <Option value="上海">上海</Option>
                      <Option value="江苏">江苏</Option>
                      <Option value="浙江">浙江</Option>
                      <Option value="安徽">安徽</Option>
                      <Option value="福建">福建</Option>
                      <Option value="江西">江西</Option>
                      <Option value="山东">山东</Option>
                      <Option value="河南">河南</Option>
                      <Option value="湖北">湖北</Option>
                      <Option value="湖南">湖南</Option>
                      <Option value="广东">广东</Option>
                      <Option value="广西">广西</Option>
                      <Option value="海南">海南</Option>
                      <Option value="重庆">重庆</Option>
                      <Option value="四川">四川</Option>
                      <Option value="贵州">贵州</Option>
                      <Option value="云南">云南</Option>
                      <Option value="西藏">西藏</Option>
                      <Option value="陕西">陕西</Option>
                      <Option value="甘肃">甘肃</Option>
                      <Option value="青海">青海</Option>
                      <Option value="宁夏">宁夏</Option>
                      <Option value="新疆">新疆</Option>
                      <Option value="台湾">台湾</Option>
                      <Option value="香港">香港</Option>
                      <Option value="澳门">澳门</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="包装方式" name="package_method_id">
                    <Select
                      placeholder="选择包装方式"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.package_methods && options.package_methods.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="条码前缀" name="barcode_prefix">
                    <Input disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="付款方式" name="payment_method_id">
                    <Select
                      placeholder="选择付款方式"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.payment_methods && options.payment_methods.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="经营业务类" name="business_type">
                    <Select
                      placeholder="选择经营业务类"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.business_types && options.business_types.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="企业类型" name="enterprise_type">
                    <Select
                      placeholder="选择企业类型"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.enterprise_types && options.enterprise_types.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="币别" name="currency_id">
                    <Select
                      placeholder="选择币别"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.currencies && options.currencies.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="信用额度" name="credit_amount">
                    <InputNumber
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      min={0}
                      step={0.01}
                      placeholder="请输入信用额度"
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="注册资金" name="registered_capital">
                    <InputNumber
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      min={0}
                      step={0.01}
                      placeholder="请输入注册资金"
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="销售提成%" name="sales_commission">
                    <InputNumber
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      min={0}
                      max={100}
                      step={0.01}
                      placeholder="请输入销售提成百分比"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="组织机构代码" name="organization_code">
                    <Input disabled={modalType === 'detail'} placeholder="请输入组织机构代码" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="公司法人" name="company_legal_person">
                    <Input disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="公司网址" name="company_website">
                    <Input disabled={modalType === 'detail'} placeholder="请输入公司网址" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="排序" name="sort_order">
                    <InputNumber
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      min={0}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="是否启用" name="is_enabled" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="旧客户" name="old_customer" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item label="公司地址" name="company_address">
                    <TextArea
                      rows={2}
                      disabled={modalType === 'detail'}
                      placeholder="请输入公司地址"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="商标证期间" name="trademark_period">
                    <DatePicker.RangePicker
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      format="YYYY.MM.DD"
                      placeholder={['开始日期', '结束日期']}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="条码证期间" name="barcode_cert_period">
                    <DatePicker.RangePicker
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      format="YYYY.MM.DD"
                      placeholder={['开始日期', '结束日期']}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="合同期间" name="contract_period">
                    <DatePicker.RangePicker
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      format="YYYY.MM.DD"
                      placeholder={['开始日期', '结束日期']}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="经营期间" name="business_period">
                    <DatePicker.RangePicker
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      format="YYYY.MM.DD"
                      placeholder={['开始日期', '结束日期']}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="生产许可期间" name="production_permit_period">
                    <DatePicker.RangePicker
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      format="YYYY.MM.DD"
                      placeholder={['开始日期', '结束日期']}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="检验报告期间" name="inspection_report_period">
                    <DatePicker.RangePicker
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      format="YYYY.MM.DD"
                      placeholder={['开始日期', '结束日期']}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="结算色差" name="settlement_color_difference">
                    <InputNumber
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      min={0}
                      step={0.0001}
                      placeholder="请输入结算色差"
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="账款期限" name="accounts_period">
                    <InputNumber
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      min={0}
                      placeholder="请输入账期天数"
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="账期" name="account_period">
                    <InputNumber
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      min={0}
                      placeholder="请输入账期"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="业务员" name="salesperson_id">
                    <Select
                      placeholder="选择业务员"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.employees && options.employees.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="条码前段编码" name="barcode_front_code">
                    <Input disabled={modalType === 'detail'} placeholder="请输入条码前段编码" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="条码后段编码" name="barcode_back_code">
                    <Input disabled={modalType === 'detail'} placeholder="请输入条码后段编码" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="用户条码" name="user_barcode">
                    <Input disabled={modalType === 'detail'} placeholder="请输入用户条码" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="发票流水号" name="invoice_water_number">
                    <Input disabled={modalType === 'detail'} placeholder="请输入发票流水号" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="水印位置" name="water_mark_position">
                    <InputNumber
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                      step={0.01}
                      placeholder="请输入水印位置"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="法人证书" name="legal_person_certificate">
                    <Input disabled={modalType === 'detail'} placeholder="请输入法人证书" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="省份" name="province">
                    <Input disabled={modalType === 'detail'} placeholder="请输入省份" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="城市" name="city">
                    <Input disabled={modalType === 'detail'} placeholder="请输入城市" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="区县" name="district">
                    <Input disabled={modalType === 'detail'} placeholder="请输入区县" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="对账日期" name="reconciliation_date">
                    <DatePicker
                      style={{ width: '100%' }}
                      disabled={modalType === 'detail'}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="外币" name="foreign_currency">
                    <Input disabled={modalType === 'detail'} placeholder="请输入外币" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="商标证书" name="trademark_certificate" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="印刷授权" name="print_authorization" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="检验报告" name="inspection_report" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="免费样品" name="free_samples" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="预付款控制" name="advance_payment_control" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="仓库" name="warehouse" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="客户档案审核" name="customer_archive_review" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item label="备注" name="remarks">
                    <TextArea
                      rows={3}
                      disabled={modalType === 'detail'}
                      placeholder="请输入备注信息"
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </TabPane>

          <TabPane tab={<span><ContactsOutlined />联系人</span>} key="contacts">
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Button
                  type="dashed"
                  onClick={() => addSubTableRow('contacts')}
                  icon={<PlusOutlined />}
                  disabled={modalType === 'detail'}
                >
                  添加联系人
                </Button>
                {modalType !== 'detail' && (
                  <Button
                    onClick={() => setSubTableData(prev => ({ ...prev, contacts: [{}] }))}
                    icon={<ReloadOutlined />}
                  >
                    重置联系人
                  </Button>
                )}
              </Space>
            </div>
            {renderContactTable()}
          </TabPane>

          <TabPane tab={<span><EnvironmentOutlined />送货地址</span>} key="delivery_addresses">
            {renderSubTable('delivery_addresses', [
              { key: 'delivery_address', title: '送货地址', width: 300, type: 'textarea' },
              { key: 'contact_name', title: '联系人', width: 120 },
              { key: 'contact_method', title: '联系方式', width: 150 }
            ], '送货地址')}
          </TabPane>

          <TabPane tab={<span><FileTextOutlined />开票单位</span>} key="invoice_units">
            {renderSubTable('invoice_units', [
              { key: 'invoice_unit', title: '开票单位', width: 180 },
              { key: 'taxpayer_id', title: '纳税人识别号', width: 180 },
              { key: 'invoice_address', title: '开票地址', width: 200 },
              { key: 'invoice_phone', title: '电话', width: 130 },
              { key: 'invoice_bank', title: '开票银行', width: 180 },
              { key: 'invoice_account', title: '开票账户', width: 180 }
            ], '开票单位')}
          </TabPane>

          <TabPane tab={<span><BankOutlined />付款单位</span>} key="payment_units">
            {renderSubTable('payment_units', [
              { key: 'payment_unit', title: '付款单位', width: 300 },
              { key: 'unit_code', title: '单位编号', width: 200 }
            ], '付款单位')}
          </TabPane>

          <TabPane tab={<span><TeamOutlined />归属公司</span>} key="affiliated_companies">
            {renderSubTable('affiliated_companies', [
              { key: 'affiliated_company', title: '归属公司', width: 400 }
            ], '归属公司')}
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  )
}

export default CustomerManagement 