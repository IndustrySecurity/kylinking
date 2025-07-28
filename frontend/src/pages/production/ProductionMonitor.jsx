import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Tag, Button, Space, Modal, Descriptions, Alert } from 'antd';
import { 
  PlayCircleOutlined, 
  PauseCircleOutlined, 
  StopOutlined, 
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  EyeOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

const PageContainer = styled.div`
  padding: 24px;
`;

const HeaderSection = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const StatusCard = styled(Card)`
  .ant-card-body {
    padding: 20px;
  }
`;

const MachineStatusCard = styled(Card)`
  margin-bottom: 16px;
  .ant-card-body {
    padding: 16px;
  }
`;

const ProductionMonitor = () => {
  const [loading, setLoading] = useState(false);
  const [machines, setMachines] = useState([]);
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);

  // 模拟数据
  const mockMachines = [
    {
      id: 1,
      name: 'MCL-235',
      status: '运行中',
      currentProduct: '牛皮纸袋 25kg',
      planQuantity: 10000,
      completedQuantity: 8500,
      efficiency: 85,
      temperature: 180,
      pressure: 2.5,
      speed: 120,
      operator: '张三',
      startTime: '2024-12-01 08:00:00',
      estimatedEndTime: '2024-12-01 18:00:00',
      alerts: ['温度偏高', '需要维护'],
    },
    {
      id: 2,
      name: 'MCL-238',
      status: '停机',
      currentProduct: '编织袋 50kg',
      planQuantity: 5000,
      completedQuantity: 5000,
      efficiency: 100,
      temperature: 0,
      pressure: 0,
      speed: 0,
      operator: '李四',
      startTime: '2024-12-02 08:00:00',
      endTime: '2024-12-02 16:00:00',
      alerts: [],
    },
    {
      id: 3,
      name: 'MCL-240',
      status: '待机',
      currentProduct: '塑料袋 10kg',
      planQuantity: 8000,
      completedQuantity: 0,
      efficiency: 0,
      temperature: 25,
      pressure: 0.1,
      speed: 0,
      operator: '王五',
      startTime: null,
      estimatedEndTime: null,
      alerts: ['等待开始'],
    },
  ];

  useEffect(() => {
    setMachines(mockMachines);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case '运行中':
        return 'success';
      case '停机':
        return 'default';
      case '待机':
        return 'warning';
      case '故障':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case '运行中':
        return <PlayCircleOutlined style={{ color: '#52c41a' }} />;
      case '停机':
        return <StopOutlined style={{ color: '#d9d9d9' }} />;
      case '待机':
        return <PauseCircleOutlined style={{ color: '#faad14' }} />;
      case '故障':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <ClockCircleOutlined />;
    }
  };

  const handleViewDetail = (machine) => {
    setSelectedMachine(machine);
    setDetailModalVisible(true);
  };

  const handleControl = (machine, action) => {
    Modal.confirm({
      title: '确认操作',
      content: `确定要${action}设备 ${machine.name} 吗？`,
      onOk: () => {
        // 这里可以调用API进行设备控制
        message.success(`${action}操作已发送`);
      },
    });
  };

  const columns = [
    {
      title: '设备名称',
      dataIndex: 'name',
      key: 'name',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
          {status}
        </Tag>
      ),
    },
    {
      title: '当前产品',
      dataIndex: 'currentProduct',
      key: 'currentProduct',
      width: 150,
    },
    {
      title: '完成进度',
      key: 'progress',
      width: 150,
      render: (_, record) => {
        const percent = Math.round((record.completedQuantity / record.planQuantity) * 100);
        return (
          <div>
            <Progress 
              percent={percent} 
              size="small" 
              status={record.status === '停机' ? 'success' : 'active'}
            />
            <div style={{ fontSize: '12px', color: '#666' }}>
              {record.completedQuantity.toLocaleString()} / {record.planQuantity.toLocaleString()}
            </div>
          </div>
        );
      },
    },
    {
      title: '效率',
      dataIndex: 'efficiency',
      key: 'efficiency',
      width: 80,
      render: (efficiency) => `${efficiency}%`,
    },
    {
      title: '温度(°C)',
      dataIndex: 'temperature',
      key: 'temperature',
      width: 100,
    },
    {
      title: '压力(MPa)',
      dataIndex: 'pressure',
      key: 'pressure',
      width: 100,
    },
    {
      title: '速度(rpm)',
      dataIndex: 'speed',
      key: 'speed',
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
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            size="small"
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          {record.status === '运行中' && (
            <>
              <Button 
                type="link" 
                icon={<PauseCircleOutlined />} 
                size="small"
                onClick={() => handleControl(record, '暂停')}
              >
                暂停
              </Button>
              <Button 
                type="link" 
                danger 
                icon={<StopOutlined />} 
                size="small"
                onClick={() => handleControl(record, '停止')}
              >
                停止
              </Button>
            </>
          )}
          {record.status === '待机' && (
            <Button 
              type="link" 
              icon={<PlayCircleOutlined />} 
              size="small"
              onClick={() => handleControl(record, '启动')}
            >
              启动
            </Button>
          )}
        </Space>
      ),
    },
  ];

  // 计算统计数据
  const totalMachines = machines.length;
  const runningMachines = machines.filter(m => m.status === '运行中').length;
  const stoppedMachines = machines.filter(m => m.status === '停机').length;
  const idleMachines = machines.filter(m => m.status === '待机').length;
  const faultMachines = machines.filter(m => m.status === '故障').length;
  const totalEfficiency = machines.length > 0 
    ? Math.round(machines.reduce((sum, m) => sum + m.efficiency, 0) / machines.length)
    : 0;

  return (
    <PageContainer>
      <HeaderSection>
        <div>
          <h2 style={{ margin: 0 }}>生产监控</h2>
          <p style={{ margin: '8px 0 0 0', color: '#666' }}>
            实时监控生产设备状态、运行参数和生产进度
          </p>
        </div>
        <Button 
          icon={<ReloadOutlined />}
          onClick={() => {
            setLoading(true);
            setTimeout(() => setLoading(false), 1000);
          }}
        >
          刷新数据
        </Button>
      </HeaderSection>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <StatusCard>
            <Statistic
              title="设备总数"
              value={totalMachines}
              valueStyle={{ color: '#1890ff' }}
            />
          </StatusCard>
        </Col>
        <Col span={4}>
          <StatusCard>
            <Statistic
              title="运行中"
              value={runningMachines}
              valueStyle={{ color: '#52c41a' }}
              prefix={<PlayCircleOutlined />}
            />
          </StatusCard>
        </Col>
        <Col span={4}>
          <StatusCard>
            <Statistic
              title="停机"
              value={stoppedMachines}
              valueStyle={{ color: '#d9d9d9' }}
              prefix={<StopOutlined />}
            />
          </StatusCard>
        </Col>
        <Col span={4}>
          <StatusCard>
            <Statistic
              title="待机"
              value={idleMachines}
              valueStyle={{ color: '#faad14' }}
              prefix={<PauseCircleOutlined />}
            />
          </StatusCard>
        </Col>
        <Col span={4}>
          <StatusCard>
            <Statistic
              title="故障"
              value={faultMachines}
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </StatusCard>
        </Col>
        <Col span={4}>
          <StatusCard>
            <Statistic
              title="平均效率"
              value={totalEfficiency}
              suffix="%"
              valueStyle={{ color: '#722ed1' }}
              prefix={<CheckCircleOutlined />}
            />
          </StatusCard>
        </Col>
      </Row>

      {/* 设备状态表格 */}
      <Card title="设备状态监控" extra={<span>最后更新: {new Date().toLocaleString()}</span>}>
        <Table
          columns={columns}
          dataSource={machines}
          rowKey="id"
          loading={loading}
          pagination={false}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 设备详情模态框 */}
      <Modal
        title={`设备详情 - ${selectedMachine?.name}`}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedMachine && (
          <div>
            <Descriptions bordered column={2} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="设备名称">{selectedMachine.name}</Descriptions.Item>
              <Descriptions.Item label="运行状态">
                <Tag color={getStatusColor(selectedMachine.status)}>
                  {selectedMachine.status}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="当前产品">{selectedMachine.currentProduct}</Descriptions.Item>
              <Descriptions.Item label="操作员">{selectedMachine.operator}</Descriptions.Item>
              <Descriptions.Item label="计划数量">{selectedMachine.planQuantity.toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="完成数量">{selectedMachine.completedQuantity.toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="运行效率">{selectedMachine.efficiency}%</Descriptions.Item>
              <Descriptions.Item label="当前温度">{selectedMachine.temperature}°C</Descriptions.Item>
              <Descriptions.Item label="当前压力">{selectedMachine.pressure} MPa</Descriptions.Item>
              <Descriptions.Item label="运行速度">{selectedMachine.speed} rpm</Descriptions.Item>
              <Descriptions.Item label="开始时间">{selectedMachine.startTime || '-'}</Descriptions.Item>
              <Descriptions.Item label="预计结束">{selectedMachine.estimatedEndTime || '-'}</Descriptions.Item>
            </Descriptions>

            {selectedMachine.alerts.length > 0 && (
              <Alert
                message="设备告警"
                description={
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    {selectedMachine.alerts.map((alert, index) => (
                      <li key={index}>{alert}</li>
                    ))}
                  </ul>
                }
                type="warning"
                showIcon
                style={{ marginTop: 16 }}
              />
            )}

            <div style={{ marginTop: 16 }}>
              <Progress
                percent={Math.round((selectedMachine.completedQuantity / selectedMachine.planQuantity) * 100)}
                status={selectedMachine.status === '停机' ? 'success' : 'active'}
                format={(percent) => `完成度 ${percent}%`}
              />
            </div>
          </div>
        )}
      </Modal>
    </PageContainer>
  );
};

export default ProductionMonitor; 