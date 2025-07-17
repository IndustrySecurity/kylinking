import request from '../../../utils/request';

// 获取产品列表
export const getProducts = (params) => {
  return request({
    url: '/tenant/base-archive/base-data/products/',
    method: 'get',
    params
  });
};

// 创建产品
export const createProduct = (data) => {
  return request({
    url: '/tenant/base-archive/base-data/products/',
    method: 'post',
    data
  });
};

// 更新产品
export const updateProduct = (id, data) => {
  return request({
    url: `/tenant/base-archive/base-data/products/${id}`,
    method: 'put',
    data
  });
};

// 删除产品
export const deleteProduct = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/products/${id}`,
    method: 'delete'
  });
};

// 获取产品详情
export const getProductById = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/products/${id}`,
    method: 'get'
  });
};

// 获取产品详情（别名方法）
export const getProductDetail = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/products/${id}`,
    method: 'get'
  });
};

// 获取启用的产品选项
export const getEnabledProducts = () => {
  return request({
    url: '/tenant/base-archive/base-data/products/enabled',
    method: 'get'
  });
};

// 批量更新产品
export const batchUpdateProducts = (data) => {
  return request({
    url: '/tenant/base-archive/base-data/products/batch-update',
    method: 'post',
    data
  });
};

// 获取产品选项（用于下拉框）
export const getProductOptions = () => {
  return request({
    url: '/tenant/base-archive/base-data/products/options',
    method: 'get'
  });
};

// 导入产品数据
export const importProducts = (formData) => {
  return request({
    url: '/tenant/base-archive/base-data/products/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

// 导出产品数据
export const exportProducts = (params) => {
  return request({
    url: '/tenant/base-archive/base-data/products/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
};

// 搜索产品
export const searchProducts = (keyword) => {
  return request({
    url: '/tenant/base-archive/base-data/products/search',
    method: 'get',
    params: { keyword }
  });
};

// 获取表单选项数据
export const getFormOptions = () => {
  return request.get('/tenant/base-archive/base-data/products/form-options');
};

// 上传产品图片
export const uploadImage = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return request.post('/tenant/base-archive/base-data/products/upload-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// 根据袋型获取产品结构模板
export const getBagTypeStructure = (bagTypeId) => {
  return request.get(`/tenant/base-archive/base-data/products/bag-type-structure/${bagTypeId}`);
};

// 根据客户获取相关信息
export const getCustomerInfo = (customerId) => {
  return request.get(`/tenant/base-archive/base-data/products/customer-info/${customerId}`);
};

// 统一导出API对象
export const productManagementApi = {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  getProductById,
  getProductDetail,
  getEnabledProducts,
  batchUpdateProducts,
  getProductOptions,
  importProducts,
  exportProducts,
  searchProducts,
  getFormOptions,
  uploadImage,
  getBagTypeStructure,
  getCustomerInfo
}; 