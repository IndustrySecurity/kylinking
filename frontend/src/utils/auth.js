/**
 * 认证相关工具函数
 */

// 保存令牌到本地存储
export const saveToken = (token) => {
  if (!token) {
    console.error('Error: Attempted to save empty token');
    return false;
  }
  
  try {
    localStorage.setItem('token', token);
    return true;
  } catch (error) {
    console.error('Failed to save token to localStorage:', error);
    return false;
  }
};

// 获取令牌
export const getToken = () => {
  try {
    return localStorage.getItem('token');
  } catch (error) {
    console.error('Failed to get token from localStorage:', error);
    return null;
  }
};

// 保存刷新令牌
export const saveRefreshToken = (refreshToken) => {
  if (!refreshToken) {
    console.error('Error: Attempted to save empty refresh token');
    return false;
  }
  
  try {
    localStorage.setItem('refreshToken', refreshToken);
    return true;
  } catch (error) {
    console.error('Failed to save refresh token to localStorage:', error);
    return false;
  }
};

// 获取刷新令牌
export const getRefreshToken = () => {
  try {
    return localStorage.getItem('refreshToken');
  } catch (error) {
    console.error('Failed to get refresh token from localStorage:', error);
    return null;
  }
};

// 保存用户信息
export const saveUser = (user) => {
  if (!user) {
    console.error('Error: Attempted to save empty user info');
    return false;
  }
  
  try {
    localStorage.setItem('user', JSON.stringify(user));
    return true;
  } catch (error) {
    console.error('Failed to save user to localStorage:', error);
    return false;
  }
};

// 获取用户信息
export const getUser = () => {
  try {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  } catch (error) {
    console.error('Failed to get user from localStorage:', error);
    return null;
  }
};

// 保存认证信息（一次性保存所有认证相关数据）
export const saveAuthInfo = (authData) => {
  if (!authData || !authData.access_token) {
    console.error('Error: Invalid auth data format');
    return false;
  }
  
  try {
    saveToken(authData.access_token);
    
    if (authData.refresh_token) {
      saveRefreshToken(authData.refresh_token);
    }
    
    if (authData.user) {
      saveUser(authData.user);
    }
    
    // 保存租户信息（如果API返回了租户信息）
    if (authData.tenant) {
      localStorage.setItem('tenant', JSON.stringify(authData.tenant));
    }
    
    return true;
  } catch (error) {
    console.error('Failed to save auth info:', error);
    return false;
  }
};

// 清除所有认证信息
export const clearAuthInfo = () => {
  try {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    localStorage.removeItem('tenant');
    return true;
  } catch (error) {
    console.error('Failed to clear auth info:', error);
    return false;
  }
};

// 检查是否已登录
export const isAuthenticated = () => {
  return !!getToken();
};

// 检查是否是管理员
export const isAdmin = () => {
  const user = getUser();
  return user && (user.is_admin || user.is_superadmin);
};

// 获取认证头部信息
export const getAuthHeader = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// 解析JWT令牌（不验证签名）
export const parseJwt = (token) => {
  try {
    if (!token) return null;
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Failed to parse JWT:', error);
    return null;
  }
};

// 检查令牌是否过期
export const isTokenExpired = (token) => {
  try {
    const decoded = parseJwt(token);
    if (!decoded || !decoded.exp) return true;
    
    // 令牌过期时间与当前时间比较（提前60秒判断过期）
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime - 60;
  } catch (error) {
    console.error('Failed to check token expiration:', error);
    return true;
  }
};

// 检查令牌是否有效（与后端验证）
export const validateTokenWithBackend = async (token) => {
  try {
    const response = await fetch('/auth/debug/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ token })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to validate token with backend:', error);
    return {
      valid: false,
      error: error.message
    };
  }
};

export default {
  saveToken,
  getToken,
  saveRefreshToken,
  getRefreshToken,
  saveUser,
  getUser,
  saveAuthInfo,
  clearAuthInfo,
  isAuthenticated,
  isAdmin,
  getAuthHeader,
  parseJwt,
  isTokenExpired,
  validateTokenWithBackend
}; 