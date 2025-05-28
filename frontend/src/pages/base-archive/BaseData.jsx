import React from 'react';
import { Card, Button, Row, Col, Typography, Tabs } from 'antd';
import { 
  UserOutlined, 
  ShoppingOutlined, 
  TeamOutlined, 
  BankOutlined,
  ApartmentOutlined,
  IdcardOutlined,
  AppstoreOutlined,
  ToolOutlined,
  InboxOutlined,
  TruckOutlined,
  BgColorsOutlined,
  TagsOutlined,
  ColumnWidthOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

const BaseData = () => {
  const navigate = useNavigate();

  // 基础数据项配置
  const dataItems = [
    {
      key: 'customers',
      title: '客户',
      icon: <UserOutlined style={{ fontSize: '48px' }} />,
      path: '/base-archive/base-data/customers',
      color: '#1890ff'
    },
    {
      key: 'products',
      title: '产品',
      icon: <ShoppingOutlined />,
      path: '/base-archive/base-data/products',
      color: '#52c41a'
    },
    {
      key: 'suppliers',
      title: '供应商',
      icon: <BankOutlined />,
      path: '/base-archive/base-data/suppliers',
      color: '#fa8c16'
    },
    {
      key: 'materials',
      title: '材料',
      icon: <ShoppingOutlined />,
      path: '/base-archive/base-data/materials',
      color: '#722ed1'
    },
    {
      key: 'materialCategories',
      title: '材料分类',
      icon: <AppstoreOutlined />,
      path: '/base-archive/material-category-management',
      color: '#722ed1'
    },
    {
      key: 'packageMethods',
      title: '包装方式',
      icon: <InboxOutlined />,
      path: '/base-archive/package-methods',
      color: '#faad14'
    },
    {
      key: 'deliveryMethods',
      title: '送货方式',
      icon: <TruckOutlined />,
      path: '/base-archive/delivery-methods',
      color: '#1890ff'
    },
    {
      key: 'colorCards',
      title: '色卡',
      icon: <BgColorsOutlined />,
      path: '/base-archive/color-cards',
      color: '#eb2f96'
    },
    {
      key: 'units',
      title: '单位',
      icon: <AppstoreOutlined />,
      path: '/base-archive/units',
      color: '#52c41a'
    },
    {
      key: 'specifications',
      title: '规格',
      icon: <ColumnWidthOutlined />,
      path: '/base-archive/specifications',
      color: '#13c2c2'
    },
    {
      key: 'customerCategories',
      title: '客户分类',
      icon: <TagsOutlined />,
      path: '/base-archive/customer-category-management',
      color: '#13c2c2'
    },
    {
      key: 'supplierCategories',
      title: '供应商分类',
      icon: <BankOutlined />,
      path: '/base-archive/supplier-category-management',
      color: '#fa8c16'
    },
    {
      key: 'departments',
      title: '部门',
      icon: <ApartmentOutlined />,
      path: '/base-archive/base-data/departments',
      color: '#eb2f96'
    },
    {
      key: 'positions',
      title: '职位',
      icon: <IdcardOutlined />,
      path: '/base-archive/base-data/positions',
      color: '#f5222d'
    },
    {
      key: 'employees',
      title: '员工',
      icon: <TeamOutlined />,
      path: '/base-archive/base-data/employees',
      color: '#13c2c2'
    }
  ];

  // 基础分类项配置
  const categoryItems = [
    {
      key: 'customerCategories',
      title: '客户分类',
      icon: <UserOutlined />,
      path: '/base-archive/base-data/base-category/customer-categories',
      color: '#1890ff'
    },
    {
      key: 'productCategories',
      title: '产品分类',
      icon: <ShoppingOutlined />,
      path: '/base-archive/base-data/base-category/product-categories',
      color: '#52c41a'
    },
    {
      key: 'supplierCategories',
      title: '供应商分类',
      icon: <BankOutlined />,
      path: '/base-archive/base-data/base-category/supplier-categories',
      color: '#fa8c16'
    },
    {
      key: 'materialCategories',
      title: '材料分类',
      icon: <AppstoreOutlined />,
      path: '/base-archive/base-data/base-category/material-categories',
      color: '#722ed1'
    },
    {
      key: 'processCategories',
      title: '工序分类',
      icon: <ToolOutlined />,
      path: '/base-archive/base-data/base-category/process-categories',
      color: '#eb2f96'
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
      key: 'baseData',
      label: '基础数据',
      children: renderCards(dataItems)
    },
    {
      key: 'baseCategory',
      label: '基础分类',
      children: renderCards(categoryItems)
    }
  ];

  return (
    <div>
      <Title level={2}>基础档案</Title>
      <Tabs defaultActiveKey="baseData" items={tabItems} />
    </div>
  );
};

export default BaseData;
