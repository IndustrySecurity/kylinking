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
  FunctionOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;
const { TabPane } = Tabs;

const ProductionManagement = () => {
  const navigate = useNavigate();
  
  // 生产档案项配置
  const archiveItems = [
    {
      key: 'bagType',
      title: '袋型',
      icon: <AppstoreOutlined />,
      path: '/production/archive/bag-type',
      color: '#1890ff'
    },
    {
      key: 'process',
      title: '工序',
      icon: <ToolOutlined />,
      path: '/production/archive/process',
      color: '#52c41a'
    },
    {
      key: 'warehouse',
      title: '仓库',
      icon: <HomeOutlined />,
      path: '/production/archive/warehouse',
      color: '#fa8c16'
    },
    {
      key: 'machine',
      title: '机台',
      icon: <DesktopOutlined />,
      path: '/production/archive/machine',
      color: '#722ed1'
    },
    {
      key: 'team',
      title: '班组',
      icon: <TeamOutlined />,
      path: '/production/archive/team',
      color: '#eb2f96'
    },
    {
      key: 'packaging',
      title: '包装方式',
      icon: <InboxOutlined />,
      path: '/production/archive/packaging',
      color: '#faad14'
    },
    {
      key: 'delivery',
      title: '送货方式',
      icon: <CarOutlined />,
      path: '/production/archive/delivery',
      color: '#13c2c2'
    },
    {
      key: 'lossType',
      title: '报损类型',
      icon: <WarningOutlined />,
      path: '/production/archive/loss-type',
      color: '#f5222d'
    },
    {
      key: 'colorCard',
      title: '色卡',
      icon: <BgColorsOutlined />,
      path: '/production/archive/color-card',
      color: '#2f54eb'
    },
    {
      key: 'unit',
      title: '单位',
      icon: <ColumnWidthOutlined />,
      path: '/production/archive/unit',
      color: '#fadb14'
    },
    {
      key: 'specification',
      title: '规格',
      icon: <FormatPainterOutlined />,
      path: '/production/archive/specification',
      color: '#a0d911'
    }
  ];

  // 生产配置项配置
  const configItems = [
    {
      key: 'calcParams',
      title: '计算参数',
      icon: <CalculatorOutlined />,
      path: '/production/config/calc-params',
      color: '#1890ff'
    },
    {
      key: 'calcScheme',
      title: '计算方案',
      icon: <SettingOutlined />,
      path: '/production/config/calc-scheme',
      color: '#52c41a'
    },
    {
      key: 'docManagement',
      title: '文档管理',
      icon: <FileTextOutlined />,
      path: '/production/config/doc-management',
      color: '#fa8c16'
    },
    {
      key: 'quoteInk',
      title: '报价油墨',
      icon: <ExperimentOutlined />,
      path: '/production/config/quote-ink',
      color: '#722ed1'
    },
    {
      key: 'quoteMaterial',
      title: '报价材料',
      icon: <ShoppingOutlined />,
      path: '/production/config/quote-material',
      color: '#eb2f96'
    },
    {
      key: 'quoteAuxiliary',
      title: '报价辅材',
      icon: <ScissorOutlined />,
      path: '/production/config/quote-auxiliary',
      color: '#faad14'
    },
    {
      key: 'quoteLoss',
      title: '报价损粍',
      icon: <WarningOutlined />,
      path: '/production/config/quote-loss',
      color: '#13c2c2'
    },
    {
      key: 'inkOptions',
      title: '油墨选项',
      icon: <BgColorsOutlined />,
      path: '/production/config/ink-options',
      color: '#f5222d'
    },
    {
      key: 'quoteFreight',
      title: '报价运费',
      icon: <CarOutlined />,
      path: '/production/config/quote-freight',
      color: '#2f54eb'
    },
    {
      key: 'bagFormula',
      title: '袋型相关公式',
      icon: <FunctionOutlined />,
      path: '/production/config/bag-formula',
      color: '#fadb14'
    }
  ];

  // 处理按钮点击
  const handleItemClick = (path) => {
    navigate(path);
  };

  return (
    <div>
      <Title level={2}>生产管理</Title>
      
      <Tabs defaultActiveKey="archive">
        <TabPane tab="生产档案" key="archive">
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
        </TabPane>
        <TabPane tab="生产配置" key="config">
          <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            {configItems.map(item => (
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
        </TabPane>
      </Tabs>
    </div>
  );
};

export default ProductionManagement;

