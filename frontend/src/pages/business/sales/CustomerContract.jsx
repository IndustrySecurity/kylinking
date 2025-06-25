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
  EditOutlined,
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

const CustomerContract = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);

  const mockData = [
    {
      id: '1',
      contract_number: 'CT202412150001',
      customer_name: '上海塑料制品有限公司',
      contract_name: '2024年度产品供应合同',
      contract_amount: 1200000.00,
      signing_date: '2024-01-15',
      start_date: '2024-01-20',
      end_date: '2024-12-31',
      status: 'active',
      sales_person: '张三',
      payment_terms: '月结30天'
    },
    {
      id: '2',
      contract_number: 'CT202412150002',
      customer_name: '北京包装材料公司',
      contract_name: '包装材料采购框架协议',
      contract_amount: 800000.00,
      signing_date: '2024-03-10',
      start_date: '2024-03-15',
      end_date: '2025-03-14',
      status: 'active',
      sales_person: '李四',
      payment_terms: '货到付款'
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
    draft: { color: 'default', text: '草稿' },
    pending: { color: 'orange', text: '待签署' },
    active: { color: 'green', text: '生效中' },
    expired: { color: 'red', text: '已过期' },
    terminated: { color: 'gray', text: '已终止' }
  };

  const columns = [
    {
      title: '合同编号',
      dataIndex: 'contract_number',
      key: 'contract_number',
      width: 150
    },
    {
      title: '合同名称',
      dataIndex: 'contract_name',
      key: 'contract_name',
      width: 250
    },
    {
      title: '客户名称',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 200
    },
    {
      title: '合同金额',
      dataIndex: 'contract_amount',
      key: 'contract_amount',
      width: 120,
      render: (amount) => `¥${amount?.toLocaleString() || 0}`
    },
    {
      title: '签署日期',
      dataIndex: 'signing_date',
      key: 'signing_date',
      width: 120
    },
    {
      title: '合同期限',
      key: 'contract_period',
      width: 180,
      render: (_, record) => `${record.start_date} 至 ${record.end_date}`
    },
    {
      title: '销售员',
      dataIndex: 'sales_person',
      key: 'sales_person',
      width: 100
    },
    {
      title: '付款条款',
      dataIndex: 'payment_terms',
      key: 'payment_terms',
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
      width: 180,
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EyeOutlined />}>
            详情
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />}>
            编辑
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
            新增客户合同
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
          scroll={{ x: 1500 }}
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

export default CustomerContract;