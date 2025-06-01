import request from '../utils/request';

/**
 * 仓库管理API
 */
export const warehouseApi = {
  // 获取仓库列表
  getWarehouses: (params = {}) => {
    return request.get('/tenant/basic-data/warehouses', { params });
  },

  // 获取仓库详情
  getWarehouse: (warehouseId) => {
    return request.get(`/tenant/basic-data/warehouses/${warehouseId}`);
  },

  // 创建仓库
  createWarehouse: (data) => {
    return request.post('/tenant/basic-data/warehouses', data);
  },

  // 更新仓库
  updateWarehouse: (warehouseId, data) => {
    return request.put(`/tenant/basic-data/warehouses/${warehouseId}`, data);
  },

  // 删除仓库
  deleteWarehouse: (warehouseId) => {
    return request.delete(`/tenant/basic-data/warehouses/${warehouseId}`);
  },

  // 批量更新仓库
  batchUpdateWarehouses: (updates) => {
    return request.put('/tenant/basic-data/warehouses/batch', { updates });
  },

  // 获取仓库选项
  getWarehouseOptions: () => {
    return request.get('/tenant/basic-data/warehouses/options');
  },

  // 获取仓库树形结构
  getWarehouseTree: () => {
    return request.get('/tenant/basic-data/warehouses/tree');
  },

  // 获取仓库类型选项
  getWarehouseTypes: () => {
    return request.get('/tenant/basic-data/warehouses/types');
  },

  // 获取核算方式选项
  getAccountingMethods: () => {
    return request.get('/tenant/basic-data/warehouses/accounting-methods');
  },

  // 获取流转类型选项
  getCirculationTypes: () => {
    return request.get('/tenant/basic-data/warehouses/circulation-types');
  },

  // 获取下一个仓库编号
  getNextWarehouseCode: () => {
    return request.get('/tenant/basic-data/warehouses/next-warehouse-code');
  }
}; 