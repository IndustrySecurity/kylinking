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
import { getLossTypes, createLossType, updateLossType, deleteLossType } from '../../../../api/production/production-archive/lossTypeApi';

const { Title } = Typography;

const LossTypeManagement = () => {
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
      const response = await getLossTypes({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      // 正确处理后端响应格式
      if (response.data && response.data.success) {
        const responseData = response.data.data || {};
        // 修正字段名：后端返回的是items而不是loss_types
        const { items, total, current_page } = responseData;
        
        // 安全检查，确保items是数组
        const lossTypesArray = Array.isArray(items) ? items : [];
        
        // 为每行数据添加key
        const dataWithKeys = lossTypesArray.map((item, index) => ({
          ...item,
          key: item.id || `temp_${index}`
        }));
        
        setData(dataWithKeys);
        setPagination(prev => ({
          ...prev,
          total: total || 0,
          current: current_page || 1
        }));
      } else {
        console.warn('报损类型 API 响应格式异常:', response.data);
        // 尝试处理不同的响应格式
        if (response.data && Array.isArray(response.data)) {
          const dataWithKeys = response.data.map((item, index) => ({
            ...item,
            key: item.id || `temp_${index}`
          }));
          setData(dataWithKeys);
        } else {
          // 如果数据格式异常，设置空数据而不是报错
          setData([]);
          console.error('数据格式异常，已设置为空数据');
        }
      }
    } catch (error) {
      console.error('加载报损类型数据失败:', error);
      message.error('加载数据失败：' + (error.response?.data?.error || error.message));
      setData([]); // 确保在错误情况下设置空数据
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
  const handleTableChange = (newPagination, filters, sorter) => {
    setPagination(newPagination);
    
    // 处理排序参数
    let sortParams = {};
    if (sorter && sorter.field && sorter.order) {
      const order = sorter.order === 'ascend' ? 'asc' : 'desc';
      sortParams.sort_by = sorter.field;
      sortParams.sort_order = order;
    }
    
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize,
      ...sortParams
    });
  };

  // 开始编辑
  const edit = (record) => {
    form.setFieldsValue({
      loss_type_name: '',
      is_assessment: false,
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
          response = await updateLossType(item.id, row);
        } else {
          // 创建新记录
          response = await createLossType(row);
        }

        // 正确处理后端响应格式
        if (response.data.success) {
          setEditingKey('');
          message.success('保存成功');
          // 总是重新加载数据以确保数据同步
          loadData({ sort_by: 'sort_order', sort_order: 'asc' });
        } else {
          throw new Error(response.data.message || '保存失败');
        }
      }
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        console.error('保存失败:', error);
        const errorMsg = error.response?.data?.message || error.response?.data?.error || error.message || '保存失败';
        message.error('保存失败：' + errorMsg);
      }
    }
  };

  // 删除记录
  const handleDelete = async (key) => {
    try {
      const record = data.find(item => item.key === key);
      
      if (record.id && !record.id.startsWith('temp_')) {
        // 删除服务器记录
        const response = await deleteLossType(record.id);
        if (response.data.success) {
          message.success('删除成功');
        }
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
      loss_type_name: '',
      is_assessment: false,
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
        // 为排序字段使用整数限制的InputNumber
        if (dataIndex === 'sort_order') {
          inputNode = <InputNumber 
            min={0} 
            precision={0} 
            style={{ width: '100%' }}
            parser={(value) => value ? value.replace(/[^\d]/g, '') : ''}
          />;
        } else {
          inputNode = <InputNumber min={0} style={{ width: '100%' }} />;
        }
        break;
      case 'switch':
        inputNode = <Switch />;
        break;
      case 'checkbox':
        inputNode = <Checkbox />;
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
                required: dataIndex === 'loss_type_name',
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
      title: '报损类型名称',
      dataIndex: 'loss_type_name',
      key: 'loss_type_name',
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
      title: '工序',
      dataIndex: 'process_id',
      key: 'process_id',
      width: 120,
      render: () => '-', // 暂时留空
    },
    {
      title: '报损分类',
      dataIndex: 'loss_category_id',
      key: 'loss_category_id',
      width: 120,
      render: () => '-', // 暂时留空
    },
    {
      title: '是否考核',
      dataIndex: 'is_assessment',
      key: 'is_assessment',
      width: 100,
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
      align: 'center',
      sorter: true,
      defaultSortOrder: 'ascend'
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
            <Title level={4} style={{ margin: 0 }}>报损类型管理</Title>
          </Col>
          <Col>
            <Space>
              <Input
                ref={searchInputRef}
                placeholder="搜索报损类型名称"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onPressEnter={handleSearch}
                style={{ width: 200 }}
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
                新增报损类型
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

export default LossTypeManagement; 