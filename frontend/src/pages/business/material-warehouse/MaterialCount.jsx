import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Button, Input, Select, Form, Modal, message, Space, Tag, Typography, DatePicker, Progress } from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckOutlined,
  CloseOutlined,
  ReloadOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

const { Title } = Typography;
const { Search } = Input;
const { Option } = Select;
const { TextArea } = Input;
const { RangePicker } = DatePicker;

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

const MaterialCount = () => {
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
      planNumber: 'CNT202412250001',
      planName: '材料仓库年末盘点',
      countType: 'full',
      planStartDate: '2024-12-25',
      planEndDate: '2024-12-27',
      warehouseNames: ['原材料一库', '原材料二库'],
      supervisor: '张主管',
      status: 'confirmed',
      progress: 65,
      totalItems: 150,
      countedItems: 98,
    },
    {
      key: '2',
      planNumber: 'CNT202412250002',
      planName: '重要材料抽盘',
      countType: 'spot',
      planStartDate: '2024-12-25',
      planEndDate: '2024-12-25',
      warehouseNames: ['原材料一库'],
      supervisor: '李主管',
      status: 'in_progress',
      progress: 80,
      totalItems: 50,
      countedItems: 40,
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

  const handleCreatePlan = () => {
    setSelectedRecord(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditPlan = (record) => {
    setSelectedRecord(record);
    form.setFieldsValue({
      ...record,
      planDateRange: [record.planStartDate, record.planEndDate]
    });
    setModalVisible(true);
  };

  const handleViewDetail = (record) => {
    setSelectedRecord(record);
    setDetailModalVisible(true);
  };

  const handleStartCount = (record) => {
    Modal.confirm({
      title: '确认开始盘点',
      content: `确定要开始盘点计划 ${record.planNumber} 吗？`,
      onOk: () => {
        message.success('盘点已开始');
        loadData();
      },
    });
  };

  const handleCompleteCount = (record) => {
    Modal.confirm({
      title: '确认完成盘点',
      content: `确定要完成盘点计划 ${record.planNumber} 吗？`,
      onOk: () => {
        message.success('盘点已完成');
        loadData();
      },
    });
  };

  const getCountTypeTag = (type) => {
    const typeMap = {
      full: { color: 'blue', text: '全盘' },
      partial: { color: 'green', text: '部分盘点' },
      spot: { color: 'orange', text: '抽盘' },
      cycle: { color: 'purple', text: '循环盘点' },
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const getStatusTag = (status) => {
    const statusMap = {
      draft: { color: 'default', text: '草稿' },
      confirmed: { color: 'blue', text: '已确认' },
      in_progress: { color: 'processing', text: '盘点中' },
      completed: { color: 'success', text: '已完成' },
      cancelled: { color: 'error', text: '已取消' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const columns = [
    {
      title: '盘点计划号',
      dataIndex: 'planNumber',
      key: 'planNumber',
      width: 150,
    },
    {
      title: '计划名称',
      dataIndex: 'planName',
      key: 'planName',
      width: 200,
    },
    {
      title: '盘点类型',
      dataIndex: 'countType',
      key: 'countType',
      width: 100,
      render: (type) => getCountTypeTag(type),
    },
    {
      title: '计划时间',
      key: 'planDate',
      width: 200,
      render: (_, record) => `${record.planStartDate} ~ ${record.planEndDate}`,
    },
    {
      title: '仓库',
      dataIndex: 'warehouseNames',
      key: 'warehouseNames',
      width: 150,
      render: (warehouses) => warehouses?.join(', '),
    },
    {
      title: '监盘人',
      dataIndex: 'supervisor',
      key: 'supervisor',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status),
    },
    {
      title: '进度',
      key: 'progress',
      width: 150,
      render: (_, record) => (
        <div>
          <Progress percent={record.progress} size="small" />
          <span style={{ fontSize: '12px', color: '#666' }}>
            {record.countedItems}/{record.totalItems}
          </span>
        </div>
      ),
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
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEditPlan(record)}>
            编辑
          </Button>
          {record.status === 'confirmed' && (
            <Button type="link" size="small" icon={<PlayCircleOutlined />} onClick={() => handleStartCount(record)}>
              开始
            </Button>
          )}
          {record.status === 'in_progress' && (
            <Button type="link" size="small" icon={<CheckOutlined />} onClick={() => handleCompleteCount(record)}>
              完成
            </Button>
          )}
          <Button type="link" size="small" icon={<FileTextOutlined />}>
            报告
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <SectionTitle level={4}>材料盘点管理</SectionTitle>
      
      <StyledCard>
        {/* 操作按钮栏 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreatePlan}>
              新增盘点计划
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
              placeholder="搜索计划号、计划名称..."
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
          scroll={{ x: 1300 }}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
          }}
        />
      </StyledCard>

      {/* 新增/编辑弹窗 */}
      <Modal
        title={selectedRecord ? "编辑盘点计划" : "新增盘点计划"}
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
              <Form.Item label="计划名称" name="planName" rules={[{ required: true, message: '请输入计划名称' }]}>
                <Input placeholder="请输入计划名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="盘点类型" name="countType" rules={[{ required: true, message: '请选择盘点类型' }]}>
                <Select placeholder="请选择盘点类型">
                  <Option value="full">全盘</Option>
                  <Option value="partial">部分盘点</Option>
                  <Option value="spot">抽盘</Option>
                  <Option value="cycle">循环盘点</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="计划时间" name="planDateRange" rules={[{ required: true, message: '请选择计划时间' }]}>
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="监盘人" name="supervisor" rules={[{ required: true, message: '请输入监盘人' }]}>
                <Input placeholder="请输入监盘人" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item label="盘点仓库" name="warehouseIds" rules={[{ required: true, message: '请选择盘点仓库' }]}>
                <Select mode="multiple" placeholder="请选择盘点仓库">
                  <Option value="1">原材料一库</Option>
                  <Option value="2">原材料二库</Option>
                  <Option value="3">辅料仓库</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item label="盘点小组" name="countTeam">
                <Select mode="tags" placeholder="请输入盘点小组成员">
                  <Option value="张三">张三</Option>
                  <Option value="李四">李四</Option>
                  <Option value="王五">王五</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item label="盘点说明" name="description">
                <TextArea rows={3} placeholder="请输入盘点说明" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 详情查看弹窗 */}
      <Modal
        title="盘点计划详情"
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
                <p><strong>计划号:</strong> {selectedRecord.planNumber}</p>
              </Col>
              <Col span={8}>
                <p><strong>计划名称:</strong> {selectedRecord.planName}</p>
              </Col>
              <Col span={8}>
                <p><strong>盘点类型:</strong> {getCountTypeTag(selectedRecord.countType)}</p>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <p><strong>开始时间:</strong> {selectedRecord.planStartDate}</p>
              </Col>
              <Col span={8}>
                <p><strong>结束时间:</strong> {selectedRecord.planEndDate}</p>
              </Col>
              <Col span={8}>
                <p><strong>监盘人:</strong> {selectedRecord.supervisor}</p>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <p><strong>状态:</strong> {getStatusTag(selectedRecord.status)}</p>
              </Col>
              <Col span={8}>
                <p><strong>进度:</strong> {selectedRecord.progress}%</p>
              </Col>
              <Col span={8}>
                <p><strong>盘点项目:</strong> {selectedRecord.countedItems}/{selectedRecord.totalItems}</p>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={24}>
                <p><strong>盘点仓库:</strong> {selectedRecord.warehouseNames?.join(', ')}</p>
              </Col>
            </Row>
            {/* TODO: 添加盘点记录表格 */}
            <div style={{ marginTop: 16 }}>
              <h4>盘点记录</h4>
              <p>此处将显示详细的盘点记录信息...</p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default MaterialCount; 