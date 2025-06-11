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
  Switch,
  InputNumber,
  Tooltip,
  Upload
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { bagTypeApi } from '../../../../api/production/production-archive/bagType';
import { bagTypeStructureApi } from '../../../../api/production/production-archive/bagType';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const BagTypeManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingBagType, setEditingBagType] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [enabledFilter, setEnabledFilter] = useState(undefined);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });

  // 表单和选项数据
  const [form] = Form.useForm();
  const [formOptions, setFormOptions] = useState({
    units: [],
    spec_expressions: [],
    structure_expressions: [],
    formulas: []
  });

  // 袋型结构数据
  const [structures, setStructures] = useState([]);
  const [structureIdCounter, setStructureIdCounter] = useState(1);

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await bagTypeApi.getBagTypes({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        is_enabled: enabledFilter,
        ...params
      });

      if (response.data.success) {
        const { bag_types, total, current_page } = response.data.data;
        
        
        // 为每行数据添加key
        const dataWithKeys = bag_types.map((item, index) => ({
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
      message.error('加载数据失败：' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  // 加载表单选项数据
  const loadFormOptions = async () => {
    try {
      const response = await bagTypeApi.getFormOptions();
      if (response.data.success) {
        setFormOptions(response.data.data);
      }
    } catch (error) {
      message.error('加载选项数据失败：' + (error.response?.data?.message || error.message));
    }
  };

  // 初始加载
  useEffect(() => {
    loadData();
    loadFormOptions();
  }, []);

  // 监听搜索和筛选条件变化
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      setPagination(prev => ({ ...prev, current: 1 }));
      loadData({ page: 1 });
    }, 300);

    return () => clearTimeout(delayedSearch);
  }, [searchText, enabledFilter]);

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setEnabledFilter(undefined);
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '', is_enabled: undefined });
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize
    });
  };

  // 显示新增/编辑模态框
  const showModal = async (record = null) => {
    setEditingBagType(record);
    if (record) {
      form.setFieldsValue({
        ...record,
        // 确保数值字段正确显示
        difficulty_coefficient: record.difficulty_coefficient || 0,
        bag_making_unit_price: record.bag_making_unit_price || 0,
        sort_order: record.sort_order || 0
      });
      
      // 加载袋型结构数据
      try {
        const response = await bagTypeStructureApi.getBagTypeStructures(record.id);
        if (response.data.success) {
          const structuresData = response.data.data.structures.map((structure, index) => ({
            ...structure,
            tempId: `temp_${index + 1}` // 添加临时ID用于前端编辑
          }));
          setStructures(structuresData);
          setStructureIdCounter(structuresData.length + 1);
        }
      } catch (error) {
        console.error('加载袋型结构失败:', error);
        setStructures([]);
      }
    } else {
      form.resetFields();
      form.setFieldsValue({
        is_enabled: true,
        is_strict_bag_type: true,
        difficulty_coefficient: 0,
        bag_making_unit_price: 0,
        sort_order: 0
      });
      setStructures([]);
      setStructureIdCounter(1);
    }
    setModalVisible(true);
  };

  // 保存袋型
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      let response;
      let bagTypeId;
      
      if (editingBagType) {
        response = await bagTypeApi.updateBagType(editingBagType.id, values);
        bagTypeId = editingBagType.id;
        if (response.data.success) {
          message.success('更新成功');
        }
      } else {
        response = await bagTypeApi.createBagType(values);
        if (response.data.success) {
          bagTypeId = response.data.data.id;
          message.success('创建成功');
        }
      }

      // 保存袋型结构数据
      if (bagTypeId && structures.length > 0) {
        try {
          const structuresData = structures.map(structure => ({
            structure_name: structure.structure_name,
            structure_expression_id: structure.structure_expression_id || null,
            expand_length_formula_id: structure.expand_length_formula_id || null,
            expand_width_formula_id: structure.expand_width_formula_id || null,
            material_length_formula_id: structure.material_length_formula_id || null,
            material_width_formula_id: structure.material_width_formula_id || null,
            single_piece_width_formula_id: structure.single_piece_width_formula_id || null,
            sort_order: structure.sort_order || 0,
            image_url: structure.image_url || null
          }));
          
          await bagTypeStructureApi.batchSaveBagTypeStructures(bagTypeId, structuresData);
        } catch (structureError) {
          message.warning('袋型保存成功，但结构数据保存失败：' + (structureError.response?.data?.message || structureError.message));
        }
      }

      setModalVisible(false);
      loadData();
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        message.error('保存失败：' + (error.response?.data?.message || error.message));
      }
    }
  };

  // 删除袋型
  const handleDelete = async (id) => {
    try {
      await bagTypeApi.deleteBagType(id);
      message.success('删除成功');
      loadData();
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.message || error.message));
    }
  };

  const handleStatusChange = async (id, checked) => {
    try {
      await bagTypeApi.updateBagType(id, { is_enabled: checked });
      message.success('状态更新成功');
      loadData();
    } catch (error) {
      message.error('状态更新失败：' + (error.response?.data?.message || error.message));
    }
  };

  // ====================== 袋型结构管理 ======================
  
  // 添加结构
  const addStructure = () => {
    const newStructure = {
      tempId: `temp_${structureIdCounter}`,
      structure_name: '',
      structure_expression_id: null,
      expand_length_formula_id: null,
      expand_width_formula_id: null,
      material_length_formula_id: null,
      material_width_formula_id: null,
      single_piece_width_formula_id: null,
      sort_order: structures.length + 1,
      image_url: ''
    };
    setStructures([...structures, newStructure]);
    setStructureIdCounter(structureIdCounter + 1);
  };

  // 删除结构
  const removeStructure = (tempId) => {
    setStructures(structures.filter(structure => structure.tempId !== tempId));
  };

  // 更新结构
  const updateStructure = (tempId, field, value) => {
    setStructures(structures.map(structure => 
      structure.tempId === tempId 
        ? { ...structure, [field]: value }
        : structure
    ));
  };

  // 结构表格列定义
  const structureColumns = [
    {
      title: '结构名称',
      dataIndex: 'structure_name',
      key: 'structure_name',
      width: 120,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => updateStructure(record.tempId, 'structure_name', e.target.value)}
          placeholder="请输入结构名称"
          size="small"
        />
      )
    },
    {
      title: '结构表达式',
      dataIndex: 'structure_expression_id',
      key: 'structure_expression_id',
      width: 150,
      render: (value, record) => (
        <Select
          value={value}
          onChange={(val) => updateStructure(record.tempId, 'structure_expression_id', val)}
          placeholder="请选择"
          allowClear
          size="small"
          style={{ width: '100%' }}
        >
          {(formOptions.structure_expressions || []).map(item => (
            <Option key={item.value} value={item.value}>
              {item.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: '展长公式',
      dataIndex: 'expand_length_formula_id',
      key: 'expand_length_formula_id',
      width: 150,
      render: (value, record) => (
        <Select
          value={value}
          onChange={(val) => updateStructure(record.tempId, 'expand_length_formula_id', val)}
          placeholder="请选择"
          allowClear
          size="small"
          style={{ width: '100%' }}
        >
          {(formOptions.formulas || []).map(item => (
            <Option key={item.value} value={item.value}>
              {item.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: '展宽公式',
      dataIndex: 'expand_width_formula_id',
      key: 'expand_width_formula_id',
      width: 150,
      render: (value, record) => (
        <Select
          value={value}
          onChange={(val) => updateStructure(record.tempId, 'expand_width_formula_id', val)}
          placeholder="请选择"
          allowClear
          size="small"
          style={{ width: '100%' }}
        >
          {(formOptions.formulas || []).map(item => (
            <Option key={item.value} value={item.value}>
              {item.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: '用料长公式',
      dataIndex: 'material_length_formula_id',
      key: 'material_length_formula_id',
      width: 150,
      render: (value, record) => (
        <Select
          value={value}
          onChange={(val) => updateStructure(record.tempId, 'material_length_formula_id', val)}
          placeholder="请选择"
          allowClear
          size="small"
          style={{ width: '100%' }}
        >
          {(formOptions.formulas || []).map(item => (
            <Option key={item.value} value={item.value}>
              {item.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: '用料宽公式',
      dataIndex: 'material_width_formula_id',
      key: 'material_width_formula_id',
      width: 150,
      render: (value, record) => (
        <Select
          value={value}
          onChange={(val) => updateStructure(record.tempId, 'material_width_formula_id', val)}
          placeholder="请选择"
          allowClear
          size="small"
          style={{ width: '100%' }}
        >
          {(formOptions.formulas || []).map(item => (
            <Option key={item.value} value={item.value}>
              {item.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: '单片宽公式',
      dataIndex: 'single_piece_width_formula_id',
      key: 'single_piece_width_formula_id',
      width: 150,
      render: (value, record) => (
        <Select
          value={value}
          onChange={(val) => updateStructure(record.tempId, 'single_piece_width_formula_id', val)}
          placeholder="请选择"
          allowClear
          size="small"
          style={{ width: '100%' }}
        >
          {(formOptions.formulas || []).map(item => (
            <Option key={item.value} value={item.value}>
              {item.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      render: (value, record) => (
        <InputNumber
          value={value}
          onChange={(val) => updateStructure(record.tempId, 'sort_order', val || 0)}
          min={0}
          size="small"
          style={{ width: '100%' }}
        />
      )
    },
    {
      title: '结构图片',
      dataIndex: 'image_url',
      key: 'image_url',
      width: 100,
      render: (imageUrl, record) => (
        <div style={{ textAlign: 'center' }}>
          {imageUrl ? (
            <div>
              <img 
                src={imageUrl} 
                alt="结构图片" 
                style={{ 
                  width: '60px', 
                  height: '40px', 
                  objectFit: 'cover',
                  cursor: 'pointer',
                  border: '1px solid #d9d9d9',
                  borderRadius: '4px'
                }}
                onClick={() => {
                  // 点击图片放大预览
                  Modal.info({
                    title: '结构图片预览',
                    content: (
                      <div style={{ textAlign: 'center' }}>
                        <img 
                          src={imageUrl} 
                          alt="结构图片预览" 
                          style={{ maxWidth: '100%', maxHeight: '400px' }}
                        />
                      </div>
                    ),
                    width: 600,
                    okText: '关闭'
                  });
                }}
              />
              <br />
              <Upload
                showUploadList={false}
                beforeUpload={(file) => {
                  // 这里可以实现图片上传逻辑
                  const reader = new FileReader();
                  reader.onload = (e) => {
                    updateStructure(record.tempId, 'image_url', e.target.result);
                  };
                  reader.readAsDataURL(file);
                  return false; // 阻止默认上传
                }}
              >
                <Button size="small" type="link" style={{ padding: 0, height: 'auto' }}>
                  更换
                </Button>
              </Upload>
            </div>
          ) : (
            <Upload
              showUploadList={false}
              beforeUpload={(file) => {
                // 这里可以实现图片上传逻辑
                const reader = new FileReader();
                reader.onload = (e) => {
                  updateStructure(record.tempId, 'image_url', e.target.result);
                };
                reader.readAsDataURL(file);
                return false; // 阻止默认上传
              }}
            >
              <Button size="small" style={{ fontSize: '12px' }}>
                上传图片
              </Button>
            </Upload>
          )}
        </div>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 60,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          danger
          onClick={() => removeStructure(record.tempId)}
        >
          删除
        </Button>
      )
    }
  ];

  // 表格列定义
  const columns = [
    {
      title: '袋型名称',
      dataIndex: 'bag_type_name',
      key: 'bag_type_name',
      width: 150,
      fixed: 'left',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '规格表达式',
      dataIndex: 'spec_expression',
      key: 'spec_expression',
      width: 150,
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      )
    },
    {
      title: '结构信息',
      dataIndex: 'structures',
      key: 'structures',
      width: 300,
      render: (structures) => {
        if (!structures || structures.length === 0) {
          return <Text type="secondary">暂无结构</Text>;
        }
        return (
          <div>
            {structures.map((structure, index) => (
              <div key={structure.id} style={{ marginBottom: index < structures.length - 1 ? 8 : 0 }}>
                <Row gutter={8} align="middle">
                  {structure.image_url && (
                    <Col>
                      <img 
                        src={structure.image_url} 
                        alt={structure.structure_name}
                        style={{ width: 40, height: 40, objectFit: 'contain' }}
                        onClick={() => window.open(structure.image_url, '_blank')}
                      />
                    </Col>
                  )}
                  <Col flex="1">
                    <div>
                      <Text strong>{structure.structure_name}</Text>
                    </div>
                    <div>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {structure.structure_expression?.name && `结构表达式: ${structure.structure_expression.name}`}
                      </Text>
                    </div>
                  </Col>
                </Row>
              </div>
            ))}
          </div>
        );
      }
    },
    {
      title: '生产单位',
      dataIndex: 'production_unit_name',
      key: 'production_unit_name',
      width: 100,
      align: 'center'
    },
    {
      title: '销售单位',
      dataIndex: 'sales_unit_name',
      key: 'sales_unit_name',
      width: 100,
      align: 'center'
    },
    {
      title: '难度系数',
      dataIndex: 'difficulty_coefficient',
      key: 'difficulty_coefficient',
      width: 100,
      align: 'right',
      render: (value) => value?.toFixed(2)
    },
    {
      title: '制袋单价',
      dataIndex: 'bag_making_unit_price',
      key: 'bag_making_unit_price',
      width: 100,
      align: 'right',
      render: (value) => value?.toFixed(2)
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      align: 'center'
    },
    {
      title: '启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      align: 'center',
      render: (enabled, record) => (
        <Switch
          checked={enabled}
          onChange={(checked) => handleStatusChange(record.id, checked)}
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
      render: (text) => text ? new Date(text).toLocaleString('zh-CN') : '-'
    },
    {
      title: '修改人',
      dataIndex: 'updated_by_name',
      key: 'updated_by_name',
      width: 100,
      align: 'center'
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      render: (text) => text ? new Date(text).toLocaleString('zh-CN') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      align: 'center',
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => showModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个袋型吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              icon={<DeleteOutlined />} 
              size="small" 
              danger
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 结构详情表格列定义
  const structureDetailColumns = [
    {
      title: '结构图片',
      dataIndex: 'image_url',
      key: 'image_url',
      width: 80,
      render: (imageUrl, record) => (
        <div style={{ textAlign: 'center' }}>
          {imageUrl ? (
            <img 
              src={imageUrl} 
              alt={record.structure_name}
              style={{ 
                width: '40px', 
                height: '30px', 
                objectFit: 'cover',
                borderRadius: '4px',
                cursor: 'pointer',
                border: '1px solid #d9d9d9'
              }}
              onClick={() => {
                Modal.info({
                  title: `结构图片预览 - ${record.structure_name}`,
                  content: (
                    <div style={{ textAlign: 'center' }}>
                      <img 
                        src={imageUrl} 
                        alt={record.structure_name}
                        style={{ maxWidth: '100%', maxHeight: '400px' }}
                      />
                    </div>
                  ),
                  width: 600,
                  okText: '关闭'
                });
              }}
            />
          ) : (
            <Text type="secondary" style={{ fontSize: '12px' }}>无图片</Text>
          )}
        </div>
      )
    },
    {
      title: '结构名称',
      dataIndex: 'structure_name',
      key: 'structure_name',
      width: 100,
      render: (text) => <Text strong style={{ fontSize: '12px' }}>{text}</Text>
    },
    {
      title: '结构表达式',
      dataIndex: 'structure_expression',
      key: 'structure_expression',
      width: 120,
      render: (expression) => (
        <Text style={{ fontSize: '12px' }}>
          {expression ? expression.name : '-'}
        </Text>
      )
    },
    {
      title: '展长公式',
      dataIndex: 'expand_length_formula',
      key: 'expand_length_formula',
      width: 120,
      render: (formula) => (
        <Text style={{ fontSize: '12px' }}>
          {formula ? formula.name : '-'}
        </Text>
      )
    },
    {
      title: '展宽公式',
      dataIndex: 'expand_width_formula',
      key: 'expand_width_formula',
      width: 120,
      render: (formula) => (
        <Text style={{ fontSize: '12px' }}>
          {formula ? formula.name : '-'}
        </Text>
      )
    },
    {
      title: '用料长公式',
      dataIndex: 'material_length_formula',
      key: 'material_length_formula',
      width: 120,
      render: (formula) => (
        <Text style={{ fontSize: '12px' }}>
          {formula ? formula.name : '-'}
        </Text>
      )
    },
    {
      title: '用料宽公式',
      dataIndex: 'material_width_formula',
      key: 'material_width_formula',
      width: 120,
      render: (formula) => (
        <Text style={{ fontSize: '12px' }}>
          {formula ? formula.name : '-'}
        </Text>
      )
    },
    {
      title: '单片宽公式',
      dataIndex: 'single_piece_width_formula',
      key: 'single_piece_width_formula',
      width: 120,
      render: (formula) => (
        <Text style={{ fontSize: '12px' }}>
          {formula ? formula.name : '-'}
        </Text>
      )
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 60,
      align: 'center',
      render: (text) => <Text style={{ fontSize: '12px' }}>{text}</Text>
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      key: 'created_by_name',
      width: 80,
      align: 'center',
      render: (text) => <Text style={{ fontSize: '12px' }}>{text || '-'}</Text>
    }
  ];

  // 展开行渲染函数
  const expandedRowRender = (record) => {
    if (!record.structures || record.structures.length === 0) {
      return (
        <div style={{ padding: '16px', textAlign: 'center', color: '#999' }}>
          暂无结构数据
        </div>
      );
    }

    return (
      <Table
        columns={structureDetailColumns}
        dataSource={record.structures}
        pagination={false}
        size="small"
        rowKey="id"
        style={{ margin: '0 24px' }}
        scroll={{ x: 'max-content' }}
      />
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>袋型管理</Title>
        </div>

        {/* 搜索和筛选区域 */}
        <Row justify="end" gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Input
              placeholder="搜索袋型名称、规格表达式"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              prefix={<SearchOutlined />}
              style={{ width: 200 }}
            />
          </Col>
          <Col>
            <Select
              placeholder="状态筛选"
              value={enabledFilter}
              onChange={setEnabledFilter}
              allowClear
              style={{ width: 120 }}
            >
              <Option value={true}>启用</Option>
              <Option value={false}>停用</Option>
            </Select>
          </Col>
          <Col>
            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => showModal()}
              >
                新增袋型
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => loadData()}
              >
                刷新
              </Button>
              <Button onClick={handleReset}>重置</Button>
            </Space>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 'max-content' }}
          size="small"
          expandable={{
            expandedRowRender,
            rowExpandable: (record) => record.structures && record.structures.length > 0
          }}
        />
      </Card>

      {/* 新增/编辑模态框 */}
      <Modal
        title={editingBagType ? '编辑袋型' : '新增袋型'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={1200}
        destroyOnClose
      >
        <div>
          {/* 袋型基本信息 */}
          <div style={{ marginBottom: 16 }}>
            <h4>袋型信息</h4>
          </div>
          
          <Form
            form={form}
            layout="vertical"
          >
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="袋型名称"
                  name="bag_type_name"
                  rules={[{ required: true, message: '请输入袋型名称' }]}
                >
                  <Input placeholder="请输入袋型名称" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="规格表达式"
                  name="spec_expression"
                >
                  <Select
                    placeholder="请选择规格表达式"
                    allowClear
                    showSearch
                    optionFilterProp="children"
                  >
                    {formOptions.spec_expressions.map(item => (
                      <Option key={item.value} value={item.value} title={item.description}>
                        {item.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="生产单位"
                  name="production_unit_id"
                >
                  <Select placeholder="请选择生产单位" allowClear>
                    {formOptions.units.map(unit => (
                      <Option key={unit.value} value={unit.value}>
                        {unit.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="销售单位"
                  name="sales_unit_id"
                >
                  <Select placeholder="请选择销售单位" allowClear>
                    {formOptions.units.map(unit => (
                      <Option key={unit.value} value={unit.value}>
                        {unit.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="difficulty_coefficient"
                  label="难易系数"
                  rules={[
                    { type: 'number', min: 0, message: '难易系数不能小于0' }
                  ]}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="请输入难易系数"
                    min={0}
                    precision={2}
                    step={0.01}
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="bag_making_unit_price"
                  label="制袋单价"
                  rules={[
                    { type: 'number', min: 0, message: '制袋单价不能小于0' }
                  ]}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="请输入制袋单价"
                    min={0}
                    precision={2}
                    step={0.01}
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  label="排序"
                  name="sort_order"
                >
                  <InputNumber 
                    min={0} 
                    style={{ width: '100%' }} 
                    placeholder="0"
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={6}>
                <Form.Item
                  label="卷膜"
                  name="is_roll_film"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  label="停用"
                  name="is_disabled"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  label="自定规格"
                  name="is_custom_spec"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  label="严格袋型"
                  name="is_strict_bag_type"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={6}>
                <Form.Item
                  label="工序判断"
                  name="is_process_judgment"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  label="是否纸尿裤"
                  name="is_diaper"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  label="是否编织袋"
                  name="is_woven_bag"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  label="是否标签"
                  name="is_label"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  label="是否天线"
                  name="is_antenna"
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
          
          {/* 袋型结构管理 */}
          <div style={{ marginTop: 24, marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h4 style={{ margin: 0 }}>袋型结构</h4>
              <Button 
                type="dashed" 
                onClick={addStructure}
                icon={<PlusOutlined />}
              >
                添加结构
              </Button>
            </div>
            
            <Table
              dataSource={structures}
              columns={structureColumns}
              pagination={false}
              rowKey="tempId"
              size="small"
              bordered
              scroll={{ x: 'max-content' }}
              locale={{ emptyText: '暂无结构数据，点击"添加结构"按钮新增' }}
            />
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default BagTypeManagement; 