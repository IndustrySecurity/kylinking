import React, { useState } from 'react';
import { Card, Button, Table, Modal, Form, Input } from 'antd';

const CustomerCategories = () => {
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();
  const [data, setData] = useState([
    { id: 1, name: 'VIP客户', creator: '张三', createdAt: '2024-01-01', updater: '李四', updatedAt: '2024-01-10' },
  ]);

  const columns = [
    { title: '客户分类名称', dataIndex: 'name', key: 'name' },
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
    <Card title="客户分类管理" extra={<Button type="primary" onClick={handleAdd}>新建</Button>}>
      <Table columns={columns} dataSource={data} rowKey="id" />
      <Modal
        title="新建客户分类"
        open={visible}
        onOk={handleOk}
        onCancel={() => setVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="客户分类名称" rules={[{ required: true, message: '请输入客户分类名称' }]}> 
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default CustomerCategories; 