import request from '../utils/request';

// 权限检查API
export const authApi = {
  // 获取当前用户信息
  getCurrentUser: () => {
    return request.get('/auth/me');
  },

  // 检查用户权限
  checkPermission: (permission) => {
    return request.get('/auth/permission', {
      params: { permission }
    });
  },

  // 检查用户是否为管理员
  checkAdminStatus: () => {
    return request.get('/auth/me').then(response => {
      const user = response.data.user;
      return {
        isAdmin: user.is_admin || user.is_superadmin,
        isSuperAdmin: user.is_superadmin,
        user: user
      };
    });
  },

  // 获取用户角色和权限
  getUserRoles: () => {
    return request.get('/auth/roles');
  }
}; 