import request from '../utils/request';

/**
 * 袋型管理API
 */
export const bagTypeApi = {
  // 获取袋型列表
  getBagTypes: (params = {}) => {
    return request.get('/tenant/basic-data/bag-types', { params });
  },

  // 获取袋型详情
  getBagType: (bagTypeId) => {
    return request.get(`/tenant/basic-data/bag-types/${bagTypeId}`);
  },

  // 创建袋型
  createBagType: (data) => {
    return request.post('/tenant/basic-data/bag-types', data);
  },

  // 更新袋型
  updateBagType: (bagTypeId, data) => {
    return request.put(`/tenant/basic-data/bag-types/${bagTypeId}`, data);
  },

  // 删除袋型
  deleteBagType: (bagTypeId) => {
    return request.delete(`/tenant/basic-data/bag-types/${bagTypeId}`);
  },

  // 批量更新袋型
  batchUpdateBagTypes: (updates) => {
    return request.put('/tenant/basic-data/bag-types/batch', { updates });
  },

  // 获取袋型选项
  getBagTypeOptions: () => {
    return request.get('/tenant/basic-data/bag-types/options');
  },

  // 获取表单选项数据
  getFormOptions: () => {
    return request.get('/tenant/basic-data/bag-types/form-options');
  }
}; 