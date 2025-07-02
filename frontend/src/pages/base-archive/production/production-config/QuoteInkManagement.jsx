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
  Checkbox,
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
import { getQuoteInks, createQuoteInk, updateQuoteInk, deleteQuoteInk } from '../../../../api/production/production-config/quoteInkApi';

const { Title } = Typography;
const { Option } = Select;

const QuoteInkManagement = () => {
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
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await getQuoteInks({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      // 正确处理后端响应格式
      if (response.data.success) {
        const { quote_inks, total, current_page } = response.data.data;
        
        // 为每行数据添加key
        const dataWithKeys = quote_inks.map((item, index) => ({
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
      message.error('加载数据失败');
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
      category_name: '',
      square_price: null,
      unit_price_formula: '',
      gram_weight: null,
      is_ink: false,
      is_solvent: false,
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
          response = await updateQuoteInk(item.id, row);
        } else {
          // 创建新记录
          response = await createQuoteInk(row);
        }

        // 正确处理后端响应格式
        if (response.data.success) {
          setEditingKey('');
          message.success('保存成功');
          
          // 如果更新了排序字段，重新加载数据以保证正确的排序
          if ('sort_order' in row) {
            await loadData();
          } else {
            // 更新本地数据
            newData.splice(index, 1, {
              ...updatedItem,
              ...response.data.data,
              key: response.data.data.id
            });
            setData(newData);
          }
        }
      }
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        console.error('保存失败:', error);
        message.error('保存失败');
      }
    }
  };

  // 删除记录
  const handleDelete = async (key) => {
    try {
      const record = data.find(item => item.key === key);
      
      if (record.id && !record.id.startsWith('temp_')) {
        // 删除服务器记录
        await deleteQuoteInk(record.id);
        message.success('删除成功');
      }
      
      // 删除本地记录
      const newData = data.filter(item => item.key !== key);
      setData(newData);
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  // 添加新行
  const handleAdd = () => {
    const newKey = `temp_${Date.now()}`;
    const newData = {
      key: newKey,
      category_name: '',
      square_price: null,
      unit_price_formula: '',
      gram_weight: null,
      is_ink: false,
      is_solvent: false,
      sort_order: 0,
      description: '',
      is_enabled: true,
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
        inputNode = <InputNumber min={0} step={0.01} style={{ width: '100%' }} />;
        break;
      case 'switch':
        inputNode = <Switch />;
        break;
      case 'checkbox':
        inputNode = <Checkbox />;
        break;
      case 'select':
        inputNode = (
          <Select style={{ width: '100%' }}>
            <Option value="按平方计算">按平方计算</Option>
            <Option value="按重量计算">按重量计算</Option>
            <Option value="按用量计算">按用量计算</Option>
            <Option value="固定单价">固定单价</Option>
            <Option value="自定义公式">自定义公式</Option>
          </Select>
        );
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
            valuePropName={inputType === 'checkbox' || inputType === 'switch' ? 'checked' : 'value'}
            rules={[
              {
                required: dataIndex === 'category_name',
                message: `请输入${title}!`,
              },
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
      title: '分类名称',
      dataIndex: 'category_name',
      key: 'category_name',
      width: 150,
      fixed: 'left',
      editable: true,
      render: (text, record) => {
        const editable = isEditing(record);
        return editable ? text : (
          <span style={{ fontWeight: 500 }}>{text}</span>
        );
      }
    },
    {
      title: '平方价',
      dataIndex: 'square_price',
      key: 'square_price',
      width: 120,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '单价计算公式',
      dataIndex: 'unit_price_formula',
      key: 'unit_price_formula',
      width: 150,
      editable: true,
      inputType: 'select',
      render: (text) => text || '-'
    },
    {
      title: '克重',
      dataIndex: 'gram_weight',
      key: 'gram_weight',
      width: 100,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '油墨',
      dataIndex: 'is_ink',
      key: 'is_ink',
      width: 80,
      editable: true,
      inputType: 'checkbox',
      align: 'center',
      render: (checked, record) => {
        const editable = isEditing(record);
        return editable ? checked : (
          <Checkbox 
            checked={checked} 
            disabled 
          />
        );
      }
    },
    {
      title: '溶剂',
      dataIndex: 'is_solvent',
      key: 'is_solvent',
      width: 80,
      editable: true,
      inputType: 'checkbox',
      align: 'center',
      render: (checked, record) => {
        const editable = isEditing(record);
        return editable ? checked : (
          <Checkbox 
            checked={checked} 
            disabled 
          />
        );
      }
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      editable: true,
      inputType: 'number',
      align: 'center'
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
          {text || '-'}
        </Tooltip>
      )
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
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
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
      }
    }
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
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Title level={4} style={{ margin: 0 }}>报价油墨管理</Title>
          </Col>
          <Col>
            <Space>
              <Input
                ref={searchInputRef}
                placeholder="搜索分类名称、公式、描述"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onPressEnter={handleSearch}
                style={{ width: 250 }}
                allowClear
              />
              <Button 
                type="primary" 
                icon={<SearchOutlined />} 
                onClick={handleSearch}
              >
                搜索
              </Button>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={handleReset}
              >
                重置
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAdd}
                disabled={editingKey !== ''}
              >
                新增报价油墨
              </Button>
            </Space>
          </Col>
        </Row>

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
            rowKey="key"
            rowClassName="editable-row"
            pagination={{
              ...pagination,
              onChange: (page, pageSize) => {
                handleTableChange({ ...pagination, current: page, pageSize });
              },
              onShowSizeChange: (current, size) => {
                handleTableChange({ ...pagination, current: 1, pageSize: size });
              }
            }}
            loading={loading}
            scroll={{ x: 1200 }}
            size="small"
          />
        </Form>
      </Card>
    </div>
  );
};

export default QuoteInkManagement; 