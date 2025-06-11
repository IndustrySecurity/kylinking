import request from '../../utils/request';

const API_BASE = '/tenant/basic-data';

// 材料管理API
export const materialManagementApi = {
  // 获取材料列表
  getMaterials: (params) => {
    return request.get(`${API_BASE}/material-management`, { params });
  },

  // 获取材料详情
  getMaterial: (id) => {
    return request.get(`${API_BASE}/material-management/${id}`);
  },

  // 创建材料
  createMaterial: (data) => {
    return request.post(`${API_BASE}/material-management`, data);
  },

  // 更新材料
  updateMaterial: (id, data) => {
    return request.put(`${API_BASE}/material-management/${id}`, data);
  },

  // 删除材料
  deleteMaterial: (id) => {
    return request.delete(`${API_BASE}/material-management/${id}`);
  },

  // 批量更新材料
  batchUpdateMaterials: (data) => {
    return request.put(`${API_BASE}/material-management/batch`, data);
  },

  // 获取表单选项
  getFormOptions: () => {
    return request.get(`${API_BASE}/material-management/form-options`);
  },

  // 获取材料分类详情（用于自动填入）
  getMaterialCategoryDetails: (categoryId) => {
    return request.get(`${API_BASE}/material-management/category-details/${categoryId}`);
  }
}; 