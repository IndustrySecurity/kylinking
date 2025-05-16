import React from 'react';
import { Row, Col, Card, Statistic, Progress, Table } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  LineChartOutlined,
  SettingOutlined,
  TeamOutlined,
  ShoppingOutlined,
} from '@ant-design/icons';
import styled from 'styled-components';

const StyledCard = styled(Card)`
  .ant-card-head {
    border-bottom: none;
  }
  
  .ant-statistic-title {
    color: rgba(0, 0, 0, 0.45);
  }
  
  .ant-statistic-content {
    color: rgba(0, 0, 0, 0.85);
  }
`;

const ProgressCard = styled(Card)`
  .ant-progress-text {
    color: rgba(0, 0, 0, 0.85);
  }
`;

const Dashboard = () => {
  const productionData = [
    {
      key: '1',
      product: 'PET薄膜',
      plan: 1000,
      actual: 850,
      status: '进行中',
    },
    {
      key: '2',
      product: 'BOPP薄膜',
      plan: 800,
      actual: 800,
      status: '已完成',
    },
    {
      key: '3',
      product: 'CPP薄膜',
      plan: 600,
      actual: 450,
      status: '进行中',
    },
  ];

  const columns = [
    {
      title: '产品',
      dataIndex: 'product',
      key: 'product',
    },
    {
      title: '计划产量',
      dataIndex: 'plan',
      key: 'plan',
    },
    {
      title: '实际产量',
      dataIndex: 'actual',
      key: 'actual',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <span style={{ color: status === '已完成' ? '#52c41a' : '#1890ff' }}>
          {status}
        </span>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={[24, 24]}>
        <Col xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="今日产量"
              value={1128}
              precision={0}
              valueStyle={{ color: '#3f8600' }}
              prefix={<LineChartOutlined />}
              suffix="吨"
            />
          </StyledCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="设备运行率"
              value={93.2}
              precision={1}
              valueStyle={{ color: '#1890ff' }}
              prefix={<SettingOutlined />}
              suffix="%"
            />
          </StyledCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="在线员工"
              value={42}
              valueStyle={{ color: '#722ed1' }}
              prefix={<TeamOutlined />}
              suffix="人"
            />
          </StyledCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="库存预警"
              value={3}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ShoppingOutlined />}
              suffix="项"
            />
          </StyledCard>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="生产进度" bordered={false}>
            <ProgressCard>
              <Progress
                type="dashboard"
                percent={85}
                format={(percent) => `${percent}%`}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
              <div style={{ textAlign: 'center', marginTop: 16 }}>
                <Statistic
                  title="今日计划完成率"
                  value={85}
                  suffix="%"
                  valueStyle={{ color: '#3f8600' }}
                />
              </div>
            </ProgressCard>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="生产计划" bordered={false}>
            <Table
              columns={columns}
              dataSource={productionData}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 