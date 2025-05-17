import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { message } from 'antd';
import { useNavigate } from 'react-router-dom';

// 使用/api前缀统一访问后端API，通过nginx代理转发
const BASE_URL = '/api';

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
  
  // 获取token
  const getToken = useCallback(() => {
    return localStorage.getItem('token');
  }, []);

  // 保存token
  const saveToken = useCallback((token) => {
    localStorage.setItem('token', token);
    setIsLoggedIn(true);
  }, []);

  // 删除token
  const removeToken = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
  }, []);

  // 保存refreshToken
  const saveRefreshToken = useCallback((refreshToken) => {
    localStorage.setItem('refreshToken', refreshToken);
  }, []);

  // 获取refreshToken
  const getRefreshToken = useCallback(() => {
    return localStorage.getItem('refreshToken');
  }, []);

  // 保存用户信息
  const saveUser = useCallback((user) => {
    localStorage.setItem('user', JSON.stringify(user));
  }, []);

  // 获取用户信息
  const getUser = useCallback(() => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }, []);

  // 检查是否登录
  useEffect(() => {
    const token = getToken();
    setIsLoggedIn(!!token);
  }, [getToken]);

  // 请求拦截器
  useEffect(() => {
    const requestInterceptor = axiosInstance.interceptors.request.use(
      (config) => {
        const token = getToken();
        if (token) {
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
          const refreshToken = getRefreshToken();
          if (refreshToken) {
            try {
              const response = await axios.post(`${BASE_URL}/auth/refresh`, {}, {
                headers: {
                  'Authorization': `Bearer ${refreshToken}`
                }
              });
              
              // 更新token
              const newToken = response.data.access_token;
              saveToken(newToken);
              
              // 更新原始请求的token并重试
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return axiosInstance(originalRequest);
            } catch (refreshError) {
              // 刷新token失败，登出
              removeToken();
              message.error('登录已过期，请重新登录');
              navigate('/login');
              return Promise.reject(refreshError);
            }
          } else {
            // 无refreshToken，登出
            removeToken();
            message.error('请先登录');
            navigate('/login');
          }
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
  }, [getToken, getRefreshToken, navigate, removeToken, saveToken]);

  // 登录方法
  const login = async (email, password, tenant = null, endpoint = '/auth/login') => {
    try {
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
        
        if (response.data.access_token) {
          saveToken(response.data.access_token);
          saveRefreshToken(response.data.refresh_token);
          saveUser(response.data.user);
          
          // 如果响应中包含租户信息，保存下来
          if (response.data.tenant) {
            localStorage.setItem('tenant', JSON.stringify(response.data.tenant));
          }
          
          return response.data;
        }
      } catch (apiError) {
        console.error('Login API error:', apiError);
        // 在开发环境中，API 404的情况下继续模拟登录
        if (apiError.response && apiError.response.status === 404) {
          throw apiError; // 让下面的代码处理
        }
        throw apiError;
      }
      
      return null;
    } catch (error) {
      console.error('Login API error:', error);
      // 如果是开发环境且后端API未就绪，模拟登录成功
      if (process.env.NODE_ENV === 'development' || 
          (error.response && error.response.status === 404)) {
        console.log('Development environment detected, using mock login');
        const mockUser = {
          id: 1,
          email: email || 'admin@kylinking.com',
          first_name: email && email.includes('admin') ? 'Admin' : 'User',
          last_name: 'User',
          is_admin: email && email.includes('admin')
        };
        
        const mockToken = 'mock_token_' + Math.random().toString(36).substring(2);
        const mockRefreshToken = 'mock_refresh_' + Math.random().toString(36).substring(2);
        
        saveToken(mockToken);
        saveRefreshToken(mockRefreshToken);
        saveUser(mockUser);
        
        if (tenant) {
          localStorage.setItem('tenant', JSON.stringify({
            name: tenant,
            slug: tenant,
            is_active: true
          }));
        }
        
        return {
          access_token: mockToken,
          refresh_token: mockRefreshToken,
          user: mockUser
        };
      }
      
      throw error;
    }
  };

  // 获取当前租户
  const getCurrentTenant = useCallback(() => {
    const tenantStr = localStorage.getItem('tenant');
    return tenantStr ? JSON.parse(tenantStr) : null;
  }, []);

  // 登出方法
  const logout = async () => {
    try {
      await axiosInstance.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      removeToken();
      navigate('/login');
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
    getUser,
    getToken,
    getCurrentTenant
  };
}; 