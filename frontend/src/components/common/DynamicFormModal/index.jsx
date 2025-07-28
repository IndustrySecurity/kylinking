import React from 'react';
import {
  Modal,
  Form,
  Row,
  Col,
  Tabs,
  Space,
  Badge,
  Input,
  InputNumber,
  Switch,
  DatePicker,
  Select
} from 'antd';

const { TabPane } = Tabs;
const { TextArea } = Input;

const DynamicFormModal = ({
  visible = false,
  title = "表单",
  fieldConfig = {},
  dynamicFields = [],
  fieldGroups = {},
  columnSettingOrder = [],
  columnConfig = {}, // 添加列配置参数
  form,
  loading = false,
  onOk,
  onCancel,
  okText = "保存",
  cancelText = "取消",
  width = 800,
  layout = "vertical"
}) => {
  // 获取可见字段列表
  const getVisibleFormFields = () => {
    if (!fieldConfig) return [];
    
    const baseFields = Object.keys(fieldConfig || {}).filter(key => key !== 'action');
    const dynamicFieldNames = Array.isArray(dynamicFields) ? dynamicFields.map(field => field.field_name) : [];
    const allFields = [...baseFields, ...dynamicFieldNames];
    
    // 如果列配置为空，显示所有字段
    if (Object.keys(columnConfig || {}).length === 0) {
      return allFields;
    }
    
    // 根据列配置过滤字段，只显示被勾选的字段
    return allFields.filter(key => {
      // 基础字段的处理
      if (key === 'action') return false;
      
      // 必填字段始终显示，不能被隐藏
      const config = fieldConfig[key];
      if (config && config.required) {
        return true;
      }
      
      // 根据列配置决定是否显示（包括动态字段）
      return !(key in (columnConfig || {})) || columnConfig[key] === true;
    });
  };

  // 获取排序后的表单字段
  const getSortedFormFields = (fields) => {
    if (!Array.isArray(fields)) return [];
    
    // 如果有列设置顺序，优先使用列设置顺序
    if (Array.isArray(columnSettingOrder) && columnSettingOrder.length > 0) {
      const sortedFields = [];
      
      // 按照列设置顺序添加字段
      columnSettingOrder.forEach(fieldName => {
        if (fields.includes(fieldName)) {
          sortedFields.push(fieldName);
        }
      });
      
      // 添加列设置中没有的字段（按display_order排序）
      const remainingFields = fields.filter(field => !sortedFields.includes(field));
      const sortedRemainingFields = remainingFields.sort((a, b) => {
        const dynamicFieldA = Array.isArray(dynamicFields) ? dynamicFields.find(df => df.field_name === a) : null;
        const dynamicFieldB = Array.isArray(dynamicFields) ? dynamicFields.find(df => df.field_name === b) : null;
        
        const configA = fieldConfig[a];
        const configB = fieldConfig[b];
        
        const orderA = dynamicFieldA?.display_order || configA?.display_order || configA?.sort_order || 0;
        const orderB = dynamicFieldB?.display_order || configB?.display_order || configB?.sort_order || 0;
        
        return orderA - orderB;
      });
      
      return [...sortedFields, ...sortedRemainingFields];
    }
    
    // 如果没有列设置顺序，使用display_order排序
    const sortedFields = [...fields].sort((a, b) => {
      const dynamicFieldA = Array.isArray(dynamicFields) ? dynamicFields.find(df => df.field_name === a) : null;
      const dynamicFieldB = Array.isArray(dynamicFields) ? dynamicFields.find(df => df.field_name === b) : null;
      
      const configA = fieldConfig[a];
      const configB = fieldConfig[b];
      
      const orderA = dynamicFieldA?.display_order || configA?.display_order || configA?.sort_order || 0;
      const orderB = dynamicFieldB?.display_order || configB?.display_order || configB?.sort_order || 0;
      
      return orderA - orderB;
    });
    
    return sortedFields;
  };

  // 渲染表单字段
  const renderFormField = (field, config, dynamicField) => {
    let formItem;
    
    // 处理动态字段
    if (dynamicField) {
      switch (config.type) {
        case 'text':
          formItem = <TextArea rows={3} placeholder={`请输入${config.title}`} />;
          break;
        case 'number':
          formItem = <InputNumber 
            style={{ width: '100%' }} 
            placeholder={`请输入${config.title}`} 
            defaultValue={config.default_value ? parseFloat(config.default_value) : undefined}
          />;
          break;
        case 'integer':
        case 'float':
          formItem = <InputNumber 
            style={{ width: '100%' }} 
            placeholder={`请输入${config.title}`} 
            defaultValue={config.default_value ? parseFloat(config.default_value) : undefined}
          />;
          break;
        case 'checkbox':
        case 'boolean':
          formItem = <Switch 
            defaultChecked={config.default_value === 'true' || config.default_value === true}
          />;
          break;
        case 'date':
          formItem = <DatePicker style={{ width: '100%' }} placeholder={`请选择${config.title}`} />;
          break;
        case 'datetime':
          formItem = <DatePicker showTime style={{ width: '100%' }} placeholder={`请选择${config.title}`} />;
          break;
        case 'select':
        case 'selection':
          if (config.options) {
            let options = [];
            try {
              if (typeof config.options === 'string') {
                const parsedOptions = JSON.parse(config.options);
                
                if (parsedOptions && parsedOptions.options) {
                  options = Array.isArray(parsedOptions.options) ? parsedOptions.options : [];
                } else if (Array.isArray(parsedOptions)) {
                  options = parsedOptions;
                } else {
                  options = [];
                }
              } else if (config.options.options) {
                options = config.options.options;
              } else if (Array.isArray(config.options)) {
                options = config.options;
              }
            } catch (error) {
              options = [];
            }
            
            if (options.length > 0) {
              const selectOptions = options.map(opt => ({
                label: opt.label || opt.name || opt.value,
                value: opt.value || opt.id
              }));
              formItem = <Select placeholder={`请选择${config.title}`} options={selectOptions} />;
            } else {
              formItem = <Input placeholder={`请输入${config.title}`} />;
            }
          } else {
            formItem = <Input placeholder={`请输入${config.title}`} />;
          }
          break;
        default:
          formItem = <Input placeholder={`请输入${config.title}`} />;
      }
    } else {
      // 处理基础字段
      if (field === 'is_enabled') {
        formItem = <Switch />;
      } else if (field === 'sort_order') {
        formItem = <InputNumber style={{ width: '100%' }} placeholder={`请输入${config.title}`} />;
      } else if (field === 'description') {
        formItem = <TextArea rows={3} placeholder={`请输入${config.title}`} />;
      } else {
        formItem = <Input placeholder={`请输入${config.title}`} />;
      }
    }
    
    return (
      <Col span={12} key={field}>
        <Form.Item 
          label={config.title} 
          name={field}
          rules={config.required ? [{ required: true, message: `请输入${config.title}` }] : []}
          valuePropName={field === 'is_enabled' || config.type === 'boolean' ? 'checked' : 'value'}
          help={config.help_text}
        >
          {formItem}
        </Form.Item>
      </Col>
    );
  };

  // 渲染表单内容
  const renderFormContent = () => {
    return (
      <Form form={form} layout={layout}>
        <Tabs>
          {Object.entries(fieldGroups || {}).map(([groupKey, group]) => {
            const groupFields = Array.isArray(group?.fields) ? group.fields : [];
            // 获取该分组的所有可见字段（包括基础字段和动态字段）
            const visibleFields = groupFields.filter(field => 
              getVisibleFormFields().includes(field) && 
              !['created_at', 'updated_at', 'created_by_name', 'updated_by_name'].includes(field)
            );
            
            // 如果是基本信息分组，还需要添加动态字段
            let allVisibleFields = [...visibleFields];
            if (groupKey === 'basic' && Array.isArray(dynamicFields)) {
              const dynamicFieldNames = dynamicFields
                .filter(field => (field.page_name || 'default').trim() === '基本信息')
                .map(field => field.field_name)
                .filter(fieldName => getVisibleFormFields().includes(fieldName))
                .filter(fieldName => !visibleFields.includes(fieldName)); // 避免重复
              allVisibleFields = [...visibleFields, ...dynamicFieldNames];
            }
            
            if (Array.isArray(allVisibleFields) && allVisibleFields.length === 0) return null;
            
            return (
              <TabPane 
                tab={
                  <Space>
                    <span>{group.icon}</span>
                    <span>{group.title}</span>
                    <Badge count={Array.isArray(allVisibleFields) ? allVisibleFields.length : 0} size="small" style={{ backgroundColor: '#52c41a' }} />
                  </Space>
                } 
                key={groupKey}
              >
                <Row gutter={16}>
                  {getSortedFormFields(allVisibleFields).map(field => {
                    // 获取字段配置：动态字段从dynamicFields中获取，基础字段从fieldConfig中获取
                    let config = null;
                    const dynamicField = Array.isArray(dynamicFields) ? dynamicFields.find(df => df.field_name === field) : null;
                    if (dynamicField) {
                      config = {
                        title: dynamicField.field_label || dynamicField.field_Label,
                        width: 120,
                        required: dynamicField.is_required || false,
                        readonly: dynamicField.is_readonly || false,
                        type: dynamicField.field_type || 'text',
                        options: dynamicField.field_options || null,
                        help_text: dynamicField.help_text || null,
                        default_value: dynamicField.default_value || null,
                        display_order: dynamicField.display_order || 4.5 // 默认在描述(4)和显示排序(5)之间
                      };
                    } else {
                      config = fieldConfig[field];
                    }
                    
                    if (!config) return null;
                    
                    return renderFormField(field, config, dynamicField);
                  })}
                </Row>
              </TabPane>
            );
          })}
        </Tabs>
      </Form>
    );
  };

  return (
    <Modal
      title={title}
      open={visible}
      onCancel={onCancel}
      onOk={onOk}
      okText={okText}
      cancelText={cancelText}
      width={width}
      confirmLoading={loading}
    >
      {renderFormContent()}
    </Modal>
  );
};

export default DynamicFormModal; 