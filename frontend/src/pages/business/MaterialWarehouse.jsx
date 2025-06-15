import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Button, Input, Select, Form, Modal, message, Space, Tag, Typography } from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  ImportOutlined,
  ExportOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

const { Title } = Typography;
const { Search } = Input;
const { Option } = Select;

// Styled Card with box-shadow and hover effect
const StyledCard = styled(Card)`
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: none;
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

const MaterialWarehouse = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  // 模拟数据
  const mockData = [
    {
      key: '1',
      warehouseCode: 'CL001',
      warehouseName: '原材料一库',
      warehouseType: '材料',
      location: 'A区1号',
      capacity: '1000',
      currentStock: '750',
      unit: 't',
      status: '正常',
    },
    {
      key: '2',
      warehouseCode: 'CL002',
      warehouseName: '原材料二库',
      warehouseType: '材料',
      location: 'A区2号',
      capacity: '800',
      currentStock: '520',
      unit: 't',
      status: '正常',
    },
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setLoading(true);
    // 模拟API调用
    setTimeout(() => {
      setData(mockData);
      setLoading(false);
    }, 1000);
  };

  const columns = [
    {
      title: '仓库编号',
      dataIndex: 'warehouseCode',
      key: 'warehouseCode',
    },
    {
      title: '仓库名称',
      dataIndex: 'warehouseName',
      key: 'warehouseName',
    },
    {
      title: '仓库类型',
      dataIndex: 'warehouseType',
      key: 'warehouseType',
      render: () => <Tag color="blue">材料</Tag>,
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: '容量',
      dataIndex: 'capacity',
      key: 'capacity',
      render: (capacity, record) => `${capacity} ${record.unit}`,
    },
    {
      title: '当前库存',
      dataIndex: 'currentStock',
      key: 'currentStock',
      render: (stock, record) => `${stock} ${record.unit}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === '正常' ? 'green' : 'red'}>
          {status}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EditOutlined />}>
            编辑
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <SectionTitle level={4}>材料仓库管理</SectionTitle>
      
      <StyledCard>
        {/* 操作按钮栏 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
              新增仓库
            </Button>
          </Col>
          <Col>
            <Button icon={<ImportOutlined />}>
              导入
            </Button>
          </Col>
          <Col>
            <Button icon={<ExportOutlined />}>
              导出
            </Button>
          </Col>
          <Col>
            <Button icon={<ReloadOutlined />} onClick={loadData}>
              刷新
            </Button>
          </Col>
          <Col flex="auto" />
          <Col>
            <Search
              placeholder="搜索仓库编号、名称..."
              allowClear
              style={{ width: 250 }}
            />
          </Col>
        </Row>

        {/* 数据表格 */}
        <Table
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
          }}
        />
      </StyledCard>

      {/* 新增/编辑弹窗 */}
      <Modal
        title="新增仓库"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => {
          form.validateFields().then(() => {
            message.success('操作成功');
            setModalVisible(false);
            loadData();
          });
        }}
        width={800}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="仓库名称" name="warehouseName" rules={[{ required: true }]}>
                <Input placeholder="请输入仓库名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="位置" name="location" rules={[{ required: true }]}>
                <Input placeholder="请输入仓库位置" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="容量" name="capacity" rules={[{ required: true }]}>
                <Input type="number" placeholder="请输入容量" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="单位" name="unit" rules={[{ required: true }]}>
                <Select placeholder="请选择单位">
                  <Option value="t">吨</Option>
                  <Option value="kg">千克</Option>
                  <Option value="m³">立方米</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default MaterialWarehouse; 