import request from '../../utils/request'

// 供应商管理API

/**
 * 获取供应商管理列表
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getSupplierManagementList(params) {
  return request({
    url: '/tenant/base-archive/base-data/suppliers',
    method: 'get',
    params
  })
}

/**
 * 获取供应商管理详情
 * @param {string} id - 供应商ID
 * @returns {Promise} API响应
 */
export function getSupplierManagementDetail(id) {
  return request({
    url: `/tenant/base-archive/base-data/suppliers/${id}`,
    method: 'get'
  })
}

/**
 * 创建供应商管理
 * @param {Object} data - 供应商数据
 * @returns {Promise} API响应
 */
export function createSupplierManagement(data) {
  return request({
    url: '/tenant/base-archive/base-data/suppliers',
    method: 'post',
    data
  })
}

/**
 * 更新供应商管理
 * @param {string} id - 供应商ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateSupplierManagement(id, data) {
  return request({
    url: `/tenant/base-archive/base-data/suppliers/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除供应商管理
 * @param {string} id - 供应商ID
 * @returns {Promise} API响应
 */
export function deleteSupplierManagement(id) {
  return request({
    url: `/tenant/base-archive/base-data/suppliers/${id}`,
    method: 'delete'
  })
}

/**
 * 切换供应商启用状态
 * @param {string} id - 供应商ID
 * @returns {Promise} API响应
 */
export function toggleSupplierStatus(id) {
  return request({
    url: `/tenant/base-archive/base-data/suppliers/${id}/toggle-status`,
    method: 'put'
  })
}

/**
 * 导出供应商管理数据
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function exportSupplierManagement(params) {
  return request({
    url: '/tenant/base-archive/base-data/suppliers/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 获取供应商管理表单选项
 * @returns {Promise} API响应
 */
export function getSupplierManagementFormOptions() {
  return request({
    url: '/tenant/base-archive/base-data/suppliers/form-options',
    method: 'get'
  })
}

// 获取供应商列表
export const getSuppliers = (params) => {
  return request({
    url: '/tenant/base-archive/base-data/suppliers',
    method: 'get',
    params
  });
};

// 创建供应商
export const createSupplier = (data) => {
  return request({
    url: '/tenant/base-archive/base-data/suppliers',
    method: 'post',
    data
  });
};

// 更新供应商
export const updateSupplier = (id, data) => {
  return request({
    url: `/tenant/base-archive/base-data/suppliers/${id}`,
    method: 'put',
    data
  });
};

// 删除供应商
export const deleteSupplier = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/suppliers/${id}`,
    method: 'delete'
  });
};

// 获取供应商详情
export const getSupplierById = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/suppliers/${id}`,
    method: 'get'
  });
};

// 获取启用的供应商选项
export const getEnabledSuppliers = () => {
  return request({
    url: '/tenant/base-archive/base-data/suppliers/enabled',
    method: 'get'
  });
};

// 批量更新供应商
export const batchUpdateSuppliers = (data) => {
  return request({
    url: '/tenant/base-archive/base-data/suppliers/batch-update',
    method: 'post',
    data
  });
};

// 获取供应商选项（用于下拉框）
export const getSupplierOptions = () => {
  return request({
    url: '/tenant/base-archive/base-data/suppliers/form-options',
    method: 'get'
  });
};

// 导入供应商数据
export const importSuppliers = (formData) => {
  return request({
    url: '/tenant/base-archive/base-data/suppliers/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

// 导出供应商数据
export const exportSuppliers = (params) => {
  return request({
    url: '/tenant/base-archive/base-data/suppliers/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
};

// 搜索供应商
export const searchSuppliers = (keyword) => {
  return request({
    url: '/tenant/base-archive/base-data/suppliers/search',
    method: 'get',
    params: { keyword }
  });
};

// 统一导出API对象
export const supplierManagementApi = {
  // 新版本API
  getSuppliers,
  getSupplierById,
  createSupplier,
  updateSupplier,
  deleteSupplier,
  getEnabledSuppliers,
  batchUpdateSuppliers,
  getSupplierOptions,
  importSuppliers,
  exportSuppliers,
  searchSuppliers,
  // 旧版本API (向后兼容)
  getSupplierManagementList,
  getSupplierManagementDetail,
  createSupplierManagement,
  updateSupplierManagement,
  deleteSupplierManagement,
  toggleSupplierStatus,
  exportSupplierManagement,
  getSupplierManagementFormOptions
}; 