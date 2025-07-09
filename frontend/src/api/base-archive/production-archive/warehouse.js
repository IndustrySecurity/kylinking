import request from '../../../utils/request';

/**
 * 仓库管理API
 */
export const warehouseApi = {
  // 获取仓库列表
  getWarehouses: (params = {}) => {
    return request.get('/tenant/base-archive/production/production-archive/warehouses', { params });
  },

  // 获取仓库详情
  getWarehouse: (warehouseId) => {
    return request.get(`/tenant/base-archive/production/production-archive/warehouses/${warehouseId}`);
  },

  // 创建仓库
  createWarehouse: (data) => {
    return request.post('/tenant/base-archive/production/production-archive/warehouses', data);
  },

  // 更新仓库
  updateWarehouse: (warehouseId, data) => {
    return request.put(`/tenant/base-archive/production/production-archive/warehouses/${warehouseId}`, data);
  },

  // 删除仓库
  deleteWarehouse: (warehouseId) => {
    return request.delete(`/tenant/base-archive/production/production-archive/warehouses/${warehouseId}`);
  },

  // 批量更新仓库
  batchUpdateWarehouses: (updates) => {
    return request.put('/tenant/base-archive/production/production-archive/warehouses/batch', { updates });
  },

  // 获取仓库选项
  getWarehouseOptions: () => {
    return request.get('/tenant/base-archive/production/production-archive/warehouses/options');
  },

  // 获取仓库树形结构
  getWarehouseTree: () => {
    return request.get('/tenant/base-archive/production/production-archive/warehouses/tree');
  },

  // 获取仓库类型选项
  getWarehouseTypes: () => {
    return request.get('/tenant/base-archive/production/production-archive/warehouses/types');
  },

  // 获取核算方式选项
  getAccountingMethods: () => {
    return request.get('/tenant/base-archive/production/production-archive/warehouses/accounting-methods');
  },

  // 获取流转类型选项
  getCirculationTypes: () => {
    return request.get('/tenant/base-archive/production/production-archive/warehouses/circulation-types');
  },

  // 获取下一个仓库编号
  getNextWarehouseCode: () => {
    return request.get('/tenant/base-archive/production/production-archive/warehouses/next-warehouse-code');
  }
}; 