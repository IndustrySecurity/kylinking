import request from '../../../utils/request';

const BASE_URL = '/tenant/base-archive/production/production-archive/package-methods';

export const packageMethodApi = {
  // 获取包装方式列表
  getPackageMethods: (params) => {
    return request.get(BASE_URL, { params });
  },

  // 获取包装方式详情
  getPackageMethod: (id) => {
    return request.get(`${BASE_URL}/${id}`);
  },

  // 创建包装方式
  createPackageMethod: (data) => {
    return request.post(BASE_URL, data);
  },

  // 更新包装方式
  updatePackageMethod: (id, data) => {
    return request.put(`${BASE_URL}/${id}`, data);
  },

  // 删除包装方式
  deletePackageMethod: (id) => {
    return request.delete(`${BASE_URL}/${id}`);
  },

  // 批量更新包装方式（用于可编辑表格）
  batchUpdatePackageMethods: (data) => {
    return request.put(`${BASE_URL}/batch`, data);
  },

  // 获取启用的包装方式列表（用于下拉选择）
  getEnabledPackageMethods: () => {
    return request.get(BASE_URL, { 
      params: { 
        enabled_only: true,
        per_page: 1000 
      } 
    });
  }
}; 