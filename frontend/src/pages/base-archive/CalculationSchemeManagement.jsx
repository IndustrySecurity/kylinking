import React, { useState, useEffect, useRef } from 'react';
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
  Divider,
  List,
  Badge,
  Tooltip,
  Tag,
  Switch
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  CalculatorOutlined,
  CheckOutlined,
  CloseOutlined,
  CopyOutlined,
  ClearOutlined
} from '@ant-design/icons';
import { calculationSchemeApi } from '../../api/calculationScheme';
import { calculationParameterApi } from '../../api/calculationParameter';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

// 计算器按钮组件
const CalculatorButton = ({ children, onClick, type = "default", style = {} }) => {
  const buttonStyle = {
    width: '60px',
    height: '40px',
    margin: '2px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
    fontWeight: 'bold',
    ...style
  };

  return (
    <Button 
      style={buttonStyle} 
      type={type}
      onClick={onClick}
    >
      {children}
    </Button>
  );
};

const CalculationSchemeManagement = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingScheme, setEditingScheme] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
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
  const [schemeCategories, setSchemeCategories] = useState([]);
  const [calculationParameters, setCalculationParameters] = useState([]);
  
  // 公式编辑相关状态
  const [currentFormula, setCurrentFormula] = useState('');
  const formulaTextAreaRef = useRef(null);

  // 加载数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await calculationSchemeApi.getCalculationSchemes({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        category: categoryFilter,
        ...params
      });

      // 正确处理后端响应格式
      if (response.data.success) {
        const { calculation_schemes, total, current_page } = response.data.data;
        
        setData(calculation_schemes || []);
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
      // 加载方案分类
      const categoriesResponse = await calculationSchemeApi.getSchemeCategories();
      if (categoriesResponse.data.success) {
        setSchemeCategories(categoriesResponse.data.data.scheme_categories || []);
      }

      // 加载计算参数
      const parametersResponse = await calculationParameterApi.getCalculationParameterOptions();
      if (parametersResponse.data.success) {
        setCalculationParameters(parametersResponse.data.data.calculation_parameters || []);
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
    setCategoryFilter('');
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '', category: '' });
  };

  // 刷新数据
  const handleRefresh = () => {
    loadData();
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
    setEditingScheme(record);
    if (record) {
      form.setFieldsValue({
        scheme_name: record.scheme_name,
        scheme_category: record.scheme_category,
        description: record.description,
        sort_order: record.sort_order || 0,
        is_enabled: record.is_enabled !== false
      });
      setCurrentFormula(record.scheme_formula || '');
    } else {
      form.resetFields();
      setCurrentFormula('');
    }
    setModalVisible(true);
  };

  // 保存方案
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const formData = {
        ...values,
        scheme_formula: currentFormula
      };

      if (editingScheme) {
        await calculationSchemeApi.updateCalculationScheme(editingScheme.id, formData);
        message.success('更新成功');
      } else {
        await calculationSchemeApi.createCalculationScheme(formData);
        message.success('创建成功');
      }

      setModalVisible(false);
      loadData();
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        message.error('保存失败：' + (error.response?.data?.error || error.message));
      }
    }
  };

  // 删除方案
  const handleDelete = async (id) => {
    try {
      await calculationSchemeApi.deleteCalculationScheme(id);
      message.success('删除成功');
      loadData();
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.error || error.message));
    }
  };

  // 公式验证相关函数
  const validateFormulaStructure = (formula) => {
    if (!formula || !formula.trim()) {
      return { valid: false, message: '公式不能为空' };
    }

    const trimmedFormula = formula.trim();
    const errors = [];
    const warnings = [];

    // 1. 括号匹配检查
    const openParens = (trimmedFormula.match(/\(/g) || []).length;
    const closeParens = (trimmedFormula.match(/\)/g) || []).length;
    if (openParens !== closeParens) {
      errors.push('括号不匹配');
    }

    // 2. 中括号匹配检查（参数）
    const openBrackets = (trimmedFormula.match(/\[/g) || []).length;
    const closeBrackets = (trimmedFormula.match(/\]/g) || []).length;
    if (openBrackets !== closeBrackets) {
      errors.push('参数中括号不匹配');
    }

    // 3. 单引号匹配检查（字符串）
    const singleQuotes = (trimmedFormula.match(/'/g) || []).length;
    if (singleQuotes % 2 !== 0) {
      errors.push('字符串单引号不匹配');
    }

    // 4. 参数有效性检查
    const parameterRegex = /\[([^\]]+)\]/g;
    const parametersInFormula = [];
    let match;
    while ((match = parameterRegex.exec(trimmedFormula)) !== null) {
      parametersInFormula.push(match[1]);
    }

    const validParameterNames = calculationParameters.map(p => p.parameter_name);
    const invalidParameters = [];
    
    parametersInFormula.forEach(paramName => {
      // 精确匹配
      if (!validParameterNames.includes(paramName)) {
        // 尝试大小写不敏感匹配
        const paramLower = paramName.toLowerCase();
        const validNamesLower = validParameterNames.map(name => name.toLowerCase());
        if (!validNamesLower.includes(paramLower)) {
          invalidParameters.push(paramName);
        } else {
          // 找到大小写不匹配的情况
          const correctName = validParameterNames[validNamesLower.indexOf(paramLower)];
          warnings.push(`参数 "${paramName}" 应该是 "${correctName}"（注意大小写）`);
        }
      }
    });

    if (invalidParameters.length > 0) {
      errors.push(`无效的参数: ${invalidParameters.join(', ')}`);
      // 提供可用参数建议
      if (validParameterNames.length > 0) {
        const suggestion = validParameterNames.slice(0, 5).join(', ');
        warnings.push(`可用的参数有: ${suggestion}${validParameterNames.length > 5 ? '...' : ''}`);
      }
    }

    // 5. 基本语法检查 - 检查是否有未被引号包围的非法字符
    const stringRegex = /'[^']*'/g;
    let formulaWithoutStrings = trimmedFormula;
    const strings = [];
    
    // 提取所有字符串
    let stringMatch;
    while ((stringMatch = stringRegex.exec(trimmedFormula)) !== null) {
      strings.push(stringMatch[0]);
      formulaWithoutStrings = formulaWithoutStrings.replace(stringMatch[0], `__STRING_${strings.length - 1}__`);
    }

    // 移除参数引用
    formulaWithoutStrings = formulaWithoutStrings.replace(/\[([^\]]+)\]/g, '__PARAM__');

    // 检查剩余内容是否包含非法字符
    const allowedPattern = /^[0-9A-Za-z+\-*/()>=<.\s如果那么否则结束或者并且__PARAM____STRING_\d+__]*$/;
    if (!allowedPattern.test(formulaWithoutStrings)) {
      // 找出具体的非法字符
      const validChars = /[0-9A-Za-z+\-*/()>=<.\s如果那么否则结束或者并且_]/g;
      const invalidChars = formulaWithoutStrings.replace(validChars, '').split('').filter((char, index, arr) => arr.indexOf(char) === index);
      if (invalidChars.length > 0) {
        errors.push(`包含非法字符: ${invalidChars.join(', ')}`);
      }
    }

    // 6. 检查运算符周围的空格（推荐但不强制）
    const operatorPattern = /[+\-*/>=<]/;
    const lines = trimmedFormula.split('\n');
    
    lines.forEach((line, lineIndex) => {
      // 检查运算符前后是否有适当的空格
      const operatorMatches = line.match(/[+\-*/>=<]/g);
      if (operatorMatches) {
        // 这里只是警告，不作为错误
        const hasProperSpacing = /\s[+\-*/>=<]\s/.test(line);
        if (!hasProperSpacing && operatorMatches.length > 0) {
          warnings.push(`第${lineIndex + 1}行建议在运算符前后添加空格`);
        }
      }
    });

    // 7. 逻辑结构检查
    const ifCount = trimmedFormula.split('如果').length - 1;
    const thenCount = trimmedFormula.split('那么').length - 1;
    const elseCount = trimmedFormula.split('否则').length - 1;
    const endCount = trimmedFormula.split('结束').length - 1;
    
    if (ifCount > 0) {
      if (thenCount < ifCount) {
        warnings.push('每个"如果"应该对应一个"那么"');
      }
      if (endCount < ifCount) {
        warnings.push('每个"如果"应该对应一个"结束"');
      }
    }

    // 8. 检查参数名称格式
    parametersInFormula.forEach(paramName => {
      if (/[^\w\u4e00-\u9fff]/.test(paramName)) {
        warnings.push(`参数名称 "${paramName}" 包含特殊字符，建议只使用字母、数字和中文`);
      }
    });

    if (errors.length > 0) {
      return { 
        valid: false, 
        message: errors.join('; '),
        warnings: warnings
      };
    }

    return { 
      valid: true, 
      message: '公式语法正确',
      warnings: warnings
    };
  };

  // 验证公式（改进版）
  const validateFormula = async () => {
    if (!currentFormula.trim()) {
      message.warning('请输入公式');
      return;
    }

    // 先进行前端验证
    const frontendValidation = validateFormulaStructure(currentFormula);
    
    if (!frontendValidation.valid) {
      message.error(`前端验证失败: ${frontendValidation.message}`);
      return;
    }

    // 显示警告信息
    if (frontendValidation.warnings && frontendValidation.warnings.length > 0) {
      frontendValidation.warnings.forEach(warning => {
        message.warning(warning);
      });
    }

    // 前端验证通过后，调用后端验证
    try {
      const response = await calculationSchemeApi.validateFormula(currentFormula);
      const { valid, message: validationMessage } = response;
      
      if (valid) {
        message.success(`验证通过: ${validationMessage}`);
      } else {
        message.error(`后端验证失败: ${validationMessage}`);
      }
    } catch (error) {
      message.error('后端验证失败：' + (error.response?.data?.error || error.message));
    }
  };

  // 插入参数时自动添加空格
  const insertParameter = (parameterName) => {
    const textarea = formulaTextAreaRef.current?.resizableTextArea?.textArea;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      
      // 检查前后是否需要添加空格
      const beforeChar = start > 0 ? currentFormula[start - 1] : '';
      const afterChar = end < currentFormula.length ? currentFormula[end] : '';
      
      let insertText = `[${parameterName}]`;
      
      // 如果前面不是空格、换行或开头，添加空格
      if (beforeChar && beforeChar !== ' ' && beforeChar !== '\n') {
        insertText = ' ' + insertText;
      }
      
      // 如果后面不是空格、运算符、换行或结尾，添加空格
      if (afterChar && afterChar !== ' ' && afterChar !== '\n' && !/[+\-*/()>=<]/.test(afterChar)) {
        insertText = insertText + ' ';
      }
      
      const newFormula = currentFormula.slice(0, start) + insertText + currentFormula.slice(end);
      setCurrentFormula(newFormula);
      
      // 设置光标位置
      setTimeout(() => {
        const newPosition = start + insertText.length;
        textarea.setSelectionRange(newPosition, newPosition);
        textarea.focus();
      }, 0);
    }
  };

  // 插入符号时自动添加空格
  const insertSymbol = (symbol) => {
    const textarea = formulaTextAreaRef.current?.resizableTextArea?.textArea;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      
      const beforeChar = start > 0 ? currentFormula[start - 1] : '';
      const afterChar = end < currentFormula.length ? currentFormula[end] : '';
      
      let insertText = symbol;
      
      // 对于运算符，自动添加空格
      if (/[+\-*/>=<]/.test(symbol)) {
        // 如果前面不是空格，添加空格
        if (beforeChar && beforeChar !== ' ' && beforeChar !== '\n') {
          insertText = ' ' + insertText;
        }
        // 如果后面不是空格，添加空格
        if (afterChar && afterChar !== ' ' && afterChar !== '\n') {
          insertText = insertText + ' ';
        }
      }
      // 对于逻辑关键词，也添加空格
      else if (['如果', '那么', '否则', '结束', '或者', '并且'].includes(symbol)) {
        // 前面添加空格（除非是开头或已经有空格）
        if (beforeChar && beforeChar !== ' ' && beforeChar !== '\n') {
          insertText = ' ' + insertText;
        }
        // 后面添加空格（除非是结尾或已经有空格）
        if (afterChar && afterChar !== ' ' && afterChar !== '\n') {
          insertText = insertText + ' ';
        }
      }
      
      const newFormula = currentFormula.slice(0, start) + insertText + currentFormula.slice(end);
      setCurrentFormula(newFormula);
      
      // 设置光标位置
      setTimeout(() => {
        const newPosition = start + insertText.length;
        textarea.setSelectionRange(newPosition, newPosition);
        textarea.focus();
      }, 0);
    }
  };

  // 清空公式
  const clearFormula = () => {
    setCurrentFormula('');
    if (formulaTextAreaRef.current?.resizableTextArea?.textArea) {
      formulaTextAreaRef.current.resizableTextArea.textArea.focus();
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '方案名称',
      dataIndex: 'scheme_name',
      key: 'scheme_name',
      width: 200,
      render: (text) => <span style={{ fontWeight: 500 }}>{text}</span>
    },
    {
      title: '方案分类',
      dataIndex: 'scheme_category',
      key: 'scheme_category',
      width: 120,
      render: (category) => {
        const categoryObj = schemeCategories.find(c => c.value === category);
        return categoryObj ? (
          <Tag color="blue">{categoryObj.label}</Tag>
        ) : category;
      }
    },
    {
      title: '公式预览',
      dataIndex: 'scheme_formula',
      key: 'scheme_formula',
      width: 300,
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          <Text code style={{ maxWidth: 280, display: 'inline-block' }}>
            {text || '暂无公式'}
          </Text>
        </Tooltip>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 200,
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
            title="确定删除这个计算方案吗？"
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
              <Title level={4} style={{ margin: 0 }}>计算方案管理</Title>
            </Col>
            <Col>
              <Space>
                <Input
                  placeholder="搜索方案名称"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={handleSearch}
                  style={{ width: 200 }}
                  prefix={<SearchOutlined />}
                />
                <Select
                  placeholder="选择分类"
                  value={categoryFilter}
                  onChange={setCategoryFilter}
                  style={{ width: 150 }}
                  allowClear
                >
                  {schemeCategories.map(category => (
                    <Option key={category.value} value={category.value}>
                      {category.label}
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
                  新增方案
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
          rowKey="id"
          pagination={pagination}
          loading={loading}
          onChange={handleTableChange}
          scroll={{ x: 1650 }}
          size="small"
        />
      </Card>

      {/* 编辑模态框 */}
      <Modal
        title={editingScheme ? '编辑计算方案' : '新增计算方案'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        width={1200}
        style={{ top: 20 }}
        footer={[
          <Button key="cancel" onClick={() => setModalVisible(false)}>
            取消
          </Button>,
          <Button key="validate" onClick={validateFormula}>
            验证公式
          </Button>,
          <Button key="submit" type="primary" onClick={handleSave}>
            保存
          </Button>
        ]}
      >
        <Row gutter={[16, 16]}>
          {/* 左侧：基本信息表单 */}
          <Col span={12}>
            <Card title="基本信息" size="small">
              <Form
                form={form}
                layout="vertical"
                initialValues={{
                  sort_order: 0,
                  is_enabled: true
                }}
              >
                <Form.Item
                  label="方案名称"
                  name="scheme_name"
                  rules={[{ required: true, message: '请输入方案名称' }]}
                >
                  <Input placeholder="请输入方案名称" />
                </Form.Item>

                <Form.Item
                  label="方案分类"
                  name="scheme_category"
                  rules={[{ required: true, message: '请选择方案分类' }]}
                >
                  <Select placeholder="请选择方案分类">
                    {schemeCategories.map(category => (
                      <Option key={category.value} value={category.value}>
                        {category.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  label="描述"
                  name="description"
                >
                  <TextArea rows={3} placeholder="请输入描述" />
                </Form.Item>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="排序"
                      name="sort_order"
                    >
                      <Input type="number" placeholder="排序值" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="是否启用"
                      name="is_enabled"
                      valuePropName="checked"
                    >
                      <Switch />
                    </Form.Item>
                  </Col>
                </Row>
              </Form>
            </Card>

            {/* 计算参数选择区域 */}
            <Card title="计算参数" size="small" style={{ marginTop: 16 }}>
              <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                <List
                  size="small"
                  dataSource={calculationParameters}
                  renderItem={(param) => (
                    <List.Item
                      actions={[
                        <Button
                          type="link"
                          size="small"
                          onClick={() => insertParameter(param.parameter_name)}
                        >
                          插入
                        </Button>
                      ]}
                    >
                      <Text strong>{param.parameter_name}</Text>
                    </List.Item>
                  )}
                />
              </div>
            </Card>
          </Col>

          {/* 右侧：公式编辑和计算器 */}
          <Col span={12}>
            {/* 公式编辑区域 */}
            <Card 
              title="方案公式" 
              size="small"
              extra={
                <Space>
                  <Button 
                    size="small" 
                    onClick={() => {
                      Modal.info({
                        title: '公式语法说明',
                        width: 600,
                        content: (
                          <div>
                            <h4>语法规则：</h4>
                            <ul>
                              <li>参数使用中括号包围，如：[长度]、[宽度]</li>
                              <li>字符串使用单引号包围，如：'标准型'</li>
                              <li>运算符前后建议添加空格，如：[长度] + [宽度]</li>
                              <li>逻辑判断使用中文关键词：如果、那么、否则、结束</li>
                            </ul>
                            <h4>公式示例：</h4>
                            <div style={{ backgroundColor: '#f5f5f5', padding: '8px', fontFamily: 'monospace' }}>
                              {'如果 [长度] > 100 那么 [长度] * [宽度] * 1.2 否则 [长度] * [宽度] 结束'}
                            </div>
                            <h4>运算符：</h4>
                            <p>{'+ - * / ( ) > < >= <= = <> 如果 那么 否则 结束 或者 并且'}</p>
                          </div>
                        )
                      });
                    }}
                  >
                    语法说明
                  </Button>
                  <Button 
                    size="small" 
                    onClick={() => {
                      const templates = [
                        {
                          name: '基本计算',
                          formula: '[长度] * [宽度] * [系数]'
                        },
                        {
                          name: '条件计算',
                          formula: '如果 [长度] > 100 那么 [长度] * [宽度] * 1.2 否则 [长度] * [宽度] 结束'
                        },
                        {
                          name: '复杂条件',
                          formula: '如果 [材料类型] = \'塑料\' 并且 [厚度] > 0.5 那么 [长度] * [宽度] * 2 否则 [长度] * [宽度] 结束'
                        },
                        {
                          name: '多级判断',
                          formula: '如果 [长度] > 200 那么 [长度] * [宽度] * 1.5 否则 如果 [长度] > 100 那么 [长度] * [宽度] * 1.2 否则 [长度] * [宽度] 结束 结束'
                        }
                      ];

                      Modal.confirm({
                        title: '选择公式模板',
                        width: 700,
                        content: (
                          <div>
                            {templates.map((template, index) => (
                              <div key={index} style={{ marginBottom: 16, padding: 12, border: '1px solid #d9d9d9', borderRadius: 4 }}>
                                <div style={{ fontWeight: 'bold', marginBottom: 8 }}>{template.name}</div>
                                <div style={{ backgroundColor: '#f5f5f5', padding: 8, fontFamily: 'monospace', fontSize: '12px' }}>
                                  {template.formula}
                                </div>
                                <Button 
                                  size="small" 
                                  type="link" 
                                  style={{ marginTop: 4 }}
                                  onClick={() => {
                                    setCurrentFormula(template.formula);
                                    Modal.destroyAll();
                                  }}
                                >
                                  使用此模板
                                </Button>
                              </div>
                            ))}
                          </div>
                        ),
                        onOk() {},
                        okText: '关闭',
                        cancelButtonProps: { style: { display: 'none' } }
                      });
                    }}
                  >
                    公式模板
                  </Button>
                  <Button size="small" icon={<CopyOutlined />}>
                    复制
                  </Button>
                  <Button size="small" icon={<ClearOutlined />} onClick={clearFormula}>
                    清空
                  </Button>
                </Space>
              }
            >
              <TextArea
                ref={formulaTextAreaRef}
                value={currentFormula}
                onChange={(e) => setCurrentFormula(e.target.value)}
                placeholder="在此编辑计算公式，参数用[参数名]表示，字符串用'文本'表示。点击上方语法说明查看详细规则。"
                rows={6}
                style={{ fontFamily: 'Monaco, Consolas, monospace' }}
              />
              {/* 实时语法提示 */}
              {currentFormula && (
                <div style={{ marginTop: 8, fontSize: '12px', color: '#666' }}>
                  <div>
                    <span>参数: {(currentFormula.match(/\[[^\]]+\]/g) || []).length} 个 | </span>
                    <span>字符串: {(currentFormula.match(/'[^']*'/g) || []).length} 个 | </span>
                    <span>行数: {currentFormula.split('\n').length}</span>
                  </div>
                </div>
              )}
            </Card>

            {/* 计算器区域 */}
            <Card title="计算器" size="small" style={{ marginTop: 16 }}>
              <div style={{ padding: '8px' }}>
                {/* 数字区域 */}
                <Row gutter={[4, 4]}>
                  <Col span={18}>
                    <Row gutter={[4, 4]}>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('1')}>1</CalculatorButton>
                      </Col>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('2')}>2</CalculatorButton>
                      </Col>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('3')}>3</CalculatorButton>
                      </Col>
                    </Row>
                    <Row gutter={[4, 4]}>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('4')}>4</CalculatorButton>
                      </Col>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('5')}>5</CalculatorButton>
                      </Col>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('6')}>6</CalculatorButton>
                      </Col>
                    </Row>
                    <Row gutter={[4, 4]}>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('7')}>7</CalculatorButton>
                      </Col>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('8')}>8</CalculatorButton>
                      </Col>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('9')}>9</CalculatorButton>
                      </Col>
                    </Row>
                    <Row gutter={[4, 4]}>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('0')}>0</CalculatorButton>
                      </Col>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('00')}>00</CalculatorButton>
                      </Col>
                      <Col span={8}>
                        <CalculatorButton onClick={() => insertSymbol('.')}>.</CalculatorButton>
                      </Col>
                    </Row>
                  </Col>
                  
                  {/* 运算符区域 */}
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('+')} type="primary">+</CalculatorButton>
                    <CalculatorButton onClick={() => insertSymbol('-')} type="primary">-</CalculatorButton>
                    <CalculatorButton onClick={() => insertSymbol('*')} type="primary">×</CalculatorButton>
                    <CalculatorButton onClick={() => insertSymbol('/')} type="primary">÷</CalculatorButton>
                  </Col>
                </Row>

                <Divider style={{ margin: '12px 0' }} />

                {/* 其他符号和函数 */}
                <Row gutter={[4, 4]}>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('(')} style={{ width: '100%' }}>(</CalculatorButton>
                  </Col>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol(')')} style={{ width: '100%' }}>)</CalculatorButton>
                  </Col>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('>')} style={{ width: '100%' }}>{'>'}</CalculatorButton>
                  </Col>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('<')} style={{ width: '100%' }}>{'<'}</CalculatorButton>
                  </Col>
                </Row>

                <Row gutter={[4, 4]} style={{ marginTop: 8 }}>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('>=')} style={{ width: '100%', fontSize: '12px' }}>
                      &gt;=
                    </CalculatorButton>
                  </Col>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('<=')} style={{ width: '100%', fontSize: '12px' }}>
                      &lt;=
                    </CalculatorButton>
                  </Col>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('=')} style={{ width: '100%' }}>
                      =
                    </CalculatorButton>
                  </Col>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('<>')} style={{ width: '100%', fontSize: '12px' }}>
                      &lt;&gt;
                    </CalculatorButton>
                  </Col>
                </Row>

                <Row gutter={[4, 4]} style={{ marginTop: 8 }}>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('如果')} style={{ width: '100%', fontSize: '12px' }}>如果</CalculatorButton>
                  </Col>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('那么')} style={{ width: '100%', fontSize: '12px' }}>那么</CalculatorButton>
                  </Col>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('或者')} style={{ width: '100%', fontSize: '12px' }}>或者</CalculatorButton>
                  </Col>
                  <Col span={6}>
                    <CalculatorButton onClick={() => insertSymbol('并且')} style={{ width: '100%', fontSize: '12px' }}>并且</CalculatorButton>
                  </Col>
                </Row>

                <Row gutter={[4, 4]} style={{ marginTop: 8 }}>
                  <Col span={8}>
                    <CalculatorButton onClick={() => insertSymbol('否则')} style={{ width: '100%', fontSize: '12px' }}>否则</CalculatorButton>
                  </Col>
                  <Col span={8}>
                    <CalculatorButton onClick={() => insertSymbol('结束')} style={{ width: '100%', fontSize: '12px' }}>结束</CalculatorButton>
                  </Col>
                </Row>
              </div>
            </Card>
          </Col>
        </Row>
      </Modal>
    </div>
  );
};

export default CalculationSchemeManagement; 