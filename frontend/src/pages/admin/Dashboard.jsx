import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Typography, 
  Table, 
  Tag, 
  Button, 
  Space,
  Spin,
  Avatar,
  Tooltip,
  Divider,
  Calendar,
  Badge,
  message
} from 'antd';
import {
  TeamOutlined,
  CloudServerOutlined,
  BarChartOutlined,
  SafetyOutlined,
  DashboardOutlined,
  RiseOutlined,
  FallOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  ClockCircleOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';
import ReactECharts from 'echarts-for-react';

const { Title, Text } = Typography;

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    tenants: { total: 0, active: 0 },
    users: { total: 0, admin: 0 },
    growth: { tenants: 0, users: 0 }
  });
  const [recentTenants, setRecentTenants] = useState([]);
  const [activities, setActivities] = useState([]);
  const navigate = useNavigate();
  const api = useApi();

  // 获取仪表盘数据
  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // 获取API统计数据，使用正确的API路径
      const response = await api.get('/admin/stats');
      
      if (response.data && response.data.stats) {
        // 使用实际API返回的数据
        setStats({
          tenants: { 
            total: response.data.stats.tenants.total || 0, 
            active: response.data.stats.tenants.active || 0
          },
          users: { 
            total: response.data.stats.users.total || 0, 
            admin: response.data.stats.users.admin || 0
          },
          growth: { 
            tenants: response.data.stats.growth?.tenants || 0,
            users: response.data.stats.growth?.users || 0
          }
        });
        
        // 使用API返回的最近租户数据
        setRecentTenants(response.data.recent_tenants || []);
      } else {
        message.error('获取统计数据失败，返回数据格式不正确');
      }
      
      // 使用API返回的系统活动数据
      setActivities(response.data.activities || []);
    } catch (error) {
      message.error('获取仪表盘数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // 租户增长图表选项
  const getTenantGrowthOptions = () => {
    return {
      title: {
        text: '租户增长趋势',
        subtext: '最近6个月',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '新增租户',
          type: 'line',
          smooth: true,
          data: [3, 5, 8, 12, 6, 9],
          itemStyle: {
            color: '#1890ff'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: 'rgba(24, 144, 255, 0.5)'
                },
                {
                  offset: 1,
                  color: 'rgba(24, 144, 255, 0.1)'
                }
              ]
            }
          }
        }
      ]
    };
  };

  // 用户分布图表选项
  const getUserDistributionOptions = () => {
    return {
      title: {
        text: '用户分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '用户类型',
          type: 'pie',
          radius: '60%',
          center: ['50%', '60%'],
          data: [
            { value: stats.users.admin, name: '管理员' },
            { value: stats.users.total - stats.users.admin, name: '普通用户' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
  };

  // 租户状态图表选项
  const getTenantStatusOptions = () => {
    return {
      title: {
        text: '租户状态分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '租户状态',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '20',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: stats.tenants.active, name: '活跃租户', itemStyle: { color: '#52c41a' } },
            { value: stats.tenants.total - stats.tenants.active, name: '停用租户', itemStyle: { color: '#f5222d' } }
          ]
        }
      ]
    };
  };

  // 最近租户列
  const recentTenantsColumns = [
    {
      title: '租户名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <Avatar 
            style={{ 
              backgroundColor: record.is_active ? '#1890ff' : '#f5222d',
              verticalAlign: 'middle' 
            }}
          >
            {text.charAt(0).toUpperCase()}
          </Avatar>
          <Text>{text}</Text>
        </Space>
      ),
    },
    {
      title: '标识',
      dataIndex: 'slug',
      key: 'slug',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'success' : 'error'}>
          {isActive ? '活跃' : '停用'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button 
          type="link" 
          icon={<EyeOutlined />}
          onClick={() => navigate(`/admin/tenants/${record.id}`)}
        >
          查看
        </Button>
      ),
    },
  ];

  // 系统活动列
  const activitiesColumns = [
    {
      title: '用户',
      dataIndex: 'user',
      key: 'user',
      width: 150,
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 150,
    },
    {
      title: '对象',
      dataIndex: 'target',
      key: 'target',
      width: 150,
    },
    {
      title: '时间',
      dataIndex: 'time',
      key: 'time',
      render: (date) => new Date(date).toLocaleString(),
    },
  ];

  // 日历数据
  const getCalendarData = (value) => {
    // 使用API返回的日历数据
    const listData = activities.filter(activity => {
      const activityDate = new Date(activity.time);
      const valueDate = value.toDate();
      return activityDate.getDate() === valueDate.getDate() &&
             activityDate.getMonth() === valueDate.getMonth() &&
             activityDate.getFullYear() === valueDate.getFullYear();
    }).map(activity => ({
      type: 'processing',
      content: activity.action
    }));
    
    return listData;
  };
  
  const dateCellRender = (value) => {
    const listData = getCalendarData(value);
    return (
      <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
        {listData.map((item, index) => (
          <li key={index}>
            <Badge status={item.type} text={item.content} />
          </li>
        ))}
      </ul>
    );
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <Title level={2}>
        <DashboardOutlined /> 系统仪表盘
      </Title>
      <Divider />
      
      <Row gutter={[24, 24]}>
        {/* 统计卡片 */}
        <Col xs={24} sm={12} lg={6}>
          <Card 
            hoverable 
            className="statistic-card"
            style={{ 
              background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
              color: 'white'
            }}
          >
            <Statistic
              title={<Text style={{ color: 'white' }}>总租户数</Text>}
              value={stats.tenants.total}
              valueStyle={{ color: 'white' }}
              prefix={<CloudServerOutlined />}
              suffix={
                <Tooltip title="较上月增长">
                  <span style={{ fontSize: '16px', marginLeft: '8px' }}>
                    <ArrowUpOutlined /> {stats.growth.tenants}%
                  </span>
                </Tooltip>
              }
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card 
            hoverable 
            className="statistic-card"
            style={{ 
              background: 'linear-gradient(135deg, #52c41a 0%, #389e0d 100%)',
              color: 'white'
            }}
          >
            <Statistic
              title={<Text style={{ color: 'white' }}>活跃租户</Text>}
              value={stats.tenants.active}
              valueStyle={{ color: 'white' }}
              prefix={<RiseOutlined />}
              suffix={
                <Tooltip title="占总租户比例">
                  <span style={{ fontSize: '16px', marginLeft: '8px' }}>
                    {Math.round((stats.tenants.active / stats.tenants.total) * 100)}%
                  </span>
                </Tooltip>
              }
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card 
            hoverable 
            className="statistic-card"
            style={{ 
              background: 'linear-gradient(135deg, #722ed1 0%, #531dab 100%)',
              color: 'white'
            }}
          >
            <Statistic
              title={<Text style={{ color: 'white' }}>总用户数</Text>}
              value={stats.users.total}
              valueStyle={{ color: 'white' }}
              prefix={<TeamOutlined />}
              suffix={
                <Tooltip title="较上月增长">
                  <span style={{ fontSize: '16px', marginLeft: '8px' }}>
                    <ArrowUpOutlined /> {stats.growth.users}%
                  </span>
                </Tooltip>
              }
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card 
            hoverable 
            className="statistic-card"
            style={{ 
              background: 'linear-gradient(135deg, #fa8c16 0%, #d46b08 100%)',
              color: 'white'
            }}
          >
            <Statistic
              title={<Text style={{ color: 'white' }}>管理员数</Text>}
              value={stats.users.admin}
              valueStyle={{ color: 'white' }}
              prefix={<SafetyOutlined />}
              suffix={
                <Tooltip title="占总用户比例">
                  <span style={{ fontSize: '16px', marginLeft: '8px' }}>
                    {Math.round((stats.users.admin / stats.users.total) * 100)}%
                  </span>
                </Tooltip>
              }
            />
          </Card>
        </Col>
        
        {/* 图表 */}
        <Col xs={24} lg={12}>
          <Card title="租户增长趋势" className="chart-card">
            <ReactECharts option={getTenantGrowthOptions()} style={{ height: 300 }} />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card title="用户分布" className="chart-card">
            <ReactECharts option={getUserDistributionOptions()} style={{ height: 300 }} />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card title="租户状态" className="chart-card">
            <ReactECharts option={getTenantStatusOptions()} style={{ height: 300 }} />
          </Card>
        </Col>
        
        {/* 最近的租户 */}
        <Col span={24}>
          <Card 
            title={
              <span>
                <CloudServerOutlined /> 最近新增租户
              </span>
            }
            extra={
              <Button type="link" onClick={() => navigate('/admin/tenants')}>
                查看全部
              </Button>
            }
          >
            <Table 
              columns={recentTenantsColumns} 
              dataSource={recentTenants}
              rowKey="id"
              pagination={false}
            />
          </Card>
        </Col>
        
        {/* 系统活动 */}
        <Col xs={24} lg={16}>
          <Card 
            title={
              <span>
                <ClockCircleOutlined /> 系统活动日志
              </span>
            }
            className="activities-card"
          >
            <Table 
              columns={activitiesColumns} 
              dataSource={activities}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        
        {/* 日历 */}
        <Col xs={24} lg={8}>
          <Card 
            title={
              <span>
                <CalendarOutlined /> 系统日程
              </span>
            }
            className="calendar-card"
          >
            <Calendar 
              fullscreen={false} 
              dateCellRender={dateCellRender}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 