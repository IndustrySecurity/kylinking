import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { message } from 'antd';
import { useNavigate } from 'react-router-dom';
import authUtils from '../utils/auth';

// 确保API请求正确路由到后端
const BASE_URL = import.meta.env.DEV ? '/api' : '/api';

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const useApi = () => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  // 检查是否登录
  useEffect(() => {
    setIsLoggedIn(authUtils.isAuthenticated());
  }, []);

  // 请求拦截器
  useEffect(() => {
    const requestInterceptor = axiosInstance.interceptors.request.use(
      (config) => {
        const token = authUtils.getToken();
        if (token) {
          // 检查令牌是否过期
          if (authUtils.isTokenExpired(token)) {
            // Token过期，让响应拦截器处理
          }
          
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    const responseInterceptor = axiosInstance.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;
        
        // 如果是401错误且没有重试过
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          // 尝试刷新token
          const refreshToken = authUtils.getRefreshToken();
          if (refreshToken) {
            try {
              // 使用refreshToken获取新的accessToken
              const response = await axios.post(`${BASE_URL}/auth/refresh`, {}, {
                headers: {
                  'Authorization': `Bearer ${refreshToken}`
                }
              });
              
              // 更新token
              if (response.data && response.data.access_token) {
                const newToken = response.data.access_token;
                authUtils.saveToken(newToken);
                
                // 更新原始请求的token并重试
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return axiosInstance(originalRequest);
              } else {
                throw new Error('Failed to refresh token: Invalid response format');
              }
            } catch (refreshError) {
              // 刷新token失败，登出并重定向到登录页
              // 如果重试刷新令牌失败，只有在非admin页面才自动登出
              // 这样可以防止管理页面突然跳转
              if (!originalRequest.url.includes('/admin/')) {
                authUtils.clearAuthInfo();
                setIsLoggedIn(false);
                message.error('登录已过期，请重新登录');
                navigate('/login');
              } else {
                // 对于管理页面的401错误，只显示警告，不跳转
                message.warning('管理员权限验证失败，部分功能可能无法使用');
              }
              
              return Promise.reject(refreshError);
            }
          } else {
            // 无refreshToken，登出
            authUtils.clearAuthInfo();
            setIsLoggedIn(false);
            message.error('请先登录');
            navigate('/login');
            return Promise.reject(new Error('No refresh token available'));
          }
        } else if (error.response?.status === 422) {
          // 处理422错误 - 通常是请求格式问题
          message.error('请求格式错误: ' + (error.response?.data?.message || '请检查输入'));
        }
        
        // 其他错误
        if (error.response?.data?.message) {
          message.error(error.response.data.message);
        } else if (error.message) {
          message.error(error.message);
        } else {
          message.error('请求错误');
        }
        
        return Promise.reject(error);
      }
    );

    // 清理拦截器
    return () => {
      axiosInstance.interceptors.request.eject(requestInterceptor);
      axiosInstance.interceptors.response.eject(responseInterceptor);
    };
  }, [navigate]);

  // 登录方法
  const login = async (email, password, tenant = null, endpoint = '/auth/login') => {
    try {
      // 如果没有提供租户信息，尝试从邮箱中提取
      if (!tenant && email && email.includes('@') && endpoint !== '/auth/admin-login') {
        // 提取邮箱域名部分，例如从 user@tenant.kylinking.com 提取 tenant
        const emailDomain = email.split('@')[1];
        if (emailDomain && emailDomain !== 'kylinking.com') {
          // 如果域名是 tenant.kylinking.com 格式，提取租户部分
          if (emailDomain.includes('.')) {
            const domainParts = emailDomain.split('.');
            if (domainParts.length > 2) {
              tenant = domainParts[0];
            }
          } else {
            // 如果域名不是多级格式，可能直接就是租户名
            tenant = emailDomain;
          }
        }
      }
      
      // 如果提供了租户信息，则添加到请求头
      const config = {};
      if (tenant) {
        config.headers = {
          'X-Tenant-ID': tenant
        };
      }
      
      // 尝试调用API
      try {
        // 使用传入的endpoint替换默认值
        const response = await axiosInstance.post(endpoint, { email, password }, config);
        
        if (response.data && response.data.access_token) {
          // 保存认证信息
          const success = authUtils.saveAuthInfo(response.data);
          
          if (success) {
            setIsLoggedIn(true);
            return response.data;
          } else {
            throw new Error('Failed to save authentication data');
          }
        } else {
          throw new Error('Invalid response format from authentication server');
        }
      } catch (apiError) {
        if (process.env.NODE_ENV === 'development' && apiError.response?.status === 404) {
          // 开发环境中，API 404的情况下继续模拟登录
          return simulateMockLogin(email, tenant);
        }
        throw apiError;
      }
    } catch (error) {
      throw error;
    }
  };

  // 模拟登录（仅用于开发环境）
  const simulateMockLogin = (email, tenant) => {
    const mockUser = {
      id: 1,
      email: email || 'admin@kylinking.com',
      first_name: email && email.includes('admin') ? 'Admin' : 'User',
      last_name: 'User',
      is_admin: email && email.includes('admin'),
      is_superadmin: email && email.includes('admin')
    };
    
    const mockToken = 'mock_token_' + Math.random().toString(36).substring(2);
    const mockRefreshToken = 'mock_refresh_' + Math.random().toString(36).substring(2);
    
    // 保存模拟认证数据
    authUtils.saveToken(mockToken);
    authUtils.saveRefreshToken(mockRefreshToken);
    authUtils.saveUser(mockUser);
    
    if (tenant) {
      localStorage.setItem('tenant', JSON.stringify({
        name: tenant,
        slug: tenant,
        is_active: true
      }));
    }
    
    setIsLoggedIn(true);
    
    return {
      access_token: mockToken,
      refresh_token: mockRefreshToken,
      user: mockUser
    };
  };

  // 获取当前租户
  const getCurrentTenant = useCallback(() => {
    const tenantStr = localStorage.getItem('tenant');
    return tenantStr ? JSON.parse(tenantStr) : null;
  }, []);

  // 登出方法
  const logout = async () => {
    try {
      // 尝试调用登出API
      await axiosInstance.post('/auth/logout');
    } catch (error) {
      // 忽略登出API错误，继续清理本地数据
    }
    
      // 清除所有认证信息
      authUtils.clearAuthInfo();
      setIsLoggedIn(false);
      // 重定向到登录页
      navigate('/login');
  };

  // 调试获取令牌信息
  const checkAuthInfo = async () => {
    try {
      // 尝试调用调试API
      const response = await axiosInstance.get('/admin/debug/auth');
      return response.data;
    } catch (error) {
      return { error: error.message };
    }
  };

  // 返回API方法和认证状态
  return {
    get: axiosInstance.get,
    post: axiosInstance.post,
    put: axiosInstance.put,
    delete: axiosInstance.delete,
    patch: axiosInstance.patch,
    login,
    logout,
    isLoggedIn,
    getUser: authUtils.getUser,
    getToken: authUtils.getToken,
    getCurrentTenant,
    isAdmin: authUtils.isAdmin,
    checkAuthInfo
  };
}; 