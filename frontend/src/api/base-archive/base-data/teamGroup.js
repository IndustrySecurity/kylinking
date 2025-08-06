import request from '../../../utils/request'

/**
 * 班组管理API
 */

/**
 * 获取班组列表
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getTeamGroups(params) {
  return request({
    url: '/tenant/base-archive/base-data/team-group/',
    method: 'get',
    params
  })
}

/**
 * 获取班组详情
 * @param {string} id - 班组ID
 * @returns {Promise} API响应
 */
export function getTeamGroup(id) {
  return request({
    url: `/tenant/base-archive/base-data/team-group/${id}`,
    method: 'get'
  })
}

/**
 * 创建班组
 * @param {Object} data - 班组数据
 * @returns {Promise} API响应
 */
export function createTeamGroup(data) {
  return request({
    url: '/tenant/base-archive/base-data/team-group/',
    method: 'post',
    data
  })
}

/**
 * 更新班组
 * @param {string} id - 班组ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateTeamGroup(id, data) {
  return request({
    url: `/tenant/base-archive/base-data/team-group/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除班组
 * @param {string} id - 班组ID
 * @returns {Promise} API响应
 */
export function deleteTeamGroup(id) {
  return request({
    url: `/tenant/base-archive/base-data/team-group/${id}`,
    method: 'delete'
  })
}

/**
 * 切换班组启用状态
 * @param {string} id - 班组ID
 * @returns {Promise} API响应
 */
export function toggleTeamGroupStatus(id) {
  return request({
    url: `/tenant/base-archive/base-data/team-group/${id}/toggle-status`,
    method: 'put'
  })
}

/**
 * 导出班组数据
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function exportTeamGroups(params) {
  return request({
    url: '/tenant/base-archive/base-data/team-group/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 获取班组表单选项数据（员工、机台、工序分类等）
 * @returns {Promise} API响应
 */
export function getTeamGroupFormOptions() {
  return request({
    url: '/tenant/base-archive/base-data/team-group/form-options',
    method: 'get'
  })
}

/**
 * 获取启用的班组选项
 * @returns {Promise} API响应
 */
export function getEnabledTeamGroups() {
  return request({
    url: '/tenant/base-archive/base-data/team-group/enabled',
    method: 'get'
  })
}

/**
 * 获取班组选项（用于下拉框）
 * @returns {Promise} API响应
 */
export function getTeamGroupOptions() {
  return request({
    url: '/tenant/base-archive/base-data/team-group/options',
    method: 'get'
  })
}

/**
 * 批量更新班组
 * @param {Object} data - 批量更新数据
 * @returns {Promise} API响应
 */
export function batchUpdateTeamGroups(data) {
  return request({
    url: '/tenant/base-archive/base-data/team-group/batch-update',
    method: 'post',
    data
  })
}

/**
 * 导入班组数据
 * @param {FormData} formData - 导入文件数据
 * @returns {Promise} API响应
 */
