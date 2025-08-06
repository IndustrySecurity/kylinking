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
  Checkbox
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
import quoteMaterialApi from '../../../api/base-archive/production-config/quoteMaterialApi';

const { Title } = Typography;
const { TextArea } = Input;

const QuoteMaterialManagement = () => {
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
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await quoteMaterialApi.getQuoteMaterials({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      // 正确处理后端响应格式
      if (response.data.success) {
        const { quote_materials, total, current_page } = response.data.data;
        
        // 为每行数据添加唯一且稳定的key
        const dataWithKeys = quote_materials.map((item, index) => ({
          ...item,
          key: item.id || `temp_${index}_${Date.now()}`
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
      density: null,
      kg_price: null,
      layer_1_optional: false,
      layer_2_optional: false,
      layer_3_optional: false,
      layer_4_optional: false,
      layer_5_optional: false,
      sort_order: 0,
      remarks: '',
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
          response = await quoteMaterialApi.updateQuoteMaterial(item.id, row);
        } else {
          // 创建新记录
          response = await quoteMaterialApi.createQuoteMaterial(row);
        }

        // 取消编辑状态
        setEditingKey('');
        message.success('保存成功');
        
        // 如果更新了排序字段，重新加载数据以保证正确的排序
        if ('sort_order' in row) {
          await loadData();
        } else {
          // 更新本地数据
          newData.splice(index, 1, {
            ...updatedItem,
            ...response,
            key: response.id
          });
          setData(newData);
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
        await quoteMaterialApi.deleteQuoteMaterial(record.id);
        message.success('删除成功');
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
    const newKey = `temp_${Date.now()}`;
    const newData = {
      key: newKey,
      material_name: '',
      density: null,
      kg_price: null,
      layer_1_optional: false,
      layer_2_optional: false,
      layer_3_optional: false,
      layer_4_optional: false,
      layer_5_optional: false,
      sort_order: 0,
      remarks: '',
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
    
    switch (inputType) {
      case 'number':
        inputNode = <InputNumber style={{ width: '100%' }} precision={2} />;
        break;
      case 'switch':
        inputNode = <Switch />;
        break;
      case 'checkbox':
        inputNode = <Checkbox />;
        break;
      case 'textarea':
        inputNode = <TextArea rows={2} />;
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
            rules={
              dataIndex === 'material_name'
                ? [{ required: true, message: `请输入${title}!` }]
                : []
            }
            valuePropName={inputType === 'switch' || inputType === 'checkbox' ? 'checked' : 'value'}
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
      title: '材料名称',
      dataIndex: 'material_name',
      key: 'material_name',
      width: 150,
      editable: true,
      inputType: 'text',
      render: (text) => text || '-',
    },
    {
      title: '密度',
      dataIndex: 'density',
      key: 'density',
      width: 100,
      editable: true,
      inputType: 'number',
      render: (value) => value !== null && value !== undefined ? value : '-',
    },
    {
      title: '公斤价',
      dataIndex: 'kg_price',
      key: 'kg_price',
      width: 100,
      editable: true,
      inputType: 'number',
      render: (value) => value !== null && value !== undefined ? `¥${value}` : '-',
    },
    {
      title: '一层可选',
      dataIndex: 'layer_1_optional',
      key: 'layer_1_optional',
      width: 80,
      editable: true,
      inputType: 'checkbox',
      render: (value) => <Checkbox checked={value} disabled />,
    },
    {
      title: '二层可选',
      dataIndex: 'layer_2_optional',
      key: 'layer_2_optional',
      width: 80,
      editable: true,
      inputType: 'checkbox',
      render: (value) => <Checkbox checked={value} disabled />,
    },
    {
      title: '三层可选',
      dataIndex: 'layer_3_optional',
      key: 'layer_3_optional',
      width: 80,
      editable: true,
      inputType: 'checkbox',
      render: (value) => <Checkbox checked={value} disabled />,
    },
    {
      title: '四层可选',
      dataIndex: 'layer_4_optional',
      key: 'layer_4_optional',
      width: 80,
      editable: true,
      inputType: 'checkbox',
      render: (value) => <Checkbox checked={value} disabled />,
    },
    {
      title: '五层可选',
      dataIndex: 'layer_5_optional',
      key: 'layer_5_optional',
      width: 80,
      editable: true,
      inputType: 'checkbox',
      render: (value) => <Checkbox checked={value} disabled />,
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      editable: true,
      inputType: 'number',
      render: (value) => value || 0,
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      width: 150,
      editable: true,
      inputType: 'textarea',
      render: (text) => text || '-',
    },
    {
      title: '启用状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 100,
      editable: true,
      inputType: 'switch',
      render: (value, record) => {
        const editing = isEditing(record);
        return editing ? null : <Switch checked={value} disabled />;
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => {
        const editing = isEditing(record);
        return editing ? (
          <Space>
            <Button
              type="link"
              icon={<CheckOutlined />}
              onClick={() => save(record.key)}
              size="small"
            >
              保存
            </Button>
            <Button
              type="link"
              icon={<CloseOutlined />}
              onClick={cancel}
              size="small"
            >
              取消
            </Button>
          </Space>
        ) : (
          <Space>
            <Tooltip title="编辑">
              <Button
                type="link"
                icon={<EditOutlined />}
                disabled={editingKey !== ''}
                onClick={() => edit(record)}
                size="small"
              />
            </Tooltip>
            <Popconfirm
              title="确定删除吗？"
              onConfirm={() => handleDelete(record.key)}
              okText="确定"
              cancelText="取消"
            >
              <Tooltip title="删除">
                <Button
                  type="link"
                  icon={<DeleteOutlined />}
                  disabled={editingKey !== ''}
                  danger
                  size="small"
                />
              </Tooltip>
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
        inputType: col.inputType,
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
          <Title level={4}>报价材料管理</Title>
          
          {/* 搜索和操作栏 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Input
                ref={searchInputRef}
                placeholder="搜索材料名称或备注"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onPressEnter={handleSearch}
                suffix={
                  <Button
                    type="text"
                    icon={<SearchOutlined />}
                    onClick={handleSearch}
                    size="small"
                  />
                }
              />
            </Col>
            <Col span={16}>
              <Space>
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
                <Button
                  onClick={handleReset}
                  disabled={editingKey !== ''}
                >
                  重置
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        {/* 表格 */}
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
              },
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

export default QuoteMaterialManagement; 