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
  Tooltip
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
  AppstoreOutlined,
  ExportOutlined
} from '@ant-design/icons';
import { inkOptionApi } from '../../../api/base-archive/production-config/inkOption';

const { Title } = Typography;

const InkOptionManagement = () => {
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
      const response = await inkOptionApi.getInkOptions({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      // 正确处理后端响应格式
      if (response.data.success) {
        const { ink_options, total, current_page } = response.data.data;
        
        // 为每行数据添加key
        const dataWithKeys = ink_options.map((item, index) => ({
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
      option_name: '',
      sort_order: 0,
      is_enabled: true,
      description: '',
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
          response = await inkOptionApi.updateInkOption(item.id, row);
        } else {
          // 创建新记录
          response = await inkOptionApi.createInkOption(row);
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
        const response = await inkOptionApi.deleteInkOption(record.id);
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
      option_name: '',
      sort_order: 0,
      is_enabled: true,
      description: '',
      created_by_name: '',
      created_at: '',
      updated_by_name: '',
      updated_at: ''
    };
    
    setData([newData, ...data]);
    edit(newData);
  };

  // 导出功能
  const handleExport = () => {
    message.info('导出功能开发中...');
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
                required: ['option_name'].includes(dataIndex),
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
      title: '选项名称',
      dataIndex: 'option_name',
      key: 'option_name',
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
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
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
                油墨选项管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索选项名称或描述"
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
                  新建
                </Button>
                <Button 
                  icon={<ExportOutlined />}
                  onClick={handleExport}
                  disabled={editingKey !== ''}
                >
                  导出
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

export default InkOptionManagement; 