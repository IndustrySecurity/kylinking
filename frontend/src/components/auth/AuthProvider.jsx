import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { message } from 'antd';
import { useApi } from '../../hooks/useApi';
import authUtils from '../../utils/auth';

// 创建认证上下文
const AuthContext = createContext(null);

// 认证提供者组件
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const api = useApi();
  const navigate = useNavigate();
  const location = useLocation();

  // 初始化时检查认证状态
  useEffect(() => {
    const initAuth = async () => {
      try {
        setLoading(true);
        
        // 检查是否有有效的令牌
        const token = authUtils.getToken();
        if (token) {
          // 检查令牌是否过期
          if (authUtils.isTokenExpired(token)) {
            // 尝试使用刷新令牌获取新令牌
            const refreshToken = authUtils.getRefreshToken();
            if (refreshToken) {
              try {
                const response = await api.post('/api/auth/refresh', {}, {
                  headers: { 
                    Authorization: `Bearer ${refreshToken}` 
                  }
                });
                
                if (response.data && response.data.access_token) {
                  // 更新令牌
                  authUtils.saveToken(response.data.access_token);
                  setUser(authUtils.getUser());
                }
              } catch (refreshError) {
                // 清除认证信息并重定向到登录页
                logout();
                return;
              }
            } else {
              // 无刷新令牌，清除认证信息
              logout();
              return;
            }
          } else {
            // 令牌有效，设置用户信息
            setUser(authUtils.getUser());
          }
        }
      } catch (error) {
        // 清除认证信息并重定向到登录页
        logout();
      } finally {
        setLoading(false);
      }
    };
    
    initAuth();
  }, []);

  // 登录方法
  const login = async (email, password, tenant = null, isAdmin = false) => {
    try {
      setLoading(true);
      
      // 选择合适的登录端点
      const endpoint = isAdmin ? '/api/auth/admin-login' : '/api/auth/login';
      
      // 调用登录API
      const authData = await api.login(email, password, tenant, endpoint);
      
      if (authData && authData.user) {
        setUser(authData.user);
        
        // 根据用户身份和登录页面选择重定向路径
        const { from } = location.state || { from: { pathname: isAdmin ? '/admin/dashboard' : '/dashboard' } };
        navigate(from);
        
        return true;
      }
      
      return false;
    } catch (error) {
      message.error(error.response?.data?.message || '登录失败，请检查您的凭据');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // 登出方法
  const logout = async () => {
    try {
      setLoading(true);
      await api.logout();
    } catch (error) {
      // 清除认证信息并重定向到登录页
      logout();
    } finally {
      setUser(null);
      setLoading(false);
      navigate('/login');
    }
  };

  // 检查是否有特定角色
  const hasRole = (role) => {
    if (!user) return false;
    
    switch (role) {
      case 'admin':
        return !!user.is_admin;
      case 'superadmin':
        return !!user.is_superadmin;
      default:
        return false;
    }
  };

  // 暴露给应用的上下文值
  const value = {
    user,
    isAuthenticated: !!user,
    isAdmin: user ? (user.is_admin || user.is_superadmin) : false,
    loading,
    login,
    logout,
    hasRole
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// 使用认证的自定义钩子
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthProvider; 