import React from 'react';
import { Row, Col, Card, Statistic, Progress, Table, Typography, Divider } from 'antd';
import {
  LineChartOutlined,
  SettingOutlined,
  TeamOutlined,
  ShoppingOutlined,
  RiseOutlined,
  BarChartOutlined,
  SyncOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

const { Title } = Typography;

// Styled Card with box-shadow and hover effect
const StyledCard = styled(Card)`
  height: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  border: none;
  
  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    transform: translateY(-4px);
  }
  
  .ant-card-head {
    border-bottom: none;
    padding-bottom: 0;
  }
  
  .ant-statistic-title {
    color: rgba(0, 0, 0, 0.5);
    font-size: 14px;
    margin-bottom: 8px;
  }
  
  .ant-statistic-content {
    color: rgba(0, 0, 0, 0.85);
    font-size: 24px;
    font-weight: 600;
  }
`;

// Card for showing progress
const ProgressCard = styled(Card)`
  height: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: none;
  
  .ant-progress-text {
    color: rgba(0, 0, 0, 0.85);
    font-weight: 600;
  }
`;

// Styled status tag
const StatusTag = styled.span`
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background-color: ${props => props.$completed ? 'rgba(82, 196, 26, 0.1)' : 'rgba(24, 144, 255, 0.1)'};
  color: ${props => props.$completed ? '#52c41a' : '#1890ff'};
`;

// Page section title
const SectionTitle = styled(Title)`
  position: relative;
  margin-bottom: 24px !important;
  font-weight: 600 !important;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 48px;
    height: 3px;
    background: #1890ff;
    border-radius: 2px;
  }
`;

// Statistic with trend
const TrendInfo = styled.div`
  margin-top: 8px;
  color: ${props => props.$color};
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

// Metric grid item
const GridItem = styled(Col)`
  margin-bottom: 24px;
`;

const Dashboard = () => {
  // Production data
  const productionData = [
    {
      key: '1',
      product: 'PET薄膜',
      plan: 1000,
      actual: 850,
      progress: 85,
      status: '进行中',
    },
    {
      key: '2',
      product: 'BOPP薄膜',
      plan: 800,
      actual: 800,
      progress: 100,
      status: '已完成',
    },
    {
      key: '3',
      product: 'CPP薄膜',
      plan: 600,
      actual: 450,
      progress: 75,
      status: '进行中',
    },
    {
      key: '4',
      product: 'PE薄膜',
      plan: 750,
      actual: 480,
      progress: 64,
      status: '进行中',
    },
  ];

  // Table columns
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
      render: (plan) => `${plan} kg`,
    },
    {
      title: '实际产量',
      dataIndex: 'actual',
      key: 'actual',
      render: (actual) => `${actual} kg`,
    },
    {
      title: '完成进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress) => (
        <Progress 
          percent={progress} 
          size="small" 
          strokeColor={{
            from: '#108ee9',
            to: '#87d068',
          }}
          strokeWidth={5}
          trailColor="#f0f0f0"
        />
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <StatusTag $completed={status === '已完成'}>
          {status === '已完成' ? <CheckCircleOutlined /> : <SyncOutlined spin />} {status}
        </StatusTag>
      ),
    },
  ];

  return (
    <div>
      {/* Overview section */}
      <SectionTitle level={4}>生产概览</SectionTitle>
      
      <Row gutter={[24, 24]}>
        <GridItem xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="今日产量"
              value={1128}
              precision={0}
              valueStyle={{ color: '#3f8600' }}
              prefix={<LineChartOutlined />}
              suffix="kg"
            />
            <TrendInfo $color="#3f8600">
              <RiseOutlined /> 较昨日增长 7.2%
            </TrendInfo>
          </StyledCard>
        </GridItem>
        
        <GridItem xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="设备运行率"
              value={93.2}
              precision={1}
              valueStyle={{ color: '#1890ff' }}
              prefix={<SettingOutlined />}
              suffix="%"
            />
            <TrendInfo $color="#1890ff">
              <BarChartOutlined /> 高于行业平均值
            </TrendInfo>
          </StyledCard>
        </GridItem>
        
        <GridItem xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="在线员工"
              value={42}
              valueStyle={{ color: '#722ed1' }}
              prefix={<TeamOutlined />}
              suffix="人"
            />
            <TrendInfo $color="#722ed1">
              <BarChartOutlined /> 当前出勤率 87.5%
            </TrendInfo>
          </StyledCard>
        </GridItem>
        
        <GridItem xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="库存预警"
              value={3}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ShoppingOutlined />}
              suffix="项"
            />
            <TrendInfo $color="#cf1322">
              <BarChartOutlined /> 请及时处理
            </TrendInfo>
          </StyledCard>
        </GridItem>
      </Row>

      <Divider style={{ margin: '24px 0' }} />
      
      {/* Sales management section */}
      <SectionTitle level={4}>销售管理</SectionTitle>
      
      <Row gutter={[24, 24]}>
        <GridItem xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="今日订单"
              value={28}
              precision={0}
              valueStyle={{ color: '#3f8600' }}
              prefix={<ShoppingOutlined />}
              suffix="单"
            />
            <TrendInfo $color="#3f8600">
              <RiseOutlined /> 较昨日增长 12.5%
            </TrendInfo>
          </StyledCard>
        </GridItem>
        
        <GridItem xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="今日销售额"
              value={368500}
              precision={2}
              valueStyle={{ color: '#1890ff' }}
              prefix={<RiseOutlined />}
              suffix="元"
            />
            <TrendInfo $color="#1890ff">
              <RiseOutlined /> 较昨日增长 8.3%
            </TrendInfo>
          </StyledCard>
        </GridItem>
        
        <GridItem xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="活跃客户"
              value={156}
              valueStyle={{ color: '#722ed1' }}
              prefix={<TeamOutlined />}
              suffix="家"
            />
            <TrendInfo $color="#722ed1">
              <BarChartOutlined /> 本月新增 15家
            </TrendInfo>
          </StyledCard>
        </GridItem>
        
        <GridItem xs={24} sm={12} lg={6}>
          <StyledCard>
            <Statistic
              title="待处理订单"
              value={12}
              valueStyle={{ color: '#fa8c16' }}
              prefix={<SyncOutlined />}
              suffix="单"
            />
            <TrendInfo $color="#fa8c16">
              <BarChartOutlined /> 需及时处理
            </TrendInfo>
          </StyledCard>
        </GridItem>
      </Row>

      <Divider style={{ margin: '24px 0' }} />
      
      {/* Production status section */}
      <SectionTitle level={4}>生产状态</SectionTitle>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={8}>
          <ProgressCard>
            <div style={{ textAlign: 'center', padding: '24px 0' }}>
              <Progress
                type="dashboard"
                percent={85}
                format={(percent) => `${percent}%`}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
                strokeWidth={8}
                width={180}
              />
              <div style={{ marginTop: 24 }}>
                <Statistic
                  title="今日计划完成率"
                  value={85}
                  suffix="%"
                  valueStyle={{ color: '#3f8600', fontSize: '20px' }}
                />
              </div>
            </div>
          </ProgressCard>
        </Col>
        
        <Col xs={24} lg={16}>
          <Card 
            title="生产计划" 
            bordered={false}
            style={{ 
              borderRadius: '8px', 
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
              height: '100%'
            }}
          >
            <Table
              columns={columns}
              dataSource={productionData}
              pagination={false}
              size="middle"
              style={{ width: '100%' }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 