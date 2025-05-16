import request from '../utils/request';

const BASE_URL = '/api/admin/tenants';

export const tenantApi = {
  // 获取租户列表
  getTenants: (params) => {
    return request.get(BASE_URL, { params });
  },

  // 获取租户详情
  getTenant: (id) => {
    return request.get(`${BASE_URL}/${id}`);
  },

  // 创建租户
  createTenant: (data) => {
    return request.post(BASE_URL, data);
  },

  // 更新租户
  updateTenant: (id, data) => {
    return request.put(`${BASE_URL}/${id}`, data);
  },

  // 删除租户
  deleteTenant: (id) => {
    return request.delete(`${BASE_URL}/${id}`);
  },

  // 启用/禁用租户
  toggleTenantStatus: (id, status) => {
 