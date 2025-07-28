import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  Form, 
  Input, 
  Select, 
  Switch, 
  Button, 
  Table, 
  Space, 
  Popconfirm, 
  message,
  Card,
  Row,
  Col,
  InputNumber,
  Divider
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, DragOutlined, MinusCircleOutlined } from '@ant-design/icons';
import dynamicFieldsApi from '../../api/system/dynamicFields';
import { useApi } from '../../hooks/useApi';
import FormulaEditor from './FormulaEditor';

const { TextArea } = Input;

// 字段选项编辑器组件
const FieldOptionsEditor = ({ value, onChange, fieldType, ...props }) => {
  const [options, setOptions] = useState([]);
  const [showJsonEditor, setShowJsonEditor] = useState(false);

  // 初始化选项
  useEffect(() => {
    if (value) {
      try {
        const parsed = JSON.parse(value);
        if (parsed && parsed.options && Array.isArray(parsed.options)) {
          setOptions(parsed.options);
        } else if (Array.isArray(parsed)) {
          setOptions(parsed);
        } else {
          setOptions([]);
        }
      } catch (error) {
        setOptions([]);
      }
    } else {
      setOptions([]);
    }
  }, [value]);

  // 添加选项
  const addOption = () => {
    const newOption = { label: '', value: '' };
    const newOptions = [...options, newOption];
    setOptions(newOptions);
    updateJsonValue(newOptions);
  };

  // 删除选项
  const removeOption = (index) => {
    const newOptions = options.filter((_, i) => i !== index);
    setOptions(newOptions);
    updateJsonValue(newOptions);
  };

  // 更新选项
  const updateOption = (index, field, value) => {
    const newOptions = [...options];
    newOptions[index] = { ...newOptions[index], [field]: value };
    setOptions(newOptions);
    updateJsonValue(newOptions);
  };

  // 更新JSON值
  const updateJsonValue = (newOptions) => {
    const jsonValue = JSON.stringify({ options: newOptions }, null, 2);
    onChange?.(jsonValue);
  };

  // 处理JSON编辑器变化
  const handleJsonChange = (e) => {
    onChange?.(e.target.value);
  };

  // 只有选择框类型才显示选项编辑器
  if (fieldType !== 'select' && fieldType !== 'selection') {
    return (
      <TextArea rows={4} placeholder="请输入JSON格式的字段选项" disabled />
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 8 }}>
        <span>选择框类型的字段需要配置选项</span>
        <Button 
          type="link" 
          size="small" 
          onClick={() => setShowJsonEditor(!showJsonEditor)}
          style={{ padding: 0, marginLeft: 8 }}
        >
          {showJsonEditor ? '使用可视化编辑器' : '使用JSON编辑器'}
        </Button>
      </div>
      {showJsonEditor ? (
        <TextArea 
          rows={6} 
          placeholder="请输入JSON格式的字段选项，如：{options: [{label: '选项1', value: 'value1'}]}"
          value={value}
          onChange={handleJsonChange}
        />
      ) : (
        <div>
          <div style={{ marginBottom: 8 }}>
            <Button 
              type="dashed" 
              onClick={addOption} 
              icon={<PlusOutlined />}
              size="small"
            >
              添加选项
            </Button>
          </div>
          
          {options.map((option, index) => (
            <div key={index} style={{ marginBottom: 8, display: 'flex', gap: 8, alignItems: 'center' }}>
              <Input
                placeholder="显示标签"
                value={option.label || ''}
                onChange={(e) => updateOption(index, 'label', e.target.value)}
                style={{ flex: 1 }}
              />
              <Input
                placeholder="选项值"
                value={option.value || ''}
                onChange={(e) => updateOption(index, 'value', e.target.value)}
                style={{ flex: 1 }}
              />
              <Button
                type="text"
                danger
                icon={<MinusCircleOutlined />}
                onClick={() => removeOption(index)}
                size="small"
              />
            </div>
          ))}
          
          {options.length === 0 && (
            <div style={{ 
              padding: 16, 
              textAlign: 'center', 
              color: '#999', 
              border: '1px dashed #d9d9d9',
              borderRadius: 6
            }}>
              暂无选项，点击"添加选项"开始配置
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const FieldManager = ({ 
  modelName, 
  visible, 
  onCancel, 
  onSuccess,
  title = '字段管理',
  predefinedPages = [] // 新增参数，用于接收预定义的页面名称
}) => {
  const [fields, setFields] = useState([]);
  const [fieldTypes, setFieldTypes] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingField, setEditingField] = useState(null);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [existingPages, setExistingPages] = useState([]); // 现有页面列表
  const [currentFieldType, setCurrentFieldType] = useState('text'); // 当前字段类型
  const { get, post, put, delete: deleteMethod } = useApi();
  
  // 清理拼音输入的函数
  const cleanPinyinEntries = (pages) => {
    return pages.filter(page => {
      // 移除看起来像拼音的条目（纯英文小写，长度小于等于4）
      const isPinyin = /^[a-z]{1,4}$/.test(page);
      return !isPinyin;
    });
  };

  
  // 加载字段列表
  const loadFields = async () => {
    try {
      setLoading(true);
      
      // 获取所有字段（不指定page_name）
      const response = await dynamicFieldsApi.getModelFields(modelName);
      
      if (response.data && response.data.success) {
        const fieldsData = response.data.data || [];
        
        // 过滤掉空对象
        const validFields = fieldsData.filter(field => field && field.field_name);
        setFields(validFields);
        
        // 提取当前模块的页面列表，过滤掉空值
        const currentPages = [...new Set(validFields.map(field => {
          const pageName = field.page_name || 'default';
          return pageName.trim() || 'default'; // 确保不是空字符串
        }))].filter(page => page && page.trim()); // 过滤掉空值
        
        // 尝试从其他模块获取页面名称作为参考
        let referencePages = [];
        try {
          const commonModels = ['customer_category', 'machine', 'product', 'order', 'supplier'];
          for (const model of commonModels) {
            if (model !== modelName) {
              const refResponse = await dynamicFieldsApi.getModelFields(model);
              if (refResponse.data && refResponse.data.success) {
                const refFields = refResponse.data.data || [];
                const refPages = [...new Set(refFields.map(field => {
                  const pageName = field.page_name || 'default';
                  return pageName.trim() || 'default'; // 确保不是空字符串
                }))];
                referencePages = [...referencePages, ...refPages];
              }
            }
          }
          // 去重并过滤空值
          referencePages = [...new Set(referencePages)].filter(page => page && page.trim());
        } catch (error) {
          // 获取参考页面失败不影响主要功能
        }
        
        // 合并当前页面、参考页面和预定义页面，过滤空值，并按中文名称排序
        const allPages = [...new Set([...currentPages, ...referencePages, ...predefinedPages])].filter(page => page && page.trim());
        // 清理拼音输入
        const cleanedPages = cleanPinyinEntries(allPages);
        const sortedPages = cleanedPages.sort((a, b) => {
          const aIsChinese = /[\u4e00-\u9fa5]/.test(a);
          const bIsChinese = /[\u4e00-\u9fa5]/.test(b);
          
          if (aIsChinese && !bIsChinese) return -1;
          if (!aIsChinese && bIsChinese) return 1;
          
          return a.localeCompare(b, 'zh-CN');
        });
        
        setExistingPages(sortedPages);
      }
    } catch (error) {
      console.error('加载字段失败:', error);
      message.error('加载字段列表失败');
    } finally {
      setLoading(false);
    }
  };
  
  // 加载字段类型
  const loadFieldTypes = async () => {
    try {
      const response = await dynamicFieldsApi.getFieldTypes();
      if (response.data && response.data.success) {
        setFieldTypes(response.data.data);
      }
    } catch (error) {
      message.error('加载字段类型失败');
    }
  };
  
  useEffect(() => {
    if (visible) {
      loadFields();
      loadFieldTypes();
    }
  }, [visible, modelName]);
  
  // 打开创建/编辑模态框
  const openModal = (field = null) => {
    setEditingField(field);
    setModalVisible(true);
    if (field) {
      // 确保页面名称是字符串格式，并添加到现有页面列表中
      const pageName = field.page_name || '';
      if (pageName && !existingPages.includes(pageName)) {
        setExistingPages(prev => {
          const newPages = [...prev, pageName];
          // 重新排序，保持中文在前
          return newPages.sort((a, b) => {
            const aIsChinese = /[\u4e00-\u9fa5]/.test(a);
            const bIsChinese = /[\u4e00-\u9fa5]/.test(b);
            
            if (aIsChinese && !bIsChinese) return -1;
            if (!aIsChinese && bIsChinese) return 1;
            
            return a.localeCompare(b, 'zh-CN');
          });
        });
      }
      
      const formData = {
        ...field,
        page_name: pageName
      };
      form.setFieldsValue(formData);
      setCurrentFieldType(field.field_type || 'text');
    } else {
      form.resetFields();
      form.setFieldsValue({
        field_type: 'text',
        is_required: false,
        is_readonly: false,
        is_visible: true,
        display_order: 0
      });
      setCurrentFieldType('text');
    }
  };
  
  // 保存字段
  const saveField = async (values) => {
    try {
      // 确保page_name有值，并处理可能的数组格式
      let pageName = values.page_name;
      if (Array.isArray(pageName)) {
        pageName = pageName[0] || '';
      }
      
      // 确保页面名称不是空字符串
      pageName = (pageName || '').trim();
      if (!pageName) {
        message.error('请输入页面名称');
        return;
      }
      
      // 构建字段数据，确保所有必需字段都有值
      const fieldData = {
        field_name: values.field_name?.trim(),
        field_label: values.field_label?.trim(),
        page_name: pageName,
        field_type: values.field_type || 'text',
        display_order: values.display_order || 999, // 新字段默认排在最后
        is_required: values.is_required || false,
        is_readonly: values.is_readonly || false,
        is_visible: values.is_visible !== false, // 默认为true
        default_value: values.default_value || null,
        help_text: values.help_text || null,
        field_options: values.field_options || null,
        validation_rules: values.validation_rules || null
      };
      
      // 如果是计算字段，添加计算相关数据
      if (values.field_type === 'calculated') {
        fieldData.calculation_formula = values.calculation_formula;
        fieldData.is_calculated = true;
        fieldData.is_readonly = true; // 计算字段默认只读
      }
      
      // 验证必需字段
      if (!fieldData.field_name) {
        message.error('请输入字段名称');
        return;
      }
      if (!fieldData.field_label) {
        message.error('请输入显示标签');
        return;
      }
      

      
      if (editingField) {
        // 更新字段
        const response = await dynamicFieldsApi.updateField(editingField.id, fieldData);
        if (response.data && response.data.success) {
          message.success('字段更新成功');
          
          // 如果页面名称发生变化，更新现有页面列表
          if (pageName && !existingPages.includes(pageName)) {
            setExistingPages(prev => {
              const newPages = [...prev, pageName];
              // 重新排序，保持中文在前
              return newPages.sort((a, b) => {
                const aIsChinese = /[\u4e00-\u9fa5]/.test(a);
                const bIsChinese = /[\u4e00-\u9fa5]/.test(b);
                
                if (aIsChinese && !bIsChinese) return -1;
                if (!aIsChinese && bIsChinese) return 1;
                
                return a.localeCompare(b, 'zh-CN');
              });
            });
          }
        }
      } else {
        // 创建字段
        try {
          const response = await dynamicFieldsApi.createField(modelName, fieldData);
          
          if (response.data && response.data.success) {
            const createdField = response.data.data;
            
            // 检查字段ID是否有效
            if (createdField?.id && createdField.id !== 'None' && createdField.id !== null) {
              message.success('字段创建成功');
              
              // 立即将新页面名称添加到现有页面列表中
              if (pageName && !existingPages.includes(pageName)) {
                setExistingPages(prev => {
                  const newPages = [...prev, pageName];
                  // 清理拼音输入并重新排序，保持中文在前
                  const cleanedPages = cleanPinyinEntries(newPages);
                  return cleanedPages.sort((a, b) => {
                    const aIsChinese = /[\u4e00-\u9fa5]/.test(a);
                    const bIsChinese = /[\u4e00-\u9fa5]/.test(b);
                    
                    if (aIsChinese && !bIsChinese) return -1;
                    if (!aIsChinese && bIsChinese) return 1;
                    
                    return a.localeCompare(b, 'zh-CN');
                  });
                });
              }
            } else {
              message.warning('字段创建成功，但可能存在数据问题，请检查字段列表');
            }
          } else {
            console.error('创建字段失败:', response);
            message.error('创建字段失败: ' + (response.data?.message || '未知错误'));
            return;
          }
        } catch (error) {
          console.error('创建字段异常:', error);
          console.error('异常详情:', error.response?.data);
          message.error('创建字段异常: ' + error.message);
          return;
        }
      }
      setModalVisible(false);
      // 立即重新加载字段
      await loadFields();
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('保存字段失败:', error);
      message.error(error.message || '保存失败');
    }
  };
  
  // 删除字段
  const deleteField = async (fieldId) => {
    try {
      const response = await dynamicFieldsApi.deleteField(fieldId);
      
      if (response.data && response.data.success) {
        message.success('字段删除成功');
        
        // 立即重新加载字段
        await loadFields();
        
        // 调用成功回调
        if (onSuccess) {
          onSuccess();
        }
      } else {
        message.error('删除失败: ' + (response.data?.message || '未知错误'));
      }
    } catch (error) {
      console.error('删除字段失败:', error);
      message.error('删除失败: ' + (error.response?.data?.message || error.message));
    }
  };
  
  // 表格列定义
  const columns = [
    {
      title: '字段名称',
      dataIndex: 'field_name',
      key: 'field_name',
    },
    {
      title: '显示标签',
      dataIndex: 'field_label',
      key: 'field_label',
    },
    {
      title: '页面',
      dataIndex: 'page_name',
      key: 'page_name',
      render: (pageName) => pageName || 'default',
    },
    {
      title: '字段类型',
      dataIndex: 'field_type',
      key: 'field_type',
      render: (type) => {
        const fieldType = fieldTypes.find(t => t.value === type);
        return fieldType ? fieldType.label : type;
      }
    },
    {
      title: '必填',
      dataIndex: 'is_required',
      key: 'is_required',
      render: (required) => required ? '是' : '否',
    },
    {
      title: '只读',
      dataIndex: 'is_readonly',
      key: 'is_readonly',
      render: (readonly) => readonly ? '是' : '否',
    },
    {
      title: '显示',
      dataIndex: 'is_visible',
      key: 'is_visible',
      render: (visible) => visible ? '是' : '否',
    },
    {
      title: '排序',
      dataIndex: 'display_order',
      key: 'display_order',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => openModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个字段吗？"
            onConfirm={() => deleteField(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];
  
  return (
    <>
      <Modal
        title={title}
        open={visible}
        onCancel={onCancel}
        footer={null}
        width={1000}
        destroyOnClose
      >
        <Card>
          <div style={{ marginBottom: 16 }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => openModal()}
            >
              添加字段
            </Button>
          </div>
          
          <Table
            columns={columns}
            dataSource={fields}
            rowKey="id"
            loading={loading}
            pagination={false}
            size="small"
          />
        </Card>
      </Modal>
      
      {/* 字段编辑模态框 */}
      <Modal
        title={editingField ? '编辑字段' : '添加字段'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={currentFieldType === 'calculated' ? 1200 : 800}
        style={{ top: 20 }}
        destroyOnHidden
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={saveField}
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="字段名称"
                name="field_name"
                rules={[
                  { required: true, message: '请输入字段名称' },
                  { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '字段名称只能包含字母、数字和下划线，且必须以字母或下划线开头' }
                ]}
              >
                <Input placeholder="请输入字段名称" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="显示标签"
                name="field_label"
                rules={[{ required: true, message: '请输入显示标签' }]}
              >
                <Input placeholder="请输入显示标签" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="页面名称"
                name="page_name"
                rules={[{ required: true, message: '请输入页面名称' }]}
                help="已有页面名称会显示在下拉框中，也可以输入新名称创建新页面。"
              >
                <Select
                  placeholder="请输入页面名称"
                  showSearch
                  allowClear
                  mode="combobox"
                  options={existingPages.map(page => {
                    // 检查是否是当前模块的页面
                    const isCurrentModulePage = fields.some(field => field.page_name === page);
                    const fieldCount = fields.filter(field => field.page_name === page).length;
                    const isPredefinedPage = predefinedPages.includes(page);
                    
                    return {
                      label: (
                        <span>
                          {page}
                          {isCurrentModulePage && fieldCount > 0 && (
                            <span style={{ color: '#1890ff', fontSize: '12px', marginLeft: '8px' }}>
                              ({fieldCount}个字段)
                            </span>
                          )}
                          {isPredefinedPage && !isCurrentModulePage && (
                            <span style={{ color: '#52c41a', fontSize: '12px', marginLeft: '8px' }}>
                              (预定义)
                            </span>
                          )}
                        </span>
                      ), 
                      value: page,
                      // 为中文页面名称添加特殊标识，当前模块页面加粗显示
                      style: {
                        fontWeight: page.match(/[\u4e00-\u9fa5]/) ? 'bold' : 'normal',
                        color: isCurrentModulePage ? '#000' : isPredefinedPage ? '#52c41a' : '#666'
                      }
                    };
                  })}
                  filterOption={(input, option) => {
                    const label = option?.label;
                    if (typeof label === 'string') {
                      return label.toLowerCase().includes(input.toLowerCase());
                    }
                    return false;
                  }}
                  onSearch={(value) => {
                    // 不在搜索时添加新页面名称，避免拼音输入过程中的临时值
                    // 只在用户真正确认输入时才添加
                  }}
                  onChange={(value) => {
                    // 当用户选择现有选项时，直接设置值
                    if (value) {
                      form.setFieldsValue({ page_name: value });
                    }
                  }}
                  onBlur={(e) => {
                    // 当用户失去焦点时，检查是否有新的页面名称需要添加
                    const inputValue = e.target.value;
                    if (inputValue && inputValue.trim()) {
                      const trimmedValue = inputValue.trim();
                      
                      // 检查是否是有效的页面名称
                      const isChinese = /[\u4e00-\u9fa5]/.test(trimmedValue);
                      const isEnglish = /^[a-zA-Z\s]+$/.test(trimmedValue);
                      const isNumber = /^\d+$/.test(trimmedValue);
                      
                      // 如果是有效的页面名称，则添加到列表中并选中
                      if (isChinese || isEnglish || isNumber) {
                        // 如果不在现有列表中，则添加
                        if (!existingPages.includes(trimmedValue)) {
                          setExistingPages(prev => {
                            const newPages = [...prev, trimmedValue];
                            // 清理拼音输入并重新排序，保持中文在前
                            const cleanedPages = cleanPinyinEntries(newPages);
                            return cleanedPages.sort((a, b) => {
                              const aIsChinese = /[\u4e00-\u9fa5]/.test(a);
                              const bIsChinese = /[\u4e00-\u9fa5]/.test(b);
                              
                              if (aIsChinese && !bIsChinese) return -1;
                              if (!aIsChinese && bIsChinese) return 1;
                              
                              return a.localeCompare(b, 'zh-CN');
                            });
                          });
                        }
                        
                        // 无论是否在现有列表中，都设置为当前值
                        form.setFieldsValue({ page_name: trimmedValue });
                      }
                    }
                  }}
                  dropdownRender={(menu) => (
                    <div>
                      {menu}
                    </div>
                  )}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="字段类型"
                name="field_type"
                rules={[{ required: true, message: '请选择字段类型' }]}
              >
                <Select 
                  placeholder="请选择字段类型"
                  onChange={(value) => setCurrentFieldType(value)}
                >
                  {fieldTypes.map(type => (
                    <Select.Option key={type.value} value={type.value}>
                      {type.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="显示顺序"
                name="display_order"
                initialValue={0}
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="必填"
                name="is_required"
                valuePropName="checked"
                initialValue={false}
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="只读"
                name="is_readonly"
                valuePropName="checked"
                initialValue={false}
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="显示"
                name="is_visible"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            label="默认值"
            name="default_value"
          >
            <Input placeholder="请输入默认值" />
          </Form.Item>
          
          <Form.Item
            label="帮助文本"
            name="help_text"
          >
            <TextArea rows={2} placeholder="请输入帮助文本" />
          </Form.Item>
          
          {/* 计算字段公式编辑器 */}
          {currentFieldType === 'calculated' && (
            <Form.Item
              label="计算公式"
              name="calculation_formula"
              rules={[{ required: true, message: '请输入计算公式' }]}
            >
              <FormulaEditor
                currentFieldName={form.getFieldValue('field_name')} // 传递当前字段名称
                availableFields={[
                  // 这里需要从父组件传入可用字段列表
                  { key: 'category_name', label: '分类名称' },
                  { key: 'category_code', label: '分类编码' },
                  { key: 'description', label: '描述' },
                  { key: 'sort_order', label: '显示排序' },
                  // 动态字段会在这里显示
                  ...fields.map(field => ({
                    key: field.field_name,
                    label: field.field_label
                  }))
                ]}
              />
            </Form.Item>
          )}
          
          <Form.Item
            label="字段选项"
            name="field_options"
          >
            <FieldOptionsEditor 
              fieldType={currentFieldType}
            />
          </Form.Item>
          
          <Form.Item
            label="验证规则"
            name="validation_rules"
            help="JSON格式的验证规则，如：{min: 1, max: 100, pattern: '^[0-9]+$'}"
          >
            <TextArea rows={3} placeholder="请输入JSON格式的验证规则" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default FieldManager; 