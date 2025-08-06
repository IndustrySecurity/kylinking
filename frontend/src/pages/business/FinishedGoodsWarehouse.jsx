import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ImportOutlined,
  ExportOutlined,
  AuditOutlined,
  SwapOutlined,
  FileTextOutlined,
  TagsOutlined,
  ReloadOutlined,
  FileSyncOutlined,
  ReconciliationOutlined,
  RetweetOutlined,
  ContainerOutlined,
  RedoOutlined,
  ToolOutlined,
  CalculatorOutlined,
  InboxOutlined,
  ShoppingOutlined
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

const FinishedGoodsWarehouse = () => {
  const navigate = useNavigate();

  // 成品仓库功能配置
  const warehouseFunctions = [
    {
      key: 'inbound',
      title: '成品入库',
      description: '成品入库管理，记录成品入库信息',
      icon: <ImportOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      path: '/business/finished-goods/inbound',
    },
    {
      key: 'outbound',
      title: '成品出库',
      description: '成品出库管理，处理成品出库业务',
      icon: <ExportOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      path: '/business/finished-goods/outbound',
    },
    {
      key: 'inventory',
      title: '成品盘点',
      description: '成品库存盘点，确保库存准确性',
      icon: <AuditOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      path: '/business/finished-goods/count',
    },
    {
      key: 'transfer',
      title: '成品调拨',
      description: '成品仓库间调拨管理',
      icon: <SwapOutlined style={{ fontSize: '32px', color: '#fa8c16' }} />,
      path: '/business/finished-goods/transfer',
    },
    {
      key: 'weighing-slip',
      title: '成品磅码单',
      description: '成品称重磅码单管理',
      icon: <FileTextOutlined style={{ fontSize: '32px', color: '#13c2c2' }} />,
      path: '/business/finished-goods/weighing-slip',
    },
    {
      key: 'packing-weighing-slip',
      title: '打包磅码单',
      description: '打包称重磅码单管理',
      icon: <TagsOutlined style={{ fontSize: '32px', color: '#eb2f96' }} />,
      path: '/business/finished-goods/packing-weighing-slip',
    },
    {
      key: 'rewinding-output-report',
      title: '复卷产量上报',
      description: '复卷工艺产量数据上报',
      icon: <ReloadOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      path: '/business/finished-goods/rewinding-output-report',
    },
    {
      key: 'bag-picking-output-report',
      title: '挑袋产量上报',
      description: '挑袋工艺产量数据上报',
      icon: <FileSyncOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      path: '/business/finished-goods/bag-picking-output-report',
    },
    {
      key: 'semi-finished-inbound',
      title: '半成品入库',
      description: '半成品入库管理',
      icon: <InboxOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      path: '/business/finished-goods/semi-finished-inbound',
    },
    {
      key: 'semi-finished-outbound',
      title: '半成品出库',
      description: '半成品出库管理',
      icon: <ShoppingOutlined style={{ fontSize: '32px', color: '#fa8c16' }} />,
      path: '/business/finished-goods/semi-finished-outbound',
    },
    {
      key: 'bag-picking-return',
      title: '挑袋返上',
      description: '挑袋返上管理',
      icon: <RetweetOutlined style={{ fontSize: '32px', color: '#13c2c2' }} />,
      path: '/business/finished-goods/bag-picking-return',
    },
    {
      key: 'to-tray',
      title: '成品入托',
      description: '成品入托管理',
      icon: <ContainerOutlined style={{ fontSize: '32px', color: '#eb2f96' }} />,
      path: '/business/finished-goods/to-tray',
    },
    {
      key: 'rework',
      title: '成品返工单',
      description: '成品返工单管理',
      icon: <RedoOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      path: '/business/finished-goods/rework',
    },
    {
      key: 'packing',
      title: '成品打包',
      description: '成品打包管理',
      icon: <ToolOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      path: '/business/finished-goods/packing',
    },
    {
      key: 'semi-finished-weighing',
      title: '半成品称重',
      description: '半成品称重管理',
      icon: <ReconciliationOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      path: '/business/finished-goods/semi-finished-weighing',
    },
    {
      key: 'inbound-accounting',
      title: '成品入库核算',
      description: '成品入库核算管理',
      icon: <CalculatorOutlined style={{ fontSize: '32px', color: '#fa8c16' }} />,
      path: '/business/finished-goods/inbound-accounting',
    },
  ];

  const handleCardClick = (path) => {
    navigate(path);
  };

  return (
    <PageContainer>
      <SectionTitle>成品仓库</SectionTitle>
      
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

export default FinishedGoodsWarehouse; 