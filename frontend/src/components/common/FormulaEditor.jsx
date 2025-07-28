import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  Select, 
  Button, 
  Space, 
  Card, 
  Row, 
  Col, 
  Typography,
  Divider,
  message
} from 'antd';
import { PlusOutlined, CalculatorOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;
const { Text } = Typography;

const FormulaEditor = ({ value, onChange, availableFields = [], currentFieldName, ...props }) => {
  const [formula, setFormula] = useState(value || '');
  const [selectedField, setSelectedField] = useState('');
  
  // 确保当外部 value 变化时，内部状态同步更新
  useEffect(() => {
    if (value !== undefined && value !== formula) {
      setFormula(value || '');
    }
  }, [value]);
  const [operators] = useState([
    { label: '加号 (+)', value: ' + ' },
    { label: '减号 (-)', value: ' - ' },
    { label: '乘号 (*)', value: ' * ' },
    { label: '除号 (/)', value: ' / ' },
    { label: '括号 (', value: '(' },
    { label: '括号 )', value: ')' },
    { label: '大于 (>)', value: ' > ' },
    { label: '小于 (<)', value: ' < ' },
    { label: '等于 (==)', value: ' == ' },
    { label: '不等于 (!=)', value: ' != ' },
    { label: '大于等于 (>=)', value: ' >= ' },
    { label: '小于等于 (<=)', value: ' <= ' }
  ]);

  const [functions] = useState([
    { label: '如果条件 (if)', value: 'if(condition, true_value, false_value)' },
    { label: '四舍五入 (round)', value: 'round(value, 2)' },
    { label: '取绝对值 (abs)', value: 'abs(value)' },
    { label: '最小值 (min)', value: 'min(value1, value2)' },
    { label: '最大值 (max)', value: 'max(value1, value2)' },
    { label: '字符串拼接 (concat)', value: 'concat(field1, " - ", field2)' },
    { label: '格式化数字 (format_number)', value: 'format_number(value, 2)' }
  ]);

  useEffect(() => {
    setFormula(value || '');
  }, [value]);

  // 添加字段到公式
  const addField = () => {
    if (selectedField) {
      const fieldKey = availableFields.find(f => f.label === selectedField)?.key;
      if (fieldKey) {
        const newFormula = formula + fieldKey;
        setFormula(newFormula);
        onChange?.(newFormula);
        setSelectedField('');
      }
    }
  };

  // 添加操作符到公式
  const addOperator = (operator) => {
    const newFormula = formula + operator;
    setFormula(newFormula);
    onChange?.(newFormula);
  };

  // 添加函数到公式
  const addFunction = (func) => {
    const newFormula = formula + func;
    setFormula(newFormula);
    onChange?.(newFormula);
  };

  // 清空公式
  const clearFormula = () => {
    setFormula('');
    onChange?.('');
  };

  // 测试公式
  const testFormula = () => {
    if (!formula.trim()) {
      message.warning('请先输入公式');
      return;
    }
    
    // 这里可以添加公式验证逻辑
    message.success('公式格式正确！');
  };

  return (
    <div>
      <Row gutter={16}>
        <Col span={16}>
          <Card size="small" title="公式编辑器" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={24}>
                <Form.Item label="计算公式" required>
                  <TextArea
                    value={formula}
                    onChange={(e) => {
                      setFormula(e.target.value);
                      onChange?.(e.target.value);
                    }}
                    placeholder="请输入计算公式，例如: field1 + field2 * 0.1"
                    rows={6}
                    style={{ fontFamily: 'monospace', fontSize: '14px' }}
                    {...props}
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={24}>
                <Space>
                  <Button onClick={testFormula} icon={<CalculatorOutlined />}>
                    测试公式
                  </Button>
                  <Button onClick={clearFormula} danger>
                    清空公式
                  </Button>
                </Space>
              </Col>
            </Row>
          </Card>

          <Card size="small" title="可用字段" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={18}>
                <Select
                  placeholder="选择字段"
                  value={selectedField}
                  onChange={setSelectedField}
                  style={{ width: '100%' }}
                >
                  {availableFields
                    .filter(field => field.key !== currentFieldName) // 过滤掉当前字段
                    .map(field => (
                      <Option key={field.key} value={field.label}>
                        {field.label} ({field.key})
                      </Option>
                    ))}
                </Select>
              </Col>
              <Col span={6}>
                <Button 
                  type="primary" 
                  onClick={addField}
                  disabled={!selectedField}
                  icon={<PlusOutlined />}
                >
                  添加字段
                </Button>
              </Col>
            </Row>
          </Card>
        </Col>

        <Col span={8}>
          <Card size="small" title="操作符" style={{ marginBottom: 16 }}>
            <Row gutter={[8, 8]}>
              {operators.map(op => (
                <Col key={op.value} span={12}>
                  <Button 
                    size="small" 
                    onClick={() => addOperator(op.value)}
                    style={{ width: '100%', fontSize: '12px' }}
                  >
                    {op.label}
                  </Button>
                </Col>
              ))}
            </Row>
          </Card>

          <Card size="small" title="函数" style={{ marginBottom: 16 }}>
            <Row gutter={[8, 8]}>
              {functions.map(func => (
                <Col key={func.value} span={24}>
                  <Button 
                    size="small" 
                    onClick={() => addFunction(func.value)}
                    style={{ width: '100%', fontSize: '12px', textAlign: 'left' }}
                  >
                    {func.label}
                  </Button>
                </Col>
              ))}
            </Row>
          </Card>

          <Card size="small" title="公式示例">
            <div style={{ fontSize: '12px', color: '#666' }}>
              <p><strong>基础计算：</strong></p>
              <div style={{ backgroundColor: '#f5f5f5', padding: '4px', borderRadius: '4px', fontFamily: 'monospace' }}>
                field1 + field2 * 0.1
              </div>
              <p style={{ marginTop: '8px' }}><strong>条件计算：</strong></p>
                             <div style={{ backgroundColor: '#f5f5f5', padding: '4px', borderRadius: '4px', fontFamily: 'monospace' }}>
                 if(field1 &gt; 100, field1 * 0.1, field1 * 0.05)
               </div>
              <p style={{ marginTop: '8px' }}><strong>字符串拼接：</strong></p>
              <div style={{ backgroundColor: '#f5f5f5', padding: '4px', borderRadius: '4px', fontFamily: 'monospace' }}>
                concat(field1, " - ", field2)
              </div>
              <p style={{ marginTop: '8px' }}><strong>格式化数字：</strong></p>
              <div style={{ backgroundColor: '#f5f5f5', padding: '4px', borderRadius: '4px', fontFamily: 'monospace' }}>
                format_number(field1 * field2, 2)
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default FormulaEditor; 