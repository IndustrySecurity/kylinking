import React, { useState, useEffect } from 'react';
import { Card, Button, Typography, Table, Tag, Space, Divider } from 'antd';
import authUtils from '../../utils/auth';
import { useApi } from '../../hooks/useApi';

const { Title, Text, Paragraph } = Typography;

const TokenDebugPage = () => {
  const [token, setToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);
  const [decodedToken, setDecodedToken] = useState(null);
  const [backendValidation, setBackendValidation] = useState(null);
  const [loading, setLoading] = useState(false);
  const api = useApi();

  useEffect(() => {
    loadTokens();
  }, []);

  const loadTokens = () => {
    const currentToken = authUtils.getToken();
    const currentRefreshToken = authUtils.getRefreshToken();
    
    setToken(currentToken);
    setRefreshToken(currentRefreshToken);
    
    if (currentToken) {
      try {
        const decoded = authUtils.parseJwt(currentToken);
        setDecodedToken(decoded);
      } catch (error) {
        console.error('Failed to decode token:', error);
      }
    }
  };

  const validateToken = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const result = await authUtils.validateTokenWithBackend(token);
      setBackendValidation(result);
    } catch (error) {
      console.error('Validation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkAuthInfo = async () => {
    setLoading(true);
    try {
      const result = await api.checkAuthInfo();
      console.log('Auth info:', result);
      alert(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('Auth check error:', error);
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const tokenColumns = [
    {
      title: '属性',
      dataIndex: 'key',
      key: 'key',
    },
    {
      title: '值',
      dataIndex: 'value',
      key: 'value',
      render: (text) => {
        if (typeof text === 'boolean') {
          return text ? <Tag color="green">True</Tag> : <Tag color="red">False</Tag>;
        }
        if (text === null || text === undefined) {
          return <Text type="secondary">null</Text>;
        }
        if (typeof text === 'object') {
          return <Text>{JSON.stringify(text)}</Text>;
        }
        return text;
      }
    },
  ];

  const tokenData = decodedToken ? 
    Object.entries(decodedToken).map(([key, value]) => ({
      key,
      value,
    })) : [];

  return (
    <div style={{ padding: '24px' }}>
      <Card title="认证调试工具" style={{ maxWidth: 800, margin: '0 auto' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Title level={4}>当前认证状态</Title>
          <Paragraph>
            <Text strong>是否已登录: </Text> 
            {authUtils.isAuthenticated() ? 
              <Tag color="green">已登录</Tag> : 
              <Tag color="red">未登录</Tag>
            }
          </Paragraph>
          <Paragraph>
            <Text strong>是否管理员: </Text> 
            {authUtils.isAdmin() ? 
              <Tag color="green">是</Tag> : 
              <Tag color="red">否</Tag>
            }
          </Paragraph>
          
          <Divider />
          
          <Title level={4}>访问令牌</Title>
          {token ? (
            <>
              <Paragraph copyable={{ text: token }} style={{ wordBreak: 'break-all' }}>
                {token}
              </Paragraph>
              <Space>
                <Button onClick={validateToken} loading={loading}>
                  验证令牌
                </Button>
                <Button onClick={checkAuthInfo} loading={loading}>
                  检查认证信息
                </Button>
              </Space>
              
              {backendValidation && (
                <Card 
                  size="small" 
                  title="后端验证结果" 
                  style={{ marginTop: 16 }}
                  type={backendValidation.valid ? "success" : "error"}
                >
                  <pre>{JSON.stringify(backendValidation, null, 2)}</pre>
                </Card>
              )}
              
              <Divider />
              
              <Title level={5}>令牌内容</Title>
              {decodedToken && (
                <Table 
                  columns={tokenColumns} 
                  dataSource={tokenData} 
                  size="small"
                  pagination={false}
                  rowKey="key"
                />
              )}
            </>
          ) : (
            <Text type="warning">未找到有效令牌</Text>
          )}
          
          <Divider />
          
          <Title level={4}>刷新令牌</Title>
          {refreshToken ? (
            <Paragraph copyable={{ text: refreshToken }} style={{ wordBreak: 'break-all' }}>
              {refreshToken}
            </Paragraph>
          ) : (
            <Text type="warning">未找到刷新令牌</Text>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default TokenDebugPage; 