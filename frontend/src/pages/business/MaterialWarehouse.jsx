import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  InboxOutlined,
  SendOutlined,
  AuditOutlined,
  SwapOutlined,
  FileTextOutlined,
  ContainerOutlined,
  ReloadOutlined,
  SettingOutlined,
  BarChartOutlined,
  SafetyOutlined,
  TagsOutlined,
  ReconciliationOutlined
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

const MaterialWarehouse = () => {
  const navigate = useNavigate();

  // 材料仓库功能配置
  const warehouseFunctions = [
    {
      key: 'inbound',
      title: '材料入库',
      description: '材料入库管理，记录材料入库信息',
      icon: <InboxOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      path: '/business/material-warehouse/inbound',
    },
    {
      key: 'outbound',
      title: '材料出库',
      description: '材料出库管理，处理材料出库业务',
      icon: <SendOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      path: '/business/material-warehouse/outbound',
    },
    {
      key: 'count',
      title: '材料盘点',
      description: '材料库存盘点，确保库存准确性',
      icon: <AuditOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      path: '/business/material-warehouse/count',
    },
    {
      key: 'transfer',
      title: '材料调拨',
      description: '材料仓库间调拨管理',
      icon: <SwapOutlined style={{ fontSize: '32px', color: '#fa8c16' }} />,
      path: '/business/material-warehouse/transfer',
    },
    {
      key: 'receipt',
      title: '材料收货单',
      description: '材料收货单管理，验收入库',
      icon: <FileTextOutlined style={{ fontSize: '32px', color: '#13c2c2' }} />,
      path: '/business/material-warehouse/receipt',
    },
    {
      key: 'requisition',
      title: '材料领用单',
      description: '生产部门材料领用申请',
      icon: <ContainerOutlined style={{ fontSize: '32px', color: '#eb2f96' }} />,
      path: '/business/material-warehouse/requisition',
    },
    {
      key: 'return',
      title: '材料退库',
      description: '剩余材料退库管理',
      icon: <ReloadOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      path: '/business/material-warehouse/return',
    },
    {
      key: 'quality',
      title: '材料质检',
      description: '材料质量检验管理',
      icon: <SafetyOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      path: '/business/material-warehouse/quality',
    },
    {
      key: 'labeling',
      title: '材料标签',
      description: '材料标签打印管理',
      icon: <TagsOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      path: '/business/material-warehouse/labeling',
    },
    {
      key: 'location',
      title: '库位管理',
      description: '材料仓库库位管理',
      icon: <SettingOutlined style={{ fontSize: '32px', color: '#fa8c16' }} />,
      path: '/business/material-warehouse/location',
    },
    {
      key: 'report',
      title: '库存报表',
      description: '材料库存统计报表',
      icon: <BarChartOutlined style={{ fontSize: '32px', color: '#13c2c2' }} />,
      path: '/business/material-warehouse/report',
    },
    {
      key: 'reconciliation',
      title: '库存对账',
      description: '材料库存对账管理',
      icon: <ReconciliationOutlined style={{ fontSize: '32px', color: '#eb2f96' }} />,
      path: '/business/material-warehouse/reconciliation',
    },
  ];

  const handleCardClick = (path) => {
    navigate(path);
  };

  return (
    <PageContainer>
      <SectionTitle>材料仓库</SectionTitle>
      
      <FunctionGrid>
        {warehouseFunctions.map((func) => (
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

export default MaterialWarehouse; 