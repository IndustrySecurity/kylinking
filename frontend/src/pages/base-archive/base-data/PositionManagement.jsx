import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Select,
  Space,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Form,
  Modal,
  InputNumber,
  Switch,
  Tag
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import positionApi from '../../../api/base-data/position';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const PositionManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPosition, setEditingPosition] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });

  // 选项数据
  const [form] = Form.useForm();
  const [departments, setDepartments] = useState([]);
  const [positions, setPositions] = useState([]);

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await positionApi.getPositions({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        department_id: departmentFilter,
        ...params
      });

      // 正确处理后端响应格式
      if (response.data.success) {
        const { positions, total, current_page } = response.data.data;
        
        // 为每行数据添加key
        const dataWithKeys = (positions || []).map((item, index) => ({
          ...item,
          key: item.id || `temp_${index}`
        }));
        
        setData(dataWithKeys);
        setPagination(prev => ({
          ...prev,
          total,
          current: current_page
        }));
      }
    } catch (error) {
      message.error('加载数据失败：' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  // 加载选项数据
  const loadOptions = async () => {
    try {
      // 加载部门选项
      const deptResponse = await positionApi.getDepartmentOptions();
      if (deptResponse.data.success) {
        setDepartments(deptResponse.data.data || []);
      }

      // 加载职位选项
      const posResponse = await positionApi.getPositionOptions();
      if (posResponse.data.success) {
        setPositions(posResponse.data.data.positions || []);
      }
    } catch (error) {
      message.error('加载选项数据失败：' + (error.response?.data?.error || error.message));
    }
  };

  // 初始加载
  useEffect(() => {
    loadData();
    loadOptions();
  }, []);

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setDepartmentFilter('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '', department_id: '' });
  };

  // 刷新数据
  const handleRefresh = () => {
    loadData();
    loadOptions();
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize
    });
  };

  // 打开编辑模态框
  const handleEdit = (record = null) => {
    setEditingPosition(record);
    if (record) {
      form.setFieldsValue({
        position_name: record.position_name,
        department_id: record.department_id,
        parent_position_id: record.parent_position_id,
        hourly_wage: record.hourly_wage,
        standard_pass_rate: record.standard_pass_rate,
        is_supervisor: record.is_supervisor,
        is_machine_operator: record.is_machine_operator,
        description: record.description,
        sort_order: record.sort_order || 0,
        is_enabled: record.is_enabled !== false
      });
    } else {
      form.resetFields();
    }
    setModalVisible(true);
  };

  // 保存职位
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      let response;
      if (editingPosition) {
        response = await positionApi.updatePosition(editingPosition.id, values);
        if (response.data.success) {
          message.success('更新成功');
        }
      } else {
        response = await positionApi.createPosition(values);
        if (response.data.success) {
          message.success('创建成功');
        }
      }

      setModalVisible(false);
      loadData();
      loadOptions(); // 重新加载职位选项
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        message.error('保存失败：' + (error.response?.data?.error || error.message));
      }
    }
  };

  // 删除职位
  const handleDelete = async (id) => {
    try {
      const response = await positionApi.deletePosition(id);
      if (response.data.success) {
        message.success('删除成功');
        loadData();
        loadOptions(); // 重新加载职位选项
      }
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.error || error.message));
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '职位名称',
      dataIndex: 'position_name',
      key: 'position_name',
      width: 150,
      render: (text) => <span style={{ fontWeight: 500 }}>{text}</span>
    },
    {
      title: '部门',
      dataIndex: 'department_name',
      key: 'department_name',
      width: 120,
      render: (text) => text || '-'
    },
    {
      title: '上级职位',
      dataIndex: 'parent_position_name',
      key: 'parent_position_name',
      width: 150,
      render: (text) => text || '-'
    },
    {
      title: '职位工资/h',
      dataIndex: 'hourly_wage',
      key: 'hourly_wage',
      width: 100,
      align: 'right',
      render: (value) => value ? `¥${value}` : '-'
    },
    {
      title: '标准合格率%',
      dataIndex: 'standard_pass_rate',
      key: 'standard_pass_rate',
      width: 110,
      align: 'center',
      render: (value) => value ? `${value}%` : '-'
    },
    {
      title: '主管',
      dataIndex: 'is_supervisor',
      key: 'is_supervisor',
      width: 80,
      align: 'center',
      render: (value) => (
        <Tag color={value ? 'green' : 'default'}>
          {value ? '是' : '否'}
        </Tag>
      )
    },
    {
      title: '机长',
      dataIndex: 'is_machine_operator',
      key: 'is_machine_operator',
      width: 80,
      align: 'center',
      render: (value) => (
        <Tag color={value ? 'blue' : 'default'}>
          {value ? '是' : '否'}
        </Tag>
      )
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      align: 'center'
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      align: 'center',
      render: (enabled) => (
        <Switch 
          checked={enabled}
          disabled
          size="small"
        />
      )
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      key: 'created_by_name',
      width: 100,
      align: 'center'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      align: 'center',
      render: (text) => text ? new Date(text).toLocaleString() : ''
    },
    {
      title: '修改人',
      dataIndex: 'updated_by_name',
      key: 'updated_by_name',
      width: 100,
      align: 'center',
      render: (text) => text || '-'
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      align: 'center',
      render: (text) => text ? new Date(text).toLocaleString() : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      align: 'center',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这个职位吗？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={4} style={{ margin: 0 }}>职位管理</Title>
            </Col>
            <Col>
              <Space>
                <Input
                  placeholder="搜索职位名称"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={handleSearch}
                  style={{ width: 200 }}
                  prefix={<SearchOutlined />}
                />
                <Select
                  placeholder="选择部门"
                  value={departmentFilter}
                  onChange={setDepartmentFilter}
                  style={{ width: 150 }}
                  allowClear
                >
                  {departments.map(dept => (
                    <Option key={dept.value} value={dept.value}>
                      {dept.label}
                    </Option>
                  ))}
                </Select>
                <Button onClick={handleSearch} type="primary">
                  搜索
                </Button>
                <Button onClick={handleReset}>
                  重置
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => handleEdit()}
                >
                  新增职位
                </Button>
                <Button 
                  icon={<ReloadOutlined />}
                  onClick={handleRefresh}
                >
                  刷新
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        <Table
          dataSource={data}
          columns={columns}
          rowKey="key"
          pagination={pagination}
          loading={loading}
          onChange={handleTableChange}
          scroll={{ x: 1300 }}
          size="small"
        />
      </Card>

      {/* 编辑模态框 */}
      <Modal
        title={editingPosition ? '编辑职位' : '新增职位'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        width={600}
        footer={[
          <Button key="cancel" onClick={() => setModalVisible(false)}>
            取消
          </Button>,
          <Button key="submit" type="primary" onClick={handleSave}>
            保存
          </Button>
        ]}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            sort_order: 0,
            is_enabled: true,
            is_supervisor: false,
            is_machine_operator: false
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="职位名称"
                name="position_name"
                rules={[{ required: true, message: '请输入职位名称' }]}
              >
                <Input placeholder="请输入职位名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="部门"
                name="department_id"
                rules={[{ required: true, message: '请选择部门' }]}
              >
                <Select placeholder="请选择部门">
                  {departments.map(dept => (
                    <Option key={dept.value} value={dept.value}>
                      {dept.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="上级职位"
                name="parent_position_id"
              >
                <Select placeholder="请选择上级职位" allowClear>
                  {positions.map(pos => (
                    <Option key={pos.value} value={pos.value}>
                      {pos.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="排序"
                name="sort_order"
              >
                <InputNumber 
                  placeholder="排序值" 
                  style={{ width: '100%' }}
                  min={0}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="职位工资/小时"
                name="hourly_wage"
              >
                <InputNumber 
                  placeholder="请输入时薪"
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                  addonAfter="元"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="标准合格率%"
                name="standard_pass_rate"
              >
                <InputNumber 
                  placeholder="请输入合格率"
                  style={{ width: '100%' }}
                  min={0}
                  max={100}
                  precision={2}
                  addonAfter="%"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="是否主管"
                name="is_supervisor"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="是否机长"
                name="is_machine_operator"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="是否启用"
                name="is_enabled"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="描述"
            name="description"
          >
            <TextArea rows={3} placeholder="请输入描述" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PositionManagement; 