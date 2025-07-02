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
  ColorPicker,
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
  BgColorsOutlined
} from '@ant-design/icons';
import { colorCardApi } from '../../../../api/production/production-archive/colorCard';

const { Title } = Typography;

const ColorCardManagement = () => {
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
      const response = await colorCardApi.getColorCards({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      // 正确处理后端响应格式
      if (response.data.success) {
        const { color_cards, total, current_page } = response.data.data;
        
        // 为每行数据添加key
        const dataWithKeys = color_cards.map((item, index) => ({
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
      color_code: '',
      color_name: '',
      color_value: '#000000',
      remarks: '',
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
        
        // 处理颜色值格式
        if (row.color_value && typeof row.color_value === 'object') {
          // 如果是ColorPicker返回的对象，转换为十六进制字符串
          row.color_value = row.color_value.toHexString ? row.color_value.toHexString() : '#000000';
        }
        
        const updatedItem = { ...item, ...row };
        
        // 调用API保存
        let response;
        if (item.id && !item.id.startsWith('temp_')) {
          // 更新现有记录
          response = await colorCardApi.updateColorCard(item.id, row);
        } else {
          // 创建新记录
          response = await colorCardApi.createColorCard(row);
        }

        // 正确处理后端响应格式
        if (response.data.success) {
          setEditingKey('');
          message.success('保存成功');
          // 如果修改了排序字段，重新加载数据以应用排序
          if (row.sort_order !== undefined) {
            loadData({ sort_by: 'sort_order', sort_order: 'asc' });
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
        const response = await colorCardApi.deleteColorCard(record.id);
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
      color_code: '',
      color_name: '',
      color_value: '#000000',
      remarks: '',
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
      case 'color':
        inputNode = (
          <ColorPicker 
            showText 
            format="hex"
            style={{ width: '100%' }}
            onChange={(color) => {
              // 确保颜色值以十六进制字符串形式保存
              const hexValue = color.toHexString();
              form.setFieldValue(dataIndex, hexValue);
            }}
          />
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
                required: ['color_name', 'color_value'].includes(dataIndex),
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
      title: '色卡编号',
      dataIndex: 'color_code',
      key: 'color_code',
      width: 150,
      editable: false,
      render: (text, record) => {
        return (
          <span style={{ fontWeight: 500 }}>
            {text || '自动生成'}
          </span>
        );
      }
    },
    {
      title: '色卡名称',
      dataIndex: 'color_name',
      key: 'color_name',
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
      title: '色值',
      dataIndex: 'color_value',
      key: 'color_value',
      width: 120,
      editable: true,
      inputType: 'color',
      align: 'center',
      render: (colorValue, record) => {
        const editable = isEditing(record);
        if (editable) {
          return colorValue;
        }
        return (
          <Space>
            <div 
              style={{
                width: 20,
                height: 20,
                backgroundColor: colorValue,
                border: '1px solid #d9d9d9',
                borderRadius: 4,
                display: 'inline-block'
              }}
            />
            <span style={{ fontSize: '12px', color: '#666' }}>{colorValue}</span>
          </Space>
        );
      }
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
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
                <BgColorsOutlined style={{ marginRight: 8 }} />
                色卡管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索色卡名称、编号或备注"
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

export default ColorCardManagement; 