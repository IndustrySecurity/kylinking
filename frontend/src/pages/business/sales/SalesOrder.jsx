import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Popconfirm,
  message,
  Tag,
  Drawer,
  Row,
  Col,
  Typography,
  Divider
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import dayjs from 'dayjs';

const { Option } = Select;
const { TextArea } = Input;
const { Text, Title } = Typography;

// 样式组件
const PageContainer = styled.div`
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
`;

const StyledCard = styled(Card)`
  margin-bottom: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const SalesOrder = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

  // 模拟数据
  const mockData = [
    {
      id: '1',
      order_number: 'SO202412150001',
      customer_name: '上海塑料制品有限公司',
      order_date: '2024-12-15',
      delivery_date: '2024-12-20',
      total_amount: 125000.00,
      status: 'pending',
      sales_person: '张三',
      contact_phone: '13800138001',
      delivery_address: '上海市浦东新区张江路123号',
      remark: '客户要求加急处理'
    },
    {
      id: '2',
      order_number: 'SO202412150002',
      customer_name: '北京包装材料公司',
      order_date: '2024-12-15',
      delivery_date: '2024-12-22',
      total_amount: 86500.00,
      status: 'confirmed',
      sales_person: '李四',
      contact_phone: '13900139001',
      delivery_address: '北京市朝阳区建国路456号',
      remark: ''
    }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // 模拟API调用
      setTimeout(() => {
        setData(mockData);
        setLoading(false);
      }, 1000);
    } catch (error) {
      message.error('获取数据失败');
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setCurrentRecord(null);
    form.resetFields();
    form.setFieldsValue({
      order_date: dayjs(),
      status: 'pending'
    });
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setCurrentRecord(record);
    form.setFieldsValue({
      ...record,
      order_date: dayjs(record.order_date),
      delivery_date: dayjs(record.delivery_date)
    });
    setModalVisible(true);
  };

  const handleDelete = async (record) => {
    try {
      message.success('删除成功');
      fetchData();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const orderData = {
        ...values,
        order_date: values.order_date ? values.order_date.format('YYYY-MM-DD') : null,
        delivery_date: values.delivery_date ? values.delivery_date.format('YYYY-MM-DD') : null
      };

      console.log('保存订单数据:', orderData);
      message.success(currentRecord ? '更新成功' : '创建成功');
      setModalVisible(false);
      fetchData();
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleViewDetail = (record) => {
    setCurrentRecord(record);
    setDetailDrawerVisible(true);
  };

  const statusConfig = {
    pending: { color: 'default', text: '待确认' },
    confirmed: { color: 'processing', text: '已确认' },
    in_production: { color: 'blue', text: '生产中' },
    ready_to_ship: { color: 'cyan', text: '待发货' },
    shipped: { color: 'success', text: '已发货' },
    completed: { color: 'success', text: '已完成' },
    cancelled: { color: 'error', text: '已取消' }
  };

  const columns = [
    {
      title: '订单号',
      dataIndex: 'order_number',
      key: 'order_number',
      width: 150
    },
    {
      title: '客户名称',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 200
    },
    {
      title: '订单日期',
      dataIndex: 'order_date',
      key: 'order_date',
      width: 120
    },
    {
      title: '交期',
      dataIndex: 'delivery_date',
      key: 'delivery_date',
      width: 120
    },
    {
      title: '订单金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 120,
      render: (amount) => `¥${amount?.toLocaleString() || 0}`
    },
    {
      title: '销售员',
      dataIndex: 'sales_person',
      key: 'sales_person',
      width: 100
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const config = statusConfig[status] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          {record.status === 'pending' && (
            <>
              <Button 
                type="link" 
                size="small" 
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定要删除这条记录吗？"
                onConfirm={() => handleDelete(record)}
                okText="确定"
                cancelText="取消"
              >
                <Button 
                  type="link" 
                  danger 
                  size="small"
                  icon={<DeleteOutlined />}
                >
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      )
    }
  ];

  return (
    <PageContainer>
      {/* 搜索区域 */}
      <StyledCard>
        <Form form={searchForm} layout="inline">
          <Form.Item name="order_number" label="订单号">
            <Input placeholder="请输入订单号" />
          </Form.Item>
          <Form.Item name="customer_name" label="客户名称">
            <Input placeholder="请输入客户名称" />
          </Form.Item>
          <Form.Item name="status" label="状态">
            <Select placeholder="请选择状态" style={{ width: 120 }} allowClear>
              <Option value="pending">待确认</Option>
              <Option value="confirmed">已确认</Option>
              <Option value="in_production">生产中</Option>
              <Option value="ready_to_ship">待发货</Option>
              <Option value="shipped">已发货</Option>
              <Option value="completed">已完成</Option>
              <Option value="cancelled">已取消</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" icon={<SearchOutlined />}>
              搜索
            </Button>
            <Button style={{ marginLeft: 8 }} icon={<ReloadOutlined />} onClick={fetchData}>
              重置
            </Button>
          </Form.Item>
        </Form>
      </StyledCard>

      {/* 操作区域 */}
      <StyledCard>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增订单
          </Button>
        </Space>
      </StyledCard>

      {/* 表格区域 */}
      <StyledCard>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
        />
      </StyledCard>

      {/* 新增/编辑模态框 */}
      <Modal
        title={currentRecord ? '编辑销售订单' : '新增销售订单'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="customer_name"
                label="客户名称"
                rules={[{ required: true, message: '请输入客户名称' }]}
              >
                <Input placeholder="请输入客户名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="sales_person"
                label="销售员"
                rules={[{ required: true, message: '请输入销售员' }]}
              >
                <Input placeholder="请输入销售员" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="order_date"
                label="订单日期"
                rules={[{ required: true, message: '请选择订单日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="delivery_date"
                label="交期"
                rules={[{ required: true, message: '请选择交期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="total_amount"
                label="订单金额"
                rules={[{ required: true, message: '请输入订单金额' }]}
              >
                <Input type="number" placeholder="请输入订单金额" addonAfter="元" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="contact_phone"
                label="联系电话"
              >
                <Input placeholder="请输入联系电话" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            name="delivery_address"
            label="交货地址"
          >
            <Input placeholder="请输入交货地址" />
          </Form.Item>
          <Form.Item
            name="remark"
            label="备注"
          >
            <TextArea rows={3} placeholder="请输入备注" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情抽屉 */}
      <Drawer
        title="销售订单详情"
        placement="right"
        onClose={() => setDetailDrawerVisible(false)}
        open={detailDrawerVisible}
        width={600}
      >
        {currentRecord && (
          <div>
            <Title level={4}>订单基本信息</Title>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Text strong>订单号：</Text>
                <Text>{currentRecord.order_number}</Text>
              </Col>
              <Col span={12}>
                <Text strong>客户名称：</Text>
                <Text>{currentRecord.customer_name}</Text>
              </Col>
              <Col span={12}>
                <Text strong>订单日期：</Text>
                <Text>{currentRecord.order_date}</Text>
              </Col>
              <Col span={12}>
                <Text strong>交期：</Text>
                <Text>{currentRecord.delivery_date}</Text>
              </Col>
              <Col span={12}>
                <Text strong>订单金额：</Text>
                <Text>¥{currentRecord.total_amount?.toLocaleString()}</Text>
              </Col>
              <Col span={12}>
                <Text strong>销售员：</Text>
                <Text>{currentRecord.sales_person}</Text>
              </Col>
              <Col span={12}>
                <Text strong>联系电话：</Text>
                <Text>{currentRecord.contact_phone}</Text>
              </Col>
              <Col span={12}>
                <Text strong>状态：</Text>
                <Tag color={statusConfig[currentRecord.status]?.color}>
                  {statusConfig[currentRecord.status]?.text}
                </Tag>
              </Col>
            </Row>
            <Divider />
            <Title level={5}>交货地址</Title>
            <Text>{currentRecord.delivery_address}</Text>
            {currentRecord.remark && (
              <>
                <Divider />
                <Title level={5}>备注</Title>
                <Text>{currentRecord.remark}</Text>
              </>
            )}
          </div>
        )}
      </Drawer>
    </PageContainer>
  );
};

export default SalesOrder; 