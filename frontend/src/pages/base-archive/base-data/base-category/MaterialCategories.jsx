import React, { useState } from 'react';
import { Card, Button, Table, Modal, Form, Input, Checkbox, InputNumber, Select } from 'antd';

const MaterialCategories = () => {
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();
  const [data, setData] = useState([
    { id: 1, name: '塑料', attr: '高密度', unit: 'kg', auxUnit: 'g', saleUnit: '包', density: 0.92, inspectType: '常规', lastPrice: 100, salePrice: 120, quotePrice: 110, weight: 50, shelfLife: 365, warnDays: 30, subject: '主营', remark: '常用', batch: true, barcode: false, customSpec: false, isInk: false, isPart: false, isResin: false, isRoll: false, isWaste: false, isGlue: false, isZip: false, isFoil: false, isBox: false, isCore: false, isSolvent: false, isSelfMade: false, noDock: false, costRequired: false, costShare: false, creator: '张三', createdAt: '2024-01-01', updater: '李四', updatedAt: '2024-01-10' },
  ]);

  const columns = [
    { title: '材料分类名称', dataIndex: 'name', key: 'name' },
    { title: '材料属性', dataIndex: 'attr', key: 'attr' },
    { title: '单位', dataIndex: 'unit', key: 'unit' },
    { title: '辅助单位', dataIndex: 'auxUnit', key: 'auxUnit' },
    { title: '销售单位', dataIndex: 'saleUnit', key: 'saleUnit' },
    { title: '密度', dataIndex: 'density', key: 'density' },
    { title: '检验类型', dataIndex: 'inspectType', key: 'inspectType' },
    { title: '最近采购价', dataIndex: 'lastPrice', key: 'lastPrice' },
    { title: '销售价', dataIndex: 'salePrice', key: 'salePrice' },
    { title: '产品报价', dataIndex: 'quotePrice', key: 'quotePrice' },
    { title: '平方克重', dataIndex: 'weight', key: 'weight' },
    { title: '保质期/天', dataIndex: 'shelfLife', key: 'shelfLife' },
    { title: '预警天数', dataIndex: 'warnDays', key: 'warnDays' },
    { title: '科目', dataIndex: 'subject', key: 'subject' },
    { title: '备注', dataIndex: 'remark', key: 'remark' },
    { title: '启用批次', dataIndex: 'batch', key: 'batch', render: v => v ? '是' : '否' },
    { title: '启用条码', dataIndex: 'barcode', key: 'barcode', render: v => v ? '是' : '否' },
    { title: '自定规格', dataIndex: 'customSpec', key: 'customSpec', render: v => v ? '是' : '否' },
    { title: '是否油墨', dataIndex: 'isInk', key: 'isInk', render: v => v ? '是' : '否' },
    { title: '是否配件', dataIndex: 'isPart', key: 'isPart', render: v => v ? '是' : '否' },
    { title: '是否树脂', dataIndex: 'isResin', key: 'isResin', render: v => v ? '是' : '否' },
    { title: '是否卷纸', dataIndex: 'isRoll', key: 'isRoll', render: v => v ? '是' : '否' },
    { title: '是否废膜', dataIndex: 'isWaste', key: 'isWaste', render: v => v ? '是' : '否' },
    { title: '是否胶水', dataIndex: 'isGlue', key: 'isGlue', render: v => v ? '是' : '否' },
    { title: '是否拉链', dataIndex: 'isZip', key: 'isZip', render: v => v ? '是' : '否' },
    { title: '是否铝箔', dataIndex: 'isFoil', key: 'isFoil', render: v => v ? '是' : '否' },
    { title: '是否纸箱', dataIndex: 'isBox', key: 'isBox', render: v => v ? '是' : '否' },
    { title: '是否纸芯', dataIndex: 'isCore', key: 'isCore', render: v => v ? '是' : '否' },
    { title: '是否溶剂', dataIndex: 'isSolvent', key: 'isSolvent', render: v => v ? '是' : '否' },
    { title: '是否自制', dataIndex: 'isSelfMade', key: 'isSelfMade', render: v => v ? '是' : '否' },
    { title: '不对接', dataIndex: 'noDock', key: 'noDock', render: v => v ? '是' : '否' },
    { title: '成本对象必填', dataIndex: 'costRequired', key: 'costRequired', render: v => v ? '是' : '否' },
    { title: '参与成本分配', dataIndex: 'costShare', key: 'costShare', render: v => v ? '是' : '否' },
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
          ...values,
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
    <Card title="材料分类管理" extra={<Button type="primary" onClick={handleAdd}>新建</Button>}>
      <Table columns={columns} dataSource={data} rowKey="id" scroll={{ x: 1500 }} />
      <Modal
        title="新建材料分类"
        open={visible}
        onOk={handleOk}
        onCancel={() => setVisible(false)}
        width={800}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="材料分类名称" rules={[{ required: true, message: '请输入材料分类名称' }]}> 
            <Input />
          </Form.Item>
          <Form.Item name="attr" label="材料属性"><Input /></Form.Item>
          <Form.Item name="unit" label="单位"><Input /></Form.Item>
          <Form.Item name="auxUnit" label="辅助单位"><Input /></Form.Item>
          <Form.Item name="saleUnit" label="销售单位"><Input /></Form.Item>
          <Form.Item name="density" label="密度"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="inspectType" label="检验类型"><Input /></Form.Item>
          <Form.Item name="lastPrice" label="最近采购价"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="salePrice" label="销售价"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="quotePrice" label="产品报价"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="weight" label="平方克重"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="shelfLife" label="保质期/天"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="warnDays" label="预警天数"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="subject" label="科目"><Input /></Form.Item>
          <Form.Item name="remark" label="备注"><Input.TextArea /> </Form.Item>
          <Form.Item name="batch" valuePropName="checked"><Checkbox>启用批次</Checkbox></Form.Item>
          <Form.Item name="barcode" valuePropName="checked"><Checkbox>启用条码</Checkbox></Form.Item>
          <Form.Item name="customSpec" valuePropName="checked"><Checkbox>自定规格</Checkbox></Form.Item>
          <Form.Item name="isInk" valuePropName="checked"><Checkbox>是否油墨</Checkbox></Form.Item>
          <Form.Item name="isPart" valuePropName="checked"><Checkbox>是否配件</Checkbox></Form.Item>
          <Form.Item name="isResin" valuePropName="checked"><Checkbox>是否树脂</Checkbox></Form.Item>
          <Form.Item name="isRoll" valuePropName="checked"><Checkbox>是否卷纸</Checkbox></Form.Item>
          <Form.Item name="isWaste" valuePropName="checked"><Checkbox>是否废膜</Checkbox></Form.Item>
          <Form.Item name="isGlue" valuePropName="checked"><Checkbox>是否胶水</Checkbox></Form.Item>
          <Form.Item name="isZip" valuePropName="checked"><Checkbox>是否拉链</Checkbox></Form.Item>
          <Form.Item name="isFoil" valuePropName="checked"><Checkbox>是否铝箔</Checkbox></Form.Item>
          <Form.Item name="isBox" valuePropName="checked"><Checkbox>是否纸箱</Checkbox></Form.Item>
          <Form.Item name="isCore" valuePropName="checked"><Checkbox>是否纸芯</Checkbox></Form.Item>
          <Form.Item name="isSolvent" valuePropName="checked"><Checkbox>是否溶剂</Checkbox></Form.Item>
          <Form.Item name="isSelfMade" valuePropName="checked"><Checkbox>是否自制</Checkbox></Form.Item>
          <Form.Item name="noDock" valuePropName="checked"><Checkbox>不对接</Checkbox></Form.Item>
          <Form.Item name="costRequired" valuePropName="checked"><Checkbox>成本对象必填</Checkbox></Form.Item>
          <Form.Item name="costShare" valuePropName="checked"><Checkbox>参与成本分配</Checkbox></Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default MaterialCategories; 