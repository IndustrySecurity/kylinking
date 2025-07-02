import React from 'react';
import { Card, Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ArrowLeftOutlined } from '@ant-design/icons';

const DeliveryOrder = () => {
  const navigate = useNavigate();

  return (
    <Card>
      <Result
        status="info"
        title="送货单功能开发中"
        subTitle="此功能正在开发中，敬请期待"
        extra={
          <Button type="primary" icon={<ArrowLeftOutlined />} onClick={() => navigate('/business/sales-management')}>
            返回销售管理
          </Button>
        }
      />
    </Card>
  );
};

export default DeliveryOrder; 