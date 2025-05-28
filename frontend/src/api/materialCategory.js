import request from '../utils/request';

const API_BASE = '/tenant/basic-data';

// 材料分类API
export const materialCategoryApi = {
  // 获取材料分类列表
  getMaterialCategories: (params) => {
    return request.get(`${API_BASE}/material-categories`, { params });
  },

  // 获取材料分类详情
  getMaterialCategory: (id) => {
    return request.get(`${API_BASE}/material-categories/${id}`);
  },

  // 创建材料分类
  createMaterialCategory: (data) => {
    return request.post(`${API_BASE}/material-categories`, data);
  },

  // 更新材料分类
  updateMaterialCategory: (id, data) => {
    return request.put(`${API_BASE}/material-categories/${id}`, data);
  },

  // 删除材料分类
  deleteMaterialCategory: (id) => {
    return request.delete(`${API_BASE}/material-categories/${id}`);
  },

  // 批量更新材料分类
  batchUpdateMaterialCategories: (data) => {
    return request.put(`${API_BASE}/material-categories/batch`, data);
  },

  // 获取材料分类选项
  getMaterialCategoryOptions: () => {
    return request.get(`${API_BASE}/material-categories/options`);
  }
}; 