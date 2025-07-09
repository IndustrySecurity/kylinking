import React from 'react';
import { Card, Button, Row, Col, Typography, Tabs } from 'antd';
import { 
  AppstoreOutlined, 
  SettingOutlined, 
  ToolOutlined, 
  HomeOutlined,
  DesktopOutlined,
  TeamOutlined,
  InboxOutlined,
  CarOutlined,
  WarningOutlined,
  BgColorsOutlined,
  ColumnWidthOutlined,
  FormatPainterOutlined,
  CalculatorOutlined,
  FileTextOutlined,
  DollarOutlined,
  ShoppingOutlined,
  ScissorOutlined,
  ExperimentOutlined,
  FunctionOutlined,
  TagsOutlined,
  TruckOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

const ProductionData = () => {
  const navigate = useNavigate();
  
  // 生产档案项配置
  const archiveItems = [
    {
      key: 'bagType',
      title: '袋型',
      icon: <AppstoreOutlined />,
      path: '/base-archive/production-archive/bag-type-management',
      color: '#1890ff'
    },
    {
      key: 'process',
      title: '工序',
      icon: <ToolOutlined />,
      path: '/base-archive/production-archive/process-management',
      color: '#52c41a'
    },
    {
      key: 'warehouse',
      title: '仓库',
      icon: <HomeOutlined />,
      path: '/base-archive/production-archive/warehouse-management',
      color: '#fa8c16'
    },
    {
      key: 'machine',
      title: '机台',
      icon: <DesktopOutlined />,
      path: '/base-archive/production-archive/machine-management',
      color: '#722ed1'
    },
    {
      key: 'packaging',
      title: '包装方式',
      icon: <InboxOutlined />,
      path: '/base-archive/production-archive/package-method-management',
      color: '#faad14'
    },
    {
      key: 'delivery',
      title: '送货方式',
      icon: <CarOutlined />,
      path: '/base-archive/production-archive/delivery-method-management',
      color: '#13c2c2'
    },
    {
      key: 'lossType',
      title: '报损类型',
      icon: <WarningOutlined />,
      path: '/base-archive/production-archive/loss-type-management',
      color: '#f5222d'
    },
    {
      key: 'colorCard',
      title: '色卡',
      icon: <BgColorsOutlined />,
      path: '/base-archive/production-archive/color-card-management',
      color: '#2f54eb'
    },
    {
      key: 'unit',
      title: '单位',
      icon: <ColumnWidthOutlined />,
      path: '/base-archive/production-archive/unit-management',
      color: '#fadb14'
    },
    {
      key: 'specification',
      title: '规格',
      icon: <FormatPainterOutlined />,
      path: '/base-archive/production-archive/specification-management',
      color: '#a0d911'
    }
  ];

  // 生产配置项配置
  const configItems = [
    {
      key: 'calcParameters',
      title: '计算参数',
      icon: <CalculatorOutlined />,
      path: '/base-archive/production-config/calculation-parameter-management',
      color: '#f759ab'
    },
    {
      key: 'calcScheme',
      title: '计算方案',
      icon: <CalculatorOutlined />,
      path: '/base-archive/production-config/calculation-scheme-management',
      color: '#52c41a'
    },
    {
      key: 'quoteInk',
      title: '报价油墨',
      icon: <ExperimentOutlined />,
      path: '/base-archive/production-config/quote-ink-management',
      color: '#722ed1'
    },
    {
      key: 'quoteMaterial',
      title: '报价材料',
      icon: <ShoppingOutlined />,
      path: '/base-archive/production-config/quote-material-management',
      color: '#eb2f96'
    },
    {
      key: 'quoteAuxiliary',
      title: '报价辅材',
      icon: <ScissorOutlined />,
      path: '/base-archive/production-config/quote-accessory-management',
      color: '#faad14'
    },
    {
      key: 'quoteLoss',
      title: '报价损耗',
      icon: <WarningOutlined />,
      path: '/base-archive/production-config/quote-loss-management',
      color: '#13c2c2'
    },
    {
      key: 'inkOptions',
      title: '油墨选项',
      icon: <BgColorsOutlined />,
      path: '/base-archive/production-config/ink-option-management',
      color: '#f5222d'
    },
    {
      key: 'quoteFreight',
      title: '报价运费',
      icon: <CarOutlined />,
      path: '/base-archive/production-config/quote-freight-management',
      color: '#2f54eb'
    },
    {
      key: 'bagFormula',
      title: '袋型相关公式',
      icon: <FunctionOutlined />,
      path: '/base-archive/production-config/bag-related-formula-management',
      color: '#fadb14'
    }
  ];

  // 处理按钮点击
  const handleItemClick = (path) => {
    navigate(path);
  };

  // 渲染卡片组件
  const renderCards = (items) => (
    <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
      {items.map(item => (
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
              onClick={(e) => {
                e.stopPropagation(); // 阻止事件冒泡到Card
                handleItemClick(item.path);
              }}
            >
              管理{item.title}
            </Button>
          </Card>
        </Col>
      ))}
    </Row>
  );

  // Tabs配置
  const tabItems = [
    {
      key: 'productionArchive',
      label: '生产档案',
      children: renderCards(archiveItems)
    },
    {
      key: 'productionConfig',
      label: '生产配置',
      children: renderCards(configItems)
    }
  ];

  return (
    <div>
      <Title level={2}>生产管理</Title>
      <Tabs defaultActiveKey="productionArchive" items={tabItems} />
    </div>
  );
};

export default ProductionData;

