import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  message,
  Progress
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

const MonthlyPlan = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);

  const mockData = [
    {
      id: '1',
      plan_number: 'MP202412',
      year: 2024,
      month: 12,
      sales_person: '张三',
      department: '销售一部',
      target_amount: 500000.00,
      actual_amount: 425000.00,
      completion_rate: 85.0,
      target_orders: 20,
      actual_orders: 18,
      status: 'in_progress',
      create_date: '2024-11-25'
    },
    {
      id: '2',
      plan_number: 'MP202411',
      year: 2024,
      month: 11,
      sales_person: '李四',
      department: '销售二部',
      target_amount: 450000.00,
      actual_amount: 467000.00,
      completion_rate: 103.8,
      target_orders: 18,
      actual_orders: 19,
      status: 'completed',
      create_date: '2024-10-25'
    },
    {
      id: '3',
      plan_number: 'MP202410',
      year: 2024,
      month: 10,
      sales_person: '王五',
      department: '销售一部',
      target_amount: 380000.00,
      actual_amount: 320000.00,
      completion_rate: 84.2,
      target_orders: 15,
      actual_orders: 13,
      status: 'completed',
      create_date: '2024-09-25'
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
    submitted: { color: 'processing', text: '已提交' },
    approved: { color: 'blue', text: '已审批' },
    in_progress: { color: 'orange', text: '执行中' },
    completed: { color: 'green', text: '已完成' },
    cancelled: { color: 'red', text: '已取消' }
  };

  const getCompletionColor = (rate) => {
    if (rate >= 100) return '#52c41a';
    if (rate >= 80) return '#1890ff';
    if (rate >= 60) return '#faad14';
    return '#f5222d';
  };

  const columns = [
    {
      title: '计划编号',
      dataIndex: 'plan_number',
      key: 'plan_number',
      width: 120
    },
    {
      title: '年月',
      key: 'period',
      width: 100,
      render: (_, record) => `${record.year}年${record.month}月`
    },
    {
      title: '销售员',
      dataIndex: 'sales_person',
      key: 'sales_person',
      width: 100
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      width: 120
    },
    {
      title: '目标金额',
      dataIndex: 'target_amount',
      key: 'target_amount',
      width: 120,
      render: (amount) => `¥${amount?.toLocaleString() || 0}`
    },
    {
      title: '实际金额',
      dataIndex: 'actual_amount',
      key: 'actual_amount',
      width: 120,
      render: (amount) => `¥${amount?.toLocaleString() || 0}`
    },
    {
      title: '完成率',
      dataIndex: 'completion_rate',
      key: 'completion_rate',
      width: 150,
      render: (rate) => (
        <Progress 
          percent={rate} 
          size="small" 
          strokeColor={getCompletionColor(rate)}
          format={(percent) => `${percent}%`}
        />
      )
    },
    {
      title: '目标订单',
      dataIndex: 'target_orders',
      key: 'target_orders',
      width: 100,
      render: (orders) => `${orders}单`
    },
    {
      title: '实际订单',
      dataIndex: 'actual_orders',
      key: 'actual_orders',
      width: 100,
      render: (orders) => `${orders}单`
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
      title: '创建日期',
      dataIndex: 'create_date',
      key: 'create_date',
      width: 120
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
          {record.status === 'draft' && (
            <Button type="link" size="small" icon={<EditOutlined />}>
              编辑
            </Button>
          )}
        </Space>
      )
    }
  ];

  return (
    <PageContainer>
      <StyledCard>
        <Space>
          <Button type="primary" icon={<PlusOutlined />}>
            新增月计划
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

export default MonthlyPlan; 