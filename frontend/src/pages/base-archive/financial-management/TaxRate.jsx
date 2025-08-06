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
  PercentageOutlined
} from '@ant-design/icons';
import { 
  getTaxRates, 
  createTaxRate, 
  updateTaxRate, 
  deleteTaxRate 
} from '../../../api/base-archive/financial-management/taxRate';

const { Title } = Typography;

const TaxRate = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingKey, setEditingKey] = useState('');
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
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
      const response = await getTaxRates(params);
      
      if (response.data?.success) {
        const { tax_rates, total } = response.data.data;
        // 为每条记录添加key属性用于React表格
        const dataWithKeys = (tax_rates || []).map(item => ({
          ...item,
          key: item.id || item.key
        }));
        setData(dataWithKeys);
        setPagination({
          ...pagination,
          total: total || 0,
        });
      } else {
        console.error('API响应失败:', response.data);
        message.error('读取数据失败');
      }
    } catch (error) {
      console.error('获取税率数据错误:', error);
      message.error('网络连接失败');
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
      tax_name: '',
      tax_rate: 0,
      description: '',
      sort_order: 0,
      is_enabled: true,
      is_default: false,
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
          response = await updateTaxRate(item.id, row);
        } else {
          response = await createTaxRate(row);
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
      const response = await deleteTaxRate(record.id);
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
    const newData = {
      key: `temp_${Date.now()}`,
      tax_name: '',
      tax_rate: 0,
      is_default: false,
      description: '',
      sort_order: 0,
      is_enabled: true,
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
      inputNode = (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          max={100}
          precision={2}
          formatter={value => `${value}%`}
          parser={value => value.replace('%', '')}
        />
      );
    } else if (inputType === 'switch') {
      inputNode = <Switch />;
    } else if (inputType === 'sort') {
      inputNode = <InputNumber style={{ width: '100%' }} min={0} />;
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
                required: ['tax_name', 'tax_rate'].includes(dataIndex),
                message: `请输入${title}!`,
              },
              ...(dataIndex === 'tax_name' ? [{
                max: 100,
                message: '税收名称不能超过100个字符'
              }] : []),
              ...(dataIndex === 'tax_rate' ? [{
                type: 'number',
                min: 0,
                max: 100,
                message: '税率必须在0-100之间'
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
      title: '税收',
      dataIndex: 'tax_name',
      key: 'tax_name',
      width: 200,
      editable: true,
      render: (text, record) => (
        <Space>
          {text}
          {record.is_default && (
            <Tag color="gold" icon={<StarOutlined />}>
              默认
            </Tag>
          )}
        </Space>
      ),
    },
    {
      title: '税率(%)',
      dataIndex: 'tax_rate',
      key: 'tax_rate',
      width: 120,
      editable: true,
      render: (value) => `${value}%`,
    },
    {
      title: '评审默认',
      dataIndex: 'is_default',
      key: 'is_default',
      width: 100,
      editable: true,
      render: (value, record) => (
        <Switch
          checked={value}
          disabled={!isEditing(record)}
          size="small"
        />
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
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
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      editable: true,
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      editable: true,
      align: 'center',
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
              title="确定删除这条记录吗？"
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
    
    let inputType = 'text';
    if (col.dataIndex === 'tax_rate') {
      inputType = 'number';
    } else if (col.dataIndex === 'is_enabled' || col.dataIndex === 'is_default') {
      inputType = 'switch';
    } else if (col.dataIndex === 'sort_order') {
      inputType = 'sort';
    }

    return {
      ...col,
      onCell: (record) => ({
        record,
        inputType,
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
                <PercentageOutlined style={{ marginRight: 8 }} />
                税率管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索税收名称、描述"
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
            onChange={handleTableChange}
            loading={loading}
            scroll={{ x: 1600 }}
            size="small"
          />
        </Form>
      </Card>
    </div>
  );
};

export default TaxRate; 