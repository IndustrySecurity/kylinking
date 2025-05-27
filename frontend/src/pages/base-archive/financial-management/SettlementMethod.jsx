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
  Typography
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SaveOutlined,
  SearchOutlined,
  TransactionOutlined
} from '@ant-design/icons';
import { settlementMethodApi } from '../../../api/settlementMethod';

const { Search } = Input;
const { Title } = Typography;

const SettlementMethod = () => {
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
  const searchInputRef = React.useRef(null);

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

      const result = await settlementMethodApi.getSettlementMethods(params);
      setData(result.settlement_methods || []);
      setPagination({
        current: page,
        pageSize,
        total: result.total || 0,
      });
    } catch (error) {
      console.error('获取结算方式列表失败:', error);
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
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
      settlement_name: '',
      description: '',
      sort_order: 0,
      is_enabled: true,
      ...record,
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
        const item = newData[index];
        
        // 如果是新增的临时记录
        if (id.startsWith('temp_')) {
          await settlementMethodApi.createSettlementMethod(row);
          message.success('创建成功');
          setEditingKey('');
          fetchData(pagination.current, pagination.pageSize, searchText);
        } else {
          // 更新现有记录
          await settlementMethodApi.updateSettlementMethod(id, row);
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

      await settlementMethodApi.deleteSettlementMethod(id);
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
      settlement_name: '',
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
                required: ['settlement_name'].includes(dataIndex),
                message: `请输入${title}!`,
              },
              ...(dataIndex === 'settlement_name' ? [{
                max: 100,
                message: '结算方式名称不能超过100个字符'
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
      title: '结算方式',
      dataIndex: 'settlement_name',
      key: 'settlement_name',
      width: 200,
      editable: true,
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
      align: 'center',
      editable: true,
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      align: 'center',
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
    
    let inputType = 'text';
    if (col.dataIndex === 'sort_order') {
      inputType = 'number';
    } else if (col.dataIndex === 'is_enabled') {
      inputType = 'switch';
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
                <TransactionOutlined style={{ marginRight: 8 }} />
                结算方式管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索结算方式名称、描述"
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
                  onClick={handleRefresh}
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
            scroll={{ x: 1600 }}
            size="small"
          />
        </Form>
      </Card>
    </div>
  );
};

export default SettlementMethod; 