export function importTeamGroups(formData) {
  return request({
    url: '/tenant/base-archive/base-data/team-group/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 搜索班组
 * @param {string} keyword - 搜索关键词
 * @returns {Promise} API响应
 */
export function searchTeamGroups(keyword) {
  return request({
    url: '/tenant/base-archive/base-data/team-group/search',
    method: 'get',
    params: { keyword }
  })
}

/**
 * 班组成员管理
 */

/**
 * 添加班组成员
 * @param {string} teamGroupId - 班组ID
 * @param {Object} data - 成员数据
 * @returns {Promise} API响应
 */
export function addTeamMember(teamGroupId, data) {
  return request({
    url: `/tenant/base-archive/base-data/team-groups/${teamGroupId}/members`,
    method: 'post',
    data
  })
}

/**
 * 更新班组成员
 * @param {string} memberId - 成员ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateTeamMember(memberId, data) {
  return request({
    url: `/tenant/base-archive/base-data/team-members/${memberId}`,
    method: 'put',
    data
  })
}

/**
 * 删除班组成员
 * @param {string} memberId - 成员ID
 * @returns {Promise} API响应
 */
export function deleteTeamMember(memberId) {
  return request({
    url: `/tenant/base-archive/base-data/team-members/${memberId}`,
    method: 'delete'
  })
}

/**
 * 班组机台管理
 */

/**
 * 添加班组机台
 * @param {string} teamGroupId - 班组ID
 * @param {Object} data - 机台数据
 * @returns {Promise} API响应
 */
export function addTeamMachine(teamGroupId, data) {
  return request({
    url: `/tenant/base-archive/base-data/team-groups/${teamGroupId}/machines`,
    method: 'post',
    data
  })
}

/**
 * 更新班组机台
 * @param {string} machineId - 机台ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateTeamMachine(machineId, data) {
  return request({
    url: `/tenant/base-archive/base-data/team-machines/${machineId}`,
    method: 'put',
    data
  })
}

/**
 * 删除班组机台
 * @param {string} machineId - 机台ID
 * @returns {Promise} API响应
 */
export function deleteTeamMachine(machineId) {
  return request({
    url: `/tenant/base-archive/base-data/team-machines/${machineId}`,
    method: 'delete'
  })
}

/**
 * 班组工序分类管理
 */

/**
 * 添加班组工序分类
 * @param {string} teamGroupId - 班组ID
 * @param {Object} data - 工序分类数据
 * @returns {Promise} API响应
 */
export function addTeamProcess(teamGroupId, data) {
  return request({
    url: `/tenant/base-archive/base-data/team-groups/${teamGroupId}/processes`,
    method: 'post',
    data
  })
}

/**
 * 更新班组工序分类
 * @param {string} processId - 工序分类ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateTeamProcess(processId, data) {
  return request({
    url: `/tenant/base-archive/base-data/team-processes/${processId}`,
    method: 'put',
    data
  })
}

/**
 * 删除班组工序分类
 * @param {string} processId - 工序分类ID
 * @returns {Promise} API响应
 */
export function deleteTeamProcess(processId) {
  return request({
    url: `/tenant/base-archive/base-data/team-processes/${processId}`,
    method: 'delete'
  })
}

/**
 * 获取员工选项
 * @returns {Promise} API响应
 */
export function getEmployeeOptions() {
  return request({
    url: '/tenant/base-archive/base-data/employees/options',
    method: 'get'
  })
}

/**
 * 获取机台选项
 * @returns {Promise} API响应
 */
export function getMachineOptions() {
  return request({
    url: '/tenant/base-archive/production-archive/machines/',
    method: 'get',
    params: { options: true }
  })
}

/**
 * 获取工序分类选项
 * @returns {Promise} API响应
 */
export function getProcessCategoryOptions() {
  return request({
    url: '/tenant/base-archive/base-category/process-categories/',
    method: 'get',
    params: { options: true }
  })
}

/**
 * 获取工序选项
 * @returns {Promise} API响应
 */
export function getProcessOptions() {
  return request({
    url: '/tenant/base-archive/production-archive/processes/',
    method: 'get',
    params: { options: true }
  })
}

// 统一导出API对象
export const teamGroupApi = {
  getTeamGroups,
  getTeamGroup,
  createTeamGroup,
  updateTeamGroup,
  deleteTeamGroup,
  toggleTeamGroupStatus,
  exportTeamGroups,
  getTeamGroupFormOptions,
  getEnabledTeamGroups,
  getTeamGroupOptions,
  batchUpdateTeamGroups,
  importTeamGroups,
  searchTeamGroups,
  addTeamMember,
  updateTeamMember,
  deleteTeamMember,
  addTeamMachine,
  updateTeamMachine,
  deleteTeamMachine,
  addTeamProcess,
  updateTeamProcess,
  deleteTeamProcess,
  getEmployeeOptions,
  getMachineOptions,
  getProcessCategoryOptions
} 