import request from '../../utils/request';

/**
 * 材料盘点API
 */

// 获取原料盘点列表
export const getMaterialCounts = (params) => {
  return request({
    url: '/tenant/business/inventory/material-count',
    method: 'get',
    params
  });
};

// 创建原料盘点
export const createMaterialCount = (data) => {
  return request({
    url: '/tenant/business/inventory/material-count',
    method: 'post',
    data
  });
};

// 更新原料盘点
export const updateMaterialCount = (id, data) => {
  return request({
    url: `/tenant/business/inventory/material-count/${id}`,
    method: 'put',
    data
  });
};

// 删除原料盘点
export const deleteMaterialCount = (id) => {
  return request({
    url: `/tenant/business/inventory/material-count/${id}`,
    method: 'delete'
  });
};

// 获取原料盘点详情
export const getMaterialCountById = (id) => {
  return request({
    url: `/tenant/business/inventory/material-count/${id}`,
    method: 'get'
  });
};

// 确认原料盘点
export const confirmMaterialCount = (id) => {
  return request({
    url: `/tenant/business/inventory/material-count/${id}/confirm`,
    method: 'post'
  });
};

// 获取原料库存
export const getMaterialInventory = (params) => {
  return request({
    url: '/tenant/business/inventory/material-inventory',
    method: 'get',
    params
  });
};

// 导出原料盘点数据
export const exportMaterialCount = (params) => {
  return request({
    url: '/tenant/business/inventory/material-count/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
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
export const getMaterialCountRecords = (planId, params = {}) => {
  return request.get(`/tenant/inventory/material-count-plans/${planId}/records`, { params });
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
export const adjustMaterialCountInventory = (planId, data) => {
  return request.post(`/tenant/inventory/material-count-plans/${planId}/adjust`, data);
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