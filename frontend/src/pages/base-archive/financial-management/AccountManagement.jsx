import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  message,
  Popconfirm,
  Switch,
  Form,
  InputNumber,
  Row,
  Col,
  Tooltip,
  Typography,
  Select,
  DatePicker
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SaveOutlined,
  SearchOutlined,
  BankOutlined
} from '@ant-design/icons';
import accountManagementApi from '../../../api/accountManagement';
import { currencyApi } from '../../../api/currency';
import dayjs from 'dayjs';

const { Search } = Input;
const { Title } = Typography;
const { Option } = Select;

const AccountManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [editingKey, setEditingKey] = useState('');
  const [form] = Form.useForm();
  const [currencies, setCurrencies] = useState([]);
  const [baseCurrency, setBaseCurrency] = useState(null);
  const searchInputRef = React.useRef(null);

  // 账户类型选项
  const accountTypeOptions = [
    { label: '现金', value: '现金' },
    { label: '支票', value: '支票' },
    { label: '银行', value: '银行' },
  ];

  // 获取币别列表
  const fetchCurrencies = async () => {
    try {
      const result = await currencyApi.getEnabledCurrencies();
      setCurrencies(result || []);
      
      // 查找本位币
      const baseCurrencyItem = (result || []).find(currency => currency.is_base_currency);
      setBaseCurrency(baseCurrencyItem);
    } catch (error) {
      console.error('获取币别列表失败:', error);
    }
  };

  // 获取数据
  const fetchData = async (page = 1, pageSize = 20, search = '') => {
    setLoading(true);
    try {
      const params = {
        page,
        per_page: pageSize,
      };
      if (search) {
        params.search = search;
      }

      const result = await accountManagementApi.getAccounts(params);
      setData(result.accounts || []);
      setPagination({
        current: page,
        pageSize,
        total: result.total || 0,
      });
    } catch (error) {
      console.error('获取账户列表失败:', error);
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    fetchCurrencies();
  }, []);

  // 搜索
  const handleSearch = () => {
    fetchData(1, pagination.pageSize, searchText);
  };

  // 重置
  const handleReset = () => {
    setSearchText('');
    fetchData(1, pagination.pageSize, '');
  };

  // 刷新
  const handleRefresh = () => {
    fetchData(pagination.current, pagination.pageSize, searchText);
  };

  // 分页变化
  const handleTableChange = (paginationConfig) => {
    fetchData(paginationConfig.current, paginationConfig.pageSize, searchText);
  };

  // 编辑行
  const isEditing = (record) => record.id === editingKey;

  const edit = (record) => {
    form.setFieldsValue({
      account_name: '',
      account_type: '',
      currency_id: baseCurrency ? baseCurrency.id : null,
      bank_name: '',
      bank_account: '',
      opening_address: '',
      description: '',
      sort_order: 0,
      is_enabled: true,
      ...record,
      opening_date: record.opening_date ? dayjs(record.opening_date) : null,
    });
    setEditingKey(record.id);
  };

  const cancel = () => {
    setEditingKey('');
  };

  // 保存编辑
  const save = async (id) => {
    try {
      const row = await form.validateFields();
      const newData = [...data];
      const index = newData.findIndex((item) => id === item.id);

      if (index > -1) {
        // 处理日期格式
        const submitData = {
          ...row,
          opening_date: row.opening_date ? row.opening_date.format('YYYY-MM-DD') : null,
        };
        
        // 如果是新增的临时记录
        if (id.startsWith('temp_')) {
          await accountManagementApi.createAccount(submitData);
          message.success('创建成功');
          setEditingKey('');
          fetchData(pagination.current, pagination.pageSize, searchText);
        } else {
          // 更新现有记录
          await accountManagementApi.updateAccount(id, submitData);
          message.success('更新成功');
          setEditingKey('');
          fetchData(pagination.current, pagination.pageSize, searchText);
        }
      }
    } catch (errInfo) {
      console.log('验证失败:', errInfo);
    }
  };

  // 删除
  const handleDelete = async (id) => {
    try {
      // 如果是临时记录，直接从列表中删除
      if (id.startsWith('temp_')) {
        const newData = data.filter(item => item.id !== id);
        setData(newData);
        message.success('删除成功');
        return;
      }

      await accountManagementApi.deleteAccount(id);
      message.success('删除成功');
      fetchData(pagination.current, pagination.pageSize, searchText);
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  // 添加新行
  const handleAdd = () => {
    const newData = {
      id: `temp_${Date.now()}`,
      account_name: '',
      account_type: '',
      currency_id: baseCurrency ? baseCurrency.id : null,
      currency_name: baseCurrency ? baseCurrency.currency_name : '',
      currency_code: baseCurrency ? baseCurrency.currency_code : '',
      bank_name: '',
      bank_account: '',
      opening_date: null,
      opening_address: '',
      description: '',
      sort_order: 0,
      is_enabled: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by_name: '当前用户',
      updated_by_name: '',
    };
    setData([newData, ...data]);
    edit(newData);
  };

  // 可编辑单元格组件
  const EditableCell = ({
    editing,
    dataIndex,
    title,
    inputType,
    record,
    index,
    children,
    ...restProps
  }) => {
    let inputNode;
    
    if (inputType === 'number') {
      inputNode = <InputNumber style={{ width: '100%' }} min={0} />;
    } else if (inputType === 'switch') {
      inputNode = <Switch />;
    } else if (inputType === 'select') {
      if (dataIndex === 'account_type') {
        inputNode = (
          <Select style={{ width: '100%' }} placeholder="请选择账户类型">
            {accountTypeOptions.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        );
      } else if (dataIndex === 'currency_id') {
        inputNode = (
          <Select style={{ width: '100%' }} placeholder="请选择币别" allowClear>
            {currencies.map(currency => (
              <Option key={currency.id} value={currency.id}>
                {currency.currency_name} ({currency.currency_code})
              </Option>
            ))}
          </Select>
        );
      }
    } else if (inputType === 'date') {
      inputNode = <DatePicker style={{ width: '100%' }} placeholder="请选择开户日期" />;
    } else if (inputType === 'textarea') {
      inputNode = <Input.TextArea rows={2} />;
    } else {
      inputNode = <Input />;
    }

    return (
      <td {...restProps}>
        {editing ? (
          <Form.Item
            name={dataIndex}
            style={{ margin: 0 }}
            rules={[
              {
                required: ['account_name', 'account_type'].includes(dataIndex),
                message: `请输入${title}!`,
              },
              ...(dataIndex === 'account_name' ? [{
                max: 200,
                message: '账户名称不能超过200个字符'
              }] : []),
              ...(dataIndex === 'bank_account' ? [{
                max: 100,
                message: '银行账户不能超过100个字符'
              }] : [])
            ]}
          >
            {inputNode}
          </Form.Item>
        ) : (
          children
        )}
      </td>
    );
  };

  // 表格列定义
  const columns = [
    {
      title: '账户名称',
      dataIndex: 'account_name',
      key: 'account_name',
      width: 200,
      editable: true,
    },
    {
      title: '账户类型',
      dataIndex: 'account_type',
      key: 'account_type',
      width: 120,
      editable: true,
      inputType: 'select',
    },
    {
      title: '币别',
      dataIndex: 'currency_id',
      key: 'currency_id',
      width: 120,
      editable: true,
      inputType: 'select',
      render: (text, record) => {
        // 如果有币别信息，显示币别名称和代码
        if (record.currency_name && record.currency_code) {
          return `${record.currency_name} (${record.currency_code})`;
        }
        // 如果只有currency_id，从currencies列表中查找对应的币别信息
        if (text && currencies.length > 0) {
          const currency = currencies.find(c => c.id === text);
          if (currency) {
            return `${currency.currency_name} (${currency.currency_code})`;
          }
        }
        return '-';
      },
    },
    {
      title: '开户银行',
      dataIndex: 'bank_name',
      key: 'bank_name',
      width: 180,
      editable: true,
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      ),
    },
    {
      title: '银行账户',
      dataIndex: 'bank_account',
      key: 'bank_account',
      width: 180,
      editable: true,
    },
    {
      title: '开户日期',
      dataIndex: 'opening_date',
      key: 'opening_date',
      width: 120,
      align: 'center',
      editable: true,
      inputType: 'date',
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD') : '-',
    },
    {
      title: '开户地址',
      dataIndex: 'opening_address',
      key: 'opening_address',
      editable: true,
      inputType: 'textarea',
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      editable: true,
      inputType: 'textarea',
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      ),
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      align: 'center',
      editable: true,
      inputType: 'number',
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      align: 'center',
      editable: true,
      inputType: 'switch',
      render: (value, record) => (
        <Switch
          checked={value}
          disabled={!isEditing(record)}
          size="small"
        />
      ),
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      key: 'created_by_name',
      width: 100,
      align: 'center',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      align: 'center',
      render: (text) => text ? new Date(text).toLocaleString() : '',
    },
    {
      title: '修改人',
      dataIndex: 'updated_by_name',
      key: 'updated_by_name',
      width: 100,
      align: 'center',
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      align: 'center',
      render: (text) => text ? new Date(text).toLocaleString() : '',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      align: 'center',
      render: (_, record) => {
        const editable = isEditing(record);
        return editable ? (
          <Space>
            <Button
              type="link"
              size="small"
              icon={<SaveOutlined />}
              onClick={() => save(record.id)}
            >
              保存
            </Button>
            <Button
              type="link"
              size="small"
              onClick={cancel}
            >
              取消
            </Button>
          </Space>
        ) : (
          <Space>
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              disabled={editingKey !== ''}
              onClick={() => edit(record)}
            >
              编辑
            </Button>
            <Popconfirm
              title="确定删除这条记录吗？"
              onConfirm={() => handleDelete(record.id)}
              disabled={editingKey !== ''}
            >
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
                disabled={editingKey !== ''}
              >
                删除
              </Button>
            </Popconfirm>
          </Space>
        );
      },
    },
  ];

  // 合并列配置
  const mergedColumns = columns.map((col) => {
    if (!col.editable) {
      return col;
    }
    
    return {
      ...col,
      onCell: (record) => ({
        record,
        inputType: col.inputType || 'text',
        dataIndex: col.dataIndex,
        title: col.title,
        editing: isEditing(record),
      }),
    };
  });

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={4} style={{ margin: 0 }}>
                <BankOutlined style={{ marginRight: 8 }} />
                账户管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索账户名称、银行名称、账户号码"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={handleSearch}
                  style={{ width: 280 }}
                  prefix={<SearchOutlined />}
                />
                <Button onClick={handleSearch} type="primary">
                  搜索
                </Button>
                <Button onClick={handleReset}>
                  重置
                </Button>
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  onClick={handleAdd}
                  disabled={editingKey !== ''}
                >
                  新增
                </Button>
                <Button 
                  icon={<ReloadOutlined />}
                  onClick={handleRefresh}
                  disabled={editingKey !== ''}
                >
                  刷新
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        <Form form={form} component={false}>
          <Table
            components={{
              body: {
                cell: EditableCell,
              },
            }}
            bordered
            dataSource={data}
            columns={mergedColumns}
            rowClassName="editable-row"
            rowKey="id"
            loading={loading}
            pagination={{
              ...pagination,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) =>
                `第 ${range[0]}-${range[1]} 条/共 ${total} 条`,
            }}
            onChange={handleTableChange}
            scroll={{ x: 1800 }}
            size="small"
          />
        </Form>
      </Card>
    </div>
  );
};

export default AccountManagement; 