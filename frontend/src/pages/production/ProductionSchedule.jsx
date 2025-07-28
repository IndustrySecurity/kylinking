import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Modal, Form, Input, DatePicker, Select, message, Tag, Progress } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, CalendarOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const { RangePicker } = DatePicker;
const { Option } = Select;

const PageContainer = styled.div`
  padding: 24px;
`;

const HeaderSection = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const FilterSection = styled.div`
  background: white;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
`;

const ProductionSchedule = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [form] = Form.useForm();

  // 模拟数据
  const mockData = [
    {
      id: 1,
      planNo: 'PS202412001',
      productName: '牛皮纸袋 25kg',
      quantity: 10000,
      completedQuantity: 8500,
      startDate: '2024-12-01',
      endDate: '2024-12-05',
      status: '进行中',
      priority: '高',
      machine: 'MCL-235',
      operator: '张三',
    },
    {
      id: 2,
      planNo: 'PS202412002',
      productName: '编织袋 50kg',
      quantity: 5000,
      completedQuantity: 5000,
      startDate: '2024-12-02',
      endDate: '2024-12-03',
      status: '已完成',
      priority: '中',
      machine: 'MCL-238',
      operator: '李四',
    },
    {
      id: 3,
      planNo: 'PS202412003',
      productName: '塑料袋 10kg',
      quantity: 8000,
      completedQuantity: 0,
      startDate: '2024-12-06',
      endDate: '2024-12-08',
      status: '待开始',
      priority: '低',
      machine: 'MCL-240',
      operator: '王五',
    },
  ];

  useEffect(() => {
    setData(mockData);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case '已完成':
        return 'success';
      case '进行中':
        return 'processing';
      case '待开始':
        return 'default';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case '高':
        return 'red';
      case '中':
        return 'orange';
      case '低':
        return 'green';
      default:
        return 'default';
    }
  };

  const columns = [
    {
      title: '计划编号',
      dataIndex: 'planNo',
      key: 'planNo',
      width: 120,
    },
    {
      title: '产品名称',
      dataIndex: 'productName',
      key: 'productName',
      width: 150,
    },
    {
      title: '计划数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      render: (text) => text.toLocaleString(),
    },
    {
      title: '完成进度',
      key: 'progress',
      width: 150,
      render: (_, record) => {
        const percent = Math.round((record.completedQuantity / record.quantity) * 100);
        return (
          <div>
            <Progress 
              percent={percent} 
              size="small" 
              status={record.status === '已完成' ? 'success' : 'active'}
            />
            <div style={{ fontSize: '12px', color: '#666' }}>
              {record.completedQuantity.toLocaleString()} / {record.quantity.toLocaleString()}
            </div>
          </div>
        );
      },
    },
    {
      title: '开始日期',
      dataIndex: 'startDate',
      key: 'startDate',
      width: 100,
    },
    {
      title: '结束日期',
      dataIndex: 'endDate',
      key: 'endDate',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => <Tag color={getStatusColor(status)}>{status}</Tag>,
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority) => <Tag color={getPriorityColor(priority)}>{priority}</Tag>,
    },
    {
      title: '设备',
      dataIndex: 'machine',
      key: 'machine',
      width: 100,
    },
    {
      title: '操作员',
      dataIndex: 'operator',
      key: 'operator',
      width: 100,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            size="small"
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            size="small"
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />} 
            size="small"
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const handleAdd = () => {
    setEditingRecord(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingRecord(record);
    form.setFieldsValue({
      productName: record.productName,
      quantity: record.quantity,
      dateRange: [record.startDate, record.endDate],
      priority: record.priority,
      machine: record.machine,
      operator: record.operator,
    });
    setModalVisible(true);
  };

  const handleView = (record) => {
    Modal.info({
      title: '生产计划详情',
      width: 600,
      content: (
        <div>
          <p><strong>计划编号：</strong>{record.planNo}</p>
          <p><strong>产品名称：</strong>{record.productName}</p>
          <p><strong>计划数量：</strong>{record.quantity.toLocaleString()}</p>
          <p><strong>完成数量：</strong>{record.completedQuantity.toLocaleString()}</p>
          <p><strong>开始日期：</strong>{record.startDate}</p>
          <p><strong>结束日期：</strong>{record.endDate}</p>
          <p><strong>状态：</strong>{record.status}</p>
          <p><strong>优先级：</strong>{record.priority}</p>
          <p><strong>设备：</strong>{record.machine}</p>
          <p><strong>操作员：</strong>{record.operator}</p>
        </div>
      ),
    });
  };

  const handleDelete = (record) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除生产计划 "${record.planNo}" 吗？`,
      onOk: () => {
        setData(data.filter(item => item.id !== record.id));
        message.success('删除成功');
      },
    });
  };

  const handleModalOk = () => {
    form.validateFields().then(values => {
      if (editingRecord) {
        // 编辑现有记录
        const updatedData = data.map(item => 
          item.id === editingRecord.id 
            ? { ...item, ...values, startDate: values.dateRange[0], endDate: values.dateRange[1] }
            : item
        );
        setData(updatedData);
        message.success('更新成功');
      } else {
        // 添加新记录
        const newRecord = {
          id: Date.now(),
          planNo: `PS${new Date().getFullYear()}${String(new Date().getMonth() + 1).padStart(2, '0')}${String(Date.now()).slice(-3)}`,
          ...values,
          startDate: values.dateRange[0],
          endDate: values.dateRange[1],
          completedQuantity: 0,
          status: '待开始',
        };
        setData([...data, newRecord]);
        message.success('添加成功');
      }
      setModalVisible(false);
    });
  };

  return (
    <PageContainer>
      <HeaderSection>
        <div>
          <h2 style={{ margin: 0 }}>生产计划管理</h2>
          <p style={{ margin: '8px 0 0 0', color: '#666' }}>
            管理和监控生产计划的制定、执行和完成情况
          </p>
        </div>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={handleAdd}
        >
          新建计划
        </Button>
      </HeaderSection>

      <FilterSection>
        <Space size="large">
          <span>筛选条件：</span>
          <Select placeholder="选择状态" style={{ width: 120 }} allowClear>
            <Option value="待开始">待开始</Option>
            <Option value="进行中">进行中</Option>
            <Option value="已完成">已完成</Option>
          </Select>
          <Select placeholder="选择优先级" style={{ width: 120 }} allowClear>
            <Option value="高">高</Option>
            <Option value="中">中</Option>
            <Option value="低">低</Option>
          </Select>
          <RangePicker placeholder={['开始日期', '结束日期']} />
          <Button type="primary" icon={<CalendarOutlined />}>
            查询
          </Button>
        </Space>
      </FilterSection>

      <Card>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            total: data.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条/共 ${total} 条`,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      <Modal
        title={editingRecord ? '编辑生产计划' : '新建生产计划'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="productName"
            label="产品名称"
            rules={[{ required: true, message: '请输入产品名称' }]}
          >
            <Input placeholder="请输入产品名称" />
          </Form.Item>
          
          <Form.Item
            name="quantity"
            label="计划数量"
            rules={[{ required: true, message: '请输入计划数量' }]}
          >
            <Input type="number" placeholder="请输入计划数量" />
          </Form.Item>
          
          <Form.Item
            name="dateRange"
            label="计划日期"
            rules={[{ required: true, message: '请选择计划日期' }]}
          >
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
          
          <Form.Item
            name="priority"
            label="优先级"
            rules={[{ required: true, message: '请选择优先级' }]}
          >
            <Select placeholder="请选择优先级">
              <Option value="高">高</Option>
              <Option value="中">中</Option>
              <Option value="低">低</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="machine"
            label="生产设备"
            rules={[{ required: true, message: '请选择生产设备' }]}
          >
            <Select placeholder="请选择生产设备">
              <Option value="MCL-235">MCL-235</Option>
              <Option value="MCL-238">MCL-238</Option>
              <Option value="MCL-240">MCL-240</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="operator"
            label="操作员"
            rules={[{ required: true, message: '请选择操作员' }]}
          >
            <Select placeholder="请选择操作员">
              <Option value="张三">张三</Option>
              <Option value="李四">李四</Option>
              <Option value="王五">王五</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default ProductionSchedule; 