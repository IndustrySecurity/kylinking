import request from '../../../utils/request';

const API_BASE = '/tenant/business/inventory/material-count';

// 材料盘点相关API
export const materialCountService = {
  // 获取盘点单列表
  getCountOrderList: (params = {}) => {
    return request.get(`${API_BASE}/material-count-orders`, { params });
  },

  // 获取盘点单详情
  getCountOrderById: (id) => {
    return request.get(`${API_BASE}/material-count-orders/${id}`);
  },

  // 创建盘点单
  createCountOrder: (data) => {
    return request.post(`${API_BASE}/material-count-orders`, data);
  },

  // 更新盘点单
  updateCountOrder: (id, data) => {
    return request.put(`${API_BASE}/material-count-orders/${id}`, data);
  },

  // 删除盘点单
  deleteCountOrder: (id) => {
    return request.delete(`${API_BASE}/material-count-orders/${id}`);
  },

  // 确认盘点单
  confirmCountOrder: (id) => {
    return request.post(`${API_BASE}/material-count-orders/${id}/approve`);
  },

  // 开始盘点
  startCountOrder: (id) => {
    return request.post(`${API_BASE}/material-count-orders/${id}/start`);
  },

  // 完成盘点
  completeCountOrder: (id) => {
    return request.post(`${API_BASE}/material-count-orders/${id}/complete`);
  },

  // 取消盘点单
  cancelCountOrder: (id, data) => {
    return request.post(`${API_BASE}/material-count-orders/${id}/cancel`, data);
  },

  // 获取盘点记录列表
  getCountRecords: (orderId, params = {}) => {
    return request.get(`${API_BASE}/material-count-orders/${orderId}/records`, { params });
  },

  // 创建盘点记录
  createCountRecord: (orderId, data) => {
    return request.post(`${API_BASE}/material-count-orders/${orderId}/records`, data);
  },

  // 更新盘点记录
  updateCountRecord: (orderId, recordId, data) => {
    return request.put(`${API_BASE}/material-count-orders/${orderId}/records/${recordId}`, data);
  },

  // 删除盘点记录
  deleteCountRecord: (orderId, recordId) => {
    return request.delete(`${API_BASE}/material-count-orders/${orderId}/records/${recordId}`);
  },

  // 批量创建盘点记录
  batchCreateCountRecords: (orderId, data) => {
    return request.post(`${API_BASE}/material-count-orders/${orderId}/records/batch`, data);
  },

  // 批量更新盘点记录
  batchUpdateCountRecords: (orderId, data) => {
    return request.put(`${API_BASE}/material-count-orders/${orderId}/records/batch`, data);
  },

  // 批量删除盘点记录
  batchDeleteCountRecords: (orderId, recordIds) => {
    return request.delete(`${API_BASE}/material-count-orders/${orderId}/records/batch`, {
      data: { record_ids: recordIds }
    });
  },

  // 调整库存
  adjustInventory: (orderId, data = {}) => {
    return request.post(`${API_BASE}/material-count-orders/${orderId}/adjust`, data);
  },

  // 导出盘点单
  exportCountOrder: (id) => {
    return request.get(`${API_BASE}/material-count-orders/${id}/export`, {
      responseType: 'blob'
    });
  },

  // 导出盘点单列表
  exportCountOrderList: (params = {}) => {
    return request.get(`${API_BASE}/material-count-orders/export`, {
      params,
      responseType: 'blob'
    });
  }
};

// 基础数据相关API
export const baseDataService = {
  // 获取仓库选项（只获取材料仓库）
  getWarehouses: (params = {}) => {
    return request.get('/tenant/base-archive/production-archive/warehouses/options', { 
      params: { ...params, warehouse_type: 'material' }
    });
  },

  // 获取材料选项
  getMaterials: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/material-management', { params });
  },

  // 获取部门选项
  getDepartments: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/departments/options', { params });
  },

  // 获取员工选项
  getEmployees: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/employees/options', { params });
  },

  // 获取单位选项
  getUnits: () => {
    return request.get('/tenant/base-archive/production-archive/units/options');
  }
};

// 库存相关API
export const inventoryService = {
  // 获取库存列表
  getInventoryList: (params = {}) => {
    return request.get('/tenant/business/inventory/inventories', { params });
  },

  // 获取库存详情
  getInventoryById: (id) => {
    return request.get(`/tenant/business/inventory/inventories/${id}`);
  },

  // 获取仓库材料库存
  getWarehouseMaterialInventory: (warehouseId) => {
    return request.get(`/tenant/business/inventory/inventories?warehouse_id=${warehouseId}`);
  },

  // 获取库存事务记录
  getInventoryTransactions: (params = {}) => {
    return request.get('/tenant/business/inventory/inventory-transactions', { params });
  },

  // 调整库存
  adjustInventory: (data) => {
    return request.post('/tenant/business/inventory/inventories/adjust', data);
  }
};

// 报表相关API
export const reportService = {
  // 获取盘点统计报表
  getCountStatistics: (params = {}) => {
    return request.get(`${API_BASE}/reports/count-statistics`, { params });
  },

  // 获取库存统计报表
  getInventoryStatistics: (params = {}) => {
    return request.get('/tenant/business/inventory/reports/inventory-statistics', { params });
  },

  // 导出盘点报表
  exportCountReport: (params = {}) => {
    return request.get(`${API_BASE}/reports/export`, {
      params,
      responseType: 'blob'
    });
  }
};

// 保持向后兼容的别名
export const materialCountApi = materialCountService;

// 默认导出
export default {
  materialCountService,
  baseDataService,
  inventoryService,
  reportService
}; 