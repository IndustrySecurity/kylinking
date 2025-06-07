import request from '@/utils/request'

// 客户管理API

/**
 * 获取客户管理列表
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getCustomerManagementList(params) {
  return request({
    url: '/tenant/basic-data/customer-management',
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
    url: `/tenant/basic-data/customer-management/${id}`,
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
    url: '/tenant/basic-data/customer-management',
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
    url: `/tenant/basic-data/customer-management/${id}`,
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
    url: `/tenant/basic-data/customer-management/${id}`,
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
    url: `/tenant/basic-data/customer-management/${id}/toggle-status`,
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
    url: '/tenant/basic-data/customer-management/export',
    method: 'get',
    params
  })
}

/**
 * 获取客户管理表单选项
 * @returns {Promise} API响应
 */
export function getCustomerManagementFormOptions() {
  return request({
    url: '/tenant/basic-data/customer-management/form-options',
    method: 'get'
  })
} 