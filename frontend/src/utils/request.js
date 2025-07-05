import axios from 'axios';
import { message } from 'antd';

const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});


// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 从localStorage获取租户信息并设置租户ID头部
    const tenantStr = localStorage.getItem('tenant');
    if (tenantStr) {
      try {
        const tenant = JSON.parse(tenantStr);
        if (tenant && tenant.slug) {
          config.headers['X-Tenant-ID'] = tenant.slug;
        }
      } catch (error) {
        console.error('Failed to parse tenant info:', error);
      }
    } else {
      // 如果没有租户信息，设置默认租户ID
      config.headers['X-Tenant-ID'] = 'public';
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 直接返回response，保持原始结构
    // 让业务代码自己处理response.data.success和response.data.data
    return response;
  },
  (error) => {
    // 处理HTTP错误
    if (error.response) {
      const { status, data } = error.response;
      
      // 尝试从响应中获取错误信息
      const errorMessage = data?.error || data?.message || '请求失败';
      
      switch (status) {
        case 401:
          // 未授权，跳转到登录页
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 403:
          message.error('没有权限访问');
          break;
        case 404:
          message.error('请求的资源不存在');
          break;
        case 500:
          message.error(errorMessage);
          break;
        default:
          message.error(errorMessage);
      }
    } else {
      message.error('网络连接失败');
    }
    
    return Promise.reject(error);
  }
);

export default request; 