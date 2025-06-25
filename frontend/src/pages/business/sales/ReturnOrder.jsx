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

const ReturnOrder = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);

  const mockData = [
    {
      id: '1',
      return_order_number: 'RO202412150001',
      customer_name: '上海塑料制品有限公司',
      return_notice_number: 'RN202412150001',
      return_reason: '质量问题',
      return_date: '2024-12-25',
      status: 'received',
      return_amount: 5000.00,
      received_date: '2024-12-26'
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
    pending: { color: 'default', text: '待收货' },
    received: { color: 'processing', text: '已收货' },
    checked: { color: 'blue', text: '已检验' },
    completed: { color: 'success', text: '已完成' },
    rejected: { color: 'error', text: '已拒绝' }
  };

  const columns = [
    {
      title: '退货单号',
      dataIndex: 'return_order_number',
      key: 'return_order_number',
      width: 150
    },
    {
      title: '客户名称',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 200
    },
    {
      title: '退货通知单号',
      dataIndex: 'return_notice_number',
      key: 'return_notice_number',
      width: 150
    },
    {
      title: '退货原因',
      dataIndex: 'return_reason',
      key: 'return_reason',
      width: 150
    },
    {
      title: '退货日期',
      dataIndex: 'return_date',
      key: 'return_date',
      width: 120
    },
    {
      title: '实际收货日期',
      dataIndex: 'received_date',
      key: 'received_date',
      width: 120
    },
    {
      title: '退货金额',
      dataIndex: 'return_amount',
      key: 'return_amount',
      width: 120,
      render: (amount) => `¥${amount?.toLocaleString() || 0}`
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
            新增退货单
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
          scroll={{ x: 1400 }}
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

export default ReturnOrder; 