import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Switch,
  InputNumber,
  Space,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Form,
  Tooltip,
  Checkbox,
  Select
} from 'antd';
import {
  PlusOutlined,
  SaveOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { machineApi } from '../../../api/base-archive/production-archive/machineApi';

const { Title } = Typography;
const { Option } = Select;

const MachineManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingKey, setEditingKey] = useState('');
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });
  
  const [form] = Form.useForm();
  const searchInputRef = useRef(null);

  // 判断是否在编辑状态
  const isEditing = (record) => record.key === editingKey;

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {

      const response = await machineApi.getMachines({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });


      // 正确处理后端响应格式
      if (response.data.success) {
        const { machines, total, current_page } = response.data.data || {};
        const machinesArray = Array.isArray(machines) ? machines : [];
        
        
        // 为每行数据添加key
        const dataWithKeys = machinesArray.map((item, index) => ({
          ...item,
          key: item.id || `temp_${index}`
        }));
        
        setData(dataWithKeys);
        setPagination(prev => ({
          ...prev,
          total: total || 0,
          current: current_page || 1
        }));
      } else {
        console.error('API返回失败:', response.data.message);
        message.error('加载数据失败：' + (response.data.message || '未知错误'));
        setData([]);
      }
    } catch (error) {
      console.error('机台数据加载错误:', error);
      const errorMsg = error.response?.data?.message || error.response?.data?.error || error.message || '网络请求失败';
      message.error('加载数据失败：' + errorMsg);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    loadData();
  }, []);

  // 搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '' });
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize
    });
  };

  // 开始编辑
  const edit = (record) => {
    form.setFieldsValue({
      machine_name: '',
      model: '',
      min_width: null,
      max_width: null,
      production_speed: null,
      preparation_time: null,
      difficulty_factor: null,
      circulation_card_id: '',
      max_colors: null,
      kanban_display: '',
      capacity_formula: '',
      gas_unit_price: null,
      power_consumption: null,
      electricity_cost_per_hour: null,
      output_conversion_factor: null,
      plate_change_time: null,
      mes_barcode_prefix: '',
      is_curing_room: false,
      material_name: '',
      remarks: '',
      sort_order: 0,
      is_enabled: true,
      ...record,
    });
    setEditingKey(record.key);
  };

  // 取消编辑
  const cancel = () => {
    setEditingKey('');
    form.resetFields();
  };

  // 保存编辑
  const save = async (key) => {
    try {
      const row = await form.validateFields();
      const newData = [...data];
      const index = newData.findIndex((item) => key === item.key);

      if (index > -1) {
        const item = newData[index];
        const updatedItem = { ...item, ...row };
        
        // 调用API保存
        let response;
        if (item.id && !item.id.startsWith('temp_')) {
          // 更新现有记录
          response = await machineApi.updateMachine(item.id, row);
        } else {
          // 创建新记录
          response = await machineApi.createMachine(row);
        }

        // 正确处理后端响应格式
        if (response.data.success) {
          // 更新本地数据
          newData.splice(index, 1, {
            ...updatedItem,
            ...response.data.data,
            key: response.data.data.id
          });
          setData(newData);
          setEditingKey('');
          message.success('保存成功');
        }
      }
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        console.error('保存失败:', error);
        message.error('保存失败');
      }
    }
  };

  // 删除记录
  const handleDelete = async (key) => {
    try {
      const record = data.find(item => item.key === key);
      
      if (record.id && !record.id.startsWith('temp_')) {
        // 删除服务器记录
        const response = await machineApi.deleteMachine(record.id);
        if (response.data.success) {
          message.success('删除成功');
        }
      }
      
      // 删除本地记录
      const newData = data.filter(item => item.key !== key);
      setData(newData);
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  // 添加新行
  const handleAdd = async () => {
    const newKey = `temp_${Date.now()}`;
    
    // 尝试获取下一个机台编号
    let machineCode = '自动生成';
    try {
      const codeResponse = await machineApi.getNextMachineCode();
      if (codeResponse.data.success) {
        machineCode = codeResponse.data.data.next_code || machineCode;
      }
    } catch (error) {
      // 如果获取失败，继续使用默认值
      console.warn('获取下一个机台编号失败:', error);
    }
    
    const newData = {
      key: newKey,
      machine_code: machineCode,
      machine_name: '',
      model: '',
      min_width: null,
      max_width: null,
      production_speed: null,
      preparation_time: null,
      difficulty_factor: null,
      circulation_card_id: '',
      max_colors: null,
      kanban_display: '',
      capacity_formula: '',
      gas_unit_price: null,
      power_consumption: null,
      electricity_cost_per_hour: null,
      output_conversion_factor: null,
      plate_change_time: null,
      mes_barcode_prefix: '',
      is_curing_room: false,
      material_name: '',
      remarks: '',
      sort_order: 0,
      is_enabled: true,
      created_by_name: '',
      created_at: '',
      updated_by_name: '',
      updated_at: ''
    };
    
    setData([newData, ...data]);
    edit(newData);
  };

  // 可编辑单元格组件
  const EditableCell = ({
    editing,
    dataIndex,
    title,
    inputType,
    record,
    index,
    children,
    ...restProps
  }) => {
    let inputNode;
    
    switch (inputType) {
      case 'number':
        inputNode = <InputNumber min={0} precision={0} style={{ width: '100%' }} />;
        break;
      case 'decimal':
        inputNode = <InputNumber min={0} step={0.01} style={{ width: '100%' }} />;
        break;
      case 'switch':
        inputNode = <Switch />;
        break;
      case 'checkbox':
        inputNode = <Checkbox />;
        break;
      case 'select':
        inputNode = (
          <Select style={{ width: '100%' }}>
            <Option value="长×宽×速度">长×宽×速度</Option>
            <Option value="长×宽×速度×难度">长×宽×速度×难度</Option>
            <Option value="长×宽×层数">长×宽×层数</Option>
            <Option value="自定义公式">自定义公式</Option>
          </Select>
        );
        break;
      default:
        inputNode = <Input />;
    }

    return (
      <td {...restProps}>
        {editing ? (
          <Form.Item
            name={dataIndex}
            style={{ margin: 0 }}
            valuePropName={inputType === 'checkbox' || inputType === 'switch' ? 'checked' : 'value'}
            rules={[
              {
                required: dataIndex === 'machine_name',
                message: `请输入${title}!`,
              },
            ]}
          >
            {inputNode}
          </Form.Item>
        ) : (
          children
        )}
      </td>
    );
  };

  // 表格列定义
  const columns = [
    {
      title: '机台编号',
      dataIndex: 'machine_code',
      key: 'machine_code',
      width: 120,
      fixed: 'left',
      render: (text, record) => {
        const editable = isEditing(record);
        if (editable) {
          // 如果是新建记录且编号为"自动生成"，显示提示
          if (record.key.startsWith('temp_') && text === '自动生成') {
            return <span style={{ color: '#999' }}>自动生成</span>;
          }
          // 其他情况显示实际编号
          return <span style={{ fontWeight: 500 }}>{text}</span>;
        }
        return <span style={{ fontWeight: 500 }}>{text}</span>;
      }
    },
    {
      title: '机台名称',
      dataIndex: 'machine_name',
      key: 'machine_name',
      width: 150,
      editable: true,
      render: (text, record) => {
        const editable = isEditing(record);
        return editable ? text : (
          <span style={{ fontWeight: 500 }}>{text}</span>
        );
      }
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      width: 120,
      editable: true,
      render: (text) => text || '-'
    },
    {
      title: '最小门幅(mm)',
      dataIndex: 'min_width',
      key: 'min_width',
      width: 120,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '最大门幅(mm)',
      dataIndex: 'max_width',
      key: 'max_width',
      width: 120,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '生产均速(m/h)',
      dataIndex: 'production_speed',
      key: 'production_speed',
      width: 120,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '准备时间(h)',
      dataIndex: 'preparation_time',
      key: 'preparation_time',
      width: 110,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '难易系数',
      dataIndex: 'difficulty_factor',
      key: 'difficulty_factor',
      width: 100,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '流转卡标识',
      dataIndex: 'circulation_card_id',
      key: 'circulation_card_id',
      width: 120,
      editable: true,
      render: (text) => text || '-'
    },
    {
      title: '最大印色',
      dataIndex: 'max_colors',
      key: 'max_colors',
      width: 100,
      editable: true,
      inputType: 'number',
      align: 'center',
      render: (value) => value || '-'
    },
    {
      title: '看板显示',
      dataIndex: 'kanban_display',
      key: 'kanban_display',
      width: 120,
      editable: true,
      render: (text) => text || '-'
    },
    {
      title: '产能公式',
      dataIndex: 'capacity_formula',
      key: 'capacity_formula',
      width: 150,
      editable: true,
      inputType: 'select',
      render: (text) => text || '-'
    },
    {
      title: '燃气单价',
      dataIndex: 'gas_unit_price',
      key: 'gas_unit_price',
      width: 100,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '功耗(kw)',
      dataIndex: 'power_consumption',
      key: 'power_consumption',
      width: 100,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '电费(/h)',
      dataIndex: 'electricity_cost_per_hour',
      key: 'electricity_cost_per_hour',
      width: 100,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '产量换算倍数',
      dataIndex: 'output_conversion_factor',
      key: 'output_conversion_factor',
      width: 120,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: '换版时间',
      dataIndex: 'plate_change_time',
      key: 'plate_change_time',
      width: 100,
      editable: true,
      inputType: 'decimal',
      align: 'right',
      render: (value) => value ? `${value}` : '-'
    },
    {
      title: 'MES条码前缀',
      dataIndex: 'mes_barcode_prefix',
      key: 'mes_barcode_prefix',
      width: 120,
      editable: true,
      render: (text) => text || '-'
    },
    {
      title: '是否熟化室',
      dataIndex: 'is_curing_room',
      key: 'is_curing_room',
      width: 100,
      editable: true,
      inputType: 'checkbox',
      align: 'center',
      render: (checked, record) => {
        const editable = isEditing(record);
        return editable ? checked : (
          <Checkbox 
            checked={checked} 
            disabled 
          />
        );
      }
    },
    {
      title: '材料名称',
      dataIndex: 'material_name',
      key: 'material_name',
      width: 120,
      editable: true,
      render: (text) => text || '-'
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      width: 150,
      editable: true,
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text || '-'}
        </Tooltip>
      )
    },
    {
      title: '显示排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 100,
      editable: true,
      inputType: 'number',
      align: 'center'
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 100,
      editable: true,
      inputType: 'switch',
      align: 'center',
      render: (enabled, record) => {
        const editable = isEditing(record);
        return editable ? enabled : (
          <Switch 
            checked={enabled} 
            disabled 
            size="small"
          />
        );
      }
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
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      align: 'center',
      render: (_, record) => {
        const editable = isEditing(record);
        return editable ? (
          <Space>
            <Button
              type="link"
              size="small"
              icon={<CheckOutlined />}
              onClick={() => save(record.key)}
            >
              保存
            </Button>
            <Button
              type="link"
              size="small"
              icon={<CloseOutlined />}
              onClick={cancel}
            >
              取消
            </Button>
          </Space>
        ) : (
          <Space>
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              disabled={editingKey !== ''}
              onClick={() => edit(record)}
            >
              编辑
            </Button>
            <Popconfirm
              title="确定删除这条记录吗？"
              onConfirm={() => handleDelete(record.key)}
              disabled={editingKey !== ''}
            >
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
                disabled={editingKey !== ''}
              >
                删除
              </Button>
            </Popconfirm>
          </Space>
        );
      }
    }
  ];

  // 合并列配置
  const mergedColumns = columns.map((col) => {
    if (!col.editable) {
      return col;
    }
    return {
      ...col,
      onCell: (record) => ({
        record,
        inputType: col.inputType || 'text',
        dataIndex: col.dataIndex,
        title: col.title,
        editing: isEditing(record),
      }),
    };
  });

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Title level={4} style={{ margin: 0 }}>机台管理</Title>
          </Col>
          <Col>
            <Space>
              <Input
                ref={searchInputRef}
                placeholder="搜索机台名称、编号、型号"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onPressEnter={handleSearch}
                style={{ width: 250 }}
                allowClear
              />
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
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAdd}
                disabled={editingKey !== ''}
              >
                新增机台
              </Button>
            </Space>
          </Col>
        </Row>

        <Form form={form} component={false}>
          <Table
            components={{
              body: {
                cell: EditableCell,
              },
            }}
            bordered
            dataSource={data}
            columns={mergedColumns}
            rowClassName="editable-row"
            pagination={{
              ...pagination,
              onChange: (page, pageSize) => {
                handleTableChange({ ...pagination, current: page, pageSize });
              },
              onShowSizeChange: (current, size) => {
                handleTableChange({ ...pagination, current: 1, pageSize: size });
              }
            }}
            loading={loading}
            scroll={{ x: 2500 }}
            size="small"
          />
        </Form>
      </Card>
    </div>
  );
};

export default MachineManagement; 