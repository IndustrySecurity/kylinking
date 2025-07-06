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
  Select,
  Modal,
  Tabs,
  Checkbox,
  Divider
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
import processCategoryApi from '../../../api/base-category/processCategoryApi';

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

const ProcessCategoryManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingKey, setEditingKey] = useState('');
  const [searchText, setSearchText] = useState('');
  const [form] = Form.useForm();
  const [modalVisible, setModalVisible] = useState(false);
  const [modalForm] = Form.useForm();
  const [editingRecord, setEditingRecord] = useState(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total) => `共 ${total} 条记录`,
  });

  // 选择选项
  const [categoryTypeOptions, setCategoryTypeOptions] = useState([]);
  const [dataCollectionModeOptions, setDataCollectionModeOptions] = useState([]);

  useEffect(() => {
    loadData();
    loadOptions();
  }, [pagination.current, pagination.pageSize, searchText]);

  const loadOptions = async () => {
    try {
      // 先设置静态选项测试
      setCategoryTypeOptions([
        { value: 'laminating', label: '淋膜' }
      ]);
      
      setDataCollectionModeOptions([
        { value: 'auto_weighing_scanning', label: '自动称重扫码模式' },
        { value: 'auto_meter_scanning', label: '自动取米扫码模式' },
        { value: 'auto_scanning', label: '自动扫码模式' },
        { value: 'auto_weighing', label: '自动称重模式' },
        { value: 'weighing_only', label: '仅称重模式' },
        { value: 'scanning_summary_weighing', label: '扫码汇总称重模式' }
      ]);

      // 尝试从API获取选项
      const [typeRes, modeRes] = await Promise.all([
        processCategoryApi.getProcessCategoryTypeOptions(),
        processCategoryApi.getDataCollectionModeOptions()
      ]);
      
      // 处理类型选项
      if (isSuccessResp(typeRes)) {
        const options = typeRes.data.data || [];
        // 过滤掉value为空字符串的选项
        setCategoryTypeOptions(options.filter(option => option.value !== ''));
      } else if (typeRes && typeRes.data && Array.isArray(typeRes.data)) {
        setCategoryTypeOptions(typeRes.data.filter(option => option.value !== ''));
      }
      
      // 处理数据采集模式选项
      if (isSuccessResp(modeRes)) {
        const options = modeRes.data.data || [];
        // 过滤掉value为空字符串的选项
        setDataCollectionModeOptions(options.filter(option => option.value !== ''));
      } else if (modeRes && modeRes.data && Array.isArray(modeRes.data)) {
        setDataCollectionModeOptions(modeRes.data.filter(option => option.value !== ''));
      }
    } catch (error) {
      console.error('加载选项失败:', error);
      // 保持静态选项作为后备
    }
  };

  // 新增: 通用成功判断函数
  const isSuccessResp = (resp) => {
    return resp && resp.data && (resp.data.success === true || resp.data.code === 200);
  };

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await processCategoryApi.getProcessCategories({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...params
      });

      if (isSuccessResp(response)) {
        const { process_categories, items, total, current_page } = response.data.data;
        const list = process_categories || items || [];
        
        // 为每行数据添加key
        const dataWithKeys = list.map((item, index) => ({
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
      console.error('加载数据失败:', error);
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理分页变化
  const handleTableChange = (paginationConfig) => {
    setPagination(prev => ({
      ...prev,
      current: paginationConfig.current,
      pageSize: paginationConfig.pageSize,
    }));
  };

  // 处理搜索
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData();
  };

  // 刷新数据
  const handleRefresh = () => {
    setSearchText('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData();
  };

  // 开启编辑
  const edit = (record) => {
    form.setFieldsValue({ ...record });
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
        
        // 调用API保存
        const response = await processCategoryApi.updateProcessCategory(item.id, row);
        
        if (isSuccessResp(response)) {
          // 保存成功后重新加载数据，确保排序和创建人修改人信息立即生效
          setEditingKey('');
          message.success('保存成功');
          loadData(); // 重新加载数据而不是仅更新本地状态
        }
      }
    } catch (errInfo) {
      console.error('保存失败:', errInfo);
      message.error('保存失败');
    }
  };

  // 删除记录
  const deleteRecord = async (record) => {
    try {
      await processCategoryApi.deleteProcessCategory(record.id);
      message.success('删除成功');
      loadData();
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  // 显示新建/编辑对话框
  const showModal = (record = null) => {
    setEditingRecord(record);
    if (record) {
      modalForm.setFieldsValue(record);
    } else {
      modalForm.resetFields();
      // 为新建记录设置默认值
      modalForm.setFieldsValue({
        sort_order: 0,
        is_enabled: true,
        show_data_collection_interface: false
      });
    }
    setModalVisible(true);
  };

  // 关闭对话框
  const handleModalCancel = () => {
    setModalVisible(false);
    setEditingRecord(null);
    modalForm.resetFields();
  };

  // 保存对话框数据
  const handleModalOk = async () => {
    try {
      const values = await modalForm.validateFields();
      console.log('表单值:', values);
      
      if (editingRecord) {
        // 更新
        console.log('更新记录:', editingRecord.id);
        const response = await processCategoryApi.updateProcessCategory(editingRecord.id, values);
        console.log('更新响应:', response);
        if (isSuccessResp(response)) {
          message.success('更新成功');
          loadData();
          handleModalCancel();
        } else {
          message.error(response?.data?.message || '更新失败');
        }
      } else {
        // 新建
        console.log('创建新记录');
        const response = await processCategoryApi.createProcessCategory(values);
        console.log('创建响应:', response);
        if (isSuccessResp(response)) {
          message.success('创建成功');
          loadData();
          handleModalCancel();
        } else {
          message.error(response?.data?.message || '创建失败');
        }
      }
    } catch (error) {
      console.error('保存失败:', error);
      if (error.errorFields) {
        message.error('请检查表单填写是否正确');
      } else {
        message.error(`保存失败: ${error.message || '未知错误'}`);
      }
    }
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
    const getInputNode = () => {
      switch (inputType) {
        case 'number':
          return <InputNumber style={{ width: '100%' }} precision={0} />;
        case 'switch':
          return <Switch />;
        case 'textarea':
          return <TextArea rows={2} />;
        case 'select':
          if (dataIndex === 'category_type') {
            return (
              <Select style={{ width: '100%' }} allowClear placeholder="请选择类型">
                {categoryTypeOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            );
          }
          return <Select style={{ width: '100%' }} />;
        case 'checkbox':
          return <Checkbox />;
        default:
          return <Input />;
      }
    };

    return (
      <td {...restProps}>
        {editing ? (
          <Form.Item
            name={dataIndex}
            style={{ margin: 0 }}
            rules={[
              {
                required: ['process_name'].includes(dataIndex),
                message: `${title}不能为空`,
              },
            ]}
            valuePropName={inputType === 'checkbox' || inputType === 'switch' ? 'checked' : 'value'}
          >
            {getInputNode()}
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
      title: '工序分类',
      dataIndex: 'process_name',
      key: 'process_name',
      width: 120,
      editable: true,
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: '类型',
      dataIndex: 'category_type',
      key: 'category_type',
      width: 100,
      editable: true,
      inputType: 'select',
      render: (text) => {
        // 显示类型的中文标签
        const option = categoryTypeOptions.find(opt => opt.value === text);
        return option ? option.label : text || '-';
      },
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      editable: true,
      inputType: 'number',
    },
    {
      title: '是否启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 100,
      editable: true,
      inputType: 'switch',
      render: (enabled) => (
        <Switch checked={enabled} size="small" disabled />
      ),
    },
    {
      title: '创建人',
      dataIndex: 'created_by_username',
      key: 'created_by_username',
      width: 100,
      render: (text) => text || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => text ? new Date(text).toLocaleString() : '-',
    },
    {
        title: '修改人',
        dataIndex: 'updated_by_username',
        key: 'updated_by_username',
        width: 100,
        render: (text) => text || '-',
      },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      render: (text) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 260,
      fixed: 'right',
      render: (_, record) => {
        const editable = isEditing(record);
        return editable ? (
          <Space>
            <Button
              icon={<CheckOutlined />}
              type="primary"
              size="small"
              onClick={() => save(record.key)}
            >
              保存
            </Button>
            <Button
              icon={<CloseOutlined />}
              size="small"
              onClick={cancel}
            >
              取消
            </Button>
          </Space>
        ) : (
          <Space>
            <Button
              icon={<EditOutlined />}
              size="small"
              disabled={editingKey !== ''}
              onClick={() => showModal(record)}
            >
              详细编辑
            </Button>
            <Button
              icon={<EditOutlined />}
              size="small"
              disabled={editingKey !== ''}
              onClick={() => edit(record)}
            >
              快速编辑
            </Button>
            <Popconfirm
              title="确定删除这条记录吗？"
              onConfirm={() => deleteRecord(record)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                icon={<DeleteOutlined />}
                size="small"
                danger
                disabled={editingKey !== ''}
              >
                删除
              </Button>
            </Popconfirm>
          </Space>
        );
      },
    },
  ];

  const isEditing = (record) => record.key === editingKey;

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

  // 定义各个配置字段分组
  const basicConfigFields = [
    { key: 'report_quantity', label: '上报数量' },
    { key: 'report_personnel', label: '上报人员' },
    { key: 'report_data', label: '上报数据' },
    { key: 'report_kg', label: '上报KG' },
    { key: 'report_number', label: '报号' },
    { key: 'report_time', label: '上报时间' },
    { key: 'down_report_time', label: '下报时间' },
    { key: 'machine_speed', label: '机速' },
    { key: 'cutting_specs', label: '分切规格' },
    { key: 'aging_room', label: '熟化室' },
    { key: 'reserved_char_1', label: '预留字符1' },
    { key: 'reserved_char_2', label: '预留字符2' },
    { key: 'net_weight', label: '净重' },
    { key: 'production_task_display_order', label: '生产任务显示序号' },
  ];

  const packingConfigFields = [
    { key: 'packing_bags_count', label: '装箱袋数' },
    { key: 'pallet_barcode', label: '托盘条码' },
    { key: 'pallet_bag_loading', label: '托盘装袋数' },
    { key: 'box_loading_count', label: '入托箱数' },
    { key: 'seed_bag_count', label: '种袋数' },
    { key: 'defect_bag_count', label: '除袋数' },
    { key: 'report_staff', label: '上报人员' },
    { key: 'shortage_count', label: '缺数' },
    { key: 'material_specs', label: '材料规格' },
    { key: 'color_mixing_count', label: '合色数' },
    { key: 'batch_bags', label: '批袋' },
    { key: 'production_date', label: '生产日期' },
    { key: 'compound', label: '复合' },
    { key: 'process_machine_allocation', label: '工艺分机台' },
  ];

  const continuityConfigFields = [
    { key: 'continuity_rate', label: '持续率' },
    { key: 'strip_head_change_count', label: '换条头数' },
    { key: 'plate_support_change_count', label: '换版支数' },
    { key: 'plate_change_count', label: '换版次数' },
    { key: 'lamination_change_count', label: '换贴合报' },
    { key: 'plate_making_multiple', label: '制版倍送' },
    { key: 'algorithm_time', label: '换算时间' },
    { key: 'timing', label: '计时' },
    { key: 'pallet_time', label: '托盘时间' },
    { key: 'glue_water_change_count', label: '换胶水数' },
    { key: 'glue_drip_bag_change', label: '换条胶袋' },
    { key: 'pallet_sub_bag_change', label: '换压报料' },
    { key: 'transfer_report_change', label: '换转报料' },
    { key: 'auto_print', label: '自动打印' },
  ];

  const processControlFields = [
    { key: 'process_rate', label: '过程率' },
    { key: 'color_set_change_count', label: '换套色数' },
    { key: 'mesh_format_change_count', label: '换网格数' },
    { key: 'overtime', label: '加班' },
    { key: 'team_date', label: '班组日期' },
    { key: 'sampling_time', label: '打样时间' },
    { key: 'start_reading', label: '开始读数' },
    { key: 'count_times', label: '计次' },
    { key: 'blade_count', label: '刀刃数' },
    { key: 'power_consumption', label: '用电量' },
    { key: 'maintenance_time', label: '维修时间' },
    { key: 'end_time', label: '结束时间' },
    { key: 'malfunction_material_collection', label: '故障次数领料' },
    { key: 'is_query_machine', label: '是否询机' },
  ];

  const mesConfigFields = [
    { key: 'mes_report_kg_manual', label: 'MES上报kg取用里kg' },
    { key: 'mes_kg_auto_calculation', label: 'MES上报kg自动接算' },
    { key: 'auto_weighing_once', label: '自动称重一次' },
    { key: 'mes_process_feedback_clear', label: 'MES工艺反馈空工艺' },
    { key: 'mes_consumption_solvent_by_ton', label: 'MES消耗溶剂用里按吨' },
    { key: 'single_report_open', label: '单报装打开' },
    { key: 'multi_condition_open', label: '多条件同时开工' },
    { key: 'mes_line_start_work_order', label: 'MES线本单开工单' },
    { key: 'mes_material_kg_consumption', label: 'MES上报材料kg用里消费kg' },
    { key: 'mes_report_not_less_than_kg', label: 'MES上报数不能小于上报kg' },
    { key: 'mes_water_consumption_by_ton', label: 'MES耗水用里按吨' },
  ];

  // 自检类型字段
  const selfCheckFields = [
    { key: 'self_check_type_1', label: '自检1' },
    { key: 'self_check_type_2', label: '自检2' },
    { key: 'self_check_type_3', label: '自检3' },
    { key: 'self_check_type_4', label: '自检4' },
    { key: 'self_check_type_5', label: '自检5' },
    { key: 'self_check_type_6', label: '自检6' },
    { key: 'self_check_type_7', label: '自检7' },
    { key: 'self_check_type_8', label: '自检8' },
    { key: 'self_check_type_9', label: '自检9' },
    { key: 'self_check_type_10', label: '自检10' },
  ];

  // 工艺预料字段
  const processMaterialFields = [
    { key: 'process_material_1', label: '工艺1' },
    { key: 'process_material_2', label: '工艺2' },
    { key: 'process_material_3', label: '工艺3' },
    { key: 'process_material_4', label: '工艺4' },
    { key: 'process_material_5', label: '工艺5' },
    { key: 'process_material_6', label: '工艺6' },
    { key: 'process_material_7', label: '工艺7' },
    { key: 'process_material_8', label: '工艺8' },
    { key: 'process_material_9', label: '工艺9' },
    { key: 'process_material_10', label: '工艺10' },
  ];

  // 预留字段
  const reservedFields = [
    { key: 'reserved_popup_1', label: '弹出1', type: 'input' },
    { key: 'reserved_popup_2', label: '弹出2', type: 'input' },
    { key: 'reserved_popup_3', label: '弹出3', type: 'input' },
    { key: 'reserved_dropdown_1', label: '下拉1', type: 'input' },
    { key: 'reserved_dropdown_2', label: '下拉2', type: 'input' },
    { key: 'reserved_dropdown_3', label: '下拉3', type: 'input' },
  ];

  // 数字字段
  const numberFields = [
    { key: 'number_1', label: '数字1' },
    { key: 'number_2', label: '数字2' },
    { key: 'number_3', label: '数字3' },
    { key: 'number_4', label: '数字4' },
  ];

  const renderCheckboxGroup = (fields, span = 8) => (
    <Row gutter={[16, 16]}>
      {fields.map(field => (
        <Col span={span} key={field.key}>
          <Form.Item
            name={field.key}
            valuePropName="checked"
            style={{ marginBottom: 8 }}
          >
            <Checkbox>{field.label}</Checkbox>
          </Form.Item>
        </Col>
      ))}
    </Row>
  );

  const modalTabItems = [
    {
      key: 'basic',
      label: '基本信息',
      children: (
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="process_name"
              label="工序分类"
              rules={[{ required: true, message: '请输入工序分类名称' }]}
            >
              <Input placeholder="请输入工序分类名称" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="category_type" label="类型">
              <Select placeholder="请选择类型" allowClear>
                {categoryTypeOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="data_collection_mode" label="数据自动采集模式">
              <Select placeholder="请选择数据自动采集模式" allowClear>
                {dataCollectionModeOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="sort_order" label="排序" initialValue={0}>
              <InputNumber placeholder="请输入排序" min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item name="show_data_collection_interface" valuePropName="checked">
              <Checkbox>显示数据采集界面</Checkbox>
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item name="description" label="描述">
              <TextArea rows={3} placeholder="请输入描述" />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item name="is_enabled" valuePropName="checked" initialValue={true} label="是否启用">
              <Switch checkedChildren="启用" unCheckedChildren="禁用" />
            </Form.Item>
          </Col>
          
          {/* 自检类型字段 */}
          <Col span={24}>
            <h4>自检类型</h4>
          </Col>
          {Array.from({ length: 10 }, (_, i) => i + 1).map(num => (
            <Col span={12} key={`self_check_type_${num}`}>
              <Form.Item name={`self_check_type_${num}`} label={`自检${num}`}>
                <Input placeholder={`请输入自检${num}`} />
              </Form.Item>
            </Col>
          ))}
          
          {/* 工艺预料字段 */}
          <Col span={24}>
            <h4>工艺预料</h4>
          </Col>
          {Array.from({ length: 10 }, (_, i) => i + 1).map(num => (
            <Col span={12} key={`process_material_${num}`}>
              <Form.Item name={`process_material_${num}`} label={`工艺${num}`}>
                <Input placeholder={`请输入工艺${num}`} />
              </Form.Item>
            </Col>
          ))}
          
          {/* 预留字段 */}
          <Col span={24}>
            <h4>预留字段</h4>
          </Col>
          {Array.from({ length: 3 }, (_, i) => i + 1).map(num => (
            <Col span={8} key={`reserved_popup_${num}`}>
              <Form.Item name={`reserved_popup_${num}`} label={`弹出${num}`}>
                <Input placeholder={`请输入弹出${num}`} />
              </Form.Item>
            </Col>
          ))}
          {Array.from({ length: 3 }, (_, i) => i + 1).map(num => (
            <Col span={8} key={`reserved_dropdown_${num}`}>
              <Form.Item name={`reserved_dropdown_${num}`} label={`下拉${num}`}>
                <Input placeholder={`请输入下拉${num}`} />
              </Form.Item>
            </Col>
          ))}
          
          {/* 数字字段 */}
          <Col span={24}>
            <h4>数字字段</h4>
          </Col>
          {Array.from({ length: 4 }, (_, i) => i + 1).map(num => (
            <Col span={6} key={`number_${num}`}>
              <Form.Item name={`number_${num}`} label={`数字${num}`}>
                <InputNumber style={{ width: '100%' }} placeholder={`请输入数字${num}`} />
              </Form.Item>
            </Col>
          ))}
        </Row>
      ),
    },
    {
      key: 'basicConfig',
      label: '基础配置',
      children: renderCheckboxGroup(basicConfigFields),
    },
    {
      key: 'packingConfig',
      label: '装箱配置',
      children: renderCheckboxGroup(packingConfigFields),
    },
    {
      key: 'continuityConfig',
      label: '持续率配置',
      children: renderCheckboxGroup(continuityConfigFields),
    },
    {
      key: 'processControl',
      label: '过程管控',
      children: renderCheckboxGroup(processControlFields),
    },
    {
      key: 'mesConfig',
      label: 'MES配置',
      children: renderCheckboxGroup(mesConfigFields, 6),
    },
  ];

  return (
    <div style={{ padding: '20px' }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Title level={4} style={{ margin: 0 }}>工序分类管理</Title>
          </Col>
          <Col>
            <Space>
              <Input
                placeholder="搜索工序分类名称、类型"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onPressEnter={handleSearch}
                style={{ width: 200 }}
                prefix={<SearchOutlined />}
              />
              <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                搜索
              </Button>
              <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
                刷新
              </Button>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={() => showModal()}
              >
                新建
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
              onChange: (page, pageSize) => handleTableChange({ current: page, pageSize }),
              onShowSizeChange: (current, size) => handleTableChange({ current, pageSize: size }),
            }}
            loading={loading}
            scroll={{ x: 1200 }}
          />
        </Form>

        {/* 详细编辑对话框 */}
        <Modal
          title={editingRecord ? "编辑工序分类" : "新建工序分类"}
          visible={modalVisible}
          onOk={handleModalOk}
          onCancel={handleModalCancel}
          width={1000}
          okText="保存"
          cancelText="取消"
        >
          <Form
            form={modalForm}
            layout="vertical"
            scrollToFirstError
          >
            <Tabs defaultActiveKey="basic" size="small">
              <TabPane tab="基本信息" key="basic">
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      name="process_name"
                      label="工序分类"
                      rules={[{ required: true, message: '请输入工序分类' }]}
                    >
                      <Input placeholder="请输入工序分类" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="category_type" label="类型">
                      <Select placeholder="请选择类型" allowClear>
                        {categoryTypeOptions.map(option => (
                          <Option key={option.value} value={option.value}>
                            {option.label}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="data_collection_mode" label="数据自动采集模式">
                      <Select placeholder="请选择数据自动采集模式" allowClear>
                        {dataCollectionModeOptions.map(option => (
                          <Option key={option.value} value={option.value}>
                            {option.label}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="sort_order" label="排序" initialValue={0}>
                      <InputNumber placeholder="请输入排序" min={0} style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                  <Col span={24}>
                    <Form.Item name="show_data_collection_interface" valuePropName="checked">
                      <Checkbox>显示数据采集界面</Checkbox>
                    </Form.Item>
                  </Col>
                  <Col span={24}>
                    <Form.Item name="description" label="描述">
                      <Input.TextArea placeholder="请输入描述" rows={3} />
                    </Form.Item>
                  </Col>
                  <Col span={24}>
                    <Form.Item name="is_enabled" valuePropName="checked" initialValue={true} label="是否启用">
                      <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                    </Form.Item>
                  </Col>
                </Row>
              </TabPane>
              
              <TabPane tab="基础配置" key="basic_config">
                {renderCheckboxGroup(basicConfigFields)}
              </TabPane>
              
              <TabPane tab="装箱配置" key="packing_config">
                {renderCheckboxGroup(packingConfigFields)}
              </TabPane>
              
              <TabPane tab="持续率配置" key="continuity_config">
                {renderCheckboxGroup(continuityConfigFields)}
              </TabPane>
              
              <TabPane tab="过程管控" key="process_control">
                {renderCheckboxGroup(processControlFields)}
              </TabPane>
              
              <TabPane tab="MES配置" key="mes_config">
                {renderCheckboxGroup(mesConfigFields)}
              </TabPane>

              <TabPane tab="自检类型" key="self_check">
                <Row gutter={16}>
                  {selfCheckFields.map((field, index) => (
                    <Col span={12} key={field.key}>
                      <Form.Item name={field.key} label={field.label}>
                        <Input placeholder={`请输入${field.label}`} />
                      </Form.Item>
                    </Col>
                  ))}
                </Row>
              </TabPane>

              <TabPane tab="工艺预料" key="process_material">
                <Row gutter={16}>
                  {processMaterialFields.map((field, index) => (
                    <Col span={12} key={field.key}>
                      <Form.Item name={field.key} label={field.label}>
                        <Input placeholder={`请输入${field.label}`} />
                      </Form.Item>
                    </Col>
                  ))}
                </Row>
              </TabPane>

              <TabPane tab="预留字段" key="reserved">
                <Row gutter={16}>
                  {reservedFields.map((field, index) => (
                    <Col span={12} key={field.key}>
                      <Form.Item name={field.key} label={field.label}>
                        <Input placeholder={`请输入${field.label}`} />
                      </Form.Item>
                    </Col>
                  ))}
                </Row>
              </TabPane>

              <TabPane tab="数字字段" key="number">
                <Row gutter={16}>
                  {numberFields.map((field, index) => (
                    <Col span={12} key={field.key}>
                      <Form.Item name={field.key} label={field.label}>
                        <InputNumber 
                          placeholder={`请输入${field.label}`} 
                          style={{ width: '100%' }}
                          precision={4}
                        />
                      </Form.Item>
                    </Col>
                  ))}
                </Row>
              </TabPane>
            </Tabs>
          </Form>
        </Modal>
      </Card>
    </div>
  );
};

export default ProcessCategoryManagement; 