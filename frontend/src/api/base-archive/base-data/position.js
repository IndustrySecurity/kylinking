import request from '../../../utils/request';

// 获取职位列表
export const getPositions = (params) => {
  return request({
    url: '/tenant/base-archive/base-data/positions',
    method: 'get',
    params
  });
};

// 创建职位
export const createPosition = (data) => {
  return request({
    url: '/tenant/base-archive/base-data/positions',
    method: 'post',
    data
  });
};

// 更新职位
export const updatePosition = (id, data) => {
  return request({
    url: `/tenant/base-archive/base-data/positions/${id}`,
    method: 'put',
    data
  });
};

// 删除职位
export const deletePosition = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/positions/${id}`,
    method: 'delete'
  });
};

// 获取职位详情
export const getPositionById = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/positions/${id}`,
    method: 'get'
  });
};

// 批量更新职位
export const batchUpdatePositions = (data) => {
  return request({
    url: '/tenant/base-archive/base-data/positions/batch-update',
    method: 'post',
    data
  });
};

// 获取职位选项
export const getPositionOptions = () => {
  return request({
    url: '/tenant/base-archive/base-data/positions/options',
    method: 'get'
  });
};

// 根据部门获取职位
export const getPositionsByDepartment = (departmentId) => {
  return request({
    url: `/tenant/base-archive/base-data/positions/by-department/${departmentId}`,
    method: 'get'
  });
};

// 启用/禁用职位
export const togglePositionStatus = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/positions/${id}/toggle-status`,
    method: 'put'
  });
};

// 获取部门选项数据
export const getDepartmentOptions = () => {
  return request({
    url: '/tenant/base-archive/base-data/departments/options',
    method: 'get'
  });
};

// 统一导出API对象作为默认导出
const positionApi = {
  getPositions,
  createPosition,
  updatePosition,
  deletePosition,
  getPositionById,
  batchUpdatePositions,
  getPositionOptions,
  getPositionsByDepartment,
  togglePositionStatus,
  getDepartmentOptions
};

export default positionApi; 