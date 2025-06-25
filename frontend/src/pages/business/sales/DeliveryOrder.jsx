import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  message
} from 'antd';
import {
  PlusOutlined,
  EyeOutlined,
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

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

const DeliveryOrder = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);

  const mockData = [
    {
      id: '1',
      delivery_number: 'DO202412150001',
      customer_name: '上海塑料制品有限公司',
      order_number: 'SO202412150001',
      delivery_date: '2024-12-20',
      status: 'delivered',
      driver_name: '王师傅',
      vehicle_number: '沪A12345'
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
    in_transit: { color: 'blue', text: '运输中' },
    delivered: { color: 'success', text: '已送达' },
    signed: { color: 'success', text: '已签收' }
  };

  const columns = [
    {
      title: '送货单号',
      dataIndex: 'delivery_number',
      key: 'delivery_number',
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
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EyeOutlined />}>
            详情
          </Button>
        </Space>
      )
    }
  ];

  return (
    <PageContainer>
      <StyledCard>
        <Space>
          <Button type="primary" icon={<PlusOutlined />}>
            新增送货单
          </Button>
          <Button icon={<ReloadOutlined />} onClick={fetchData}>
            刷新
          </Button>
        </Space>
      </StyledCard>

      <StyledCard>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1000 }}
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

export default DeliveryOrder; 