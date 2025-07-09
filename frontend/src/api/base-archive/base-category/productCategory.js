import request from '../../../utils/request';

// 获取产品分类列表
export const getProductCategories = (params) => {
  return request({
    url: '/tenant/base-archive/base-category/product-categories',
    method: 'get',
    params
  });
};

// 创建产品分类
export const createProductCategory = (data) => {
  return request({
    url: '/tenant/base-archive/base-category/product-categories',
    method: 'post',
    data
  });
};

// 更新产品分类
export const updateProductCategory = (id, data) => {
  return request({
    url: `/tenant/base-archive/base-category/product-categories/${id}`,
    method: 'put',
    data
  });
};

// 删除产品分类
export const deleteProductCategory = (id) => {
  return request({
    url: `/tenant/base-archive/base-category/product-categories/${id}`,
    method: 'delete'
  });
};

// 获取产品分类详情
export const getProductCategoryById = (id) => {
  return request({
    url: `/tenant/base-archive/base-category/product-categories/${id}`,
    method: 'get'
  });
};

// 获取启用的产品分类选项
export const getEnabledProductCategories = () => {
  return request({
    url: '/tenant/base-archive/base-category/product-categories/enabled',
    method: 'get'
  });
};

// 获取产品分类选项（用于下拉框）
export const getProductCategoryOptions = () => {
  return request({
    url: '/tenant/base-archive/base-category/product-categories/options',
    method: 'get'
  });
};

// 批量更新产品分类（用于可编辑表格）
export const batchUpdateProductCategories = (data) => {
  return request.put(`/tenant/base-archive/base-category/product-category/batch`, data);
};

// 统一导出API对象
export const productCategoryApi = {
  getProductCategories,
  createProductCategory,
  updateProductCategory,
  deleteProductCategory,
  getProductCategoryById,
  getEnabledProductCategories,
  getProductCategoryOptions,
  batchUpdateProductCategories
}; 