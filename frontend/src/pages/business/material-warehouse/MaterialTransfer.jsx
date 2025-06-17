import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Button, Input, Select, Form, Modal, message, Space, Tag, Typography, DatePicker } from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckOutlined,
  CloseOutlined,
  ReloadOutlined,
  EyeOutlined,
  SwapOutlined,
  PlayCircleOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

const { Title } = Typography;
const { Search } = Input;
const { Option } = Select;
const { TextArea } = Input;

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

const MaterialTransfer = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [form] = Form.useForm();

  // 模拟数据
  const mockData = [
    {
      key: '1',
      transferNumber: 'TRF202412250001',
      transferDate: '2024-12-25',
      fromWarehouse: '原材料一库',
      toWarehouse: '原材料二库',
      transferPerson: '张三',
      department: '仓储部',
      status: 'draft',
      approvalStatus: 'pending',
      totalQuantity: 200,
      totalAmount: 3000,
      reason: '库存调整',
    },
    {
      key: '2',
      transferNumber: 'TRF202412250002',
      transferDate: '2024-12-25',
      fromWarehouse: '原材料二库',
      toWarehouse: '辅料仓库',
      transferPerson: '李四',
      department: '仓储部',
      status: 'confirmed',
      approvalStatus: 'approved',
      totalQuantity: 150,
      totalAmount: 2250,
      reason: '生产需要',
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

  const handleCreateTransfer = () => {
    setSelectedRecord(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditTransfer = (record) => {
    setSelectedRecord(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleViewDetail = (record) => {
    setSelectedRecord(record);
    setDetailModalVisible(true);
  };

  const handleApprove = (record) => {
    Modal.confirm({
      title: '确认审核',
      content: `确定要审核通过调拨单 ${record.transferNumber} 吗？`,
      onOk: () => {
        message.success('审核通过');
        loadData();
      },
    });
  };

  const handleReject = (record) => {
    Modal.confirm({
      title: '确认拒绝',
      content: `确定要拒绝调拨单 ${record.transferNumber} 吗？`,
      onOk: () => {
        message.success('已拒绝');
        loadData();
      },
    });
  };

  const handleExecute = (record) => {
    Modal.confirm({
      title: '确认执行',
      content: `确定要执行调拨单 ${record.transferNumber} 吗？执行后将进行库存转移。`,
      onOk: () => {
        message.success('执行成功，库存已转移');
        loadData();
      },
    });
  };

  const getStatusTag = (status) => {
    const statusMap = {
      draft: { color: 'default', text: '草稿' },
      confirmed: { color: 'blue', text: '已确认' },
      in_progress: { color: 'processing', text: '执行中' },
      completed: { color: 'success', text: '已完成' },
      cancelled: { color: 'error', text: '已取消' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const getApprovalStatusTag = (status) => {
    const statusMap = {
      pending: { color: 'warning', text: '待审核' },
      approved: { color: 'success', text: '已审核' },
      rejected: { color: 'error', text: '已拒绝' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const columns = [
    {
      title: '调拨单号',
      dataIndex: 'transferNumber',
      key: 'transferNumber',
      width: 150,
    },
    {
      title: '调拨日期',
      dataIndex: 'transferDate',
      key: 'transferDate',
      width: 120,
    },
    {
      title: '调出仓库',
      dataIndex: 'fromWarehouse',
      key: 'fromWarehouse',
      width: 120,
    },
    {
      title: '调入仓库',
      dataIndex: 'toWarehouse',
      key: 'toWarehouse',
      width: 120,
    },
    {
      title: '调拨人',
      dataIndex: 'transferPerson',
      key: 'transferPerson',
      width: 100,
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      width: 100,
    },
    {
      title: '单据状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status),
    },
    {
      title: '审核状态',
      dataIndex: 'approvalStatus',
      key: 'approvalStatus',
      width: 100,
      render: (status) => getApprovalStatusTag(status),
    },
    {
      title: '总数量',
      dataIndex: 'totalQuantity',
      key: 'totalQuantity',
      width: 100,
      align: 'right',
    },
    {
      title: '总金额',
      dataIndex: 'totalAmount',
      key: 'totalAmount',
      width: 100,
      align: 'right',
      render: (amount) => `¥${amount?.toLocaleString()}`,
    },
    {
      title: '调拨原因',
      dataIndex: 'reason',
      key: 'reason',
      width: 120,
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => handleViewDetail(record)}>
            查看
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEditTransfer(record)}>
            编辑
          </Button>
          {record.approvalStatus === 'pending' && (
            <>
              <Button type="link" size="small" icon={<CheckOutlined />} onClick={() => handleApprove(record)}>
                审核
              </Button>
              <Button type="link" size="small" danger icon={<CloseOutlined />} onClick={() => handleReject(record)}>
                拒绝
              </Button>
            </>
          )}
          {record.approvalStatus === 'approved' && record.status === 'confirmed' && (
            <Button type="link" size="small" icon={<PlayCircleOutlined />} onClick={() => handleExecute(record)}>
              执行
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <SectionTitle level={4}>材料调拨管理</SectionTitle>
      
      <StyledCard>
        {/* 操作按钮栏 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateTransfer}>
              新增调拨单
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
              placeholder="搜索调拨单号、仓库..."
              allowClear
              style={{ width: 300 }}
            />
          </Col>
        </Row>

        {/* 数据表格 */}
        <Table
          columns={columns}
          dataSource={data}
          loading={loading}
          scroll={{ x: 1400 }}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
          }}
        />
      </StyledCard>

      {/* 新增/编辑弹窗 */}
      <Modal
        title={selectedRecord ? "编辑调拨单" : "新增调拨单"}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => {
          form.validateFields().then((values) => {
            console.log('Form values:', values);
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
              <Form.Item label="调拨日期" name="transferDate" rules={[{ required: true, message: '请选择调拨日期' }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="调拨人" name="transferPerson" rules={[{ required: true, message: '请输入调拨人' }]}>
                <Input placeholder="请输入调拨人" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="调出仓库" name="fromWarehouseId" rules={[{ required: true, message: '请选择调出仓库' }]}>
                <Select placeholder="请选择调出仓库">
                  <Option value="1">原材料一库</Option>
                  <Option value="2">原材料二库</Option>
                  <Option value="3">辅料仓库</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="调入仓库" name="toWarehouseId" rules={[{ required: true, message: '请选择调入仓库' }]}>
                <Select placeholder="请选择调入仓库">
                  <Option value="1">原材料一库</Option>
                  <Option value="2">原材料二库</Option>
                  <Option value="3">辅料仓库</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="部门" name="department" rules={[{ required: true, message: '请输入部门' }]}>
                <Input placeholder="请输入部门" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="调拨类型" name="transferType">
                <Select placeholder="请选择调拨类型">
                  <Option value="warehouse_transfer">仓库间调拨</Option>
                  <Option value="location_transfer">库位调拨</Option>
                  <Option value="emergency_transfer">紧急调拨</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item label="调拨原因" name="reason" rules={[{ required: true, message: '请输入调拨原因' }]}>
                <TextArea rows={2} placeholder="请输入调拨原因" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item label="备注" name="notes">
                <TextArea rows={3} placeholder="请输入备注" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 详情查看弹窗 */}
      <Modal
        title="调拨单详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={1000}
      >
        {selectedRecord && (
          <div>
            <Row gutter={16}>
              <Col span={8}>
                <p><strong>调拨单号:</strong> {selectedRecord.transferNumber}</p>
              </Col>
              <Col span={8}>
                <p><strong>调拨日期:</strong> {selectedRecord.transferDate}</p>
              </Col>
              <Col span={8}>
                <p><strong>调拨人:</strong> {selectedRecord.transferPerson}</p>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <p><strong>调出仓库:</strong> {selectedRecord.fromWarehouse}</p>
              </Col>
              <Col span={8}>
                <p><strong>调入仓库:</strong> {selectedRecord.toWarehouse}</p>
              </Col>
              <Col span={8}>
                <p><strong>部门:</strong> {selectedRecord.department}</p>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <p><strong>状态:</strong> {getStatusTag(selectedRecord.status)}</p>
              </Col>
              <Col span={8}>
                <p><strong>审核状态:</strong> {getApprovalStatusTag(selectedRecord.approvalStatus)}</p>
              </Col>
              <Col span={8}>
                <p><strong>总数量:</strong> {selectedRecord.totalQuantity}</p>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <p><strong>总金额:</strong> ¥{selectedRecord.totalAmount?.toLocaleString()}</p>
              </Col>
              <Col span={12}>
                <p><strong>调拨原因:</strong> {selectedRecord.reason}</p>
              </Col>
            </Row>
            {/* TODO: 添加调拨明细表格 */}
            <div style={{ marginTop: 16 }}>
              <h4>调拨明细</h4>
              <p>此处将显示调拨明细信息...</p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default MaterialTransfer; 