import React, { useState, useEffect } from 'react';
import { Card, Button, Modal, Form, Input, Select, Switch, message, Space, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import dynamicFieldsApi from '../../api/system/dynamicFields';

const { Option } = Select;
const { TextArea } = Input;

const PageFieldManager = ({ modelName, pageName, pageTitle, visible, onClose }) => {
  const [fields, setFields] = useState([]);
  const [fieldTypes, setFieldTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingField, setEditingField] = useState(null);
  const [form] = Form.useForm();

  // 加载字段列表
  const loadFields = async () => {
    try {
      setLoading(true);
      const response = await dynamicFieldsApi.getPageFields(modelName, pageName);
      if (response.data && response.data.success) {
        setFields(response.data.data || []);
      }
    } catch (error) {
      console.error('加载字段列表失败:', error);
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
        setFieldTypes(response.data.data || []);
      }
    } catch (error) {
      console.error('加载字段类型失败:', error);
      message.error('加载字段类型失败');
    }
  };

  useEffect(() => {
    if (visible) {
      loadFields();
      loadFieldTypes();
    }
  }, [visible, modelName, pageName]);

  // 打开新增/编辑模态框
  const openModal = (field = null) => {
    setEditingField(field);
    setModalVisible(true);
    if (field) {
      form.setFieldsValue(field);
    } else {
      form.resetFields();
      form.setFieldsValue({
        model_name: modelName,
        page_name: pageName,
        field_type: 'text',
        is_required: false,
        is_readonly: false,
        is_visible: true,
        display_order: 0
      });
    }
  };

  // 保存字段
  const saveField = async (values) => {
    try {
      if (editingField) {
        await dynamicFieldsApi.updateField(editingField.id, values);
        message.success('字段更新成功');
      } else {
        await dynamicFieldsApi.createField(modelName, values);
        message.success('字段创建成功');
      }
      setModalVisible(false);
      loadFields();
    } catch (error) {
      console.error('保存字段失败:', error);
      message.error('保存字段失败');
    }
  };

  // 删除字段
  const deleteField = async (fieldId) => {
    try {
      await dynamicFieldsApi.deleteField(fieldId);
      message.success('字段删除成功');
      loadFields();
    } catch (error) {
      console.error('删除字段失败:', error);
      message.error('删除字段失败');
    }
  };

  // 渲染字段类型选项
  const renderFieldTypeOptions = () => {
    return fieldTypes.map(type => (
      <Option key={type.value} value={type.value}>
        {type.label}
      </Option>
    ));
  };

  return (
    <Modal
      title={`${pageTitle} - 自定义字段管理`}
      open={visible}
      onCancel={onClose}
      width={800}
      footer={null}
      destroyOnHidden
    >
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => openModal()}
        >
          新增字段
        </Button>
      </div>

      <div style={{ maxHeight: 400, overflowY: 'auto' }}>
        {fields.map(field => (
          <Card
            key={field.id}
            size="small"
            style={{ marginBottom: 8 }}
            title={field.field_label}
            extra={
              <Space>
                <Button
                  type="link"
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => openModal(field)}
                >
                  编辑
                </Button>
                <Popconfirm
                  title="确定删除这个字段吗？"
                  onConfirm={() => deleteField(field.id)}
                  okText="确定"
                  cancelText="取消"
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
            }
          >
            <p><strong>字段名：</strong>{field.field_name}</p>
            <p><strong>类型：</strong>{field.field_type}</p>
            <p><strong>必填：</strong>{field.is_required ? '是' : '否'}</p>
            <p><strong>只读：</strong>{field.is_readonly ? '是' : '否'}</p>
            {field.help_text && <p><strong>帮助文本：</strong>{field.help_text}</p>}
          </Card>
        ))}
      </div>

      <Modal
        title={editingField ? '编辑字段' : '新增字段'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
        destroyOnHidden
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={saveField}
        >
          <Form.Item
            name="field_name"
            label="字段名"
            rules={[{ required: true, message: '请输入字段名' }]}
          >
            <Input placeholder="请输入字段名（英文）" />
          </Form.Item>

          <Form.Item
            name="field_label"
            label="显示标签"
            rules={[{ required: true, message: '请输入显示标签' }]}
          >
            <Input placeholder="请输入显示标签" />
          </Form.Item>

          <Form.Item
            name="field_type"
            label="字段类型"
            rules={[{ required: true, message: '请选择字段类型' }]}
          >
            <Select placeholder="请选择字段类型">
              {renderFieldTypeOptions()}
            </Select>
          </Form.Item>

          <Form.Item
            name="field_options"
            label="选项（选择框类型）"
          >
            <TextArea
              placeholder="请输入选项，每行一个"
              rows={3}
            />
          </Form.Item>

          <Form.Item
            name="default_value"
            label="默认值"
          >
            <Input placeholder="请输入默认值" />
          </Form.Item>

          <Form.Item
            name="help_text"
            label="帮助文本"
          >
            <Input placeholder="请输入帮助文本" />
          </Form.Item>

          <Form.Item
            name="display_order"
            label="显示顺序"
          >
            <Input type="number" placeholder="请输入显示顺序" />
          </Form.Item>

          <Form.Item
            name="is_required"
            label="是否必填"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="is_readonly"
            label="是否只读"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="is_visible"
            label="是否可见"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </Modal>
  );
};

export default PageFieldManager; 