import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShoppingCartOutlined,
  FileProtectOutlined,
  DeliveredProcedureOutlined,
  RollbackOutlined,
  UndoOutlined,
  ContactsOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

// 页面容器
const PageContainer = styled.div`
  padding: 0;
`;

// 主标题样式
const SectionTitle = styled.h2`
  margin: 0 0 32px 0;
  color: #1c1c1c;
  font-size: 24px;
  font-weight: 600;
  position: relative;
  padding-left: 12px;
  
  &:before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(135deg, #1890ff, #40a9ff);
    border-radius: 2px;
  }
`;

// 功能网格容器
const FunctionGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 24px;
`;

// 功能卡片样式
const FunctionCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 32px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  overflow: hidden;
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #1890ff, #40a9ff);
    transform: scaleX(0);
    transition: transform 0.3s ease;
  }
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    border-color: #1890ff;
    
    &:before {
      transform: scaleX(1);
    }
    
    .card-icon {
      transform: scale(1.1);
      color: #1890ff;
    }
    
    .card-title {
      color: #1890ff;
    }
  }
`;

// 图标容器
const IconContainer = styled.div`
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #f0f9ff, #e6f4ff);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  transition: all 0.3s ease;
`;

// 卡片标题
const CardTitle = styled.h3`
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1c1c1c;
  transition: color 0.3s ease;
`;

// 卡片描述
const CardDescription = styled.p`
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
`;

const SalesManagement = () => {
  const navigate = useNavigate();

  // 销售功能配置
  const salesFunctions = [
    {
      key: 'sales-order',
      title: '销售订单',
      description: '销售订单管理，处理客户订单信息',
      icon: <ShoppingCartOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      path: '/business/sales/sales-order',
    },
    {
      key: 'delivery-notice',
      title: '送货通知单',
      description: '送货通知单管理，准备送货计划',
      icon: <FileProtectOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      path: '/business/sales/delivery-notice',
    },
    {
      key: 'delivery-order',
      title: '送货单',
      description: '送货单管理，记录商品送货信息',
      icon: <DeliveredProcedureOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      path: '/business/sales/delivery-order',
    },
    {
      key: 'return-notice',
      title: '退货通知单',
      description: '退货通知单管理，处理退货申请',
      icon: <RollbackOutlined style={{ fontSize: '32px', color: '#fa8c16' }} />,
      path: '/business/sales/return-notice',
    },
    {
      key: 'return-order',
      title: '退货单',
      description: '退货单管理，处理商品退货业务',
      icon: <UndoOutlined style={{ fontSize: '32px', color: '#eb2f96' }} />,
      path: '/business/sales/return-order',
    },
    {
      key: 'customer-contract',
      title: '客户合同',
      description: '客户合同管理，维护合同信息',
      icon: <ContactsOutlined style={{ fontSize: '32px', color: '#13c2c2' }} />,
      path: '/business/sales/customer-contract',
    },
    {
      key: 'monthly-plan',
      title: '销售月计划',
      description: '销售月计划管理，制定销售目标',
      icon: <CalendarOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      path: '/business/sales/monthly-plan',
    }
  ];

  const handleCardClick = (path) => {
    navigate(path);
  };

  return (
    <PageContainer>
      <SectionTitle>销售管理</SectionTitle>
      
      <FunctionGrid>
        {salesFunctions.map((func) => (
          <FunctionCard
            key={func.key}
            onClick={() => handleCardClick(func.path)}
          >
            <IconContainer className="card-icon">
              {func.icon}
            </IconContainer>
            <CardTitle className="card-title">{func.title}</CardTitle>
            <CardDescription>{func.description}</CardDescription>
          </FunctionCard>
        ))}
      </FunctionGrid>
    </PageContainer>
  );
};

export default SalesManagement; 