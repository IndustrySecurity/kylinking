import request from '../../utils/request';

/**
 * 成品盘点API
 */

// 获取盘点计划列表
export const getProductCountPlans = (params = {}) => {
  return request.get('/tenant/inventory/product-count-plans', { params });
};

// 创建盘点计划
export const createProductCountPlan = (data) => {
  return request.post('/tenant/inventory/product-count-plans', data);
};

// 获取盘点计划详情
export const getProductCountPlan = (planId) => {
  return request.get(`/tenant/inventory/product-count-plans/${planId}`);
};

// 获取盘点记录
export const getProductCountRecords = (planId, params = {}) => {
  return request.get(`/tenant/inventory/product-count-plans/${planId}/records`, { params });
};

// 更新盘点记录
export const updateProductCountRecord = (planId, recordId, data) => {
  return request.put(`/tenant/inventory/product-count-plans/${planId}/records/${recordId}`, data);
};

// 开始盘点计划
export const startProductCountPlan = (planId) => {
  return request.post(`/tenant/inventory/product-count-plans/${planId}/start`);
};

// 完成盘点计划
export const completeProductCountPlan = (planId) => {
  return request.post(`/tenant/inventory/product-count-plans/${planId}/complete`);
};

// 调整库存
export const adjustProductCountInventory = (planId, data) => {
  return request.post(`/tenant/inventory/product-count-plans/${planId}/adjust`, data);
};

// 删除盘点计划
export const deleteProductCountPlan = (planId) => {
  return request.delete(`/tenant/inventory/product-count-plans/${planId}`);
};

// 获取盘点统计信息
export const getProductCountStatistics = (planId) => {
  return request.get(`/tenant/inventory/product-count-plans/${planId}/statistics`);
};

// 获取仓库成品库存
export const getWarehouseProductInventory = (warehouseId) => {
  return request.get(`/tenant/inventory/warehouses/${warehouseId}/product-inventory`);
};

// 获取仓库列表
export const getWarehouses = () => {
  return request.get('/tenant/basic-data/warehouses/options');
};

// 获取员工列表
export const getEmployees = () => {
  return request.get('/tenant/basic-data/employees/options');
};

// 获取部门列表
export const getDepartments = () => {
  return request.get('/tenant/basic-data/departments/options');
};

export default {
  getProductCountPlans,
  createProductCountPlan,
  getProductCountPlan,
  getProductCountRecords,
  updateProductCountRecord,
  startProductCountPlan,
  completeProductCountPlan,
  adjustProductCountInventory,
  deleteProductCountPlan,
  getProductCountStatistics,
  getWarehouseProductInventory,
  getWarehouses,
  getEmployees,
  getDepartments
}; 