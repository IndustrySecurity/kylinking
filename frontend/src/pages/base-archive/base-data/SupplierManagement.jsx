import React, { useState, useEffect } from 'react';
import {
  Table, Button, Modal, Form, Input, Select, DatePicker, InputNumber, Switch,
  Space, Popconfirm, message, Row, Col, Tabs, Card, Divider, Upload
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  SearchOutlined, UploadOutlined, ReloadOutlined, ExportOutlined,
  UserOutlined, ContactsOutlined, EnvironmentOutlined, FileTextOutlined, TeamOutlined
} from '@ant-design/icons';
import {
  getSupplierManagementList,
  getSupplierManagementDetail,
  createSupplierManagement,
  updateSupplierManagement,
  deleteSupplierManagement,
  toggleSupplierStatus,
  exportSupplierManagement,
  getSupplierManagementFormOptions
} from '../../../api/base-archive/base-data/supplierManagement';
import dayjs from 'dayjs';

const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

const SupplierManagement = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState('add'); // add, edit, detail
  const [currentSupplier, setCurrentSupplier] = useState(null);
  const [form] = Form.useForm();
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

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

  // 格式化日期范围为字符串
  const formatDateRangeForSubmit = (dates) => {
    if (!dates || dates.length !== 2) return {};
    const [start, end] = dates;
    return {
      start: start ? start.toISOString().split('T')[0] : null,
      end: end ? end.toISOString().split('T')[0] : null
    };
  }
  const [options, setOptions] = useState({
    supplier_categories: [],
    delivery_methods: [],
    tax_rates: [],
    currencies: [],
    payment_methods: [],
    supplier_levels: [],
    enterprise_types: [],
    provinces: [],
    employees: []
  });

  // 子表数据状态
  const [contacts, setContacts] = useState([]);
  const [deliveryAddresses, setDeliveryAddresses] = useState([]);
  const [invoiceUnits, setInvoiceUnits] = useState([]);
  const [affiliatedCompanies, setAffiliatedCompanies] = useState([]);

  useEffect(() => {
    loadSuppliers();
    loadOptions();
  }, []);

  const loadOptions = async () => {
    try {
      const response = await getSupplierManagementFormOptions();
      if (response?.data?.success) {
        setOptions(response.data.data);
      }
    } catch (error) {
      console.error('加载选项数据失败:', error);
      message.error('加载选项数据失败');
    }
  };

  const loadSuppliers = async (page = 1, pageSize = 20, search = '') => {
    setLoading(true);
    try {
      const response = await getSupplierManagementList({
        page,
        per_page: pageSize,
        search
      });
      
      if (response?.data?.success) {
        const data = response.data.data;
        
        // 为数据添加唯一key
        const suppliersWithKeys = (data.suppliers || []).map((item, index) => ({
          ...item,
          key: item.id || `supplier-${index}-${Date.now()}`, // 使用id作为key，如果没有id则生成唯一key
        }));
        
        setSuppliers(suppliersWithKeys);
        setPagination(prev => ({
          ...prev,
          current: data.page || page,
          pageSize,
          total: data.total || 0
        }));
      } else {
        message.error(response?.data?.error || '获取供应商列表失败');
      }
    } catch (error) {
      console.error('获取供应商列表失败:', error);
      message.error('获取供应商列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadSuppliers(1, pagination.pageSize, searchText);
  };

  const handleAdd = () => {
    setModalType('add');
    setCurrentSupplier(null);
    setContacts([]);
    setDeliveryAddresses([]);
    setInvoiceUnits([]);
    setAffiliatedCompanies([]);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = async (record) => {
    setModalType('edit');
    setCurrentSupplier(record);
    try {
      const response = await getSupplierManagementDetail(record.id);
      if (response?.data?.success) {
        const supplierData = response.data.data;
        
        // 处理日期范围数据
        const formData = { ...supplierData }
        
        // 处理营业期间
        if (supplierData.business_start_date || supplierData.business_end_date) {
          formData.business_period = [
            supplierData.business_start_date ? dayjs(supplierData.business_start_date) : null,
            supplierData.business_end_date ? dayjs(supplierData.business_end_date) : null
          ]
        }
        
        // 处理生产许可期间
        if (supplierData.production_permit_start_date || supplierData.production_permit_end_date) {
          formData.production_permit_period = [
            supplierData.production_permit_start_date ? dayjs(supplierData.production_permit_start_date) : null,
            supplierData.production_permit_end_date ? dayjs(supplierData.production_permit_end_date) : null
          ]
        }
        
        // 处理检测报告期间
        if (supplierData.inspection_report_start_date || supplierData.inspection_report_end_date) {
          formData.inspection_report_period = [
            supplierData.inspection_report_start_date ? dayjs(supplierData.inspection_report_start_date) : null,
            supplierData.inspection_report_end_date ? dayjs(supplierData.inspection_report_end_date) : null
          ]
        }
        
        form.setFieldsValue(formData);
        
        // 设置子表数据
        setContacts(supplierData.contacts || []);
        setDeliveryAddresses(supplierData.delivery_addresses || []);
        setInvoiceUnits(supplierData.invoice_units || []);
        setAffiliatedCompanies(supplierData.affiliated_companies || []);
      } else {
        message.error(response?.data?.error || '获取供应商详情失败');
      }
    } catch (error) {
      console.error('获取供应商详情失败:', error);
      message.error('获取供应商详情失败');
    }
    setModalVisible(true);
  };



  const handleDelete = async (id) => {
    try {
      const response = await deleteSupplierManagement(id);
      if (response?.data?.success) {
        message.success('删除成功');
        loadSuppliers(pagination.current, pagination.pageSize, searchText);
      } else {
        message.error(response?.data?.error || '删除失败');
      }
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      // 处理日期范围数据
      const processedData = { ...values }
      
      // 处理营业期间
      if (values.business_period) {
        const { start, end } = formatDateRangeForSubmit(values.business_period)
        processedData.business_start_date = start
        processedData.business_end_date = end
        delete processedData.business_period
      }
      
      // 处理生产许可期间
      if (values.production_permit_period) {
        const { start, end } = formatDateRangeForSubmit(values.production_permit_period)
        processedData.production_permit_start_date = start
        processedData.production_permit_end_date = end
        delete processedData.production_permit_period
      }
      
      // 处理检测报告期间
      if (values.inspection_report_period) {
        const { start, end } = formatDateRangeForSubmit(values.inspection_report_period)
        processedData.inspection_report_start_date = start
        processedData.inspection_report_end_date = end
        delete processedData.inspection_report_period
      }

      const submitData = {
        ...processedData,
        contacts,
        delivery_addresses: deliveryAddresses,
        invoice_units: invoiceUnits,
        affiliated_companies: affiliatedCompanies
      };

      let response;
      if (modalType === 'add') {
        response = await createSupplierManagement(submitData);
      } else {
        response = await updateSupplierManagement(currentSupplier.id, submitData);
      }

      if (response?.data?.success) {
        message.success(modalType === 'add' ? '创建成功' : '更新成功');
        setModalVisible(false);
        loadSuppliers(pagination.current, pagination.pageSize, searchText);
      } else {
        message.error(response?.data?.error || '提交失败');
      }
    } catch (error) {
      console.error('提交失败:', error);
      message.error('提交失败');
    }
  };

  const columns = [
    {
      title: '供应商编号',
      dataIndex: 'supplier_code',
      key: 'supplier_code',
      width: 120,
      render: (text) => text || '-'
    },
    {
      title: '供应商名称',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      width: 200,
    },
    {
      title: '供应商简称',
      dataIndex: 'supplier_abbreviation',
      key: 'supplier_abbreviation',
      width: 150,
      render: (text) => text || '-'
    },
    {
      title: '供应商分类',
      dataIndex: 'supplier_category_name',
      key: 'supplier_category_name',
      width: 120,
      render: (text) => text || '-'
    },
    {
      title: '等级',
      dataIndex: 'supplier_level',
      key: 'supplier_level',
      width: 80,
      render: (text) => text || '-'
    },
    {
      title: '区域',
      dataIndex: 'region',
      key: 'region',
      width: 100,
      render: (text) => text || '-'
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      render: (value) => value ? '是' : '否',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
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
            title="确定要删除这个供应商吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 联系人子表列
  const contactColumns = [
    {
      title: '联系人',
      dataIndex: 'contact_name',
      key: 'contact_name',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newContacts = [...contacts];
            newContacts[index].contact_name = e.target.value;
            setContacts(newContacts);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入联系人"
          size="small"
        />
      )
    },
    {
      title: '座机',
      dataIndex: 'landline',
      key: 'landline',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newContacts = [...contacts];
            newContacts[index].landline = e.target.value;
            setContacts(newContacts);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入座机"
          size="small"
        />
      )
    },
    {
      title: '手机',
      dataIndex: 'mobile',
      key: 'mobile',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newContacts = [...contacts];
            newContacts[index].mobile = e.target.value;
            setContacts(newContacts);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入手机"
          size="small"
        />
      )
    },
    {
      title: '传真',
      dataIndex: 'fax',
      key: 'fax',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newContacts = [...contacts];
            newContacts[index].fax = e.target.value;
            setContacts(newContacts);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入传真"
          size="small"
        />
      )
    },
    {
      title: 'QQ',
      dataIndex: 'qq',
      key: 'qq',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newContacts = [...contacts];
            newContacts[index].qq = e.target.value;
            setContacts(newContacts);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入QQ"
          size="small"
        />
      )
    },
    {
      title: '微信',
      dataIndex: 'wechat',
      key: 'wechat',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newContacts = [...contacts];
            newContacts[index].wechat = e.target.value;
            setContacts(newContacts);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入微信"
          size="small"
        />
      )
    },
    {
      title: 'e-mail',
      dataIndex: 'email',
      key: 'email',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newContacts = [...contacts];
            newContacts[index].email = e.target.value;
            setContacts(newContacts);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入邮箱"
          size="small"
        />
      )
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newContacts = [...contacts];
            newContacts[index].department = e.target.value;
            setContacts(newContacts);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入部门"
          size="small"
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record, index) => (
        modalType !== 'detail' && contacts.length > 1 ? (
          <Button
            danger
            size="small"
            onClick={() => {
              const newContacts = [...contacts];
              newContacts.splice(index, 1);
              setContacts(newContacts);
            }}
          >
            删除
          </Button>
        ) : null
      ),
    },
  ];

  // 发货地址子表列
  const deliveryAddressColumns = [
    {
      title: '发货地址',
      dataIndex: 'delivery_address',
      key: 'delivery_address',
      render: (text, record, index) => (
        <Input.TextArea
          value={text}
          onChange={(e) => {
            const newAddresses = [...deliveryAddresses];
            newAddresses[index].delivery_address = e.target.value;
            setDeliveryAddresses(newAddresses);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入发货地址"
          rows={2}
          size="small"
        />
      )
    },
    {
      title: '联系人',
      dataIndex: 'contact_name',
      key: 'contact_name',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newAddresses = [...deliveryAddresses];
            newAddresses[index].contact_name = e.target.value;
            setDeliveryAddresses(newAddresses);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入联系人"
          size="small"
        />
      )
    },
    {
      title: '联系方式',
      dataIndex: 'contact_method',
      key: 'contact_method',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newAddresses = [...deliveryAddresses];
            newAddresses[index].contact_method = e.target.value;
            setDeliveryAddresses(newAddresses);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入联系方式"
          size="small"
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record, index) => (
        modalType !== 'detail' && deliveryAddresses.length > 1 ? (
          <Button
            danger
            size="small"
            onClick={() => {
              const newAddresses = [...deliveryAddresses];
              newAddresses.splice(index, 1);
              setDeliveryAddresses(newAddresses);
            }}
          >
            删除
          </Button>
        ) : null
      ),
    },
  ];

  // 开票单位子表列
  const invoiceUnitColumns = [
    {
      title: '开票单位',
      dataIndex: 'invoice_unit',
      key: 'invoice_unit',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newUnits = [...invoiceUnits];
            newUnits[index].invoice_unit = e.target.value;
            setInvoiceUnits(newUnits);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入开票单位"
          size="small"
        />
      )
    },
    {
      title: '纳税人识别号',
      dataIndex: 'taxpayer_id',
      key: 'taxpayer_id',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newUnits = [...invoiceUnits];
            newUnits[index].taxpayer_id = e.target.value;
            setInvoiceUnits(newUnits);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入纳税人识别号"
          size="small"
        />
      )
    },
    {
      title: '开票地址',
      dataIndex: 'invoice_address',
      key: 'invoice_address',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newUnits = [...invoiceUnits];
            newUnits[index].invoice_address = e.target.value;
            setInvoiceUnits(newUnits);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入开票地址"
          size="small"
        />
      )
    },
    {
      title: '电话',
      dataIndex: 'invoice_phone',
      key: 'invoice_phone',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newUnits = [...invoiceUnits];
            newUnits[index].invoice_phone = e.target.value;
            setInvoiceUnits(newUnits);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入电话"
          size="small"
        />
      )
    },
    {
      title: '开票银行',
      dataIndex: 'invoice_bank',
      key: 'invoice_bank',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newUnits = [...invoiceUnits];
            newUnits[index].invoice_bank = e.target.value;
            setInvoiceUnits(newUnits);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入开票银行"
          size="small"
        />
      )
    },
    {
      title: '开票账户',
      dataIndex: 'invoice_account',
      key: 'invoice_account',
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => {
            const newUnits = [...invoiceUnits];
            newUnits[index].invoice_account = e.target.value;
            setInvoiceUnits(newUnits);
          }}
          disabled={modalType === 'detail'}
          placeholder="请输入开票账户"
          size="small"
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record, index) => (
        modalType !== 'detail' && invoiceUnits.length > 1 ? (
          <Button
            danger
            size="small"
            onClick={() => {
              const newUnits = [...invoiceUnits];
              newUnits.splice(index, 1);
              setInvoiceUnits(newUnits);
            }}
          >
            删除
          </Button>
        ) : null
      ),
    },
  ];

  // 归属公司子表列
  const affiliatedCompanyColumns = [
    { title: '归属公司', dataIndex: 'affiliated_company', key: 'affiliated_company' },
    {
      title: '操作',
      key: 'action',
      render: (_, record, index) => (
        modalType !== 'detail' && (
          <Button
            danger
            size="small"
            onClick={() => {
              const newCompanies = [...affiliatedCompanies];
              newCompanies.splice(index, 1);
              setAffiliatedCompanies(newCompanies);
            }}
          >
            删除
          </Button>
        )
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Input
              placeholder="搜索供应商名称、编号、简称等"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 300 }}
              prefix={<SearchOutlined />}
              onPressEnter={handleSearch}
            />
            <Button type="primary" onClick={handleSearch}>
              搜索
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新建供应商
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={suppliers}
          rowKey="key"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              loadSuppliers(page, pageSize, searchText);
            },
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      <Modal
        title={
          modalType === 'add' ? '新建供应商' : 
          modalType === 'edit' ? '编辑供应商' : '供应商详情'
        }
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        width={1200}
        style={{ top: 20 }}
        footer={
          modalType === 'detail' ? [
            <Button key="close" onClick={() => setModalVisible(false)}>
              关闭
            </Button>
          ] : [
            <Button key="cancel" onClick={() => setModalVisible(false)}>
              取消
            </Button>,
            <Button key="submit" type="primary" onClick={handleSubmit}>
              {modalType === 'add' ? '创建' : '更新'}
            </Button>
          ]
        }
      >
        <Form
          form={form}
          layout="vertical"
          disabled={modalType === 'detail'}
        >
          <Tabs defaultActiveKey="basic" type="card">
            <TabPane tab="基本信息" key="basic">
                              <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="供应商编号"
                      name="supplier_code"
                    >
                      <Input disabled placeholder={modalType === 'create' ? '自动生成' : ''} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="供应商名称"
                      name="supplier_name"
                      rules={[{ required: true, message: '请输入供应商名称' }]}
                    >
                      <Input />
                    </Form.Item>
                  </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="供应商简称" name="supplier_abbreviation">
                    <Input disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="供应商分类" name="supplier_category_id">
                    <Select
                      placeholder="选择供应商分类"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.supplier_categories && options.supplier_categories.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="采购员" name="purchaser_id">
                    <Select
                      placeholder="选择采购员"
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
                  <Form.Item label="是否停用" name="is_disabled" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="区域(省份)" name="region">
                    <Select
                      placeholder="选择省份"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.provinces && options.provinces.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="送货方式" name="delivery_method_id">
                    <Select
                      placeholder="选择送货方式"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.delivery_methods && options.delivery_methods.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
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
                        const selectedTax = options.tax_rates && options.tax_rates.find(item => item.value === value);
                        if (selectedTax) {
                          form.setFieldsValue({ tax_rate: selectedTax.rate });
                        }
                      }}
                    >
                      {options.tax_rates && options.tax_rates.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="税率%" name="tax_rate">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      max={100}
                      precision={2}
                      disabled
                    />
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
                  <Form.Item label="定金比例" name="deposit_ratio">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      precision={4}
                      placeholder="默认0"
                      disabled={modalType === 'detail'}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="交期预备(天)" name="delivery_preparation_days">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      placeholder="默认0"
                      disabled={modalType === 'detail'}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="版权平方价" name="copyright_square_price">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      precision={4}
                      placeholder="默认0"
                      disabled={modalType === 'detail'}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="供应商等级" name="supplier_level">
                    <Select
                      placeholder="选择供应商等级"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      <Option value="A">A</Option>
                      <Option value="B">B</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="组织机构代码" name="organization_code">
                    <Input disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="公司网址" name="company_website">
                    <Input disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="外币" name="foreign_currency_id">
                    <Select
                      placeholder="选择外币"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.currencies && options.currencies.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="条码前缀码" name="barcode_prefix_code">
                    <Input disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="条码授权" name="barcode_authorization">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      precision={4}
                      placeholder="默认0"
                      disabled={modalType === 'detail'}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Divider>日期信息</Divider>
              
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="营业期间" name="business_period">
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
                  <Form.Item label="检测报告期间" name="inspection_report_period">
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
                  <Form.Item label="用友编码" name="ufriend_code">
                    <Input disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="企业类型" name="enterprise_type">
                    <Select
                      placeholder="选择企业类型"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      <Option value="individual">个人</Option>
                      <Option value="individual_business">个体工商户</Option>
                      <Option value="limited_company">有限责任公司</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="排序" name="sort_order">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      placeholder="排序序号"
                      disabled={modalType === 'detail'}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="是否启用" name="is_enabled" valuePropName="checked">
                    <Switch disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Divider>地址信息</Divider>
              
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="省份" name="province">
                    <Select
                      placeholder="选择省份"
                      disabled={modalType === 'detail'}
                      allowClear
                    >
                      {options.provinces && options.provinces.map(item => (
                        <Option key={item.value} value={item.value}>{item.label}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="市" name="city">
                    <Input placeholder="选择市" disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="县/区" name="district">
                    <Input placeholder="选择县/区" disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item label="公司地址" name="company_address">
                    <TextArea rows={2} disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item label="备注" name="remarks">
                    <TextArea rows={3} disabled={modalType === 'detail'} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item label="图片" name="image_url">
                    <Upload disabled={modalType === 'detail'}>
                      <Button icon={<UploadOutlined />} disabled={modalType === 'detail'}>
                        上传图片
                      </Button>
                    </Upload>
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            <TabPane tab="联系人信息" key="contacts">
              {modalType !== 'detail' && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  style={{ marginBottom: 16 }}
                  onClick={() => {
                    setContacts([...contacts, {
                      contact_name: '',
                      landline: '',
                      mobile: '',
                      fax: '',
                      qq: '',
                      wechat: '',
                      email: '',
                      department: ''
                    }]);
                  }}
                >
                  添加联系人
                </Button>
              )}
              <Table
                columns={contactColumns}
                dataSource={contacts}
                rowKey={(record, index) => index}
                pagination={false}
                size="small"
              />
            </TabPane>

            <TabPane tab="发货地址" key="delivery">
              {modalType !== 'detail' && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  style={{ marginBottom: 16 }}
                  onClick={() => {
                    setDeliveryAddresses([...deliveryAddresses, {
                      delivery_address: '',
                      contact_name: '',
                      contact_method: ''
                    }]);
                  }}
                >
                  添加发货地址
                </Button>
              )}
              <Table
                columns={deliveryAddressColumns}
                dataSource={deliveryAddresses}
                rowKey={(record, index) => index}
                pagination={false}
                size="small"
              />
            </TabPane>

            <TabPane tab="开票单位" key="invoice">
              {modalType !== 'detail' && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  style={{ marginBottom: 16 }}
                  onClick={() => {
                    setInvoiceUnits([...invoiceUnits, {
                      invoice_unit: '',
                      taxpayer_id: '',
                      invoice_address: '',
                      invoice_phone: '',
                      invoice_bank: '',
                      invoice_account: ''
                    }]);
                  }}
                >
                  添加开票单位
                </Button>
              )}
              <Table
                columns={invoiceUnitColumns}
                dataSource={invoiceUnits}
                rowKey={(record, index) => index}
                pagination={false}
                size="small"
              />
            </TabPane>

            <TabPane tab="归属公司" key="companies">
              {modalType !== 'detail' && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  style={{ marginBottom: 16 }}
                  onClick={() => {
                    setAffiliatedCompanies([...affiliatedCompanies, {
                      affiliated_company: ''
                    }]);
                  }}
                >
                  添加归属公司
                </Button>
              )}
              <Table
                columns={affiliatedCompanyColumns}
                dataSource={affiliatedCompanies}
                rowKey={(record, index) => index}
                pagination={false}
                size="small"
              />
            </TabPane>
          </Tabs>
        </Form>
      </Modal>
    </div>
  );
};

export default SupplierManagement; 