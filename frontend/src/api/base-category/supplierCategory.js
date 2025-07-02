import request from '../../utils/request';

// 供应商分类管理API
export const supplierCategoryApi = {
  // 获取供应商分类列表
  getSupplierCategories: (params = {}) => {
    return request({
      url: '/tenant/base-archive/base-category/supplier-categories',
      method: 'get',
      params
    });
  },

  // 获取供应商分类详情
  getSupplierCategory: (id) => {
    return request({
      url: `/tenant/base-archive/base-category/supplier-categories/${id}`,
      method: 'get'
    });
  },

  // 创建供应商分类
  createSupplierCategory: (data) => {
    return request({
      url: '/tenant/base-archive/base-category/supplier-categories',
      method: 'post',
      data
    });
  },

  // 更新供应商分类
  updateSupplierCategory: (id, data) => {
    return request({
      url: `/tenant/base-archive/base-category/supplier-categories/${id}`,
      method: 'put',
      data
    });
  },

  // 删除供应商分类
  deleteSupplierCategory: (id) => {
    return request({
      url: `/tenant/base-archive/base-category/supplier-categories/${id}`,
      method: 'delete'
    });
  },

  // 批量更新供应商分类
  batchUpdateSupplierCategories: (data) => {
    return request({
      url: '/tenant/base-archive/base-category/supplier-categories/batch-update',
      method: 'post',
      data
    });
  },

  // 获取启用的供应商分类列表（用于下拉选择）
  getEnabledSupplierCategories: () => {
    return request({
      url: '/tenant/base-archive/base-category/supplier-categories/enabled',
      method: 'get'
    });
  },

  // 获取供应商分类选项（用于下拉框）
  getSupplierCategoryOptions: () => {
    return request({
      url: '/tenant/base-archive/base-category/supplier-categories/options',
      method: 'get'
    });
  }
}; 