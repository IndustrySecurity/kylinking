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
  Select,
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
  CloseOutlined,
  AppstoreOutlined
} from '@ant-design/icons';
import { productCategoryApi } from '../../../api/base-archive/base-category/productCategory';

const { Title } = Typography;
const { Option } = Select;

const ProductCategoryManagement = () => {
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
    try {
      setLoading(true);
      const response = await productCategoryApi.getProductCategories({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      if (response.data.success) {
        const { product_categories, total, current_page } = response.data.data;
        
        const dataWithKeys = product_categories.map((item, index) => ({
          ...item,
          key: item.id || `temp-${index}`,
          index: (current_page - 1) * pagination.pageSize + index + 1
        }));
        
        setData(dataWithKeys);
        setPagination(prev => ({
          ...prev,
          current: current_page,
          total: total
        }));
      }
    } catch (error) {
      console.error('Load data error:', error);
      message.error('加载数据失败：' + (error.response?.data?.error || error.message));
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
      subject_name: '',
      is_blown_film: false,
      delivery_days: null,
      description: '',
      sort_order: 0,
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
          response = await productCategoryApi.updateProductCategory(item.id, row);
        } else {
          // 创建新记录
          response = await productCategoryApi.createProductCategory(row);
        }

        // 正确处理后端响应格式
        if (response.data.success) {
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
      console.error('Save error:', error);
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        message.error('保存失败：' + (error.response?.data?.error || error.message));
      }
    }
  };

  // 删除记录
  const handleDelete = async (key) => {
    try {
      const record = data.find(item => item.key === key);
      
      if (record.id && !record.id.startsWith('temp_')) {
        // 删除服务器记录
        const response = await productCategoryApi.deleteProductCategory(record.id);
        if (response.data.success) {
          message.success('删除成功');
        }
      }
      
      // 删除本地记录
      const newData = data.filter(item => item.key !== key);
      setData(newData);
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.error || error.message));
    }
  };

  // 添加新行
  const handleAdd = () => {
    const newKey = `temp_${Date.now()}`;
    const newData = {
      key: newKey,
      category_name: '',
      subject_name: '',
      is_blown_film: false,
      delivery_days: null,
      description: '',
      sort_order: 0,
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
      case 'switch':
        inputNode = <Switch />;
        break;
      case 'checkbox':
        inputNode = <Checkbox />;
        break;
      case 'select':
        inputNode = (
          <Select placeholder="请选择科目名称" allowClear>
            {/* 这里可以添加科目选项，当前先留空 */}
          </Select>
        );
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

  // 表格列配置
  const columns = [
    {
      title: '产品分类',
      dataIndex: 'category_name',
      key: 'category_name',
      width: 200,
      editable: true,
      render: (text, record) => {
        const editable = isEditing(record);
        return editable ? text : (
          <span style={{ fontWeight: 500 }}>{text}</span>
        );
      }
    },
    {
      title: '科目名称',
      dataIndex: 'subject_name',
      key: 'subject_name',
      width: 150,
      editable: true,
      inputType: 'select',
      render: (text) => text || '-'
    },
    {
      title: '是否吹膜',
      dataIndex: 'is_blown_film',
      key: 'is_blown_film',
      width: 100,
      editable: true,
      inputType: 'checkbox',
      align: 'center',
      render: (value, record) => {
        const editable = isEditing(record);
        return editable ? value : (
          <Checkbox 
            checked={value} 
            disabled 
          />
        );
      }
    },
    {
      title: '交货天数',
      dataIndex: 'delivery_days',
      key: 'delivery_days',
      width: 100,
      editable: true,
      inputType: 'number',
      align: 'center',
      render: (value) => value || '-'
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 200,
      editable: true,
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
              <Title level={4} style={{ margin: 0 }}>
                <AppstoreOutlined style={{ marginRight: 8 }} />
                产品分类管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索产品分类名称、科目名称或描述"
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
            rowKey="key"
            rowClassName="editable-row"
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) =>
                `第 ${range[0]}-${range[1]} 条/共 ${total} 条`,
              onChange: handleTableChange,
              onShowSizeChange: handleTableChange,
            }}
            loading={loading}
            scroll={{ x: 1400 }}
            size="small"
          />
        </Form>
      </Card>
    </div>
  );
};

export default ProductCategoryManagement; 