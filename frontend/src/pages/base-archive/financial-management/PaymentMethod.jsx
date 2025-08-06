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
  Typography,
  App
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SaveOutlined,
  SearchOutlined,
  CreditCardOutlined
} from '@ant-design/icons';
import { paymentMethodApi } from '../../../api/base-archive/financial-management/paymentMethod';

const { Search } = Input;
const { Title } = Typography;

const PaymentMethod = () => {
  const { message } = App.useApp();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
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

      const result = await paymentMethodApi.getPaymentMethods(params);
      // 正确处理后端响应格式
      if (result.data && result.data.success) {
        const { payment_methods, total, current_page } = result.data.data;
        setData(payment_methods || []);
        setPagination({
          current: current_page || page,
          pageSize,
          total: total || 0,
        });
      }
    } catch (error) {
      console.error('获取付款方式列表失败:', error);
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
      payment_name: '',
      cash_on_delivery: false,
      monthly_settlement: false,
      next_month_settlement: false,
      cash_on_delivery_days: 0,
      monthly_settlement_days: 0,
      monthly_reconciliation_day: 0,
      next_month_settlement_count: 0,
      monthly_payment_day: 0,
      description: '',
      sort_order: 0,
      is_enabled: true,
      ...record,
    });
    setEditingKey(record.id);
  };

  // 处理付款方式类型变化
  const handlePaymentTypeChange = (type, checked, record) => {
    const currentValues = form.getFieldsValue();
    
    if (checked) {
      // 如果选中，则取消其他两个选项并清空对应字段
      const updates = {
        cash_on_delivery: type === 'cash_on_delivery',
        monthly_settlement: type === 'monthly_settlement',
        next_month_settlement: type === 'next_month_settlement'
      };
      
      // 清空所有相关字段，然后根据选择的类型保留对应字段
      updates.cash_on_delivery_days = 0;
      updates.monthly_settlement_days = 0;
      updates.monthly_reconciliation_day = 0;
      updates.next_month_settlement_count = 0;
      updates.monthly_payment_day = 0;
      
      form.setFieldsValue(updates);
    } else {
      // 如果取消选中，检查是否至少有一个被选中
      const otherTypes = ['cash_on_delivery', 'monthly_settlement', 'next_month_settlement'].filter(t => t !== type);
      const hasOtherSelected = otherTypes.some(t => currentValues[t]);
      
      if (!hasOtherSelected) {
        message.warning('必须选择一种付款方式类型');
        return false; // 阻止取消选中
      } else {
        // 允许取消选中，并清空对应字段
        const updates = {};
        updates[type] = false;
        
        // 清空对应的字段
        if (type === 'cash_on_delivery') {
          updates.cash_on_delivery_days = 0;
        } else if (type === 'monthly_settlement') {
          updates.monthly_settlement_days = 0;
          updates.monthly_reconciliation_day = 0;
        } else if (type === 'next_month_settlement') {
          updates.next_month_settlement_count = 0;
          updates.monthly_payment_day = 0;
        }
        
        form.setFieldsValue(updates);
      }
    }
    
    return true;
  };

  const cancel = () => {
    setEditingKey('');
  };

  // 保存编辑
  const save = async (id) => {
    try {
      const row = await form.validateFields();
      
      // 验证付款方式类型：必须选择一个且只能选择一个
      const paymentTypes = [row.cash_on_delivery, row.monthly_settlement, row.next_month_settlement];
      const selectedCount = paymentTypes.filter(Boolean).length;
      
      if (selectedCount === 0) {
        message.error('请选择一种付款方式类型（货到付款、月结或次月结）');
        return;
      }
      
      if (selectedCount > 1) {
        message.error('只能选择一种付款方式类型');
        return;
      }
      
      const newData = [...data];
      const index = newData.findIndex((item) => id === item.id);

      if (index > -1) {
        const item = newData[index];
        
        // 如果是新增的临时记录
        if (id.startsWith('temp_')) {
          await paymentMethodApi.createPaymentMethod(row);
          message.success('创建成功');
          setEditingKey('');
          fetchData(pagination.current, pagination.pageSize, searchText);
        } else {
          // 更新现有记录
          await paymentMethodApi.updatePaymentMethod(id, row);
          message.success('更新成功');
          setEditingKey('');
          fetchData(pagination.current, pagination.pageSize, searchText);
        }
      }
    } catch (errInfo) {
      // 表单验证失败，不做处理
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

      await paymentMethodApi.deletePaymentMethod(id);
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
      payment_name: '',
      cash_on_delivery: true, // 默认选择货到付款
      monthly_settlement: false,
      next_month_settlement: false,
      cash_on_delivery_days: 0,
      monthly_settlement_days: 0,
      monthly_reconciliation_day: 0,
      next_month_settlement_count: 0,
      monthly_payment_day: 0,
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
    // 判断是否需要根据付款方式类型控制禁用状态
    const isControlledField = [
      'cash_on_delivery_days',
      'monthly_settlement_days', 
      'monthly_reconciliation_day',
      'next_month_settlement_count', 
      'monthly_payment_day'
    ].includes(dataIndex);

    return (
      <td {...restProps}>
        {editing ? (
          isControlledField ? (
            // 对于需要控制的字段，使用Form.Item的shouldUpdate来实时监听
            <Form.Item
              shouldUpdate={(prevValues, currentValues) => {
                return prevValues.cash_on_delivery !== currentValues.cash_on_delivery ||
                       prevValues.monthly_settlement !== currentValues.monthly_settlement ||
                       prevValues.next_month_settlement !== currentValues.next_month_settlement;
              }}
              style={{ margin: 0 }}
            >
                             {({ getFieldValue, setFieldsValue }) => {
                 const isCashOnDelivery = getFieldValue('cash_on_delivery');
                 const isMonthlySettlement = getFieldValue('monthly_settlement');
                 const isNextMonthSettlement = getFieldValue('next_month_settlement');
                 
                 let disabled = false;
                 
                 // 货到付款日：只有选择货到付款时才能编辑
                 if (dataIndex === 'cash_on_delivery_days') {
                   disabled = !isCashOnDelivery;
                   // 如果禁用且当前值不为0，则重置为0
                   if (disabled && getFieldValue(dataIndex) !== 0) {
                     setFieldsValue({ [dataIndex]: 0 });
                   }
                 }
                 // 月结天数、每月对账日：只有选择月结时才能编辑
                 else if (dataIndex === 'monthly_settlement_days' || dataIndex === 'monthly_reconciliation_day') {
                   disabled = !isMonthlySettlement;
                   // 如果禁用且当前值不为0，则重置为0
                   if (disabled && getFieldValue(dataIndex) !== 0) {
                     setFieldsValue({ [dataIndex]: 0 });
                   }
                 }
                 // 次月月结数、每月付款日：只有选择次月结时才能编辑
                 else if (dataIndex === 'next_month_settlement_count' || dataIndex === 'monthly_payment_day') {
                   disabled = !isNextMonthSettlement;
                   // 如果禁用且当前值不为0，则重置为0
                   if (disabled && getFieldValue(dataIndex) !== 0) {
                     setFieldsValue({ [dataIndex]: 0 });
                   }
                 }
                
                let inputNode;
                if (inputType === 'number') {
                  inputNode = <InputNumber style={{ width: '100%' }} min={0} max={31} disabled={disabled} />;
                } else if (inputType === 'switch') {
                  inputNode = <Switch disabled={disabled} />;
                } else {
                  inputNode = <Input disabled={disabled} />;
                }
                
                return (
                  <Form.Item
                    name={dataIndex}
                    style={{ margin: 0 }}
                    rules={[
                      {
                        required: ['payment_name'].includes(dataIndex),
                        message: `请输入${title}!`,
                      },
                      ...(dataIndex === 'payment_name' ? [{
                        max: 100,
                        message: '付款方式名称不能超过100个字符'
                      }] : [])
                    ]}
                  >
                    {inputNode}
                  </Form.Item>
                );
              }}
            </Form.Item>
          ) : (
            // 对于普通字段，直接使用Form.Item
            <Form.Item
              name={dataIndex}
              style={{ margin: 0 }}
              rules={[
                {
                  required: ['payment_name'].includes(dataIndex),
                  message: `请输入${title}!`,
                },
                ...(dataIndex === 'payment_name' ? [{
                  max: 100,
                  message: '付款方式名称不能超过100个字符'
                }] : [])
              ]}
            >
              {inputType === 'number' ? (
                <InputNumber style={{ width: '100%' }} min={0} max={31} />
              ) : inputType === 'switch' ? (
                <Switch />
              ) : (
                <Input />
              )}
            </Form.Item>
          )
        ) : (
          children
        )}
      </td>
    );
  };

  // 表格列定义
  const columns = [
    {
      title: '付款方式',
      dataIndex: 'payment_name',
      key: 'payment_name',
      width: 150,
      editable: true,
    },
    {
      title: '货到付款',
      dataIndex: 'cash_on_delivery',
      key: 'cash_on_delivery',
      width: 80,
      align: 'center',
      editable: true,
      render: (value, record) => {
        if (isEditing(record)) {
          return (
            <Form.Item
              name="cash_on_delivery"
              valuePropName="checked"
              style={{ margin: 0 }}
            >
              <Switch
                size="small"
                onChange={(checked) => {
                  handlePaymentTypeChange('cash_on_delivery', checked, record);
                }}
              />
            </Form.Item>
          );
        }
        return <Switch checked={value} disabled size="small" />;
      },
    },
    {
      title: '月结',
      dataIndex: 'monthly_settlement',
      key: 'monthly_settlement',
      width: 60,
      align: 'center',
      editable: true,
      render: (value, record) => {
        if (isEditing(record)) {
          return (
            <Form.Item
              name="monthly_settlement"
              valuePropName="checked"
              style={{ margin: 0 }}
            >
              <Switch
                size="small"
                onChange={(checked) => {
                  handlePaymentTypeChange('monthly_settlement', checked, record);
                }}
              />
            </Form.Item>
          );
        }
        return <Switch checked={value} disabled size="small" />;
      },
    },
    {
      title: '次月结',
      dataIndex: 'next_month_settlement',
      key: 'next_month_settlement',
      width: 70,
      align: 'center',
      editable: true,
      render: (value, record) => {
        if (isEditing(record)) {
          return (
            <Form.Item
              name="next_month_settlement"
              valuePropName="checked"
              style={{ margin: 0 }}
            >
              <Switch
                size="small"
                onChange={(checked) => {
                  handlePaymentTypeChange('next_month_settlement', checked, record);
                }}
              />
            </Form.Item>
          );
        }
        return <Switch checked={value} disabled size="small" />;
      },
    },
    {
      title: '货到付款日',
      dataIndex: 'cash_on_delivery_days',
      key: 'cash_on_delivery_days',
      width: 90,
      align: 'center',
      editable: true,
    },
    {
      title: '月结天数',
      dataIndex: 'monthly_settlement_days',
      key: 'monthly_settlement_days',
      width: 80,
      align: 'center',
      editable: true,
    },
    {
      title: '每月对账日',
      dataIndex: 'monthly_reconciliation_day',
      key: 'monthly_reconciliation_day',
      width: 90,
      align: 'center',
      editable: true,
    },
    {
      title: '次月月结数',
      dataIndex: 'next_month_settlement_count',
      key: 'next_month_settlement_count',
      width: 90,
      align: 'center',
      editable: true,
    },
    {
      title: '每月付款日',
      dataIndex: 'monthly_payment_day',
      key: 'monthly_payment_day',
      width: 90,
      align: 'center',
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
      width: 60,
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
    
    // 付款方式类型的开关已经在render中处理了，不需要onCell
    if (['cash_on_delivery', 'monthly_settlement', 'next_month_settlement'].includes(col.dataIndex)) {
      return col;
    }
    
    let inputType = 'text';
    if (['cash_on_delivery_days', 'monthly_settlement_days', 'monthly_reconciliation_day', 
         'next_month_settlement_count', 'monthly_payment_day', 'sort_order'].includes(col.dataIndex)) {
      inputType = 'number';
    } else if (['is_enabled'].includes(col.dataIndex)) {
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
                <CreditCardOutlined style={{ marginRight: 8 }} />
                付款方式管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Input
                  ref={searchInputRef}
                  placeholder="搜索付款方式名称、描述"
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
            scroll={{ x: 1800 }}
            size="small"
          />
        </Form>
      </Card>
    </div>
  );
};

export default PaymentMethod; 