import React, { useState } from 'react';
import { Card, Button, Table, Modal, Form, Input, Select, Checkbox } from 'antd';

const ProductCategories = () => {
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();
  const [data, setData] = useState([
    { id: 1, name: '塑料袋', subject: '主营业务', isBlow: true, creator: '张三', createdAt: '2024-01-01', updater: '李四', updatedAt: '2024-01-10' },
  ]);

  const columns = [
    { title: '产品分类名称', dataIndex: 'name', key: 'name' },
    { title: '科目名称', dataIndex: 'subject', key: 'subject' },
    { title: '是否吹膜', dataIndex: 'isBlow', key: 'isBlow', render: v => v ? '是' : '否' },
    { title: '创建人', dataIndex: 'creator', key: 'creator' },
    { title: '创建日期', dataIndex: 'createdAt', key: 'createdAt' },
    { title: '修改人', dataIndex: 'updater', key: 'updater' },
    { title: '修改日期', dataIndex: 'updatedAt', key: 'updatedAt' },
  ];

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
          subject: values.subject,
          isBlow: values.isBlow || false,
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
    <Card title="产品分类管理" extra={<Button type="primary" onClick={handleAdd}>新建</Button>}>
      <Table columns={columns} dataSource={data} rowKey="id" />
      <Modal
        title="新建产品分类"
        open={visible}
        onOk={handleOk}
        onCancel={() => setVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="产品分类名称" rules={[{ required: true, message: '请输入产品分类名称' }]}> 
            <Input />
          </Form.Item>
          <Form.Item name="subject" label="科目名称" rules={[{ required: true, message: '请选择科目名称' }]}> 
            <Select options={[{ value: '主营业务', label: '主营业务' }, { value: '其他', label: '其他' }]} />
          </Form.Item>
          <Form.Item name="isBlow" valuePropName="checked">
            <Checkbox>是否吹膜</Checkbox>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default ProductCategories; 