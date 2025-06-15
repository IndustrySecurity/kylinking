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

const StyledCard = styled(Card)`
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: none;
`;

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

const FinishedGoodsOutbound = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const mockData = [
    {
      key: '1',
      outboundNo: 'CK202401001',
      productName: 'PET薄膜',
      specification: '12μm×1000mm',
      quantity: 500,
      unit: 'kg',
      customer: '客户A',
      outboundDate: '2024-01-15',
      status: '已出库',
    },
    {
      key: '2',
      outboundNo: 'CK202401002',
      productName: 'BOPP薄膜',
      specification: '15μm×1200mm',
      quantity: 300,
      unit: 'kg',
      customer: '客户B',
      outboundDate: '2024-01-16',
      status: '待出库',
    },
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setLoading(true);
    setTimeout(() => {
      setData(mockData);
      setLoading(false);
    }, 1000);
  };

  const columns = [
    {
      title: '出库单号',
      dataIndex: 'outboundNo',
      key: 'outboundNo',
    },
    {
      title: '产品名称',
      dataIndex: 'productName',
      key: 'productName',
    },
    {
      title: '规格',
      dataIndex: 'specification',
      key: 'specification',
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (quantity, record) => `${quantity} ${record.unit}`,
    },
    {
      title: '客户',
      dataIndex: 'customer',
      key: 'customer',
    },
    {
      title: '出库日期',
      dataIndex: 'outboundDate',
      key: 'outboundDate',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === '已出库' ? 'green' : 'orange'}>
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
      <SectionTitle level={4}>成品出库管理</SectionTitle>
      
      <StyledCard>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
              新增出库单
            </Button>
          </Col>
          <Col>
            <Button icon={<ImportOutlined />}>导入</Button>
          </Col>
          <Col>
            <Button icon={<ExportOutlined />}>导出</Button>
          </Col>
          <Col>
            <Button icon={<ReloadOutlined />} onClick={loadData}>刷新</Button>
          </Col>
          <Col flex="auto" />
          <Col>
            <Search placeholder="搜索出库单号、产品名称..." allowClear style={{ width: 250 }} />
          </Col>
        </Row>

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

      <Modal
        title="新增出库单"
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
              <Form.Item label="产品名称" name="productName" rules={[{ required: true }]}>
                <Select placeholder="请选择产品">
                  <Option value="PET薄膜">PET薄膜</Option>
                  <Option value="BOPP薄膜">BOPP薄膜</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="规格" name="specification" rules={[{ required: true }]}>
                <Input placeholder="请输入规格" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="数量" name="quantity" rules={[{ required: true }]}>
                <Input type="number" placeholder="请输入数量" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="客户" name="customer" rules={[{ required: true }]}>
                <Select placeholder="请选择客户">
                  <Option value="客户A">客户A</Option>
                  <Option value="客户B">客户B</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default FinishedGoodsOutbound; 