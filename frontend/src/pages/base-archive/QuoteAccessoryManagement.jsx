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
  Select
} from 'antd';
import {
  PlusOutlined,
  SaveOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined
} from '@ant-design/icons';
import quoteAccessoryApi from '../../api/quoteAccessoryApi';

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const QuoteAccessoryManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingKey, setEditingKey] = useState('');
  const [searchText, setSearchText] = useState('');
  const [calculationSchemes, setCalculationSchemes] = useState([]);
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

  // 加载计算方案选项
  const loadCalculationSchemes = async () => {
    try {
      const response = await quoteAccessoryApi.getMaterialQuoteCalculationSchemes();
      
      if (response.data.code === 200) {
        setCalculationSchemes(response.data.data || []);
      }
    } catch (error) {
      console.error('加载计算方案失败:', error);
      message.error('加载计算方案失败：' + (error.response?.data?.message || error.message));
    }
  };

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await quoteAccessoryApi.getQuoteAccessories({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      // 正确处理后端响应格式
      if (response.data.code === 200) {
        const { quote_accessories, total, current_page } = response.data.data;
        
        // 为每行数据添加key
        const dataWithKeys = quote_accessories.map((item, index) => ({
          ...item,
          key: item.id || `temp_${index}`
        }));
        
        setData(dataWithKeys);
        setPagination(prev => ({
          ...prev,
          total,
          current: current_page
        }));
      }
    } catch (error) {
      console.error('加载数据失败:', error);
      message.error('加载数据失败：' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    loadData();
    loadCalculationSchemes();
  }, []);

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '' });
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize
    });
  };

  // 开始编辑
  const edit = (record) => {
    form.setFieldsValue({
      material_name: '',
      unit_price: null,
      calculation_scheme_id: '',
      sort_order: 0,
      description: '',
      is_enabled: true,
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
        const updatedItem = { ...item, ...row };
        
        // 调用API保存
        let response;
        if (item.id && !item.id.startsWith('temp_')) {
          // 更新现有记录
          response = await quoteAccessoryApi.updateQuoteAccessory(item.id, row);
        } else {
          // 创建新记录
          response = await quoteAccessoryApi.createQuoteAccessory(row);
        }

        // 正确处理后端响应格式
        if (response.data.code === 200) {
          // 更新本地数据
          newData.splice(index, 1, {
            ...updatedItem,
            ...response.data.data,
            key: response.data.data.id
          });
          setData(newData);
          setEditingKey('');
          message.success('保存成功');
        }
      }
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        console.error('保存失败:', error);
        message.error('保存失败：' + (error.response?.data?.message || error.message));
      }
    }
  };

  // 删除记录
  const handleDelete = async (key) => {
    try {
      const record = data.find(item => item.key === key);
      
      if (record.id && !record.id.startsWith('temp_')) {
        // 删除服务器记录
        const response = await quoteAccessoryApi.deleteQuoteAccessory(record.id);
        if (response.data.code === 200) {
          message.success('删除成功');
        }
      }
      
      // 删除本地记录
      const newData = data.filter(item => item.key !== key);
      setData(newData);
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败：' + (error.response?.data?.message || error.message));
    }
  };

  // 添加新行
  const handleAdd = () => {
    if (editingKey !== '') {
      message.warning('请先保存当前编辑的记录');
      return;
    }

    const newKey = `temp_${Date.now()}`;
    const newData = {
      key: newKey,
      id: newKey,
      material_name: '',
      unit_price: null,
      calculation_scheme_id: '',
      sort_order: 0,
      description: '',
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
    const getInputNode = () => {
      switch (inputType) {
        case 'number':
          return <InputNumber style={{ width: '100%' }} precision={2} />;
        case 'integer':
          return <InputNumber style={{ width: '100%' }} precision={0} />;
        case 'switch':
          return <Switch />;
        case 'textarea':
          return <TextArea rows={2} />;
        case 'select':
          return (
            <Select style={{ width: '100%' }} allowClear>
              {calculationSchemes.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          );
        default:
          return <Input />;
      }
    };

    return (
      <td {...restProps}>
        {editing ? (
          <Form.Item
            name={dataIndex}
            style={{ margin: 0 }}
            rules={[
              {
                required: dataIndex === 'material_name',
                message: `请输入${title}!`,
              },
            ]}
          >
            {getInputNode()}
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
      title: '材料名称',
      dataIndex: 'material_name',
      key: 'material_name',
      width: 150,
      editable: true,
      inputType: 'text',
      align: 'center',
      render: (text) => text || '-',
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 120,
      editable: true,
      inputType: 'number',
      align: 'center',
      render: (value) => value ? `¥${Number(value).toFixed(2)}` : '-',
    },
    {
      title: '计算方案',
      dataIndex: 'calculation_scheme_id',
      key: 'calculation_scheme_id',
      width: 150,
      editable: true,
      inputType: 'select',
      align: 'center',
      render: (value, record) => {
        // 显示计算方案名称
        return record.calculation_scheme_name || '-';
      },
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      editable: true,
      inputType: 'integer',
      align: 'center',
      render: (value) => value || 0,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 200,
      editable: true,
      inputType: 'textarea',
      align: 'center',
      render: (text) => text || '-',
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
      width: 150,
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
              onConfirm={() => handleDelete(record.key)}
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
              <Title level={4} style={{ margin: 0 }}>报价辅材管理</Title>
            </Col>
            <Col>
              <Space>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索材料名称或描述"
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
            scroll={{ x: 1400 }}
            size="small"
          />
        </Form>
      </Card>
    </div>
  );
};

export default QuoteAccessoryManagement; 