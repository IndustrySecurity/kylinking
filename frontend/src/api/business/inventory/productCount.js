import request from '../../../utils/request';

/**
 * 成品盘点API
 */

// 获取产品盘点列表
export const getProductCounts = (params) => {
  return request({
    url: '/tenant/business/inventory/product-count/product-count-plans',
    method: 'get',
    params
  });
};

// 创建产品盘点
export const createProductCount = (data) => {
  return request({
    url: '/tenant/business/inventory/product-count/product-count-plans',
    method: 'post',
    data
  });
};

// 获取产品盘点详情
export const getProductCountById = (id) => {
  return request({
    url: `/tenant/business/inventory/product-count/product-count-plans/${id}`,
    method: 'get'
  });
};

// 更新产品盘点
export const updateProductCount = (id, data) => {
  return request({
    url: `/tenant/business/inventory/product-count/product-count-plans/${id}`,
    method: 'put',
    data
  });
};

// 删除产品盘点
export const deleteProductCount = (id) => {
  return request({
    url: `/tenant/business/inventory/product-count/product-count-plans/${id}`,
    method: 'delete'
  });
};

// 确认产品盘点
export const confirmProductCount = (id) => {
  return request({
    url: `/tenant/business/inventory/product-count/product-count-plans/${id}/complete`,
    method: 'post'
  });
};


// 导出产品盘点
export const exportProductCount = (params) => {
  return request({
    url: '/tenant/business/inventory/product-count/product-count-plans/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
};

// ==================== 盘点计划API ====================

// 获取盘点计划列表
export const getProductCountPlans = (params = {}) => {
  return request.get('/tenant/business/inventory/product-count/product-count-plans', { params });
};

// 创建盘点计划
export const createProductCountPlan = (data) => {
  return request.post('/tenant/business/inventory/product-count/product-count-plans', data);
};

// 获取盘点计划详情
export const getProductCountPlan = (planId) => {
  return request.get(`/tenant/business/inventory/product-count/product-count-plans/${planId}`);
};

// 获取盘点记录
export const getProductCountRecords = (planId, params = {}) => {
  return request.get(`/tenant/business/inventory/product-count/product-count-plans/${planId}/records`, { params });
};

// 更新盘点记录
export const updateProductCountRecord = (planId, recordId, data) => {
  return request.put(`/tenant/business/inventory/product-count/product-count-plans/${planId}/records/${recordId}`, data);
};

// 开始盘点
export const startProductCountPlan = (planId) => {
  return request.post(`/tenant/business/inventory/product-count/product-count-plans/${planId}/start`);
};

// 完成盘点
export const completeProductCountPlan = (planId) => {
  return request.post(`/tenant/business/inventory/product-count/product-count-plans/${planId}/complete`);
};

// 调整库存
export const adjustProductCountInventory = (planId, data) => {
  return request.post(`/tenant/business/inventory/product-count/product-count-plans/${planId}/adjust`, data);
};

// 删除盘点计划
export const deleteProductCountPlan = (planId) => {
  return request.delete(`/tenant/business/inventory/product-count/product-count-plans/${planId}`);
};

// 获取盘点统计
export const getProductCountStatistics = (planId) => {
  return request.get(`/tenant/business/inventory/product-count/product-count-plans/${planId}/statistics`);
};

// 获取仓库成品库存
export const getWarehouseProductInventory = (warehouseId) => {
  return request.get(`/tenant/business/inventory/product-count/warehouses/${warehouseId}/product-inventory`);
};

// 获取仓库列表
export const getWarehouses = () => {
  return request.get('/tenant/base-archive/production-archive/warehouses/options');
};

// 获取员工列表
export const getEmployees = () => {
  return request.get('/tenant/base-archive/base-data/employees/options');
};

// 获取部门列表
export const getDepartments = () => {
  return request.get('/tenant/base-archive/base-data/departments/options');
};

// 统一导出API对象
export const productCountApi = {
  // 基础盘点API
  getProductCounts,
  createProductCount,
  updateProductCount,
  deleteProductCount,
  getProductCountById,
  confirmProductCount,
  exportProductCount,
  // 盘点计划API
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

// 保持向后兼容的默认导出
export default productCountApi; 