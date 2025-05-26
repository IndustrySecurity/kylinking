import request from '../utils/request';

// 客户分类管理API
export const customerCategoryApi = {
  // 获取客户分类列表
  getCustomerCategories: (params = {}) => {
    return request({
      url: '/tenant/basic-data/customer-category-management',
      method: 'get',
      params
    });
  },

  // 获取客户分类详情
  getCustomerCategory: (id) => {
    return request({
      url: `/tenant/basic-data/customer-category-management/${id}`,
      method: 'get'
    });
  },

  // 创建客户分类
  createCustomerCategory: (data) => {
    return request({
      url: '/tenant/basic-data/customer-category-management',
      method: 'post',
      data
    });
  },

  // 更新客户分类
  updateCustomerCategory: (id, data) => {
    return request({
      url: `/tenant/basic-data/customer-category-management/${id}`,
      method: 'put',
      data
    });
  },

  // 删除客户分类
  deleteCustomerCategory: (id) => {
    return request({
      url: `/tenant/basic-data/customer-category-management/${id}`,
      method: 'delete'
    });
  },

  // 批量更新客户分类
  batchUpdateCustomerCategories: (data) => {
    return request({
      url: '/tenant/basic-data/customer-category-management/batch',
      method: 'put',
      data
    });
  },

  // 获取启用的客户分类列表（用于下拉选择）
  getEnabledCustomerCategories: () => {
    return request({
      url: '/tenant/basic-data/customer-category-management',
      method: 'get',
      params: { enabled_only: true, per_page: 1000 }
    });
  }
}; 