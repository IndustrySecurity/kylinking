import request from '../../utils/request';

/**
 * 材料盘点API
 */

// 获取材料盘点列表
export const getMaterialCounts = (params) => {
  return request({
    url: '/tenant/business/inventory/material-count/material-count-orders',
    method: 'get',
    params
  });
};

// 创建材料盘点
export const createMaterialCount = (data) => {
  return request({
    url: '/tenant/business/inventory/material-count/material-count-orders',
    method: 'post',
    data
  });
};

// 获取材料盘点详情
export const getMaterialCountById = (id) => {
  return request({
    url: `/tenant/business/inventory/material-count/material-count-orders/${id}`,
    method: 'get'
  });
};

// 更新材料盘点
export const updateMaterialCount = (id, data) => {
  return request({
    url: `/tenant/business/inventory/material-count/material-count-orders/${id}`,
    method: 'put',
    data
  });
};

// 删除材料盘点
export const deleteMaterialCount = (id) => {
  return request({
    url: `/tenant/business/inventory/material-count/material-count-orders/${id}`,
    method: 'delete'
  });
};

// 确认材料盘点
export const confirmMaterialCount = (id) => {
  return request({
    url: `/tenant/business/inventory/material-count/material-count-orders/${id}/approve`,
    method: 'post'
  });
};

// 获取材料库存
export const getMaterialInventory = (params) => {
  return request({
    url: '/tenant/business/inventory/inventories',
    method: 'get',
    params
  });
};

// 导出材料盘点
export const exportMaterialCount = (params) => {
  return request({
    url: '/tenant/business/inventory/material-count/material-count-orders/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
};

// 获取仓库材料库存
export const getWarehouseMaterialInventory = (warehouseId) => {
  return request.get(`/tenant/business/inventory/inventories?warehouse_id=${warehouseId}`);
};

// 获取仓库列表（用于选择仓库，只获取材料仓）
export const getWarehouses = (params = {}) => {
  return request.get('/tenant/base-archive/base-data/warehouses/options', { 
    params: { 
      ...params,
      warehouse_type: 'material' // 只获取材料仓
    } 
  });
};

// 获取盘点计划列表（实际就是盘点列表）
export const getMaterialCountPlans = (params = {}) => {
  return request.get('/tenant/business/inventory/material-count/material-count-orders', { params });
};

// 创建盘点计划（实际就是创建盘点）
export const createMaterialCountPlan = (data) => {
  return request.post('/tenant/business/inventory/material-count/material-count-orders', data);
};

// 获取盘点计划详情（实际就是盘点详情）
export const getMaterialCountPlan = (planId) => {
  return request.get(`/tenant/business/inventory/material-count/material-count-orders/${planId}`);
};

// 获取盘点记录
export const getMaterialCountRecords = (planId, params = {}) => {
  return request.get(`/tenant/business/inventory/material-count/material-count-orders/${planId}/records`, { params });
};

// 更新盘点记录
export const updateMaterialCountRecord = (planId, recordId, data) => {
  return request.put(`/tenant/business/inventory/material-count/material-count-orders/${planId}/records/${recordId}`, data);
};

// 开始盘点
export const startMaterialCountPlan = (planId) => {
  return request.post(`/tenant/business/inventory/material-count/material-count-orders/${planId}/start`);
};

// 完成盘点
export const completeMaterialCountPlan = (planId) => {
  return request.post(`/tenant/business/inventory/material-count/material-count-orders/${planId}/complete`);
};

// 调整库存
export const adjustMaterialCountInventory = (planId, data = {}) => {
  return request.post(`/tenant/business/inventory/material-count/material-count-orders/plans/${planId}/adjust`, data);
};

// 统一导出API对象
export const materialCountApi = {
  // 基础盘点API
  getMaterialCounts,
  createMaterialCount,
  updateMaterialCount,
  deleteMaterialCount,
  getMaterialCountById,
  confirmMaterialCount,
  getMaterialInventory,
  exportMaterialCount,
  // 盘点计划API
  getMaterialCountPlans,
  createMaterialCountPlan,
  getMaterialCountPlan,
  getMaterialCountRecords,
  updateMaterialCountRecord,
  startMaterialCountPlan,
  completeMaterialCountPlan,
  adjustMaterialCountInventory,
  getWarehouseMaterialInventory,
  getWarehouses
};

// 保持向后兼容的默认导出
export default materialCountApi; 