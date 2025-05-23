import React, { useState, useEffect } from 'react';
import { Card, Button, Typography, Space, Tag } from 'antd';
import authUtils from '../utils/auth';
import { useApi } from '../hooks/useApi';

const { Text, Paragraph } = Typography;

const DebugAuth = () => {
  const [authInfo, setAuthInfo] = useState({});
  const [tokenInfo, setTokenInfo] = useState({});
  const [testResult, setTestResult] = useState(null);
  const api = useApi();

  useEffect(() => {
    loadAuthInfo();
  }, []);

  const loadAuthInfo = () => {
    const token = authUtils.getToken();
    const user = authUtils.getUser();
    const isAuthenticated = authUtils.isAuthenticated();
    const isAdmin = authUtils.isAdmin();

    setAuthInfo({
      isAuthenticated,
      isAdmin,
      user,
      hasToken: !!token
    });

    if (token) {
      const decoded = authUtils.parseJwt(token);
      const isExpired = authUtils.isTokenExpired(token);
      setTokenInfo({
        token: token.substring(0, 50) + '...',
        decoded,
        isExpired
      });
    }
  };

  const testAdminAPI = async () => {
    try {
      console.log('测试管理员API...');
      console.log('请求URL:', '/admin/tenants');
      console.log('axios baseURL:', '/api');
      console.log('最终URL:', '/api/admin/tenants');
      
      const response = await api.get('/admin/tenants');
      console.log('API响应:', response.data);
      console.log('响应头:', response.headers);
      console.log('状态码:', response.status);
      
      setTestResult({
        success: true,
        data: response.data,
        status: response.status,
        headers: response.headers
      });
    } catch (error) {
      console.error('API测试失败:', error);
      console.error('错误响应:', error.response);
      setTestResult({
        success: false,
        error: error.response?.data || error.message,
        status: error.response?.status,
        statusText: error.response?.statusText
      });
    }
  };

  const forceRelogin = () => {
    // 清除所有认证信息并重定向到登录页
    authUtils.clearAuthInfo();
    window.location.href = '/login';
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px' }}>
      <Card title="认证状态调试" style={{ marginBottom: '20px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>认证状态: </Text>
            <Tag color={authInfo.isAuthenticated ? 'green' : 'red'}>
              {authInfo.isAuthenticated ? '已登录' : '未登录'}
            </Tag>
          </div>
          
          <div>
            <Text strong>管理员权限: </Text>
            <Tag color={authInfo.isAdmin ? 'blue' : 'default'}>
              {authInfo.isAdmin ? '是' : '否'}
            </Tag>
          </div>

          <div>
            <Text strong>Token状态: </Text>
            <Tag color={authInfo.hasToken ? 'green' : 'red'}>
              {authInfo.hasToken ? '存在' : '不存在'}
            </Tag>
          </div>

          {tokenInfo.decoded && (
            <div>
              <Text strong>Token用户ID: </Text>
              <Text code>{tokenInfo.decoded.sub}</Text>
              <br />
              <Text type="warning">
                如果遇到权限问题，可能是token中的用户ID与数据库不匹配
              </Text>
            </div>
          )}

          {authInfo.user && (
            <div>
              <Text strong>用户信息:</Text>
              <Paragraph code>
                {JSON.stringify(authInfo.user, null, 2)}
              </Paragraph>
            </div>
          )}
        </Space>
      </Card>

      {tokenInfo.decoded && (
        <Card title="Token信息" style={{ marginBottom: '20px' }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>Token过期状态: </Text>
              <Tag color={tokenInfo.isExpired ? 'red' : 'green'}>
                {tokenInfo.isExpired ? '已过期' : '有效'}
              </Tag>
            </div>
            
            <div>
              <Text strong>Token内容:</Text>
              <Paragraph code>
                {JSON.stringify(tokenInfo.decoded, null, 2)}
              </Paragraph>
            </div>
          </Space>
        </Card>
      )}

      <Card title="API测试">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Button type="primary" onClick={testAdminAPI}>
            测试管理员API (/admin/tenants)
          </Button>
          
          <Button onClick={loadAuthInfo}>
            刷新认证信息
          </Button>

          <Button 
            type="danger" 
            onClick={forceRelogin}
            style={{ marginLeft: 8 }}
          >
            强制重新登录
          </Button>

          {testResult && (
            <div>
              <Text strong>测试结果:</Text>
              <Paragraph code>
                {JSON.stringify(testResult, null, 2)}
              </Paragraph>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default DebugAuth; 