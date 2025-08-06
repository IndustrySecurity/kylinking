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
  ToolOutlined
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
      path: '/base-archive/base-data/customer-management',
      color: '#1890ff'
    },
    {
      key: 'products',
      title: '产品',
      icon: <ShoppingOutlined />,
      path: '/base-archive/base-data/product-management',
      color: '#52c41a'
    },
    {
      key: 'suppliers',
      title: '供应商',
      icon: <BankOutlined />,
      path: '/base-archive/base-data/supplier-management',
      color: '#fa8c16'
    },
    {
      key: 'materials',
      title: '材料',
      icon: <ShoppingOutlined />,
      path: '/base-archive/base-data/material-management',
      color: '#722ed1'
    },
    {
      key: 'departments',
      title: '部门管理',
      icon: <ApartmentOutlined />,
      path: '/base-archive/base-data/department-management',
      color: '#eb2f96'
    },
    {
      key: 'positions',
      title: '职位',
      icon: <IdcardOutlined />,
      path: '/base-archive/base-data/position-management',
      color: '#f5222d'
    },
    {
      key: 'employees',
      title: '员工',
      icon: <TeamOutlined />,
      path: '/base-archive/base-data/employee-management',
      color: '#13c2c2'
    },
    {
      key: 'teamGroups',
      title: '班组',
      icon: <TeamOutlined style={{ fontSize: '48px' }} />,
      path: '/base-archive/base-data/team-group-management',
      color: '#faad14'
    }
  ];

  // 基础分类项配置
  const categoryItems = [
    {
      key: 'customerCategories',
      title: '客户分类',
      icon: <UserOutlined />,
      path: '/base-archive/base-category/customer-category-management',
      color: '#1890ff'
    },
    {
      key: 'productCategories',
      title: '产品分类',
      icon: <ShoppingOutlined />,
      path: '/base-archive/base-category/product-category-management',
      color: '#52c41a'
    },
    {
      key: 'supplierCategories',
      title: '供应商分类',
      icon: <BankOutlined />,
      path: '/base-archive/base-category/supplier-category-management',
      color: '#fa8c16'
    },
    {
      key: 'materialCategories',
      title: '材料分类',
      icon: <AppstoreOutlined />,
      path: '/base-archive/base-category/material-category-management',
      color: '#722ed1'
    },
    {
      key: 'processCategories',
      title: '工序分类',
      icon: <ToolOutlined />,
      path: '/base-archive/base-category/process-category-management',
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
