import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Space,
  Row,
  Col,
  Tag,
  Statistic,
  Typography,
  Tooltip,
  Badge,
  Collapse,
  message
} from 'antd';
import { 
  SearchOutlined,
  ReloadOutlined,
  FilterOutlined,
  BarChartOutlined,
  DownloadOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import dayjs from 'dayjs';
import { useApi } from '../../hooks/useApi';
import { inventoryService, baseDataService } from '../../services/inventoryService';
import request from '../../utils/request';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title, Text } = Typography;

// 页面容器
const PageContainer = styled.div`
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
`;

// 卡片样式
const StyledCard = styled(Card)`
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
  
  .ant-card-head {
    border-bottom: 1px solid #f0f0f0;
    background: #fafafa;
  }
  
  .ant-card-head-title {
    font-weight: 600;
  }
`;

// 操作按钮
const ActionButton = styled(Button)`
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

// 统计卡片
const StatCard = styled(Card)`
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  
  .ant-card-body {
    padding: 20px;
  }
  
  .ant-statistic-title {
    color: rgba(255, 255, 255, 0.8);
    font-size: 14px;
  }
  
  .ant-statistic-content {
    color: white;
  }
`;

// 状态标签样式
const getStatusTag = (status, type = 'inventory') => {
  const statusConfig = {
    inventory: {
      normal: { color: 'green', text: '正常' },
      blocked: { color: 'red', text: '冻结' },
      quarantine: { color: 'orange', text: '隔离' },
      damaged: { color: 'volcano', text: '损坏' }
    },
    quality: {
      qualified: { color: 'green', text: '合格' },
      unqualified: { color: 'red', text: '不合格' },
      pending: { color: 'orange', text: '待检' }
    }
  };
  
  const config = statusConfig[type][status] || { color: 'default', text: status };
  return <Tag color={config.color}>{config.text}</Tag>;
};

// 预警状态图标
const getWarningIcon = (current, safety, min) => {
  if (current <= safety) {
    return <Tooltip title="低于安全库存"><WarningOutlined style={{ color: '#f5222d' }} /></Tooltip>;
  }
  if (current <= min) {
    return <Tooltip title="低于最小库存"><ExclamationCircleOutlined style={{ color: '#fa8c16' }} /></Tooltip>;
  }
  return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
};

const InventoryOverview = () => {
  const api = useApi();
  const [form] = Form.useForm();
  
  // 状态管理
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });
  
  // 基础数据
  const [warehouses, setWarehouses] = useState([]);
  const [products, setProducts] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [statistics, setStatistics] = useState({
    totalItems: 0,
    totalValue: 0,
    lowStockItems: 0,
    expiredItems: 0
  });
  
  // 搜索参数
  const [searchParams, setSearchParams] = useState({});

  // 获取基础数据
  useEffect(() => {
    Promise.all([
      fetchWarehouses(),
      fetchProducts(), 
      fetchMaterials()
    ]);
  }, []);

  // 获取库存数据
  useEffect(() => {
    fetchInventoryData();
  }, [pagination.current, pagination.pageSize, searchParams]);

  const fetchWarehouses = async () => {
    try {
      // 使用仓库基础档案API获取仓库数据
      const response = await request.get('/tenant/base-archive/base-data/warehouses/options');
      
      if (response.data?.success) {
        const warehouseData = response.data.data;
        
        let warehouses = [];
        if (Array.isArray(warehouseData)) {
          warehouses = warehouseData.map(item => ({
            id: item.value || item.id,
            warehouse_name: item.label || item.warehouse_name || item.name,
            warehouse_code: item.code || item.warehouse_code
          }));
        } else if (warehouseData?.warehouses && Array.isArray(warehouseData.warehouses)) {
          warehouses = warehouseData.warehouses.map(item => ({
            id: item.id,
            warehouse_name: item.warehouse_name || item.name,
            warehouse_code: item.warehouse_code || item.code
          }));
        } else if (warehouseData?.items && Array.isArray(warehouseData.items)) {
          warehouses = warehouseData.items.map(item => ({
            id: item.id,
            warehouse_name: item.warehouse_name || item.name,
            warehouse_code: item.warehouse_code || item.code
          }));
        }
        
        setWarehouses(warehouses);
        
      } else {
        message.warning('仓库数据加载失败');
        setWarehouses([]);
      }
    } catch (error) {
      message.error('获取仓库数据失败');
      setWarehouses([]);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await baseDataService.getProducts();
      if (response.data?.success) {
        const productData = response.data.data;
        // 处理分页数据或直接数组
        let products = [];
        if (Array.isArray(productData)) {
          products = productData;
        } else if (productData?.products && Array.isArray(productData.products)) {
          products = productData.products;
        } else if (productData?.items && Array.isArray(productData.items)) {
          products = productData.items;
        } else if (productData?.data && Array.isArray(productData.data)) {
          products = productData.data;
        }
        setProducts(products);
      }
    } catch (error) {
      message.error('获取产品数据失败');
      setProducts([]);
    }
  };

  const fetchMaterials = async () => {
    try {
      const response = await request.get('/tenant/basic-data/material-management');
      if (response.data?.success) {
        const materialData = response.data.data;
        let materials = [];
        if (Array.isArray(materialData)) {
          materials = materialData;
        } else if (materialData?.materials && Array.isArray(materialData.materials)) {
          materials = materialData.materials;
        } else if (materialData?.items && Array.isArray(materialData.items)) {
          materials = materialData.items;
        } else if (materialData?.data && Array.isArray(materialData.data)) {
          materials = materialData.data;
        }
        setMaterials(materials);
      }
    } catch (error) {
      message.error('获取材料数据失败');
      setMaterials([]);
    }
  };

  const fetchInventoryData = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.current,
        page_size: pagination.pageSize,
        ...searchParams
      };
      
      const response = await inventoryService.getInventoryList(params);
      
      if (response.data?.success) {
        const inventoryData = response.data.data;
        let inventories = [];
        let total = 0;
        
        if (Array.isArray(inventoryData)) {
          inventories = inventoryData;
          total = inventoryData.length;
        } else if (inventoryData?.items && Array.isArray(inventoryData.items)) {
          inventories = inventoryData.items;
          total = inventoryData.total || inventoryData.items.length;
        } else if (inventoryData?.data && Array.isArray(inventoryData.data)) {
          inventories = inventoryData.data;
          total = inventoryData.total || inventoryData.data.length;
        }
        
        setData(inventories);
        setPagination(prev => ({
          ...prev,
          total: total
        }));
        
        // 计算统计信息
        const totalValue = inventories.reduce((sum, item) => sum + (parseFloat(item.total_cost) || 0), 0);
        const lowStockItems = inventories.filter(item => 
          parseFloat(item.current_quantity) <= parseFloat(item.safety_stock)
        ).length;
        const expiredItems = inventories.filter(item => {
          if (!item.expiry_date) return false;
          return dayjs(item.expiry_date).isBefore(dayjs());
        }).length;
        
        setStatistics({
          totalItems: total,
          totalValue: totalValue,
          lowStockItems: lowStockItems,
          expiredItems: expiredItems
        });
      }
    } catch (error) {
      message.error('获取库存数据失败');
      setData([]);
      setStatistics({
        totalItems: 0,
        totalValue: 0,
        lowStockItems: 0,
        expiredItems: 0
      });
    } finally {
      setLoading(false);
    }
  };

  // 搜索处理
  const handleSearch = (values) => {
    const params = {
      ...values,
      production_date_start: values.production_date_range?.[0]?.format('YYYY-MM-DD'),
      production_date_end: values.production_date_range?.[1]?.format('YYYY-MM-DD'),
      expiry_date_start: values.expiry_date_range?.[0]?.format('YYYY-MM-DD'),
      expiry_date_end: values.expiry_date_range?.[1]?.format('YYYY-MM-DD')
    };
    delete params.production_date_range;
    delete params.expiry_date_range;
    
    setSearchParams(params);
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  // 重置搜索
  const handleReset = () => {
    form.resetFields();
    setSearchParams({});
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  // 刷新数据
  const handleRefresh = () => {
    fetchInventoryData();
  };

  // 表格列定义
  const columns = [
    {
      title: '仓库',
      dataIndex: 'warehouse_name', 
      key: 'warehouse_name',
      width: 120,
      render: (text, record) => {
        const warehouse = warehouses.find(w => w.id === record.warehouse_id);
        return warehouse?.warehouse_name || '-';
      }
    },
    {
      title: '物料信息',
      key: 'item_info',
      width: 220,
      render: (_, record) => {
        let itemName = '-';
        let itemCode = '-';
        
        if (record.product_id) {
          const product = products.find(p => p.id === record.product_id);
          itemName = product?.product_name || '-';
          itemCode = product?.product_code || '-';
        } else if (record.material_id) {
          const material = materials.find(m => m.id === record.material_id);
          itemName = material?.material_name || '-';
          itemCode = material?.material_code || '-';
        }
        
        return (
          <div style={{ fontWeight: 500 }}>
            {itemName} ({itemCode})
          </div>
        );
      }
    },
    {
      title: '当前库存',
      dataIndex: 'current_quantity',
      key: 'current_quantity',
      width: 120,
      align: 'right',
      render: (value, record) => (
        <div style={{ textAlign: 'right', fontWeight: 500, color: value > 0 ? '#52c41a' : '#f5222d' }}>
          {(+value).toFixed(3)} {record.unit}
        </div>
      )
    },
    {
      title: '可用库存',
      dataIndex: 'available_quantity',
      key: 'available_quantity',
      width: 120,
      align: 'right',
      render: (value, record) => (
        <div style={{ textAlign: 'right', fontWeight: 500, color: value > 0 ? '#52c41a' : '#f5222d' }}>
          {(+value).toFixed(3)} {record.unit}
        </div>
      )
    },
    {
      title: '预留库存',
      dataIndex: 'reserved_quantity',
      key: 'reserved_quantity',
      width: 120,
      align: 'right',
      render: (value, record) => (
        <div style={{ textAlign: 'right', fontWeight: 500 }}>
          {(+value).toFixed(3)} {record.unit}
        </div>
      )
    },
    {
      title: '在途库存',
      dataIndex: 'in_transit_quantity',
      key: 'in_transit_quantity',
      width: 120,
      align: 'right',
      render: (value, record) => (
        <div style={{ textAlign: 'right', fontWeight: 500 }}>
          {(+value).toFixed(3)} {record.unit}
        </div>
      )
    },
    {
      title: '批次号',
      dataIndex: 'batch_number',
      key: 'batch_number',
      width: 120,
      render: text => text || '-'
    },
    {
      title: '库位',
      dataIndex: 'location_code',
      key: 'location_code',
      width: 100,
      render: text => text || '-'
    },
    {
      title: '存储区域',
      dataIndex: 'storage_area',
      key: 'storage_area',
      width: 100,
      render: text => text || '-'
    },
    {
      title: '库存状态',
      dataIndex: 'inventory_status',
      key: 'inventory_status',
      width: 100,
      render: text => getStatusTag(text, 'inventory')
    },
    {
      title: '质量状态',
      dataIndex: 'quality_status',
      key: 'quality_status',
      width: 100,
      render: text => getStatusTag(text, 'quality')
    },
    {
      title: '单位成本',
      dataIndex: 'unit_cost',
      key: 'unit_cost',
      width: 120,
      align: 'right',
      render: value => value ? `¥${(+value).toFixed(4)}` : '-'
    },
    {
      title: '总成本',
      dataIndex: 'total_cost',
      key: 'total_cost',
      width: 120,
      align: 'right',
      render: value => value ? `¥${(+value).toFixed(2)}` : '-'
    },
    {
      title: '安全库存',
      dataIndex: 'safety_stock',
      key: 'safety_stock',
      width: 120,
      align: 'right',
      render: (value, record) => (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 4 }}>
          {getWarningIcon(+record.current_quantity, +value, +record.min_stock)}
          <span>{(+value).toFixed(3)}</span>
        </div>
      )
    },
    {
      title: '最小库存',
      dataIndex: 'min_stock',
      key: 'min_stock',
      width: 120,
      align: 'right',
      render: value => (+(value || 0)).toFixed(3)
    },
    {
      title: '最大库存',
      dataIndex: 'max_stock',
      key: 'max_stock',
      width: 120,
      align: 'right',
      render: value => value ? (+value).toFixed(3) : '-'
    },
    {
      title: '生产日期',
      dataIndex: 'production_date',
      key: 'production_date',
      width: 120,
      render: text => text ? dayjs(text).format('YYYY-MM-DD') : '-'
    },
    {
      title: '到期日期',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      width: 120,
      render: (text) => {
        if (!text) return '-';
        const date = dayjs(text);
        const isExpired = date.isBefore(dayjs());
        const isNearExpiry = date.isBefore(dayjs().add(30, 'day'));
        
        return (
          <div style={{ color: isExpired ? '#f5222d' : isNearExpiry ? '#fa8c16' : 'inherit' }}>
            {date.format('YYYY-MM-DD')}
            {isExpired && <Badge status="error" />}
            {!isExpired && isNearExpiry && <Badge status="warning" />}
          </div>
        );
      }
    },
    {
      title: '最后盘点',
      dataIndex: 'last_count_date',
      key: 'last_count_date',
      width: 120,
      render: text => text ? dayjs(text).format('YYYY-MM-DD') : '-'
    },
    {
      title: '差异数量',
      dataIndex: 'variance_quantity',
      key: 'variance_quantity',
      width: 120,
      align: 'right',
      render: (value, record) => {
        const val = +(value || 0);
        return (
          <div style={{ 
            textAlign: 'right',
            color: val > 0 ? '#52c41a' : val < 0 ? '#f5222d' : 'inherit'
          }}>
            {val.toFixed(3)}
          </div>
        );
      }
    },
    {
      title: '备注',
      dataIndex: 'notes',
      key: 'notes',
      width: 150,
      ellipsis: true,
      render: text => text || '-'
    }
  ];

  return (
    <PageContainer>
      {/* 统计概览 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <StatCard>
            <Statistic 
              title="库存物料总数"
              value={statistics.totalItems}
              prefix={<BarChartOutlined />}
            />
          </StatCard>
        </Col>
        <Col span={6}>
          <StatCard>
            <Statistic 
              title="库存总价值"
              value={statistics.totalValue}
              precision={2}
              prefix="¥"
            />
          </StatCard>
        </Col>
        <Col span={6}>
          <StatCard>
            <Statistic 
              title="低库存预警"
              value={statistics.lowStockItems}
              valueStyle={{ color: statistics.lowStockItems > 0 ? '#f5222d' : '#52c41a' }}
              prefix={<WarningOutlined />}
            />
          </StatCard>
        </Col>
        <Col span={6}>
          <StatCard>
            <Statistic 
              title="过期物料"
              value={statistics.expiredItems}
              valueStyle={{ color: statistics.expiredItems > 0 ? '#f5222d' : '#52c41a' }}
              prefix={<ClockCircleOutlined />}
            />
          </StatCard>
        </Col>
      </Row>

      {/* 搜索筛选 */}
      <StyledCard 
        title={
          <Space>
            <FilterOutlined />
            筛选条件
          </Space>
        }
        size="small"
        style={{ marginBottom: 16 }}
      >
        <Collapse 
          ghost
          items={[
            {
              key: '1',
              label: '展开筛选',
              children: (
                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleSearch}
                >
                  <Row gutter={16}>
                    <Col span={6}>
                      <Form.Item name="search" label="关键字搜索">
                        <Input 
                          placeholder="批次号、库位编码等"
                          allowClear
                          prefix={<SearchOutlined />}
                        />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="warehouse_id" label="仓库">
                        <Select placeholder="选择仓库" allowClear>
                          {warehouses.map(warehouse => (
                            <Option key={warehouse.id} value={warehouse.id}>
                              {warehouse.warehouse_name}
                            </Option>
                          ))}
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="inventory_status" label="库存状态">
                        <Select placeholder="选择库存状态" allowClear>
                          <Option value="normal">正常</Option>
                          <Option value="blocked">冻结</Option>
                          <Option value="quarantine">隔离</Option>
                          <Option value="damaged">损坏</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="quality_status" label="质量状态">
                        <Select placeholder="选择质量状态" allowClear>
                          <Option value="qualified">合格</Option>
                          <Option value="unqualified">不合格</Option>
                          <Option value="pending">待检</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                  </Row>
                  <Row gutter={16}>
                    <Col span={8}>
                      <Form.Item name="production_date_range" label="生产日期">
                        <RangePicker 
                          style={{ width: '100%' }}
                          format="YYYY-MM-DD"
                        />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item name="expiry_date_range" label="到期日期">
                        <RangePicker 
                          style={{ width: '100%' }}
                          format="YYYY-MM-DD"
                        />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item label=" " style={{ marginTop: 8 }}>
                        <Space>
                          <ActionButton type="primary" htmlType="submit" icon={<SearchOutlined />}>
                            搜索
                          </ActionButton>
                          <ActionButton onClick={handleReset} icon={<ReloadOutlined />}>
                            重置
                          </ActionButton>
                          <ActionButton onClick={handleRefresh} icon={<ReloadOutlined />}>
                            刷新
                          </ActionButton>
                        </Space>
                      </Form.Item>
                    </Col>
                  </Row>
                </Form>
              )
            }
          ]}
        />
      </StyledCard>

      {/* 库存明细表 */}
      <StyledCard 
        title={
          <Space>
            <BarChartOutlined />
            库存明细
          </Space>
        }
        extra={
          <ActionButton icon={<DownloadOutlined />}>
            导出数据
          </ActionButton>
        }
      >
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={pagination}
          onChange={(pag) => setPagination(pag)}
          scroll={{ x: 2400, y: 600 }}
          size="small"
          bordered
        />
      </StyledCard>
    </PageContainer>
  );
};

export default InventoryOverview; 