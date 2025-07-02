import request from '../../utils/request'

// 客户管理API

/**
 * 获取客户管理列表
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getCustomerManagementList(params) {
  return request({
    url: '/tenant/base-archive/base-data/customers',
    method: 'get',
    params
  })
}

/**
 * 获取客户管理详情
 * @param {string} id - 客户ID
 * @returns {Promise} API响应
 */
export function getCustomerManagementDetail(id) {
  return request({
    url: `/tenant/base-archive/base-data/customers/${id}`,
    method: 'get'
  })
}

/**
 * 创建客户管理
 * @param {Object} data - 客户数据
 * @returns {Promise} API响应
 */
export function createCustomerManagement(data) {
  return request({
    url: '/tenant/base-archive/base-data/customers',
    method: 'post',
    data
  })
}

/**
 * 更新客户管理
 * @param {string} id - 客户ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateCustomerManagement(id, data) {
  return request({
    url: `/tenant/base-archive/base-data/customers/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除客户管理
 * @param {string} id - 客户ID
 * @returns {Promise} API响应
 */
export function deleteCustomerManagement(id) {
  return request({
    url: `/tenant/base-archive/base-data/customers/${id}`,
    method: 'delete'
  })
}

/**
 * 切换客户启用状态
 * @param {string} id - 客户ID
 * @returns {Promise} API响应
 */
export function toggleCustomerStatus(id) {
  return request({
    url: `/tenant/base-archive/base-data/customers/${id}/toggle-status`,
    method: 'put'
  })
}

/**
 * 导出客户管理数据
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function exportCustomerManagement(params) {
  return request({
    url: '/tenant/base-archive/base-data/customers/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 获取客户管理表单选项
 * @returns {Promise} API响应
 */
export function getCustomerManagementFormOptions() {
  return request({
    url: '/tenant/base-archive/base-data/customers/form-options',
    method: 'get'
  })
}

// 获取启用的客户选项
export function getEnabledCustomers() {
  return request({
    url: '/tenant/base-archive/base-data/customers/enabled',
    method: 'get'
  })
}

// 批量更新客户
export function batchUpdateCustomers(data) {
  return request({
    url: '/tenant/base-archive/base-data/customers/batch-update',
    method: 'post',
    data
  })
}

// 获取客户选项（用于下拉框）
export function getCustomerOptions() {
  return request({
    url: '/tenant/base-archive/base-data/customers/form-options',
    method: 'get'
  })
}

// 导入客户数据
export function importCustomers(formData) {
  return request({
    url: '/tenant/base-archive/base-data/customers/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 搜索客户
export function searchCustomers(keyword) {
  return request({
    url: '/tenant/base-archive/base-data/customers/search',
    method: 'get',
    params: { keyword }
  })
}

// 统一导出API对象
export const customerManagementApi = {
  getCustomerManagementList,
  getCustomerManagementDetail,
  createCustomerManagement,
  updateCustomerManagement,
  deleteCustomerManagement,
  toggleCustomerStatus,
  exportCustomerManagement,
  getCustomerManagementFormOptions,
  getEnabledCustomers,
  batchUpdateCustomers,
  getCustomerOptions,
  importCustomers,
  searchCustomers
}; 