import React, { useState, useEffect } from 'react';
import { Form, Input, InputNumber, DatePicker, Select, Switch, message } from 'antd';
import dynamicFieldsApi from '../../api/system/dynamicFields';

const { TextArea } = Input;
const { Option } = Select;

const PageDynamicForm = ({ 
  modelName, 
  pageName, 
  recordId, 
  form, 
  onValuesChange,
  initialValues = {} 
}) => {
  const [dynamicFields, setDynamicFields] = useState([]);
  const [loading, setLoading] = useState(false);

  // 加载页面动态字段定义
  const loadPageFields = async () => {
    try {
      setLoading(true);
      const response = await dynamicFieldsApi.getPageFields(modelName, pageName);
      if (response.data && response.data.success) {
        setDynamicFields(response.data.data || []);
      }
    } catch (error) {
      console.error('加载页面字段失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载记录动态字段值
  const loadRecordValues = async () => {
    if (!recordId) return;
    
    try {
      const response = await dynamicFieldsApi.getRecordPageValues(modelName, pageName, recordId);
      if (response.data && response.data.success) {
        const values = response.data.data || {};
        
        // 为没有值的字段设置默认值
        const formValues = { ...values };
        dynamicFields.forEach(field => {
          if (!(field.field_name in formValues) && field.default_value) {
            // 根据字段类型转换默认值
            let convertedValue = field.default_value;
            if (field.field_type === 'number') {
              convertedValue = parseFloat(field.default_value);
            } else if (field.field_type === 'checkbox') {
              convertedValue = field.default_value === 'true' || field.default_value === true;
            }
            formValues[field.field_name] = convertedValue;
          }
        });
        
        // 设置表单初始值
        form.setFieldsValue(formValues);
      }
    } catch (error) {
      console.error('加载记录字段值失败:', error);
    }
  };

  useEffect(() => {
    loadPageFields();
  }, [modelName, pageName]);

  useEffect(() => {
    if (recordId) {
      loadRecordValues();
    } else {
      // 新增记录时，为所有字段设置默认值
      const defaultValues = {};
      dynamicFields.forEach(field => {
        if (field.default_value) {
          // 根据字段类型转换默认值
          let convertedValue = field.default_value;
          if (field.field_type === 'number') {
            convertedValue = parseFloat(field.default_value);
          } else if (field.field_type === 'checkbox') {
            convertedValue = field.default_value === 'true' || field.default_value === true;
          }
          defaultValues[field.field_name] = convertedValue;
        }
      });
      if (Object.keys(defaultValues).length > 0) {
        form.setFieldsValue(defaultValues);
      }
    }
  }, [recordId, modelName, pageName, dynamicFields]);

  // 渲染动态字段
  const renderDynamicField = (field) => {
    const { field_name, field_label, field_type, field_options, is_required, is_readonly, help_text, default_value } = field;

    const commonProps = {
      name: field_name,
      label: field_label,
      required: is_required,
      disabled: is_readonly,
      help: help_text,
      initialValue: default_value, // 添加默认值
    };

    switch (field_type) {
      case 'text':
        return (
          <Form.Item key={field_name} {...commonProps}>
            <Input placeholder={`请输入${field_label}`} />
          </Form.Item>
        );

      case 'textarea':
        return (
          <Form.Item key={field_name} {...commonProps}>
            <TextArea rows={3} placeholder={`请输入${field_label}`} />
          </Form.Item>
        );

      case 'number':
        return (
          <Form.Item key={field_name} {...commonProps}>
            <InputNumber 
              style={{ width: '100%' }} 
              placeholder={`请输入${field_label}`} 
              defaultValue={default_value ? parseFloat(default_value) : undefined}
            />
          </Form.Item>
        );

      case 'date':
        return (
          <Form.Item key={field_name} {...commonProps}>
            <DatePicker 
              style={{ width: '100%' }} 
              placeholder={`请选择${field_label}`} 
            />
          </Form.Item>
        );

      case 'select':
        const options = field_options ? field_options.split('\n').filter(opt => opt.trim()) : [];
        return (
          <Form.Item key={field_name} {...commonProps}>
            <Select placeholder={`请选择${field_label}`}>
              {options.map((option, index) => (
                <Option key={index} value={option.trim()}>
                  {option.trim()}
                </Option>
              ))}
            </Select>
          </Form.Item>
        );

      case 'checkbox':
        return (
          <Form.Item key={field_name} {...commonProps} valuePropName="checked">
            <Switch 
              defaultChecked={default_value === 'true' || default_value === true}
            />
          </Form.Item>
        );

      default:
        return (
          <Form.Item key={field_name} {...commonProps}>
            <Input placeholder={`请输入${field_label}`} />
          </Form.Item>
        );
    }
  };

  if (loading) {
    return <div>加载中...</div>;
  }

  return (
    <div>
      {dynamicFields.map(field => renderDynamicField(field))}
    </div>
  );
};

export default PageDynamicForm; 