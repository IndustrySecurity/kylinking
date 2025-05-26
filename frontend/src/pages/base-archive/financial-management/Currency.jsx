import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Switch,
  Space,
  Popconfirm,
  message,
  Card,
  Row,
  Col,
  Tag
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, StarOutlined } from '@ant-design/icons';
import { currencyApi } from '../../../api/currency';

const Currency = () => {
  const [loading, setLoading] = useState(false);
  const [currencies, setCurrencies] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  useEffect(() => {
    fetchData();
  }, [pagination.current, pagination.pageSize]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await currencyApi.getCurrencies({
        page: pagination.current,
        per_page: pagination.pageSize
      });
      
      if (response.success) {
        setCurrencies(response.data.currencies);
        setPagination({
          ...pagination,
          total: response.data.total
        });
      }
    } catch (error) {
      message.error('获取币别列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingId(record.id);
    form.setFieldsValue({
      ...record,
      exchange_rate: parseFloat(record.exchange_rate)
    });
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await currencyApi.deleteCurrency(id);
      message.success('删除成功');
      fetchData();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSetBase = async (id) => {
    try {
      await currencyApi.setBaseCurrency(id);
      message.success('设置本位币成功');
      fetchData();
    } catch (error) {
      message.error('设置本位币失败');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingId) {
        await currencyApi.updateCurrency(editingId, values);
        message.success('更新成功');
      } else {
        await currencyApi.createCurrency(values);
        message.success('创建成功');
      }
      
      setModalVisible(false);
      fetchData();
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  const handleTableChange = (pagination) => {
    setPagination({
      ...pagination,
      current: pagination.current,
      pageSize: pagination.pageSize
    });
  };

  const columns = [
    {
      title: '币别代码',
      dataIndex: 'currency_code',
      key: 'currency_code',
      width: 120,
      render: (text, record) => (
        <span>
          {text}
          {record.is_base_currency && (
            <Tag color="gold" style={{ marginLeft: 8 }}>
              <StarOutlined /> 本位币
            </Tag>
          )}
        </span>
      )
    },
    {
      title: '币别名称',
      dataIndex: 'currency_name',
      key: 'currency_name',
      width: 150
    },
    {
      title: '货币符号',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      align: 'center'
    },
    {
      title: '汇率',
      dataIndex: 'exchange_rate',
      key: 'exchange_rate',
      width: 120,
      align: 'right',
      render: (value) => parseFloat(value).toFixed(4)
    },
    {
      title: '小数位数',
      dataIndex: 'decimal_places',
      key: 'decimal_places',
      width: 100,
      align: 'center'
    },
    {
      title: '状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      align: 'center',
      render: (enabled) => (
        <Tag color={enabled ? 'green' : 'red'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      align: 'center'
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          {!record.is_base_currency && (
            <Button
              type="link"
              size="small"
              icon={<StarOutlined />}
              onClick={() => handleSetBase(record.id)}
            >
              设为本位币
            </Button>
          )}
          {!record.is_base_currency && (
            <Popconfirm
              title="确定删除这个币别吗？"
              onConfirm={() => handleDelete(record.id)}
              okText="是"
              cancelText="否"
            >
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
              >
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  return (
    <Card title="币别管理">
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAdd}
        >
          新增币别
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={currencies}
        loading={loading}
        rowKey="id"
        pagination={{
          ...pagination,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条记录`
        }}
        onChange={handleTableChange}
        scroll={{ x: 1200 }}
      />

      <Modal
        title={editingId ? '编辑币别' : '新增币别'}
        open={modalVisible}
        onOk={handleOk}
        onCancel={() => setModalVisible(false)}
        width={600}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            exchange_rate: 1.0000,
            decimal_places: 2,
            sort_order: 0,
            is_enabled: true,
            is_base_currency: false
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="币别代码"
                name="currency_code"
                rules={[
                  { required: true, message: '请输入币别代码' },
                  { max: 10, message: '币别代码不能超过10个字符' }
                ]}
              >
                <Input placeholder="如：CNY、USD" style={{ textTransform: 'uppercase' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="币别名称"
                name="currency_name"
                rules={[
                  { required: true, message: '请输入币别名称' },
                  { max: 100, message: '币别名称不能超过100个字符' }
                ]}
              >
                <Input placeholder="如：人民币、美元" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="货币符号"
                name="symbol"
                rules={[{ max: 10, message: '货币符号不能超过10个字符' }]}
              >
                <Input placeholder="如：¥、$" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="汇率"
                name="exchange_rate"
                rules={[
                  { required: true, message: '请输入汇率' },
                  { type: 'number', min: 0.0001, message: '汇率必须大于0' }
                ]}
              >
                <InputNumber
                  placeholder="1.0000"
                  precision={4}
                  min={0.0001}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="小数位数"
                name="decimal_places"
                rules={[
                  { required: true, message: '请输入小数位数' },
                  { type: 'number', min: 0, max: 6, message: '小数位数在0-6之间' }
                ]}
              >
                <InputNumber min={0} max={6} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="排序"
                name="sort_order"
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="是否启用"
                name="is_enabled"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="是否本位币"
                name="is_base_currency"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="描述"
            name="description"
          >
            <Input.TextArea rows={3} placeholder="币别描述" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default Currency; 