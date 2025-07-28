import React from 'react';
import { Form, Input, InputNumber, Select, DatePicker, Switch, Checkbox, Radio } from 'antd';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { RangePicker } = DatePicker;

const DynamicForm = ({ 
  fields = [], 
  values = {}, 
  onChange, 
  form, 
  layout = 'horizontal',
  labelCol = { span: 6 },
  wrapperCol = { span: 18 }
}) => {
  
  const renderField = (field) => {
    const { field_name, field_label, field_type, field_options, is_required, help_text, validation_rules } = field;
    
    const rules = [];
    if (is_required) {
      rules.push({ required: true, message: `${field_label}不能为空` });
    }
    
    // 添加自定义验证规则
    if (validation_rules) {
      if (validation_rules.min) {
        rules.push({ min: validation_rules.min, message: `${field_label}最小长度为${validation_rules.min}` });
      }
      if (validation_rules.max) {
        rules.push({ max: validation_rules.max, message: `${field_label}最大长度为${validation_rules.max}` });
      }
      if (validation_rules.pattern) {
        rules.push({ pattern: new RegExp(validation_rules.pattern), message: validation_rules.message || `${field_label}格式不正确` });
      }
    }
    
    const commonProps = {
      placeholder: `请输入${field_label}`,
      onChange: (value) => {
        if (onChange) {
          onChange(field_name, value);
        }
      },
      value: values[field_name],
    };
    
    switch (field_type) {
      case 'char':
        return (
          <Input 
            {...commonProps}
            maxLength={validation_rules?.max}
          />
        );
        
      case 'text':
        return (
          <TextArea 
            {...commonProps}
            rows={4}
            maxLength={validation_rules?.max}
          />
        );
        
      case 'integer':
        return (
          <InputNumber 
            {...commonProps}
            style={{ width: '100%' }}
            min={validation_rules?.min}
            max={validation_rules?.max}
          />
        );
        
      case 'float':
        return (
          <InputNumber 
            {...commonProps}
            style={{ width: '100%' }}
            precision={2}
            min={validation_rules?.min}
            max={validation_rules?.max}
          />
        );
        
      case 'boolean':
        return (
          <Switch 
            {...commonProps}
            checked={values[field_name] === true || values[field_name] === 'true'}
          />
        );
        
      case 'date':
        return (
          <DatePicker 
            {...commonProps}
            style={{ width: '100%' }}
            format="YYYY-MM-DD"
            value={values[field_name] ? dayjs(values[field_name]) : null}
            onChange={(date, dateString) => {
              if (onChange) {
                onChange(field_name, dateString);
              }
            }}
          />
        );
        
      case 'datetime':
        return (
          <DatePicker 
            {...commonProps}
            style={{ width: '100%' }}
            showTime
            format="YYYY-MM-DD HH:mm:ss"
            value={values[field_name] ? dayjs(values[field_name]) : null}
            onChange={(date, dateString) => {
              if (onChange) {
                onChange(field_name, dateString);
              }
            }}
          />
        );
        
      case 'selection':
        const options = field_options?.options || [];
        return (
          <Select 
            {...commonProps}
            options={options.map(opt => ({
              label: opt.label || opt.value,
              value: opt.value
            }))}
            allowClear
          />
        );
        
      case 'many2one':
        // 这里需要根据关联模型获取选项
        return (
          <Select 
            {...commonProps}
            placeholder={`请选择${field_label}`}
            allowClear
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
          />
        );
        
      default:
        return <Input {...commonProps} />;
    }
  };
  
  return (
    <Form
      form={form}
      layout={layout}
      labelCol={labelCol}
      wrapperCol={wrapperCol}
    >
      {fields.map(field => (
        <Form.Item
          key={field.field_name}
          label={field.field_label}
          name={field.field_name}
          rules={field.is_required ? [{ required: true, message: `${field.field_label}不能为空` }] : []}
          help={field.help_text}
        >
          {renderField(field)}
        </Form.Item>
      ))}
    </Form>
  );
};

export default DynamicForm; 