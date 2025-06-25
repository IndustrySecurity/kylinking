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
  Tag
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

const { Option } = Select;
const { TextArea } = Input;

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

const DeliveryNotice = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [form] = Form.useForm();

  // 模拟数据
  const mockData = [
    {
      id: '1',
      notice_number: 'DN202412150001',
      customer_name: '上海塑料制品有限公司',
      order_number: 'SO202412150001',
      delivery_date: '2024-12-20',
      status: 'pending',
      driver_name: '王师傅',
      vehicle_number: '沪A12345',
      contact_phone: '13800138001'
    }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      setTimeout(() => {
        setData(mockData);
        setLoading(false);
      }, 1000);
    } catch (error) {
      message.error('获取数据失败');
      setLoading(false);
    }
  };

  const statusConfig = {
    pending: { color: 'default', text: '待发货' },
    confirmed: { color: 'processing', text: '已确认' },
    in_transit: { color: 'blue', text: '运输中' },
    delivered: { color: 'success', text: '已送达' },
    cancelled: { color: 'error', text: '已取消' }
  };

  const columns = [
    {
      title: '通知单号',
      dataIndex: 'notice_number',
      key: 'notice_number',
      width: 150
    },
    {
      title: '客户名称',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 200
    },
    {
      title: '订单号',
      dataIndex: 'order_number',
      key: 'order_number',
      width: 150
    },
    {
      title: '送货日期',
      dataIndex: 'delivery_date',
      key: 'delivery_date',
      width: 120
    },
    {
      title: '司机',
      dataIndex: 'driver_name',
      key: 'driver_name',
      width: 100
    },
    {
      title: '车牌号',
      dataIndex: 'vehicle_number',
      key: 'vehicle_number',
      width: 120
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
          <Button type="link" size="small" icon={<EyeOutlined />}>
            详情
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />}>
            编辑
          </Button>
          <Popconfirm title="确定要删除吗？" okText="确定" cancelText="取消">
            <Button type="link" danger size="small" icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <PageContainer>
      <StyledCard>
        <Form layout="inline">
          <Form.Item name="notice_number" label="通知单号">
            <Input placeholder="请输入通知单号" />
          </Form.Item>
          <Form.Item name="customer_name" label="客户名称">
            <Input placeholder="请输入客户名称" />
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

      <StyledCard>
        <Space>
          <Button type="primary" icon={<PlusOutlined />}>
            新增送货通知单
          </Button>
        </Space>
      </StyledCard>

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
    </PageContainer>
  );
};

export default DeliveryNotice; 