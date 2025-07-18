import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Switch,
  InputNumber,
  Space,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Form,
  Tooltip,
  Tag
} from 'antd';
import {
  PlusOutlined,
  SaveOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined,
  StarOutlined,
  DollarOutlined
} from '@ant-design/icons';
import { 
  getCurrencies, 
  createCurrency, 
  updateCurrency, 
  deleteCurrency, 
  getCurrencyById 
} from '../../../api/base-archive/financial-management/currency';

const { Title } = Typography;

const Currency = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingKey, setEditingKey] = useState('');
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });
  
  const [form] = Form.useForm();
  const searchInputRef = useRef(null);

  // 判断是否在编辑状态
  const isEditing = (record) => record.key === editingKey;

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
      };
      const response = await getCurrencies(params);
      
      if (response.data?.success) {
        const { currencies, total } = response.data.data;
        // 为每个数据项添加key属性，解决React key警告
        const dataWithKeys = (currencies || []).map(item => ({
          ...item,
          key: item.id || item.key || `temp_${Date.now()}_${Math.random()}`
        }));
        setData(dataWithKeys);
        setPagination({
          ...pagination,
          total: total || 0,
        });
      }
    } catch (error) {
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    loadData();
  }, []);

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData();
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData();
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData();
  };

  // 开始编辑
  const edit = (record) => {
    form.setFieldsValue({
      currency_code: '',
      currency_name: '',
      exchange_rate: 1.0000,
      description: '',
      sort_order: 0,
      is_enabled: true,
      is_base_currency: false,
      ...record,
    });
    setEditingKey(record.key);
  };

  // 取消编辑
  const cancel = () => {
    setEditingKey('');
    form.resetFields();
  };

  // 保存编辑
  const save = async (key) => {
    try {
      const row = await form.validateFields();
      const newData = [...data];
      const index = newData.findIndex((item) => key === item.key);

      if (index > -1) {
        const item = newData[index];
        let response;
        
        if (item.id && !item.id.toString().startsWith('temp_')) {
          response = await updateCurrency(item.id, row);
        } else {
          response = await createCurrency(row);
        }
        
        if (response.data?.success) {
          message.success(item.id ? '更新成功' : '创建成功');
          setEditingKey('');
          loadData();
        }
      }
    } catch (error) {
      message.error('保存失败');
    }
  };

  // 删除记录
  const handleDelete = async (record) => {
    try {
      const response = await deleteCurrency(record.id);
      if (response.data?.success) {
        message.success('删除成功');
        loadData();
      }
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 添加新行
  const handleAdd = () => {
    const newKey = `temp_${Date.now()}`;
    const newData = {
      key: newKey,
      currency_code: '',
      currency_name: '',
      exchange_rate: 1.0000,
      description: '',
      sort_order: 0,
      is_enabled: true,
      is_base_currency: false,
      created_by_name: '',
      created_at: '',
      updated_by_name: '',
      updated_at: ''
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
    
    switch (inputType) {
      case 'number':
        inputNode = <InputNumber min={0} style={{ width: '100%' }} />;
        break;
      case 'decimal':
        inputNode = <InputNumber min={0.01} precision={2} style={{ width: '100%' }} />;
        break;
      case 'integer':
        inputNode = <InputNumber min={0} max={6} style={{ width: '100%' }} />;
        break;
      case 'switch':
        inputNode = <Switch />;
        break;
      case 'textarea':
        inputNode = <Input.TextArea rows={2} />;
        break;
      default:
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
                required: ['currency_code', 'currency_name', 'exchange_rate'].includes(dataIndex),
                message: `请输入${title}!`,
              },
              ...(dataIndex === 'currency_code' ? [
                { max: 10, message: '币别代码不能超过10个字符' }
              ] : []),
                             ...(dataIndex === 'currency_name' ? [
                 { max: 100, message: '币别名称不能超过100个字符' }
               ] : []),
               ...(dataIndex === 'exchange_rate' ? [
                 { type: 'number', min: 0.0001, message: '汇率必须大于0' }
               ] : [])
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
      title: '币别代码',
      dataIndex: 'currency_code',
      key: 'currency_code',
      width: 120,
      editable: true,
      render: (text, record) => {
        const editable = isEditing(record);
        return editable ? text : (
          <span style={{ fontWeight: 500 }}>
            {text}
            {record.is_base_currency && (
              <Tag color="gold" style={{ marginLeft: 8 }}>
                <StarOutlined /> 本位币
              </Tag>
            )}
          </span>
        );
      }
    },
    {
      title: '币别名称',
      dataIndex: 'currency_name',
      key: 'currency_name',
      width: 150,
      editable: true,
      render: (text, record) => {
        const editable = isEditing(record);
        return editable ? text : (
          <span style={{ fontWeight: 500 }}>{text}</span>
        );
      }
    },
    {
      title: '汇率',
      dataIndex: 'exchange_rate',
      key: 'exchange_rate',
      width: 120,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value, record) => {
        const editable = isEditing(record);
        return editable ? value : parseFloat(value).toFixed(2);
      }
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 200,
      editable: true,
      inputType: 'textarea',
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      )
    },
    {
      title: '显示排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 100,
      editable: true,
      inputType: 'number',
      align: 'center'
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 100,
      editable: true,
      inputType: 'switch',
      align: 'center',
      render: (enabled, record) => {
        const editable = isEditing(record);
        return editable ? enabled : (
          <Switch 
            checked={enabled} 
            disabled 
            size="small"
          />
        );
      }
    },
    {
      title: '是否本位币',
      dataIndex: 'is_base_currency',
      key: 'is_base_currency',
      width: 120,
      editable: true,
      inputType: 'switch',
      align: 'center',
      render: (isBase, record) => {
        const editable = isEditing(record);
        return editable ? isBase : (
          <Switch 
            checked={isBase} 
            disabled 
            size="small"
          />
        );
      }
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      key: 'created_by_name',
      width: 100,
      align: 'center'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      align: 'center',
      render: (text) => text ? new Date(text).toLocaleString() : ''
    },
    {
      title: '修改人',
      dataIndex: 'updated_by_name',
      key: 'updated_by_name',
      width: 100,
      align: 'center'
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      align: 'center',
      render: (text) => text ? new Date(text).toLocaleString() : ''
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
              icon={<CheckOutlined />}
                              onClick={() => save(record.key)}
            >
              保存
            </Button>
            <Button
              type="link"
              size="small"
              icon={<CloseOutlined />}
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
                title="确定删除这个币别吗？"
                onConfirm={() => handleDelete(record)}
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
                <DollarOutlined style={{ marginRight: 8 }} />
                币别管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索币别代码、名称或描述"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={handleSearch}
                  style={{ width: 250 }}
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
                  onClick={() => loadData()}
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
            pagination={pagination}
            loading={loading}
            onChange={handleTableChange}
            scroll={{ x: 1800 }}
            size="small"
          />
        </Form>
      </Card>
    </div>
  );
};

export default Currency; 