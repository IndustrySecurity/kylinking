import request from '../utils/request';

const BASE_URL = '/tenant/basic-data/product-categories';

export const productCategoryApi = {
  // 获取产品分类列表
  getProductCategories: (params) => {
    return request.get(BASE_URL, { params });
  },

  // 获取产品分类详情
  getProductCategory: (id) => {
    return request.get(`${BASE_URL}/${id}`);
  },

  // 创建产品分类
  createProductCategory: (data) => {
    return request.post(BASE_URL, data);
  },

  // 更新产品分类
  updateProductCategory: (id, data) => {
    return request.put(`${BASE_URL}/${id}`, data);
  },

  // 删除产品分类
  deleteProductCategory: (id) => {
    return request.delete(`${BASE_URL}/${id}`);
  },

  // 批量更新产品分类（用于可编辑表格）
  batchUpdateProductCategories: (data) => {
    return request.put(`${BASE_URL}/batch`, data);
  },

  // 获取启用的产品分类列表（用于下拉选择）
  getEnabledProductCategories: () => {
    return request.get(BASE_URL, { 
      params: { 
        enabled_only: true,
        per_page: 1000 
      } 
    });
  }
}; 