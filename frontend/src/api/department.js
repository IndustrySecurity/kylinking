import api from '../utils/request';

/**
 * 部门管理 API
 */

// 获取部门列表
export const getDepartments = (params = {}) => {
  return api.get('/tenant/basic-data/departments', { params });
};

// 获取部门详情
export const getDepartment = (id) => {
  return api.get(`/tenant/basic-data/departments/${id}`);
};

// 创建部门
export const createDepartment = (data) => {
  return api.post('/tenant/basic-data/departments', data);
};

// 更新部门
export const updateDepartment = (id, data) => {
  return api.put(`/tenant/basic-data/departments/${id}`, data);
};

// 删除部门
export const deleteDepartment = (id) => {
  return api.delete(`/tenant/basic-data/departments/${id}`);
};

// 批量更新部门
export const batchUpdateDepartments = (data) => {
  return api.put('/tenant/basic-data/departments/batch', data);
};

// 获取部门选项数据
export const getDepartmentOptions = () => {
  return api.get('/tenant/basic-data/departments/options');
};

// 获取部门树形结构
export const getDepartmentTree = () => {
  return api.get('/tenant/basic-data/departments/tree');
}; 