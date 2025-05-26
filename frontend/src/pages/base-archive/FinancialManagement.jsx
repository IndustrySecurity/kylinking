import React from 'react';
import { Card, Button, Row, Col, Typography, Tabs } from 'antd';
import { 
  DollarOutlined, 
  PercentageOutlined, 
  BankOutlined,
  TransactionOutlined,
  CreditCardOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;
const { TabPane } = Tabs;

const FinancialManagement = () => {
  const navigate = useNavigate();
  
  // 财务档案项配置
  const archiveItems = [
    {
      key: 'currency',
      title: '币别',
      icon: <DollarOutlined />,
      path: '/base-archive/financial-management/currency',
      color: '#1890ff'
    },
    {
      key: 'taxRate',
      title: '税率',
      icon: <PercentageOutlined />,
      path: '/base-archive/financial-management/tax-rate',
      color: '#52c41a'
    },
    {
      key: 'account',
      title: '账户',
      icon: <BankOutlined />,
      path: '/base-archive/financial-management/account',
      color: '#fa8c16'
    },
    {
      key: 'settlement',
      title: '结算方式',
      icon: <TransactionOutlined />,
      path: '/base-archive/financial-management/settlement',
      color: '#722ed1'
    },
    {
      key: 'payment',
      title: '付款方式',
      icon: <CreditCardOutlined />,
      path: '/base-archive/financial-management/payment',
      color: '#eb2f96'
    }
  ];

  // 处理按钮点击
  const handleItemClick = (path) => {
    navigate(path);
  };

  return (
    <div>
      <Title level={2}>财务管理</Title>
      
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        {archiveItems.map(item => (
          <Col xs={24} sm={12} md={8} lg={6} key={item.key}>
            <Card 
              hoverable
              style={{ textAlign: 'center' }}
              onClick={() => handleItemClick(item.path)}
            >
              <div style={{ 
                fontSize: 48, 
                color: item.color,
                marginBottom: 16 
              }}>
                {item.icon}
              </div>
              <Title level={4}>{item.title}</Title>
              <Button 
                type="primary" 
                style={{ backgroundColor: item.color, borderColor: item.color }}
                onClick={() => handleItemClick(item.path)}
              >
                管理{item.title}
              </Button>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default FinancialManagement;
