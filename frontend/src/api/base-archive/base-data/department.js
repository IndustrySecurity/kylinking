import request from '../../../utils/request';

/**
 * 部门管理 API
 */

// 获取部门列表
export const getDepartments = (params) => {
  return request({
    url: '/tenant/base-archive/base-data/departments/',
    method: 'get',
    params
  });
};

// 获取部门详情
export const getDepartmentById = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/departments/${id}`,
    method: 'get'
  });
};

// 创建部门
export const createDepartment = (data) => {
  return request({
    url: '/tenant/base-archive/base-data/departments/',
    method: 'post',
    data
  });
};

// 更新部门
export const updateDepartment = (id, data) => {
  return request({
    url: `/tenant/base-archive/base-data/departments/${id}`,
    method: 'put',
    data
  });
};

// 删除部门
export const deleteDepartment = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/departments/${id}`,
    method: 'delete'
  });
};

// 批量更新部门
export const batchUpdateDepartments = (data) => {
  return request({
    url: '/tenant/base-archive/base-data/departments/batch',
    method: 'put',
    data
  });
};

// 获取部门选项
export const getDepartmentOptions = () => {
  return request({
    url: '/tenant/base-archive/base-data/departments/options',
    method: 'get'
  });
};

// 获取部门树形结构
export const getDepartmentTree = () => {
  return request({
    url: '/tenant/base-archive/base-data/departments/tree',
    method: 'get'
  });
};

// 为向后兼容添加getDepartment别名
export const getDepartment = getDepartmentById;

// 统一导出API对象
export const departmentApi = {
  getDepartments,
  getDepartmentById,
  getDepartment: getDepartmentById,
  createDepartment,
  updateDepartment,
  deleteDepartment,
  batchUpdateDepartments,
  getDepartmentOptions,
  getDepartmentTree
}; 