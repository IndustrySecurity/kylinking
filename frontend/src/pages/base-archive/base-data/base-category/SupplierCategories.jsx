import React, { useState } from 'react';
import { Card, Button, Table, Modal, Form, Input, Checkbox } from 'antd';

const SupplierCategories = () => {
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();
  const [data, setData] = useState([
    { id: 1, name: '原材料供应商', plate: true, outsource: false, knife: false, creator: '张三', createdAt: '2024-01-01', updater: '李四', updatedAt: '2024-01-10' },
  ]);

  const columns = [
    { title: '供应商分类名称', dataIndex: 'name', key: 'name' },
    { title: '制版', dataIndex: 'plate', key: 'plate', render: v => v ? '是' : '否' },
    { title: '外发', dataIndex: 'outsource', key: 'outsource', render: v => v ? '是' : '否' },
    { title: '刀版', dataIndex: 'knife', key: 'knife', render: v => v ? '是' : '否' },
    { title: '创建人', dataIndex: 'creator', key: 'creator' },
    { title: '创建日期', dataIndex: 'createdAt', key: 'createdAt' },
    { title: '修改人', dataIndex: 'updater', key: 'updater' },
    { title: '修改日期', dataIndex: 'updatedAt', key: 'updatedAt' },
  ];

  // 互斥逻辑
  const handleCheck = (key) => {
    const values = form.getFieldsValue();
    const newValues = { plate: false, outsource: false, knife: false, ...values, [key]: !values[key] };
    Object.keys(newValues).forEach(k => {
      if (k !== key) newValues[k] = false;
    });
    form.setFieldsValue(newValues);
  };

  const handleAdd = () => {
    form.resetFields();
    setVisible(true);
  };

  const handleOk = () => {
    form.validateFields().then(values => {
      setData([
        ...data,
        {
          id: data.length + 1,
          name: values.name,
          plate: values.plate || false,
          outsource: values.outsource || false,
          knife: values.knife || false,
          creator: '当前用户',
          createdAt: new Date().toISOString().slice(0, 10),
          updater: '当前用户',
          updatedAt: new Date().toISOString().slice(0, 10),
        },
      ]);
      setVisible(false);
    });
  };

  return (
    <Card title="供应商分类管理" extra={<Button type="primary" onClick={handleAdd}>新建</Button>}>
      <Table columns={columns} dataSource={data} rowKey="id" />
      <Modal
        title="新建供应商分类"
        open={visible}
        onOk={handleOk}
        onCancel={() => setVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="供应商分类名称" rules={[{ required: true, message: '请输入供应商分类名称' }]}> 
            <Input />
          </Form.Item>
          <Form.Item label="分类类型">
            <Checkbox checked={form.getFieldValue('plate')} onChange={() => handleCheck('plate')}>制版</Checkbox>
            <Checkbox checked={form.getFieldValue('outsource')} onChange={() => handleCheck('outsource')}>外发</Checkbox>
            <Checkbox checked={form.getFieldValue('knife')} onChange={() => handleCheck('knife')}>刀版</Checkbox>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default SupplierCategories; 