import request from '../../utils/request';

/**
 * 材料盘点API
 */

// 获取盘点计划列表
export const getMaterialCountPlans = (params = {}) => {
  return request.get('/tenant/inventory/material-count-plans', { params });
};

// 创建盘点计划
export const createMaterialCountPlan = (data) => {
  return request.post('/tenant/inventory/material-count-plans', data);
};

// 获取盘点计划详情
export const getMaterialCountPlan = (planId) => {
  return request.get(`/tenant/inventory/material-count-plans/${planId}`);
};

// 获取盘点记录
export const getMaterialCountRecords = (planId) => {
  return request.get(`/tenant/inventory/material-count-plans/${planId}/records`);
};

// 更新盘点记录
export const updateMaterialCountRecord = (planId, recordId, data) => {
  return request.put(`/tenant/inventory/material-count-plans/${planId}/records/${recordId}`, data);
};

// 开始盘点
export const startMaterialCountPlan = (planId) => {
  return request.post(`/tenant/inventory/material-count-plans/${planId}/start`);
};

// 完成盘点
export const completeMaterialCountPlan = (planId) => {
  return request.post(`/tenant/inventory/material-count-plans/${planId}/complete`);
};

// 调整库存
export const adjustMaterialCountInventory = (planId) => {
  return request.post(`/tenant/inventory/material-count-plans/${planId}/adjust`);
};

// 获取仓库材料库存
export const getWarehouseMaterialInventory = (warehouseId) => {
  return request.get(`/tenant/inventory/warehouses/${warehouseId}/material-inventory`);
};

// 获取仓库列表（用于选择仓库，只获取材料仓）
export const getWarehouses = (params = {}) => {
  return request.get('/tenant/basic-data/warehouses/options', { 
    params: { 
      ...params,
      warehouse_type: 'material' // 只获取材料仓
    } 
  });
};

export default {
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