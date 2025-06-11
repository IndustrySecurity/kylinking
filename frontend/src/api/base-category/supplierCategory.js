import request from '../../utils/request';

// 供应商分类管理API
export const supplierCategoryApi = {
  // 获取供应商分类列表
  getSupplierCategories: (params = {}) => {
    return request({
      url: '/tenant/basic-data/supplier-category-management',
      method: 'get',
      params
    });
  },

  // 获取供应商分类详情
  getSupplierCategory: (id) => {
    return request({
      url: `/tenant/basic-data/supplier-category-management/${id}`,
      method: 'get'
    });
  },

  // 创建供应商分类
  createSupplierCategory: (data) => {
    return request({
      url: '/tenant/basic-data/supplier-category-management',
      method: 'post',
      data
    });
  },

  // 更新供应商分类
  updateSupplierCategory: (id, data) => {
    return request({
      url: `/tenant/basic-data/supplier-category-management/${id}`,
      method: 'put',
      data
    });
  },

  // 删除供应商分类
  deleteSupplierCategory: (id) => {
    return request({
      url: `/tenant/basic-data/supplier-category-management/${id}`,
      method: 'delete'
    });
  },

  // 批量更新供应商分类
  batchUpdateSupplierCategories: (data) => {
    return request({
      url: '/tenant/basic-data/supplier-category-management/batch',
      method: 'put',
      data
    });
  },

  // 获取启用的供应商分类列表（用于下拉选择）
  getEnabledSupplierCategories: () => {
    return request({
      url: '/tenant/basic-data/supplier-category-management',
      method: 'get',
      params: { enabled_only: true, per_page: 1000 }
    });
  }
}; 