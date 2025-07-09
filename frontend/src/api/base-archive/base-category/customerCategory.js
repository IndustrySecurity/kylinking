import request from '../../../utils/request';

// 获取客户分类列表
export const getCustomerCategories = (params) => {
  return request({
    url: '/tenant/base-archive/base-category/customer-categories',
    method: 'get',
    params
  });
};

// 创建客户分类
export const createCustomerCategory = (data) => {
  return request({
    url: '/tenant/base-archive/base-category/customer-categories',
    method: 'post',
    data
  });
};

// 更新客户分类
export const updateCustomerCategory = (id, data) => {
  return request({
    url: `/tenant/base-archive/base-category/customer-categories/${id}`,
    method: 'put',
    data
  });
};

// 删除客户分类
export const deleteCustomerCategory = (id) => {
  return request({
    url: `/tenant/base-archive/base-category/customer-categories/${id}`,
    method: 'delete'
  });
};

// 获取客户分类详情
export const getCustomerCategoryById = (id) => {
  return request({
    url: `/tenant/base-archive/base-category/customer-categories/${id}`,
    method: 'get'
  });
};

// 获取启用的客户分类选项
export const getEnabledCustomerCategories = () => {
  return request({
    url: '/tenant/base-archive/base-category/customer-categories/enabled',
    method: 'get'
  });
};

// 批量更新客户分类
export const batchUpdateCustomerCategories = (data) => {
  return request({
    url: '/tenant/base-archive/base-category/customer-categories/batch-update',
    method: 'post',
    data
  });
};

// 获取客户分类选项（用于下拉框）
export const getCustomerCategoryOptions = () => {
  return request({
    url: '/tenant/base-archive/base-category/customer-categories/options',
    method: 'get'
  });
};

// 统一导出API对象
export const customerCategoryApi = {
  getCustomerCategories,
  createCustomerCategory,
  updateCustomerCategory,
  deleteCustomerCategory,
  getCustomerCategoryById,
  getEnabledCustomerCategories,
  batchUpdateCustomerCategories,
  getCustomerCategoryOptions
}; 