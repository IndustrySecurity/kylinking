import request from '@/utils/request'

// 供应商管理API

/**
 * 获取供应商管理列表
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getSupplierManagementList(params) {
  return request({
    url: '/tenant/basic-data/supplier-management',
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
    url: `/tenant/basic-data/supplier-management/${id}`,
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
    url: '/tenant/basic-data/supplier-management',
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
    url: `/tenant/basic-data/supplier-management/${id}`,
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
    url: `/tenant/basic-data/supplier-management/${id}`,
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
    url: `/tenant/basic-data/supplier-management/${id}/toggle-status`,
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
    url: '/tenant/basic-data/supplier-management/export',
    method: 'get',
    params
  })
}

/**
 * 获取供应商管理表单选项
 * @returns {Promise} API响应
 */
export function getSupplierManagementFormOptions() {
  return request({
    url: '/tenant/basic-data/supplier-management/form-options',
    method: 'get'
  })
} 