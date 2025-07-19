import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Popconfirm,
  message,
  Tag,
  Drawer,
  Row,
  Col,
  Typography,
  Tabs,
  InputNumber,
  Divider
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined,
  ReloadOutlined,
  CheckOutlined,
  SendOutlined,
  CheckCircleOutlined,
  PrinterOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import dayjs from 'dayjs';
import deliveryNoticeService from '../../../api/business/sales/deliveryNotice';
import salesOrderService from '../../../api/business/sales/salesOrder';

const { Option } = Select;
const { TextArea } = Input;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

const PageContainer = styled.div`
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
`;

const StyledCard = styled(Card)`
  margin-bottom: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const DeliveryNotice = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });
  const [details, setDetails] = useState([]);
  const [customerOptions, setCustomerOptions] = useState([]);
  const [productOptions, setProductOptions] = useState([]);
  const [salesOrderOptions, setSalesOrderOptions] = useState([]);
  const [unitOptions, setUnitOptions] = useState([]);

  useEffect(() => {
    fetchData();
    fetchOptions();
  }, []);

  const fetchData = async (params = {}) => {
    setLoading(true);
    try {
      const queryParams = { page: pagination.current, per_page: pagination.pageSize, ...params };
      const response = await deliveryNoticeService.getDeliveryNotices(queryParams);
      if (response.data.success) {
        setData(response.data.data.items || []);
        setPagination(prev => ({ ...prev, total: response.data.data.total }));
      }
    } catch (error) {
      message.error('获取送货通知单失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchOptions = async () => {
    try {
      const [customerRes, productRes, salesOrderRes, unitRes] = await Promise.all([
        salesOrderService.getCustomerOptions(),
        salesOrderService.getProductOptions(),
        salesOrderService.getActiveSalesOrderOptions(null, 100), // 使用新的API，限制100条，排除completed状态
        salesOrderService.getUnitOptions()
      ]);
      if (customerRes.data.success) setCustomerOptions(customerRes.data.data);
      if (productRes.data.success) setProductOptions(productRes.data.data);
      if (salesOrderRes.data.success) {
        const orderOptions = salesOrderRes.data.data.map(order => ({
          value: order.value,
          label: order.label,
          data: order.data
        }));
        setSalesOrderOptions(orderOptions);
      }
      if (unitRes.data.success) setUnitOptions(unitRes.data.data);
    } catch (error) {
      console.error('获取选项数据失败:', error);
    }
  };

  const handleSearch = () => searchForm.validateFields().then(values => fetchData(values));
  const handleReset = () => {
    searchForm.resetFields();
    fetchData();
  };

  const handleAdd = () => {
    setCurrentRecord(null);
    form.resetFields();
    form.setFieldsValue({ 
      delivery_date: dayjs(), 
      status: 'draft' 
    });
    setDetails([]);
    setModalVisible(true);
  };

  const handleEdit = async (record) => {
    try {
      const response = await deliveryNoticeService.getDeliveryNoticeById(record.id);
      if (response.data.success) {
        const noticeData = response.data.data;
        setCurrentRecord(noticeData);
        form.setFieldsValue({
          ...noticeData,
          delivery_date: noticeData.delivery_date ? dayjs(noticeData.delivery_date) : null
        });
        setDetails(noticeData.details || []);
        setModalVisible(true);
      }
    } catch (error) {
      message.error('获取详情失败');
    }
  };

  const handleDelete = async (record) => {
    try {
      await deliveryNoticeService.deleteDeliveryNotice(record.id);
      message.success('删除成功');
      fetchData();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();

      const payload = {
        ...values,
        delivery_date: values.delivery_date ? values.delivery_date.format('YYYY-MM-DD HH:mm:ss') : null,
        details: details,
      };
      
      // 检查明细中notice_quantity是否大于remaining_quantity
      const hasInvalidQuantity = details.some(detail => detail.notice_quantity > detail.remaining_quantity);
      if (hasInvalidQuantity) {
        // 使用Modal.confirm显示警告，但允许继续
        Modal.confirm({
          title: '数量警告',
          content: '通知数量大于未安排数量，是否继续保存？',
          okText: '继续保存',
          cancelText: '取消',
          onOk: async () => {
            await saveDeliveryNotice(payload);
          }
        });
        return;
      }
      
      // 如果没有数量问题，直接保存
      await saveDeliveryNotice(payload);
    } catch (error) {
      message.error('保存失败');
    }
  };

  const saveDeliveryNotice = async (payload) => {
    try {
      if (currentRecord) {
        await deliveryNoticeService.updateDeliveryNotice(currentRecord.id, payload);
      } else {
        await deliveryNoticeService.createDeliveryNotice(payload);
      }
      
      message.success(currentRecord ? '更新成功' : '创建成功');
      setModalVisible(false);
      fetchData();
    } catch (error) {
      message.error('保存失败');
      throw error; // 重新抛出错误，让调用方处理
    }
  };

  const handleViewDetail = (record) => {
    setCurrentRecord(record);
    setDetailDrawerVisible(true);
  };

  const handleStatusChange = async (record, action) => {
    try {
      if (action === 'confirm') {
        await deliveryNoticeService.confirmDelivery(record.id);
      } else if (action === 'ship') {
        // 调用发货接口
        await deliveryNoticeService.shipDelivery?.(record.id);
      } else if (action === 'complete') {
        // 调用完成接口
        await deliveryNoticeService.completeDelivery?.(record.id);
      } else {
        return;
      }

      message.success('状态更新成功');
      fetchData();
    } catch (error) {
      message.error('状态更新失败');
    }
  };


  const updateDetail = (index, field, value) => {
    const newDetails = [...details];
    newDetails[index][field] = value;
    
    // 自动计算金额
    if (field === 'notice_quantity' || field === 'price') {
      const quantity = newDetails[index].notice_quantity || 0;
      const price = newDetails[index].price || 0;
      newDetails[index].amount = quantity * price;
    }
    
    setDetails(newDetails);
  };

  const removeDetail = (index) => {
    const newDetails = details.filter((_, i) => i !== index);
    setDetails(newDetails);
  };

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'default',
      'confirmed': 'processing',
      'shipped': 'warning',
      'completed': 'success',
      'cancelled': 'error'
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status) => {
    const texts = {
      'draft': '草稿',
      'confirmed': '已确认',
      'shipped': '已发货',
      'completed': '已完成',
      'cancelled': '已取消'
    };
    return texts[status] || status;
  };

  const columns = [
    {
      title: '通知单号',
      dataIndex: 'notice_number',
      key: 'notice_number',
      width: 150,
    },
    {
      title: '客户名称',
      dataIndex: ['customer', 'customer_name'],
      key: 'customer_name',
      width: 200,
    },
    {
      title: '销售订单号',
      dataIndex: ['sales_order', 'order_number'],
      key: 'order_number',
      width: 150,
    },
    {
      title: '送货地址',
      dataIndex: 'delivery_address',
      key: 'delivery_address',
      width: 200,
      ellipsis: true,
    },
    {
      title: '送货日期',
      dataIndex: 'delivery_date',
      key: 'delivery_date',
      width: 120,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD') : '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD HH:mm') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 280,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
          {record.status === 'draft' && (
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            >
              编辑
            </Button>
          )}
          {record.status === 'draft' && (
            <Button
              type="link"
              icon={<CheckOutlined />}
              onClick={() => handleStatusChange(record, 'confirm')}
            >
              确认
            </Button>
          )}
          {record.status === 'draft' && (
            <Popconfirm
              title="确定要删除这条记录吗？"
              onConfirm={() => handleDelete(record)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="link"
                danger
                icon={<DeleteOutlined />}
              >
                删除
              </Button>
            </Popconfirm>
          )}
          {record.status === 'confirmed' && (
            <Button
              type="link"
              icon={<SendOutlined />}
              onClick={() => handleStatusChange(record, 'ship')}
            >
              发货
            </Button>
          )}
          {record.status === 'shipped' && (
            <Button
              type="link"
              icon={<CheckCircleOutlined />}
              onClick={() => handleStatusChange(record, 'complete')}
            >
              完成
            </Button>
          )}
          <Button
            type="link"
            icon={<PrinterOutlined />}
            onClick={() => handlePrint(record)}
          >
            打印
          </Button>
        </Space>
      ),
    },
  ];

  const detailColumns = [
    {
      title: '销售单号',
      dataIndex: 'sales_order_number',
      key: 'sales_order_number',
      width: 100,
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => updateDetail(index, 'sales_order_number', e.target.value)}
          size="small"
          readOnly
          style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
        />
      ),
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 100,
      render: (text, record, index) => (
        <Input
          value={text}
          placeholder="从销售订单自动加载"
          readOnly
          size="small"
          style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
        />
      ),
    },
    {
      title: '产品编号',
      dataIndex: 'product_code',
      key: 'product_code',
      width: 100,
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => updateDetail(index, 'product_code', e.target.value)}
          size="small"
          readOnly
          style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
        />
      ),
    },
    {
      title: '规格',
      dataIndex: 'specification',
      key: 'specification',
      width: 130,
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => updateDetail(index, 'specification', e.target.value)}
          size="small"
          readOnly
          style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
        />
      ),
    },
    {
      title: '订单数量',
      dataIndex: 'order_quantity',
      key: 'order_quantity',
      width: 70,
      render: (text, record, index) => (
        <InputNumber
          value={text}
          onChange={(value) => updateDetail(index, 'order_quantity', value)}
          size="small"
          precision={2}
          readOnly
          style={{ width: '100%', backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
        />
      ),
    },
    {
      title: '未安排数量',
      dataIndex: 'remaining_quantity',
      key: 'remaining_quantity',
      width: 70,
      render: (text) => (
        <InputNumber
          value={text}
          onChange={(value) => updateDetail(index, 'remaining_quantity', value)}
          size="small"
          precision={2}
          readOnly
          style={{ width: '100%', backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
        />
      ),
    },
    {
      title: '通知数量',
      dataIndex: 'notice_quantity',
      key: 'notice_quantity',
      width: 70,
      render: (text, record, index) => (
        <InputNumber
          value={text}
          onChange={(value) => updateDetail(index, 'notice_quantity', value)}
          size="small"
          style={{ width: '100%' }}
          precision={2}
        />
      ),
    },
    {
      title: '单位',
      dataIndex: 'unit_id',
      key: 'unit_id',
      width: 50,
      render: (value, record, index) => {
        // 根据unit_id找到对应的单位名称
        const unitOption = unitOptions.find(opt => opt.value === value);
        const unitName = unitOption ? unitOption.label : record.unit_name || '';
        
        return (
          <Input
            value={unitName}
            placeholder="从销售订单自动加载"
            readOnly
            size="small"
            style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
          />
        );
      },
    },
    {
      title: '赠送数',
      dataIndex: 'gift_quantity',
      key: 'gift_quantity',
      width: 70,
      render: (text, record, index) => (
        <InputNumber
          value={text}
          onChange={(value) => updateDetail(index, 'gift_quantity', value)}
          size="small"
          style={{ width: '100%' }}
          precision={2}
        />
      ),
    },
    {
      title: '工单号',
      dataIndex: 'work_order_number',
      key: 'work_order_number',
      width: 120,
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => updateDetail(index, 'work_order_number', e.target.value)}
          size="small"
        />
      ),
    },
    {
      title: '客户订单号',
      dataIndex: 'customer_order_number',
      key: 'customer_order_number',
      width: 120,
      render: (text, record, index) => (
        <Input
          value={text}
          onChange={(e) => updateDetail(index, 'customer_order_number', e.target.value)}
          size="small"
        />
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record, index) => (
        <Button
          type="link"
          danger
          size="small"
          onClick={() => removeDetail(index)}
        >
          删除
        </Button>
      ),
    },
  ];

  const fetchSalesOrdersForCustomer = async (custId) => {
    if (!custId) {
      setSalesOrderOptions([]);
      return;
    }
    try {
      // 使用新的API获取该客户未完成的销售订单
      const res = await salesOrderService.getActiveSalesOrderOptions(custId, 50);
      if (res.data.success) {
        const opts = res.data.data.map(order => ({
          value: order.value,
          label: order.label,
          data: order.data
        }));
        setSalesOrderOptions(opts);
      }
    } catch (e) {
      console.error('加载销售订单失败', e);
    }
  };

  // 监听客户选择
  const onCustomerChange = (value) => {
    form.setFieldsValue({ sales_order_id: undefined });
    fetchSalesOrdersForCustomer(value);
  };

  // 监听销售订单选择，自动导入明细
  const onSalesOrderChange = async (orderId) => {
    if (!orderId) {
      setDetails([]);
      return;
    }
    try {
      const res = await deliveryNoticeService.getDetailsFromSalesOrder(orderId);
      if (res.data.success) {
        // 为每个明细添加初始通知数量字段
        const detailsWithInitialQuantity = res.data.data.map(detail => ({
          ...detail,
          remaining_quantity: detail.notice_quantity || 0
        }));
        setDetails(detailsWithInitialQuantity);
      }
    } catch (e) {
      console.error('获取销售订单明细失败', e);
    }
  };

  const handlePrint = async (record) => {
    try {
      const res = await deliveryNoticeService.getDeliveryNoticeById(record.id);
      if (!res.data.success) {
        message.error('获取打印数据失败');
        return;
      }
      const notice = res.data.data;
      // 构建打印HTML
      const html = `<!DOCTYPE html><html><head><meta charset="utf-8"/><title>送货通知单打印</title>
      <style>
        body{font-family:Arial,Helvetica,sans-serif;padding:20px}
        h2{text-align:center;margin-bottom:24px}
        table{width:100%;border-collapse:collapse;margin-top:16px}
        th,td{border:1px solid #000;padding:4px;text-align:left;font-size:12px}
        th{background:#f5f5f5}
      </style></head><body onload="window.print();setTimeout(()=>window.close(),100);">
      <h2>送货通知单</h2>
      <div>通知单号：${notice.notice_number || ''}</div>
      <div>客户名称：${notice.customer?.customer_name || ''}</div>
      <div>销售订单号：${notice.sales_order?.order_number || ''}</div>
      <div>送货日期：${notice.delivery_date ? dayjs(notice.delivery_date).format('YYYY-MM-DD') : ''}</div>
      <table><thead><tr><th>产品编号</th><th>产品名称</th><th>规格</th><th>通知数量</th><th>单位</th></tr></thead><tbody>
      ${notice.details.map(d=>{
        const pname = d.product_name || (d.product?.product_name ?? '');
        const pcode = d.product_code || (d.product?.product_code ?? '');
        const unitName = d.unit_name || (d.unit?.unit_name ?? '');
        return `<tr><td>${pcode}</td><td>${pname}</td><td>${d.specification||''}</td><td>${d.notice_quantity||0}</td><td>${unitName}</td></tr>`;
      }).join('')}
      </tbody></table>
      </body></html>`;
      const printWindow = window.open('', '_blank');
      if (printWindow) {
        printWindow.document.open();
        printWindow.document.write(html);
        printWindow.document.close();
      }
    } catch (e) {
      message.error('打印失败');
    }
  };

  return (
    <PageContainer>
      <StyledCard>
        <div style={{ marginBottom: 16 }}>
          <Title level={4}>送货通知单管理</Title>
        </div>
        
        {/* 搜索表单 */}
        <Form
          form={searchForm}
          layout="inline"
          style={{ marginBottom: 16 }}
        >
          <Form.Item name="notice_number" label="通知单号">
            <Input placeholder="请输入通知单号" />
          </Form.Item>
          <Form.Item name="customer_id" label="客户">
            <Select
              placeholder="选择客户"
              style={{ width: 200 }}
              showSearch
              optionFilterProp="children"
              allowClear
              onChange={onCustomerChange}
            >
              {customerOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="status" label="状态">
            <Select placeholder="选择状态" style={{ width: 120 }} allowClear>
              <Option value="draft">草稿</Option>
              <Option value="confirmed">已确认</Option>
              <Option value="shipped">已发货</Option>
              <Option value="completed">已完成</Option>
              <Option value="cancelled">已取消</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleSearch}
              >
                搜索
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
              >
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>

        {/* 操作按钮 */}
        <div style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAdd}
          >
            新增送货通知单
          </Button>
        </div>

        {/* 数据表格 */}
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              setPagination(prev => ({ ...prev, current: page, pageSize }));
              fetchData();
            },
          }}
          scroll={{ x: 1500 }}
        />
      </StyledCard>

      {/* 编辑/新增弹窗 */}
      <Modal
        title={currentRecord ? '编辑送货通知单' : '新增送货通知单'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={1200}
        style={{ top: 20 }}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="notice_number" label="通知单号">
                <Input disabled placeholder="自动生成" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item 
                name="customer_id" 
                label="客户" 
                rules={[{ required: true, message: '请选择客户' }]}
              >
                <Select
                  showSearch
                  optionFilterProp="children"
                  placeholder="选择客户"
                  onChange={onCustomerChange}
                >
                  {customerOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="sales_order_id" label="关联销售订单">
                <Select
                  showSearch
                  optionFilterProp="children"
                  placeholder="选择销售订单"
                  allowClear
                  disabled={!form.getFieldValue('customer_id')}
                  onChange={onSalesOrderChange}
                >
                  {salesOrderOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="delivery_date" label="送货日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="delivery_method" label="送货方式">
                <Input placeholder="请输入送货方式" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="status" label="状态">
                <Select placeholder="选择状态">
                  <Option value="draft">草稿</Option>
                  <Option value="confirmed">已确认</Option>
                  <Option value="shipped">已发货</Option>
                  <Option value="completed">已完成</Option>
                  <Option value="cancelled">已取消</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="delivery_address" label="送货地址">
                <TextArea rows={2} placeholder="请输入送货地址" />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="logistics_info" label="物流信息">
                <TextArea rows={2} placeholder="请输入物流信息" />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="remark" label="备注">
                <TextArea rows={2} placeholder="请输入备注" />
              </Form.Item>
            </Col>
          </Row>
          
          <Divider>送货明细</Divider>
          
          
          <Table
            columns={detailColumns}
            dataSource={details}
            rowKey={(record, index) => record.id || index}
            pagination={false}
            scroll={{ x: 1800 }}
            size="small"
          />
        </Form>
      </Modal>

      {/* 详情抽屉 */}
      <Drawer
        title="送货通知单详情"
        placement="right"
        width={800}
        onClose={() => setDetailDrawerVisible(false)}
        open={detailDrawerVisible}
      >
        {currentRecord && (
          <div>
            <Title level={5}>基本信息</Title>
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>通知单号：</Text>
                <Text>{currentRecord.notice_number}</Text>
              </Col>
              <Col span={12}>
                <Text strong>客户名称：</Text>
                <Text>{currentRecord.customer?.customer_name}</Text>
              </Col>
              <Col span={12}>
                <Text strong>送货日期：</Text>
                <Text>{currentRecord.delivery_date ? dayjs(currentRecord.delivery_date).format('YYYY-MM-DD') : '-'}</Text>
              </Col>
              <Col span={12}>
                <Text strong>状态：</Text>
                <Tag color={getStatusColor(currentRecord.status)}>
                  {getStatusText(currentRecord.status)}
                </Tag>
              </Col>
              <Col span={24}>
                <Text strong>送货地址：</Text>
                <Text>{currentRecord.delivery_address || '-'}</Text>
              </Col>
              <Col span={24}>
                <Text strong>物流信息：</Text>
                <Text>{currentRecord.logistics_info || '-'}</Text>
              </Col>
              <Col span={24}>
                <Text strong>备注：</Text>
                <Text>{currentRecord.remark || '-'}</Text>
              </Col>
            </Row>
            
            {currentRecord.details && currentRecord.details.length > 0 && (
              <>
                <Divider />
                <Title level={5}>送货明细</Title>
                <Table
                  columns={[
                    { title: '工单号', dataIndex: 'work_order_number', key: 'work_order_number' },
                    { title: '产品名称', dataIndex: 'product_name', key: 'product_name' },
                    { title: '产品编号', dataIndex: 'product_code', key: 'product_code' },
                    { title: '规格', dataIndex: 'specification', key: 'specification' },
                    { 
                      title: '订单数量', 
                      dataIndex: 'order_quantity', 
                      key: 'order_quantity',
                      render: (text) => text ? parseFloat(text).toFixed(2) : '0.00'
                    },
                    { 
                      title: '通知数量', 
                      dataIndex: 'notice_quantity', 
                      key: 'notice_quantity',
                      render: (text) => text ? parseFloat(text).toFixed(2) : '0.00'
                    },
                    { 
                      title: '单位', 
                      dataIndex: 'unit_id', 
                      key: 'unit_id',
                      render: (value, record) => {
                        const unitOption = unitOptions.find(opt => opt.value === value);
                        return unitOption ? unitOption.label : record.unit_name || '-';
                      }
                    }
                  ]}
                  dataSource={currentRecord.details}
                  rowKey="id"
                  pagination={false}
                  size="small"
                />
              </>
            )}
          </div>
        )}
      </Drawer>
    </PageContainer>
  );
};

export default DeliveryNotice; 